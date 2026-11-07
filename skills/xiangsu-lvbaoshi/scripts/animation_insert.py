"""Assemble a provider-owned frozen full-frame video, retaining its editable source."""
import html
import json
import math
import subprocess
from prepare import read, sha, dump
from animation_contract import provider, credit_source, validate_lemo, selected_routes


def local_file(p, value):
    if not isinstance(value, str) or not value or ':' in value or '\\' in value:
        raise ValueError('Animation paths must be project-relative')
    path = (p/value).resolve()
    if not path.is_relative_to(p.resolve()) or not path.is_file():
        raise ValueError('Animation file missing/outside project')
    return path


def validate(p, plan):
    selected_routes(p,plan)
    credits = None
    for i, b in enumerate(plan['beats']):
        if b['kind'] != 'animation':
            continue
        if set(b)-{'id','kind','start','end','title','video','mediaStart','editableSource','sourceLabel','transitionIn','display','provider','styleId'}:
            raise ValueError('Animation retains its own frame; unsupported decoration or camera')
        file = local_file(p, b.get('video'))
        source = b.get('editableSource')
        if not isinstance(source, str) or not source or ':' in source or '\\' in source:
            raise ValueError('Animation needs its project-relative editable source')
        root = (p/source).resolve()
        if not root.is_relative_to((p/'animations').resolve()) or not root.is_dir():
            raise ValueError('Editable animation source must stay inside project/animations')
        for name in (('index.html', 'STORYBOARD.md', 'frame.md') if provider(b) == 'xiangsu-mg' else ('index.html', 'TREATMENT.md')):
            if not (root/name).is_file():
                raise ValueError('Editable animation source missing '+name)
        if provider(b) == 'lemo-opuscar':
            validate_lemo(root,b)
        offset = b.get('mediaStart', 0)
        if type(offset) not in (int, float) or not math.isfinite(offset) or offset < 0:
            raise ValueError('Invalid animation media offset')
        info = json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(file)]))
        streams = [s for s in info['streams'] if s['codec_type'] == 'video']
        if not streams or abs(streams[0]['width']/streams[0]['height']-16/9) > .001:
            raise ValueError('Full-frame animation needs a 16:9 video')
        tail = plan['beats'][i+1].get('transitionIn',0) if i+1 < len(plan['beats']) else 0
        if offset+b['end']-b['start']+tail > float(info['format']['duration'])+.001:
            raise ValueError('Animation source window too short, including transition tail')
        if credits is None:
            credits = read(p/'asset-credits.json') if (p/'asset-credits.json').exists() else []
        if not any(c.get('path') == b['video'] and c.get('sha256') == sha(file) and
                   c.get('sourcePage') == credit_source(b) for c in credits):
            raise ValueError('Animation needs matching frozen animation provider credit')
        if any(s < b['end']+tail and e > b['start'] for s,e in plan.get('pip', [])):
            raise ValueError('Full-frame animation does not add an Editorial speaker window')


def compile_one(p, b, tail=0):
    ident = b['id']; duration = round(b['end']-b['start']+tail,4)
    video = html.escape(b['video'], quote=True); fade = b.get('transitionIn',0)
    motion = f'tl.fromTo("#{ident} .animation-frame",{{opacity:0}},{{opacity:1,duration:{fade},ease:"none"}},0);' if fade else ''
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"></head><body><template>
<main id="{ident}" data-composition-id="{ident}" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080" data-fps="30">
<style>#{ident}{{position:relative;width:1920px;height:1080px;overflow:hidden}}#{ident} .animation-frame{{position:absolute;inset:0}}#{ident} video{{width:1920px;height:1080px;object-fit:contain}}</style>
<div class="animation-frame"><video id="{ident}-animation-video" class="clip" src="{video}" data-start="0" data-duration="{duration}" data-media-start="{b.get('mediaStart',0)}" data-track-index="0" muted playsinline></video></div>
<script src="assets/vendor/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});{motion}window.__timelines=window.__timelines||{{}};window.__timelines['{ident}']=tl;</script>
</main></template></body></html>'''
    (p/'compositions'/f'{ident}.html').write_text(page,encoding='utf-8')
    return f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{b["start"]}" data-duration="{duration}" data-track-index="20" style="z-index:20"></div>'


def record(p, plan):
    entries = [{'id':b['id'],'provider':provider(b),'video':b['video'],'editableSource':b['editableSource'],'sha256':sha(p/b['video'])} for b in plan['beats'] if b['kind']=='animation']
    if entries:
        from animation_contract import record as record_routes
        record_routes(p,plan)
        report = read(p/'build-report.json'); report['animationInserts'] = {'version':'mav-full-frame/v1','entries':entries,'visualApproval':'pending'}; dump(p/'build-report.json',report)
