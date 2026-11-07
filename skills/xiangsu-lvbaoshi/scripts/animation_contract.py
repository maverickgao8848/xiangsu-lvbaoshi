"""Provider identity and source handoff shared by planning and compilation."""
import json
from prepare import read, sha

PROVIDERS = {'xiangsu-mg', 'lemo-opuscar'}
VERSION = 'editorial-animation-routing/v1'


def canonical(value):
    return 'xiangsu-mg' if value == 'mav-mg' else value


def provider(beat):
    value = canonical(beat.get('provider', 'xiangsu-mg'))
    if value not in PROVIDERS:
        raise ValueError('Unknown animation provider: ' + str(value))
    return value


def credit_source(beat):
    prefix = 'generated:lemo-opuscar:' if provider(beat) == 'lemo-opuscar' else 'generated:mav-mg:'
    return prefix + beat['id']


def check_owner(segment, beat):
    if beat.get('kind') == 'animation' and canonical(segment['producer']) != provider(beat):
        raise ValueError('Animation provider differs from orchestration producer: ' + beat['id'])


def local(root, relative):
    if not isinstance(relative, str) or not relative or ':' in relative or '\\' in relative:
        raise ValueError('Animation source needs a relative file path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Missing/outside animation source: ' + relative)
    return path


def validate_lemo(root, beat):
    """Check reproducible source identity, not artistic quality or executed motion."""
    data = read(local(root, 'animation-source.json'))
    if data.get('provider') != 'lemo-opuscar' or data.get('styleId') != beat.get('styleId') or not isinstance(beat.get('styleId'), str) or not beat['styleId'].strip():
        raise ValueError('Lemo handoff must retain the selected styleId/provider')
    files = data.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Lemo handoff needs hashed source files')
    for relative, digest in files.items():
        if sha(local(root, relative)) != digest:
            raise ValueError('Lemo editable source drift: ' + relative)
    for name in ('index.html', 'TREATMENT.md', data.get('buildEntry'), data.get('styleFile')):
        if name not in files:
            raise ValueError('Lemo handoff must freeze index, treatment, build entry and selected STYLE')
        local(root, name)
    return data


def selected_routes(project, plan):
    from animation_routing import discover
    result = {}
    for beat in plan.get('beats', []):
        if beat.get('kind') != 'animation':
            continue
        ident = provider(beat)
        if ident not in result:
            result[ident] = discover(project, ident)
        route = result[ident]
        if route['provider'] not in ({'xiangsu-mg','mav-mg'} if ident == 'xiangsu-mg' else {'lemo-opuscar'}):
            raise ValueError('Selected animation Skill is unavailable: ' + ident)
    return result


def record(project, plan):
    beats = [b for b in plan.get('beats', []) if b.get('kind') == 'animation']
    if not beats:
        return
    routes = selected_routes(project, plan)
    entries = [dict(id=b['id'], provider=provider(b), video=b['video'],
                    editableSource=b['editableSource'], videoSha256=sha(project/b['video']),
                    **({'styleId': b['styleId'], 'sourceManifestSha256': sha(project/b['editableSource']/'animation-source.json')}
                       if provider(b) == 'lemo-opuscar' else {})) for b in beats]
    report = dict(version=VERSION, routes=routes, entries=entries, visualApproval='pending')
    from prepare import dump
    build=read(project/'build-report.json');build['animationRouting']=report;dump(project/'build-report.json',build)
    (project/'ANIMATION-ROUTING.md').write_text(
        '# 动画制作与交接\n\n' + json.dumps(report, ensure_ascii=False, indent=2) +
        '\n\n原声与字幕由主工程管理；动画静音展映，完整可编辑图形保留在各自源工程。技术交接不代表艺术验收。\n',
        encoding='utf-8')
