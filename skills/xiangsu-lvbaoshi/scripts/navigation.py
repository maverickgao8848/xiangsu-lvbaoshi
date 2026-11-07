"""A · silver frosted segmented chapter progress, assembled as a full-film navigation layer."""
import math
import re
from copy import deepcopy
from pathlib import Path
from prepare import SKILL, read, sha

VERSION = 'glass-lime-navigation-progress-a/v1'
HEIGHT_PX = 40
Z_INDEX = 46
MAX_CHAPTERS = 6
MIN_CHAPTER_SECONDS = 1.0
DEFAULTS_VERSION = 'glass-lime-navigation-defaults/v1'
DEFAULT_ABOVE_SECONDS = 180


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def effective_plan(plan, lock=None):
    """New freezes default to the existing badge/progress/transition group above 180s."""
    version = (lock or {}).get('navigationDefaultsVersion')
    if version not in (None, DEFAULTS_VERSION):
        raise ValueError('Unsupported navigation defaults version')
    nav = plan.get('navigation')
    if 'navigation' in plan:
        if not isinstance(nav, dict) or set(nav) != {'progress'} or type(nav['progress']) is not bool:
            raise ValueError('navigation is optional {progress:true|false}; chapters live in chapters.json')
        enabled = nav['progress']
    else:
        # A lock without the defaults marker belongs to a historical freeze.
        enabled = plan.get('duration', 0) > DEFAULT_ABOVE_SECONDS if lock is None or version else False
    result = deepcopy(plan)
    result['navigation'] = {'progress': enabled}
    return result


def resolve(p, duration):
    source = Path(p) / 'chapters.json'
    if not source.is_file():
        raise ValueError('navigation.progress needs chapters.json in the project root')
    data = read(source)
    if isinstance(data, dict):
        if set(data) != {'chapters'}:
            raise ValueError('chapters.json must be an array or {chapters:[...]}')
        data = data['chapters']
    if not isinstance(data, list) or not 1 <= len(data) <= MAX_CHAPTERS:
        raise ValueError('chapters.json needs 1–6 chapters')
    chapters = []
    numbers = set()
    previous = None
    for index, row in enumerate(data):
        if not isinstance(row, dict) or set(row) != {'number', 'title', 'start'}:
            raise ValueError('Each chapter needs exactly number, title and start')
        number, title, start = row['number'], row['title'], row['start']
        if not isinstance(number, str) or not re.fullmatch(r'\d{1,3}', number) or number in numbers:
            raise ValueError('Chapter numbers must be unique 1–3 digit strings')
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 14 or '\n' in title:
            raise ValueError('Chapter titles must be 1–14 characters on one line')
        if not finite(start) or start < 0 or start >= duration:
            raise ValueError('Chapter starts must be finite and inside the film')
        if index == 0 and abs(start) > 0.001:
            raise ValueError('The first chapter must start at 0')
        if previous is not None and start <= previous + 0.001:
            raise ValueError('Chapter starts must increase strictly')
        numbers.add(number)
        chapters.append({'number': number, 'title': title.strip(), 'start': round(float(start), 4)})
        previous = start
    for index, chapter in enumerate(chapters):
        chapter['end'] = round(float(chapters[index + 1]['start'] if index + 1 < len(chapters) else duration), 4)
        if chapter['end'] - chapter['start'] < MIN_CHAPTER_SECONDS:
            raise ValueError('Each chapter needs at least one second of screen time')
    return chapters


def validate(p, plan, ids):
    lock = read(Path(p) / 'input-lock.json') if (Path(p) / 'input-lock.json').is_file() else None
    nav = effective_plan(plan, lock)['navigation']
    if not nav['progress']:
        return None
    chapters = resolve(p, plan['duration'])
    if plan.get('id') == 'navigation-progress' or 'navigation-progress' in ids:
        raise ValueError('Navigation progress id collides with another scene')
    ids.add('navigation-progress')
    source = SKILL / 'assets/navigation-progress'
    frozen = Path(p) / 'assets/glass-lime/navigation-progress'
    for name in ('style.css', 'runtime.js'):
        if not (frozen / name).is_file():
            raise ValueError('Navigation progress assets missing; prepare a new project with the current Skill')
        if sha(frozen / name) != sha(source / name):
            raise ValueError('Frozen navigation progress renderer changed; prepare a new project')
    return chapters


def build(p, plan, fonts):
    lock = read(Path(p) / 'input-lock.json') if (Path(p) / 'input-lock.json').is_file() else None
    nav = effective_plan(plan, lock)['navigation']
    stale = Path(p) / 'compositions/navigation-progress.html'
    if not nav['progress']:
        if stale.exists():
            stale.unlink()
        return None, None
    chapters = resolve(p, plan['duration'])
    frozen = Path(p) / 'assets/glass-lime/navigation-progress'
    css = (frozen / 'style.css').read_text(encoding='utf-8')
    # Full-frame screen windows (no cinema stage) would put the badge on the source's own UI.
    hide = [
        [round(float(b['start']), 4), round(float(b['end']), 4)]
        for b in plan.get('beats', [])
        if b.get('kind') == 'screen' and 'display' not in b
    ]
    payload = {'chapters': chapters, 'duration': plan['duration'], 'hide': hide}
    from compile import literal
    page = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"></head><body><template>'
        f'<main id="navigation-progress" data-composition-id="navigation-progress" data-start="0" data-duration="{plan["duration"]}" data-width="1920" data-height="1080" data-fps="30">'
        f'<style>{fonts}{css}#navigation-progress{{position:relative;width:1920px;height:1080px;background:transparent;pointer-events:none}}</style>'
        '<div class="gl-progress"></div>'
        '<script src="assets/vendor/gsap.min.js"></script>'
        '<script src="assets/glass-lime/navigation-progress/runtime.js"></script>'
        f'<script>const data={literal(payload)};const tl=GLNavProgress.mount(document.getElementById("navigation-progress"),data,data.duration);window.__timelines=window.__timelines||{{}};window.__timelines["navigation-progress"]=tl;</script>'
        '</main></template></body></html>'
    )
    (Path(p) / 'compositions/navigation-progress.html').write_text(page, encoding='utf-8')
    layer = f'<div id="slot-navigation-progress" class="clip" data-composition-id="navigation-progress" data-composition-src="compositions/navigation-progress.html" data-start="0" data-duration="{plan["duration"]}" data-track-index="46" style="z-index:46"></div>'
    info = {
        'version': VERSION,
        'defaultsVersion': (lock or {}).get('navigationDefaultsVersion'),
        'defaultAboveSeconds': DEFAULT_ABOVE_SECONDS,
        'heightPx': HEIGHT_PX,
        'zIndex': Z_INDEX,
        'chapterCount': len(chapters),
        'chapters': chapters,
        'cornerBadge': True,
        'cornerHideWindows': hide,
        'chaptersSha256': sha(Path(p) / 'chapters.json'),
        'assetSha256': {
            'style.css': sha(frozen / 'style.css'),
            'runtime.js': sha(frozen / 'runtime.js'),
        },
    }
    return layer, info
