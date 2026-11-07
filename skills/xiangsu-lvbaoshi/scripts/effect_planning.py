"""Enumerate production candidates and audit authored semantic/material decisions."""
import argparse
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
VERSION = 'glass-lime-editorial-effect-planning/v1'


def fail(message):
    raise ValueError('Effect planning: ' + message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def catalog(selection=None):
    items=json.loads((SKILL/'references/effect-catalog.json').read_text(encoding='utf-8'))
    excluded={'L19','L27','L28','L30','L31'}
    rows=[dict(id='effect:'+x['id'],group=x['group'],reference='plan-format.md',trigger=x['trigger'],match={'templateId':x['id']},objectRole='none' if x['id'] in excluded else 'paired',baseWeight=1) for x in items]
    for ident,kind in [('route:animation','animation'),('route:interface','interface'),('route:screen','screen'),('route:media','media')]:
        rows.append(dict(id=ident,group='制作路线',reference='plan-format.md',trigger=kind+' 完整主画面',match={'kind':kind, **({'producer':'mav-mg'} if kind=='animation' else {})},objectRole='paired' if kind=='animation' else 'none',baseWeight=1))
    rows.append(dict(id='animation:lemo-opuscar',group='制作路线',reference='animation-routing.md',trigger='情境、隐喻、表演、产品空间与风格化机制解释',match={'kind':'animation','producer':'lemo-opuscar'},objectRole='style-owned',baseWeight=1))
    rows.append(dict(id='finish:host-edge-shadow',group='背景修饰',reference='host-edge-shadow.md',trigger='真人边缘收光',match={'hostFinish.enabled':True},objectRole='none',baseWeight=1))
    rows.append(dict(id='display:cinema',group='素材与动画画框',reference='material-display.md',trigger='白金22号窄暖白电影画框：图片、视频素材或完整MG动画可选展映',match={'display.style':'cinema'},objectRole='none',baseWeight=1))
    rows.append(dict(id='navigation:progress',group='导航',reference='navigation-progress.md',
                     trigger='按真实章节时长常驻全片进度（A 银灰磨砂分章底栏）',
                     match={'navigation.progress':True},objectRole='none',baseWeight=1))
    from roll_transitions import STYLES
    for style in STYLES:
        rows.append(dict(id='roll:'+style,group='主画面与B-roll转场',reference='roll-transitions.md',
                         trigger='真人 ↔ 完整MG／素材双向交接；两款均可由编排自行选择',
                         match={'rollTransitionStyle':style},objectRole='none',baseWeight=1))
    from production_layers import specifications
    rows.extend({**s,'reference':'production-layers.md','baseWeight':1} for s in specifications())
    rows.append(dict(id='exit:domain-warp',group='局部退出材质',reference='plan-format.md',
                     trigger='B/D入场的实际前景，在阅读完成后局部扭曲并溶解至透明',
                     match={'exitMotion':'domain-warp'},objectRole='none',baseWeight=1))
    return rows


DEFAULTS = {}


def value(entry, path):
    current = entry
    for key in path.split('.'):
        if not isinstance(current, dict) or key not in current:
            return DEFAULTS.get(path)
        current = current[key]
    return current


def entries(plan):
    from animation_contract import provider as animation_provider
    result = {}
    producers = {ref: ('mav-mg' if segment['producer'] == 'xiangsu-mg' else segment['producer']) for segment in plan.get('orchestration', {}).get('segments', [])
                 for ref in segment.get('beatIds', [])}
    for field in ('effects', 'beats'):
        for entry in plan.get(field, []):
            result[field+':'+entry['id']] = {**entry, 'producer': ('mav-mg' if animation_provider(entry) == 'xiangsu-mg' else animation_provider(entry)) if field == 'beats' and entry.get('kind') == 'animation' else producers.get(entry['id']) if field == 'beats' else None}
    result['plan'] = plan
    for field,kind in [('screenEffects','screen'),('companions','companion'),('editorialScenes','reference')]:
        for entry in plan.get(field,[]):result[field+':'+entry['id']]={**entry,'nativeKind':kind}
    from roll_transitions import entries as handoffs
    for item in handoffs(plan):
        result['rollTransitions:'+item['id']]={**item,'rollTransitionStyle':item['style']}
    return result


def selected(plan, choices):
    from navigation import effective_plan
    plan = effective_plan(plan)
    selected_ids = {}
    for choice in choices:
        refs = []
        for ref, entry in entries(plan).items():
            if ref == 'plan' and not any(k.startswith(('navigation.', 'hostFinish.')) for k in choice['match']):
                continue
            if choice['id'].startswith('screen:') and not (ref.startswith('screenEffects:') or entry.get('kind') == 'screen'):
                continue
            if all(bool(value(entry, key)) if expected == 'nonempty' else value(entry, key) == expected
                   for key, expected in choice['match'].items()):
                refs.append(ref)
        if refs:
            selected_ids[choice['id']] = refs
    return selected_ids


def usage(plan, choices, uses, decisions):
    """Expose every candidate, including zero-use alternatives, without auto-picking."""
    execution=entries(plan)
    def seconds(entry):
        if 'start' in entry and 'end' in entry:return max(0,entry['end']-entry['start'])
        return max(0,entry.get('duration',0))
    config=json.loads((SKILL/'references/motion.json').read_text(encoding='utf-8'))
    candidates=[]
    for choice in choices:
        refs=uses.get(choice['id'],[]);decision=decisions.get(choice['id'],{})
        total=len(refs)*config['exitTreatments']['domain-warp']['durationSec'] if choice['id']=='exit:domain-warp' else sum(seconds(execution[r]) for r in refs)
        candidates.append(dict(id=choice['id'],count=len(refs),seconds=round(total,3),
            alternativeSegmentIds=decision.get('segmentIds',[]) if not refs and decision.get('decision')=='considered' else []))
    motions=[]
    for variant in config['variants']:
        refs=[ref for ref,e in execution.items() if ref.startswith(('effects:','beats:')) and e.get('motion')==variant['id']]
        motions.append(dict(id=variant['id'],name=variant['name'],count=len(refs),seconds=round(sum(seconds(execution[r]) for r in refs),3)))
    return dict(candidates=candidates,motions=motions,motionPolicy=config.get('selectionPolicy',{}))


def image_paths(entry):
    """Only actual image slots; labels, source notes and review text do not count."""
    paths = []
    if not isinstance(entry, dict):
        return paths
    if entry.get('templateId') == 'side-glow-media':
        content = entry.get('content', {})
        side = content.get('side')
        return [content[key] for key, enabled in (('leftAsset', side in {'left', 'both'}),
                ('rightAsset', side in {'right', 'both'})) if enabled and text(content.get(key))]
    for key, item in entry.items():
        if key in {'image', 'rightImage', 'replacementImage', 'leftAsset', 'rightAsset', 'localImage'} and text(item):
            paths.append(item)
        elif key in {'localImages', 'stepImages', 'images'} and isinstance(item, list):
            paths.extend(item)
        elif key in {'content', 'items', 'left', 'right'}:
            for child in item if isinstance(item, list) else [item]:
                paths.extend(image_paths(child))
    if text(entry.get('asset')):paths.append(entry['asset'])
    return paths


def validate_asset(project, path, entry, source_id='pixel2all'):
    project = Path(project).resolve()
    file = (project/path).resolve()
    if not file.is_relative_to(project) or not file.is_file() or file.suffix.lower() != '.png':
        fail('Object binding needs a local project PNG: '+path)
    data = file.read_bytes()
    if len(data) < 26 or data[:8] != b'\x89PNG\r\n\x1a\n' or not int.from_bytes(data[16:20], 'big') or not int.from_bytes(data[20:24], 'big'):
        fail('Object binding has an invalid PNG header: '+path)
    from object_assets import validate_credit
    validate_credit(project, path, source_id)
    if entry.get('kind') == 'animation':
        source = (project/entry['editableSource']).resolve()
        if not file.is_relative_to(source) or not source.is_relative_to(project):
            fail('animation object must belong to its editableSource')
        # A source reference is a sanity check, never visual/runtime proof.
        if not any(source_mentions(f, file.name) for f in source.rglob('*')
                   if f.is_file() and f.suffix.lower() in {'.html', '.js', '.mjs'} and 'node_modules' not in f.parts):
            fail('animation object has no executable source reference: '+path)


def source_mentions(file, name):
    source = file.read_text(encoding='utf-8-sig')
    # Strip comments while preserving quoted URLs/strings. Dynamic load/visibility
    # still needs 像素 MG's frame/seek review; do not label this check as that review.
    pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|<!--[\s\S]*?-->|/\*[\s\S]*?\*/|//[^\r\n]*'
    source = re.sub(pattern, lambda m: '' if m.group().startswith(('<!--', '/*', '//')) else m.group(), source)
    return name in source


def material_fields(plan, lock=None):
    if 'thiingsReview' in plan.get('orchestration', {}):fail('像素·绿宝石 uses objectReview and Pixel2All')
    return 'objectReview', 'objectMajorityException', 'pixel2all'


def audit(plan, required=False, draft=False, project=None, lock=None):
    choices = catalog()
    # Historical freezes do not acquire new visuals or mandatory new reviews.
    if lock is not None and not lock.get('rollTransitionsVersion') and 'rollTransitions' not in plan:
        choices = [c for c in choices if not c['id'].startswith('roll:')]
    reviews = (plan.get('orchestration') or {}).get('candidateReview') or []
    reviewed = {c for row in reviews if isinstance(row,dict) for c in row.get('candidateIds',[]) if isinstance(c,str)}
    if lock is not None and not lock.get('animationRoutingVersion') and 'animation:lemo-opuscar' not in reviewed and not any(b.get('provider') == 'lemo-opuscar' for b in plan.get('beats', [])):
        choices = [c for c in choices if c['id'] != 'animation:lemo-opuscar']
    by_id = {x['id']: x for x in choices}
    from navigation import effective_plan
    from roll_transitions import resolve
    selection_plan = resolve(effective_plan(plan, lock), lock)
    uses = selected(selection_plan, choices)
    orchestration = plan.get('orchestration') or {}
    segment_ids = {s['id'] for s in orchestration.get('segments', [])}
    review = orchestration.get('candidateReview')
    decisions = {}
    if required and not isinstance(review, list):
        fail('new plans require orchestration.candidateReview')
    if review is not None:
        if not isinstance(review, list):
            fail('candidateReview must be a list')
        for row in review:
            if not isinstance(row, dict) or set(row) != {'candidateIds', 'decision', 'segmentIds', 'reason'}:
                fail('candidate review needs candidateIds, decision, segmentIds and reason')
            ids, segments = row['candidateIds'], row['segmentIds']
            if not isinstance(ids, list) or not ids or not isinstance(segments, list) or any(not text(s) or s not in segment_ids for s in segments):
                fail('candidate review needs known candidates/segments')
            if row['decision'] not in {'considered', 'inapplicable', 'unavailable'} or not text(row['reason']):
                fail('candidate review needs a concrete semantic/input reason')
            if row['decision'] == 'considered' and not segments:
                fail('considered candidates need narration segments')
            for ident in ids:
                if not text(ident) or ident not in by_id or ident in decisions:
                    fail('unknown or duplicate reviewed candidate')
                if ident in uses and row['decision'] != 'considered':
                    fail('selected candidate cannot be declared inapplicable/unavailable: '+ident)
                decisions[ident] = row
    missing = sorted(set(by_id)-set(uses)-set(decisions))
    if required and missing and not draft:
        fail('unreviewed candidates: '+', '.join(missing))
    eligible_entries = {ref for ident, refs in uses.items() if by_id[ident]['objectRole'] in {'native', 'paired'} for ref in refs}
    native_entries = {ref for ident, refs in uses.items() if by_id[ident]['objectRole'] == 'native' for ref in refs}
    review_field, exception_field, source_id = material_fields(plan, lock)
    material_review = orchestration.get(review_field)
    if required and not isinstance(material_review, list):
        fail('plans require orchestration.'+review_field)
    material_review = material_review if material_review is not None else []
    if not isinstance(material_review, list):
        fail(review_field+' must be a list')
    assigned, used, exceptions, pending = set(), 0, 0, 0
    execution = entries(plan)
    for row in material_review:
        if not isinstance(row, dict) or set(row) != {'entryIds', 'decision', 'searchTerms', 'bindings', 'reason'}:
            fail('Object review needs entryIds, decision, searchTerms, bindings and reason')
        refs, bindings = row['entryIds'], row['bindings']
        if not isinstance(refs, list) or not refs or any(not text(r) or r not in eligible_entries or r in assigned for r in refs) or len(refs) != len(set(refs)):
            fail('Object review needs unique eligible expression entries')
        assigned.update(refs)
        if not text(row['reason']) or row['decision'] not in {'used', 'exception', 'pending'}:
            fail('Object decision needs an actual use or concrete exception')
        if not isinstance(row['searchTerms'], list) or any(not text(t) for t in row['searchTerms']) or not isinstance(bindings, list):
            fail('invalid Object search terms/bindings')
        if row['decision'] == 'used':
            if not bindings:
                fail('used Object must bind actual execution assets')
            if any(not isinstance(b, dict) or set(b) != {'entryId', 'path'} or not text(b['entryId']) for b in bindings):
                fail('binding needs an execution entryId and path')
            bound_entries = {b['entryId'] for b in bindings}
            if not (set(refs) & native_entries) <= bound_entries:
                fail('each native expression needs its own Object binding; record other entries as exceptions')
            # A paired expression and its object must share an authored semantic window.
            owners = [set('effects:'+r for r in s.get('effectIds', [])) |
                      set('beats:'+r for r in s.get('beatIds', [])) |
                      set(ref for ref,entry in entries(plan).items() if entry.get('id') in s.get('layerIds',[])) for s in orchestration.get('segments', [])]
            if not any(set(refs) <= owner for owner in owners):
                fail('paired expressions must share a narration segment')
            for binding in bindings:
                if not isinstance(binding, dict) or set(binding) != {'entryId', 'path'} or binding['entryId'] not in refs:
                    fail('binding must belong to its expression entries')
                path = binding['path']
                if not text(path) or ':' in path or '\\' in path or Path(path).is_absolute() or '..' in Path(path).parts:
                    fail('binding needs a project-relative path')
                entry = execution[binding['entryId']]
                animation = entry.get('kind') == 'animation' and text(entry.get('editableSource')) and path.startswith(entry['editableSource'].rstrip('/')+'/')
                if path not in image_paths(entry) and not animation:
                    fail('search result is not an actual execution image slot: '+path)
                if project is not None:
                    validate_asset(project, path, entry, source_id)
            used += 1
        else:
            if bindings:
                fail('exception/pending cannot claim used asset bindings')
            if row['decision'] == 'pending':
                pending += 1
                if not draft:
                    fail('unresolved Object material decision')
            else:
                exceptions += 1
    missing_material = sorted(eligible_entries-assigned)
    if required and missing_material and not draft:
        fail('unreviewed Object expressions: '+', '.join(missing_material))
    warnings = []
    if missing:
        warnings.append('候选尚未全量评估；未使用不等于不适用。')
    if missing_material:
        warnings.append('适用表达尚未记录物件 使用或例外。')
    if used+exceptions and used <= exceptions:
        reason = orchestration.get(exception_field)
        if not text(reason):
            if required:
                fail('Objects should serve most expression windows; explain '+exception_field+' for this narration')
            warnings.append('物件未覆盖多数适用表达窗；需要整片语义/素材例外说明。')
    result = {'version': (lock or {}).get('effectPlanningVersion', VERSION), 'sourceId': source_id, 'candidateCount': len(choices), 'selected': uses,
            'decisions': decisions, 'unreviewed': missing, 'thiingsUsedWindows': used,
            'thiingsExceptionWindows': exceptions, 'thiingsPendingWindows': pending,
            'unreviewedThiingsEntries': missing_material, 'warnings': warnings}
    result['usage']=usage(selection_plan,choices,uses,decisions)
    if source_id != 'thiings':
        for old, new in [('thiingsUsedWindows', 'objectUsedWindows'), ('thiingsExceptionWindows', 'objectExceptionWindows'),
                         ('thiingsPendingWindows', 'objectPendingWindows'), ('unreviewedThiingsEntries', 'unreviewedObjectEntries')]:
            result[new] = result.pop(old)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', action='store_true')
    parser.add_argument('--plan')
    parser.add_argument('--project', help='Also verify actual Object files/source SHA')
    parser.add_argument('--strict', action='store_true', help='Require every candidate/material decision')
    parser.add_argument('--draft', action='store_true')
    args = parser.parse_args()
    if args.catalog:
        result = catalog()
    elif args.plan:
        lock = json.loads((Path(args.project)/'input-lock.json').read_text(encoding='utf-8-sig')) if args.project else None
        result = audit(json.loads(Path(args.plan).read_text(encoding='utf-8-sig')),
                       required=args.strict, draft=args.draft, project=args.project, lock=lock)
    else:
        parser.error('pass --catalog or --plan')
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
