"""Approved bidirectional host/B-roll handoffs, resolved before assembly."""
from copy import deepcopy
import hashlib
import json
import re
from prepare import SKILL, read, dump, sha

ASSETS = 'assets/glass-lime/roll-transitions'
PRESET = read(SKILL/'assets/roll-transitions/preset.json')
VERSION = PRESET['version']
STYLES = tuple(PRESET['durations'])
EPS = .001


def resolve(plan, lock=None):
    version = (lock or {}).get('rollTransitionsVersion')
    if version not in (None, VERSION):
        raise ValueError('Unsupported roll transitions version')
    if 'rollTransitions' in plan or not version:
        return plan
    result = deepcopy(plan)
    result['rollTransitions'] = {'default': 'auto', 'beats': {}}
    return result


def config(plan):
    cfg = plan.get('rollTransitions', False)
    if cfg is False:
        return None
    if not isinstance(cfg, dict) or set(cfg)-{'default', 'beats'}:
        raise ValueError('rollTransitions needs {default:auto|glass-slide|lime-leak, beats:{id:style|false}} or false')
    default = cfg.get('default', 'auto')
    overrides = cfg.get('beats', {})
    if not isinstance(default, str) or default not in ('auto', *STYLES) or not isinstance(overrides, dict):
        raise ValueError('Invalid rollTransitions default/beat overrides')
    known = {b['id'] for b in plan.get('beats', [])}
    if any(k not in known or (v is not False and (not isinstance(v, str) or v not in STYLES)) for k, v in overrides.items()):
        raise ValueError('Roll transition overrides need known beat IDs and approved styles or false')
    return {'default': default, 'beats': overrides}


def style_for(beat, cfg):
    selected = cfg['beats'].get(beat['id'], cfg['default'])
    if selected == 'auto':
        # A discretionary fallback must remain stable across compile/render/seek.
        index = int(hashlib.sha256(beat['id'].encode('utf-8')).hexdigest()[:8], 16) % len(STYLES)
        return STYLES[index]
    return selected


def entries(plan):
    cfg = config(plan)
    if cfg is None:
        return []
    result = []
    beats = plan.get('beats', [])
    for i, beat in enumerate(beats):
        style = style_for(beat, cfg)
        if style is False:
            continue
        duration = PRESET['durations'][style]
        for incoming, cut in ((True, beat['start']), (False, beat['end'])):
            neighbor = (beats[i-1]['end'] if i else None) if incoming else (beats[i+1]['start'] if i+1 < len(beats) else None)
            # Only A/B boundaries. B/B cuts and film starts/ends are not handoffs.
            if cut <= EPS or cut >= plan['duration']-EPS or (neighbor is not None and abs(cut-neighbor) < EPS):
                continue
            result.append(dict(id=beat['id']+('-in' if incoming else '-out'), beatId=beat['id'],
                               direction='A-to-B' if incoming else 'B-to-A', style=style, cut=cut,
                               start=round(cut-duration/2, 4), end=round(cut+duration/2, 4), duration=duration))
    return sorted(result, key=lambda item: item['start'])


def owns_entry(plan, beat):
    return any(e['beatId'] == beat['id'] and e['direction'] == 'A-to-B' for e in entries(plan))


def validate(p, plan, lock):
    # Check configuration even when the plan contains no boundaries.
    items = entries(plan)
    if not items:
        return
    reserved = {plan['id']} | {e['id'] for name in ('beats', 'effects', 'screenEffects', 'companions', 'editorialScenes') for e in plan.get(name, [])}
    if any(name.startswith('gl-roll-') for name in reserved):
        raise ValueError('gl-roll- IDs are reserved for B-roll handoffs')
    for name in ('preset.json', 'runtime.js', 'style.css', 'dust.svg', 'grain.svg'):
        path = p/ASSETS/name
        rel = 'roll-transitions/'+name
        if not path.is_file() or lock.get('resources', {}).get(rel) != sha(path) or sha(path) != sha(SKILL/'assets'/rel):
            raise ValueError('Frozen roll transition asset missing/changed; prepare a new project: '+name)
    for item in items:
        if item['start'] < 0 or item['end'] > plan['duration']:
            raise ValueError('Roll transition needs a full boundary window; replan or explicitly disable this beat')
    for a, b in zip(items, items[1:]):
        if a['end'] > b['start']+EPS:
            raise ValueError('Roll transition windows overlap; replan the short host/B-roll gap')
    for beat in plan.get('beats', []):
        windows = [x['duration']/2 for x in items if x['beatId'] == beat['id']]
        if windows and beat['end']-beat['start'] < sum(windows)+PRESET['minimumHoldSec']-EPS:
            raise ValueError('Roll transition must leave a readable B-roll hold')


def assemble(source, layers, plan):
    """Untimed visual shells keep media timing framework-owned, including annotations."""
    if not entries(plan):
        return source+''.join(layers)
    beats = {b['id']: [] for b in plan.get('beats', [])}
    host_ids = {e['id'] for name in ('effects', 'companions', 'editorialScenes') for e in plan.get(name, [])}
    targets = {e['id']: e['targetBeat'] for e in plan.get('screenEffects', [])}
    host, global_layers = [source], []
    for layer in layers:
        match = re.search(r'\bid="slot-([a-z0-9-]+)"', layer)
        ident = match.group(1) if match else None
        if ident in beats:
            beats[ident].append(layer)
        elif ident in targets:
            beats[targets[ident]].append(layer)
        elif ident in host_ids or re.match(r'<div id="finish-\d+"', layer):
            host.append(layer)
        else:
            global_layers.append(layer)
    wrapped = '<div id="gl-roll-host" class="gl-roll-visual" style="z-index:0">'+''.join(host)+'</div>'
    for ident, nodes in beats.items():
        if not nodes:
            raise ValueError('Roll transition beat has no assembled visual: '+ident)
        wrapped += f'<div id="gl-roll-visual-{ident}" class="gl-roll-visual" style="z-index:20">'+''.join(nodes)+'</div>'
    return wrapped+''.join(global_layers)


def compile_layers(p, plan):
    items = entries(plan)
    if not items:
        return [], '', '', ''
    layers, motion = [], []
    for item in items:
        key = 'gl-roll-'+item['id']
        layers.append(f'''<div id="{key}-blank" class="gl-roll-blank" data-layout-ignore></div>
<div id="{key}" class="gl-roll-fx {item['style']}" data-layout-ignore><div class="slide-rim"></div><div class="lime-sweep"></div>
<div class="film-fx"><div class="film-dim"></div><div class="film-vignette"></div><div class="film-gate"></div><div class="film-grain"></div><div class="film-dust"></div>
<svg class="film-scratches" viewBox="0 0 1920 1080"><path d="M182,20L188,1060M1672,0L1668,1080M1455,125L1458,970" stroke="#e2dbc7" stroke-width="1.3" opacity=".68" fill="none"/></svg><div class="film-leak"></div><div class="film-flash"></div></div></div>''')
        args = [item['style'], '#gl-roll-host', '#gl-roll-visual-'+item['beatId'], '#'+key,
                '#'+key+'-blank', item['cut'], item['duration'], item['direction'] == 'A-to-B']
        motion.append('GLRollTransition.apply(tl,'+','.join(json.dumps(x) for x in args)+');')
    css = (p/ASSETS/'style.css').read_text(encoding='utf-8')
    script = f'<script src="{ASSETS}/runtime.js"></script>'
    return layers, ''.join(motion), css, script


def record(p, plan):
    items = entries(plan)
    # Always save the effective choice: an auto fallback cannot drift on re-render.
    effective = deepcopy(plan)
    cfg = config(plan)
    if cfg is not None:
        effective['rollTransitions'] = {'default': cfg['default'], 'beats': {
            b['id']: style_for(b, cfg) for b in plan.get('beats', [])}}
    dump(p/'effective-plan.json', effective)
    report = read(p/'build-report.json')
    report['rollTransitions'] = dict(version=VERSION, entries=items, config=cfg,
        assetSha256={name: sha(p/ASSETS/name) for name in ('preset.json', 'runtime.js', 'style.css', 'dust.svg', 'grain.svg')} if items else {},
        sourceTimeTreatment='unchanged; no extra media handles or duplicated frames', voiceTreatment='unchanged continuous original track',
        selectionStatus='both recipes approved 2026-10-18; per-beat choice delegated', visualApproval='recipes approved; each film still needs preview')
    dump(p/'build-report.json', report)
