"""Optional Baijin #22 cinema stage for media and frozen MG videos."""
import html
import math
from prepare import SKILL, read, dump, sha

KINDS = {'media', 'broll', 'screen', 'animation'}


def selected(beat):
    return 'display' in beat


def validate(p, plan):
    for beat in plan.get('effects', []) + plan.get('beats', []):
        if not selected(beat):
            continue
        cfg = beat['display']
        if beat not in plan.get('beats', []) or beat.get('kind') not in KINDS:
            raise ValueError('Cinema display belongs to media/broll/screen/animation beats')
        if not isinstance(cfg, dict) or set(cfg)-{'style', 'fit', 'scale', 'light'} or cfg.get('style') != 'cinema':
            raise ValueError('Display requires style cinema and supported cinema fields')
        if cfg.get('fit', 'contain') != 'contain':
            raise ValueError('Cinema preserves the complete image with contain')
        if ('image' in beat) == ('video' in beat) or 'config' in beat:
            raise ValueError('Cinema needs exactly one frozen image or video')
        preset = read(SKILL/'assets/material-display/preset.json')['styles']['cinema']
        for key, low, high, default in [('scale', .8, preset['maxScale'], preset['defaultScale']), ('light', 0, 1, preset['defaultLight'])]:
            value = cfg.get(key, default)
            if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError('Cinema '+key+' outside safe bounds')
        if beat['end']-beat['start'] < 2:
            raise ValueError('Cinema needs at least two seconds of reading time')
        # Existing circle annotations assume the unframed full-canvas source.
        if any(e.get('targetBeat') == beat['id'] for e in plan.get('screenEffects', [])):
            raise ValueError('Cinema source-pixel callouts need a separate unframed screen beat')
        for name in ('style.css', 'preset.json'):
            frozen = p/'assets/glass-lime/material-display'/name
            if not frozen.is_file() or sha(frozen) != sha(SKILL/'assets/material-display'/name):
                raise ValueError('Cinema renderer changed or missing; prepare a new project')


def compile_one(p, beat, fonts, handoff=False):
    ident = beat['id']; duration = round(beat['end']-beat['start'], 4)
    cfg = beat['display']
    preset = read(p/'assets/glass-lime/material-display/preset.json')['styles']['cinema']
    scale = cfg.get('scale', preset['defaultScale']); light = cfg.get('light', preset['defaultLight'])
    esc = lambda value: html.escape(str(value), quote=True)
    if 'video' in beat:
        media = f'<video id="{ident}-video" class="clip material-media" src="{esc(beat["video"])}" data-start="0" data-duration="{duration}" data-media-start="{beat.get("mediaStart",0)}" data-track-index="21" muted playsinline></video>'
    else:
        media = f'<img id="{ident}-image" class="material-media" src="{esc(beat["image"])}" alt="">'
    css = (p/'assets/glass-lime/material-display/style.css').read_text(encoding='utf-8')
    css = css.replace('.stage-shell', '#'+ident+' .stage-shell')
    sel = '#'+ident
    # Geometry/light/entrance copied from Baijin's selected #22 cinema stage.
    motion = [
        f'tl.fromTo("{sel} .stage-shell",{{opacity:0}},{{opacity:1,duration:.45,ease:"power2.out"}},0);',
        f'tl.fromTo("{sel} .display-body",{{opacity:0,x:0,y:28,scale:{.965*scale}}},{{opacity:1,x:0,y:0,scale:{scale},duration:.85,ease:"power3.out"}},.08);',
        f'tl.fromTo("{sel} .stage-light",{{opacity:0}},{{opacity:{light},duration:1.2,ease:"sine.out"}},.2);',
        f'tl.fromTo("{sel} .stage-light",{{x:-24}},{{x:36,duration:{duration},ease:"sine.inOut"}},0);',
        f'tl.fromTo("{sel} .material-caption",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.4,ease:"power2.out"}},.7);',
    ]
    if handoff:
        # A/B handoff owns the stage entrance; preserve its steady frame/light.
        motion[:3] = [
            f'tl.set("{sel} .stage-shell",{{opacity:1}},0);',
            f'tl.set("{sel} .display-body",{{opacity:1,x:0,y:0,scale:{scale}}},0);',
            f'tl.set("{sel} .stage-light",{{opacity:{light}}},0);',
        ]
    page = f'''<!doctype html><html lang="zh-CN"><body><template>
<main id="{ident}" data-composition-id="{ident}" data-duration="{duration}" data-width="1920" data-height="1080" data-fps="30">
<style>{fonts}{css}#{ident}{{position:relative;width:100%;height:100%;overflow:hidden}}</style>
<div class="stage-shell cinema"><div class="stage-fill"></div><div class="stage-light" data-layout-ignore></div><div class="stage-floor" data-layout-ignore></div><div class="stage-content"><div class="display-body"><div class="bezel"><div class="material-viewport">{media}</div></div></div><div class="material-caption"><span class="material-source">{esc(beat['sourceLabel'])}</span></div></div></div>
<script src="assets/vendor/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});{''.join(motion)}window.__timelines=window.__timelines||{{}};window.__timelines['{ident}']=tl;</script>
</main></template></body></html>'''
    (p/'compositions'/f'{ident}.html').write_text(page, encoding='utf-8')
    return f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{beat["start"]}" data-duration="{duration}" data-track-index="20" style="z-index:20"></div>'


def record(p, plan):
    entries = [dict(id=b['id'], kind=b['kind'], display=b['display'], media=b.get('image', b.get('video'))) for b in plan['beats'] if selected(b)]
    if entries:
        report = read(p/'build-report.json')
        report['materialDisplay'] = dict(version='glass-lime-cinema/v1', origin='xiangsu-baijin #22', entries=entries, visualApproval='pending')
        dump(p/'build-report.json', report)
