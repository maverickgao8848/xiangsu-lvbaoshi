"""Validate decisions in edit-plan and derive their editorial review table."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import effect_planning

VERSION = 'glass-lime-editorial-orchestration/v1'
GENERATED_NOTICE = '此文件由 edit-plan.json 生成；修改该计划后重新生成。它不代表视觉或用户审核通过。'
# Assembly routes, not additional renderer/effect IDs.
ROUTES = {
    ('host', 'editorial'): ('人物表达与重点强调', set()),
    ('data', 'editorial'): ('用户提供的数字证据阅读', {'evidence', 'material', 'explanation','editorial'}),
    ('dialogue', 'scene-kit'): ('对话与界面情境', {'interface'}),
    ('evidence', 'editorial'): ('证据阅读', {'evidence', 'material', 'explanation','editorial'}),
    ('illustration', 'editorial'): ('实物、例子与情境', {'media', 'material', 'broll','editorial'}),
    ('mechanism', 'mav-mg'): ('机制、关系与流程', {'animation'}),
    ('mechanism', 'xiangsu-mg'): ('机制、关系与流程', {'animation'}),
    ('mechanism', 'lemo-opuscar'): ('按所选风格表现机制与空间过程', {'animation'}),
    ('illustration', 'lemo-opuscar'): ('风格化情境、隐喻、表演与产品叙事', {'animation'}),
    ('operation', 'editorial'): ('真实操作演示', {'screen','editorial'}),
}
EPS = .001


def fail(message):
    raise ValueError('Orchestration: ' + message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def references(segment, key, available):
    refs = segment.get(key)
    if not isinstance(refs, list) or any(not text(x) for x in refs):
        fail(f'{segment["id"]}.{key} must be a list of IDs')
    if len(refs) != len(set(refs)) or any(x not in available for x in refs):
        fail(f'{segment["id"]}.{key} contains duplicate or unknown IDs')
    return refs


def validate(plan, lock=None, draft=False):
    """Drafts can expose missing assets; compilation needs complete coverage."""
    required = (lock or {}).get('orchestrationVersion')
    if required not in (None, VERSION):
        fail('unsupported input-lock orchestration version')
    orchestration = plan.get('orchestration')
    if orchestration is None:
        if (required and plan.get('fixture') is not True) or draft:
            fail('new inputs require an authored orchestration in edit-plan')
        return None  # Historical freezes and explicit module fixtures remain untouched.
    if not isinstance(orchestration, dict) or orchestration.get('version') != VERSION:
        fail('unsupported orchestration version')
    duration = plan.get('duration')
    if not finite(duration) or duration <= 0:
        fail('invalid plan duration')
    if lock and (not finite(lock.get('duration')) or abs(duration-lock['duration']) > .02):
        fail('plan/source duration mismatch')
    segments = orchestration.get('segments')
    if not isinstance(segments, list) or not segments:
        fail('segments must cover complete narration, including clean host passages')
    indexed = {}
    for key in ('beats', 'effects'):
        entries = plan.get(key, [])
        if not isinstance(entries, list) or any(not isinstance(x, dict) or not text(x.get('id')) for x in entries):
            fail(f'invalid {key}')
        indexed[key] = {x['id']: x for x in entries}
        if len(indexed[key]) != len(entries):
            fail(f'duplicate {key} IDs')
        for item in entries:
            if not all(finite(item.get(k)) for k in ('start', 'end')) or not 0 <= item['start'] < item['end'] <= duration:
                fail(f'invalid {key} time range')
    beat_owners, effect_uses, ids, missing = Counter(), set(), set(), []
    previous = 0
    for segment in segments:
        if not isinstance(segment, dict):
            fail('segment must be an object')
        ident = segment.get('id')
        if not text(ident) or not re.fullmatch('[a-z0-9-]+', ident) or ident in ids:
            fail('invalid or duplicate segment ID')
        ids.add(ident)
        start, end = segment.get('start'), segment.get('end')
        if not finite(start) or not finite(end) or not 0 <= start < end <= duration or abs(start-previous) > EPS:
            fail(f'{ident}: segment ranges must be ordered, contiguous and within duration')
        previous = end
        if not all(text(segment.get(k)) for k in ('narration', 'purpose', 'entry', 'exit')):
            fail(f'{ident}: narration, purpose, entry and exit need concrete descriptions')
        scenario, producer = segment.get('scenario'), segment.get('producer')
        if not text(scenario) or not text(producer) or (scenario, producer) not in ROUTES:
            fail(f'{ident}: unsupported scenario/producer route')
        allowed = ROUTES[(scenario, producer)][1]
        inputs = segment.get('inputs')
        if not isinstance(inputs, list):
            fail(f'{ident}: inputs must be a list')
        for item in inputs:
            if not isinstance(item, dict) or not text(item.get('need')) or item.get('status') not in ('ready', 'missing'):
                fail(f'{ident}: inputs require need and ready/missing status')
            if item['status'] == 'missing':
                missing.append(f'{ident}: {item["need"]}')
        if not draft and any(item['status'] == 'missing' for item in inputs):
            fail(f'{ident}: unresolved inputs prevent compilation')
        beat_ids = references(segment, 'beatIds', indexed['beats'])
        effect_ids = references(segment, 'effectIds', indexed['effects'])
        selected = sorted((indexed['beats'][x] for x in beat_ids), key=lambda b: b['start'])
        if scenario == 'host' and selected:
            fail(f'{ident}: host passages use source picture and effects, not main-picture beats')
        for beat in selected:
            if not text(beat.get('kind')) or beat['kind'] not in allowed:
                fail(f'{ident}: beat kind does not match the selected route')
            if beat['start'] < start-EPS or beat['end'] > end+EPS:
                fail(f'{ident}: beat outside its segment')
            from animation_contract import check_owner
            check_owner(segment, beat)
            beat_owners[beat['id']] += 1
        if scenario != 'host' and not draft:
            cursor = start
            for beat in selected:
                if abs(beat['start']-cursor) > EPS:
                    fail(f'{ident}: main-picture beats must cover the selected segment')
                cursor = beat['end']
            if abs(cursor-end) > EPS:
                fail(f'{ident}: main-picture beats must cover the selected segment')
        for ref in effect_ids:
            effect = indexed['effects'][ref]
            if effect['start'] >= end or effect['end'] <= start:
                fail(f'{ident}: effect does not overlap its segment')
            effect_uses.add(ref)
    if abs(previous-duration) > EPS:
        fail('segments must cover complete narration')
    if set(beat_owners) != set(indexed['beats']) or any(count != 1 for count in beat_owners.values()):
        fail('each main-picture beat needs exactly one segment owner')
    if effect_uses != set(indexed['effects']):
        fail('each authored effect needs a segment reference')
    planning_version = (lock or {}).get('effectPlanningVersion')
    if planning_version not in (None, effect_planning.VERSION):
        fail('unsupported effect planning version')
    planning = effect_planning.audit(plan, required=bool(planning_version) and plan.get('fixture') is not True, draft=draft, lock=lock)
    return {'version': VERSION, 'stage': 'draft' if draft else 'assembly-ready',
            'segments': len(segments), 'missingInputs': missing, 'effectPlanning': planning}


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')


def markdown(plan, summary):
    lines = ['# 像素·绿宝石 Editorial 编排表', '',
             GENERATED_NOTICE, '',
             f'编排版本：{VERSION}；阶段：{summary["stage"]}；输入缺口：{len(summary["missingInputs"])} 项。', '',
             '| 时段 / 段落 | 口播锚点与观看目的 | 主画面 / 制作方 | 执行引用 | 输入状态 | 进入 → 退出 |',
             '|---|---|---|---|---|---|']
    for segment in plan['orchestration']['segments']:
        route = (segment['scenario'], segment['producer'])
        inputs = '\n'.join(f'{x["status"]}: {x["need"]}' for x in segment['inputs']) or '沿用已冻结输入'
        refs = 'beats: ' + ', '.join(segment['beatIds']) + '\neffects: ' + ', '.join(segment['effectIds'])
        if segment.get('layerIds'):refs += '\nnative layers: ' + ', '.join(segment['layerIds'])
        row = [f'{segment["start"]:g}–{segment["end"]:g}s / {segment["id"]}',
               segment['narration'] + '\n目的：' + segment['purpose'],
               ROUTES[route][0] + '\n' + segment['producer'], refs, inputs,
               segment['entry'] + ' → ' + segment['exit']]
        lines.append('| ' + ' | '.join(cell(x) for x in row) + ' |')
    lines += ['', '字幕、导航、人物窗和声音读取同一 edit-plan 的原字段；本表不复制它们的参数。', '']
    planning = summary['effectPlanning']
    legacy = planning['sourceId'] == 'thiings'
    prefix = 'thiings' if legacy else 'object'
    review_field = 'thiingsReview' if legacy else 'objectReview'
    exception_field = 'thiingsMajorityException' if legacy else 'objectMajorityException'
    lines += ['## 候选覆盖与物件', '',
              f'可规划候选：{planning["candidateCount"]}；未评估：{len(planning["unreviewed"])}。',
              f'物件表达窗：实际使用 {planning[prefix+"UsedWindows"]}；具体例外 {planning[prefix+"ExceptionWindows"]}；待补 {planning[prefix+"PendingWindows"]}。', '',
              '| 候选 / 能力组 | 语义触发 | 次数 / 窗口秒数 | 规划结论 | 物件分工 |', '|---|---|---|---|---|']
    usage={row['id']:row for row in planning['usage']['candidates']}
    for choice in effect_planning.catalog():
        ident = choice['id']
        if ident not in usage:continue  # New candidates are absent from historical freezes.
        if ident in planning['selected']:
            decision = '已使用：' + ', '.join(planning['selected'][ident])
        elif ident in planning['decisions']:
            row = planning['decisions'][ident]
            decision = row['decision'] + ': ' + row['reason']
        else:
            decision = '待评估（不能自动当作不适用）'
        row=usage[ident]
        if row['alternativeSegmentIds']:decision+='；可替代段：'+', '.join(row['alternativeSegmentIds'])
        lines.append('| ' + ' | '.join(cell(x) for x in [ident+' / '+choice['group'], choice['trigger'], f'{row["count"]} / {row["seconds"]:g}s', decision, choice['objectRole']]) + ' |')
    lines+=['','### 入退场使用分布','','B/D高频只影响动作选择；模板、参考配方和制作路线按语义与必要输入公平比较。',
            '| 动作 | 次数 | 窗口秒数 |','|---|---|---|']
    for row in planning['usage']['motions']:
        lines.append(f'| {cell(row["id"]+" / "+row["name"])} | {row["count"]} | {row["seconds"]:g}s |')
    lines += ['', *[cell(x) for x in planning['warnings']], '']
    for row in plan['orchestration'].get(review_field, []):
        lines.append('- ' + cell(', '.join(row['entryIds']) + ' → ' + row['decision'] + ': ' + row['reason']))
        for binding in row['bindings']:
            lines.append('  - ' + cell(binding['entryId'] + ' → ' + binding['path']))
    if plan['orchestration'].get(exception_field):
        lines += ['', '本片多数例外：' + cell(plan['orchestration'][exception_field])]
    from roll_transitions import entries as handoffs
    transitions=handoffs(plan)
    if transitions:
        lines+=['','## 主画面 ↔ B-roll 转场','','| 切点 | 方向 | B-roll | 配方 | 时窗 |','|---|---|---|---|---|']
        for e in transitions:
            lines.append(f'| {e["cut"]:g}s | {e["direction"]} | {cell(e["beatId"])} | {cell(e["style"])} | {e["start"]:g}–{e["end"]:g}s |')
    return '\n'.join(lines)


def write(project, plan, summary):
    (Path(project)/'ORCHESTRATION.md').write_text(markdown(plan, summary), encoding='utf-8')


def record(project, plan):
    summary = validate(plan)
    if summary is None:
        table = Path(project)/'ORCHESTRATION.md'
        if table.is_file() and GENERATED_NOTICE in table.read_text(encoding='utf-8'):
            table.unlink()  # Only remove this generator's obsolete view.
        return
    write(project, plan, summary)
    report_path = Path(project)/'build-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report['orchestration'] = {**summary, 'reviewTable': 'ORCHESTRATION.md',
        'planSha256': hashlib.sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--draft', action='store_true', help='Expose missing inputs before production; not compiler validation')
    args = parser.parse_args()
    project = Path(args.project).resolve()
    plan = json.loads(Path(args.plan).read_text(encoding='utf-8-sig'))
    lock = json.loads((project/'input-lock.json').read_text(encoding='utf-8-sig'))
    from roll_transitions import resolve
    plan=resolve(plan,lock)
    summary = validate(plan, lock, draft=args.draft)
    if summary is None:
        fail('author orchestration before generating its table')
    write(project, plan, summary)
    print(json.dumps(summary))  # Machine output is stable on GBK and UTF-8 consoles.


if __name__ == '__main__':
    main()
