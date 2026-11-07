"""User-retained native layers and reference-led R01–R05 recipes."""
import json,math,re,struct,subprocess
from pathlib import Path
from prepare import SKILL,local_file,probe
from object_assets import validate_credit

FIELDS=('screenEffects','companions','editorialScenes')
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def text(v):return isinstance(v,str) and bool(v.strip())
def overlap(a,b):return a['start']<b['end'] and a['end']>b['start']
def specifications():return json.loads((SKILL/'references/production-layers.json').read_text(encoding='utf-8'))
def dimensions(p,source):
    f=local_file(p,source)
    if f.suffix.lower()=='.png':return struct.unpack('>II',f.read_bytes()[16:24])
    s=next(s for s in probe(f)['streams'] if s['codec_type']=='video');return s['width'],s['height']
def entries(plan):
    for field in FIELDS:
        for e in plan.get(field,[]):yield field,e
    for b in plan.get('beats',[]):
        if b.get('kind')=='editorial':yield 'editorialBeats',b
def rect(r,w,h):return isinstance(r,dict) and set(r)=={'x','y','width','height'} and all(finite(v) for v in r.values()) and 0<=r['x']<r['x']+r['width']<=w and 0<=r['y']<r['y']+r['height']<=h
def media(p,m,seconds,credit):
    if not isinstance(m,dict) or set(m)-{'source','mediaStart','crop'} or not text(m.get('source')):raise ValueError('Media requires an actual source; only mediaStart/crop are optional')
    # The primary host already has stronger SHA provenance in input-lock.
    f=local_file(p,m['source']) if m['source']=='assets/source.mp4' else credit(p,m['source'])
    if f.suffix.lower() in {'.mp4','.webm'}:
        o=m.get('mediaStart',0)
        if not finite(o) or o<0 or o+seconds>float(probe(f)['format']['duration'])+.02:raise ValueError('Actual media does not cover its reading window')
    elif f.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.svg'} or 'mediaStart' in m:raise ValueError('Unsupported image/source offset')
    if 'crop' in m and not rect(m['crop'],*dimensions(p,m['source'])):raise ValueError('Media crop outside actual pixels')
def box(r,extra):
    return isinstance(r,dict) and not set(r)-set(extra)-{'x','y','width','height','at'} and all(finite(r.get(k)) for k in ('x','y','width','height','at')) and 0<=r['x']<r['x']+r['width']<=1920 and 0<=r['y']<r['y']+r['height']<=1080 and r['height']>=24
def content(p,tid,c,seconds,credit):
    if not isinstance(c,dict):raise ValueError('Reference recipe needs explicit content')
    if tid=='R01':
        if set(c)!={'lines'} or not isinstance(c['lines'],list) or not 1<=len(c['lines'])<=5:raise ValueError('R01 needs actual stacked lines')
        for r in c['lines']:
            if not box(r,['text']) or not text(r.get('text')) or not 0<=r['at']<seconds-.5:raise ValueError('Invalid R01 text geometry/time')
    elif tid=='R02':
        if set(c)!={'title','width','height','corners','media'} or not text(c['title']) or not all(finite(c[k]) for k in ('width','height')) or not 260<=c['width']<=1000 or not 160<=c['height']<=700 or not isinstance(c['corners'],list) or len(c['corners'])!=4 or any(not isinstance(q,dict) or set(q)!={'x','y'} or not all(finite(q[k]) for k in ('x','y')) or not 0<=q['x']<=1920 or not 70<=q['y']<=1050 for q in c['corners']):raise ValueError('Invalid R02 panel corners/title')
        qs=c['corners'];turns=[(qs[(i+1)%4]['x']-qs[i]['x'])*(qs[(i+2)%4]['y']-qs[(i+1)%4]['y'])-(qs[(i+1)%4]['y']-qs[i]['y'])*(qs[(i+2)%4]['x']-qs[(i+1)%4]['x']) for i in range(4)]
        if any(v<=1 for v in turns):raise ValueError('Panel corners must be convex, ordered and nondegenerate')
        media(p,c['media'],seconds,credit)
    elif tid=='R03':
        if set(c)!={'items'} or not isinstance(c['items'],list) or not 1<=len(c['items'])<=4:raise ValueError('R03 needs actual phase labels')
        for r in c['items']:
            if not box(r,['label','caption','captionWidth']) or not text(r.get('label')) or not 0<=r['at']<seconds-.5 or ('caption' in r and (not text(r['caption']) or r['y']<76)) or ('captionWidth' in r and ('caption' not in r or not finite(r['captionWidth']) or not 30<=r['captionWidth']<=500)):raise ValueError('Invalid R03 labels/geometry/time')
    elif tid=='R04':
        if set(c)!={'kicker','title','side','media','steps'} or not all(text(c[k]) for k in ('kicker','title')) or c['side'] not in {'left','right'} or not isinstance(c['steps'],list) or not 1<=len(c['steps'])<=3 or any(not text(v) or len(v)>45 for v in c['steps']):raise ValueError('Invalid R04 explanation layout/content')
        media(p,c['media'],seconds,credit)
    elif tid=='R05':
        if set(c)!={'hostSide','hostSource','hostMediaStart','title','media','note'} or c['hostSide'] not in {'left','center','right'} or not all(text(c[k]) for k in ('title','note')):raise ValueError('Invalid R05 host/companion layout')
        media(p,{'source':c['hostSource'],'mediaStart':c['hostMediaStart']},seconds,credit);media(p,c['media'],seconds,credit)
    else:raise ValueError('Use retained R01–R05 recipes')
def validate(p,plan,credit,ids):
    for f in FIELDS:
        if not isinstance(plan.get(f,[]),list):raise ValueError(f+' must be a list')
    for field,e in entries(plan):
        if not isinstance(e,dict) or not re.fullmatch('[a-z0-9-]+',e.get('id','')) or (field!='editorialBeats' and e['id'] in ids):raise ValueError('Duplicate/invalid native layer ID')
        ids.add(e['id'])
        if not all(finite(e.get(k)) for k in ('start','end')) or not 0<=e['start']<e['end']<=plan['duration'] or e['end']-e['start']<1.5:raise ValueError('Native reading window is too short/outside the film')
        if field=='screenEffects':
            if set(e)-{'id','start','end','targetBeat','mode','region','label','definition','note','card'} or e.get('mode')!='callout' or not all(text(e.get(k)) for k in ('label','definition')):raise ValueError('Only original-glass circle callout is retained')
            b=next((b for b in plan['beats'] if b['id']==e.get('targetBeat')),None)
            if not b or b['kind'] not in {'screen','media','broll'} or not b['start']<=e['start']<e['end']<=b['end'] or not rect(e.get('region'),*dimensions(p,b.get('image',b.get('video')))):raise ValueError('Circle must bind visible source pixels')
            c=e.get('card',{})
            if not isinstance(c,dict) or set(c)!={'x','y'} or not all(finite(v) for v in c.values()) or not 0<=c['x']<=1375 or not 0<=c['y']<=500:raise ValueError('Place the actual 545px L02 glass card inside the canvas')
        elif field=='companions':
            if set(e)-{'id','start','end','left','right'} or not any(e.get(s) for s in ('left','right')):raise ValueError('Companions need a visible side')
            for side in ('left','right'):
                if side not in e:continue
                o=e[side]
                if not isinstance(o,dict) or set(o)!={'asset','label','motion','x','y','size'} or not text(o['label']) or o['motion'] not in {'hold','float','nod','pulse'} or not all(finite(o[k]) for k in ('x','y','size')) or not 160<=o['size']<=460 or not 20<=o['x']<=1900-o['size'] or not 120<=o['y']<=820-o['size']:raise ValueError('Invalid white object placement/action')
                f=credit(p,o['asset']);validate_credit(p,o['asset'],'pixel2all')
                data=f.read_bytes()
                if f.suffix.lower()!='.png' or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[25] not in (4,6):raise ValueError('Pixel2all companion needs its actual RGBA PNG')
        else:
            allowed={'id','start','end','templateId','content'}|({'kind'} if field=='editorialBeats' else set())
            if set(e)!=allowed or (e['templateId'] not in {'R04','R05'} if field=='editorialBeats' else e['templateId'] not in {'R01','R02','R03'}):raise ValueError('R01–R03 are overlays; R04/R05 are complete main-picture editorial beats')
            content(p,e['templateId'],e['content'],e['end']-e['start'],credit)
        if field in {'companions','editorialScenes'} and (any(overlap(e,b) for b in plan['beats']) or any(overlap(e,b) for b in plan['effects'])):raise ValueError('Retained host layers need an unoccupied host window')
        if field!='editorialBeats':
            owners=[s for s in plan['orchestration']['segments'] if e['id'] in s.get('layerIds',[])]
            if len(owners)!=1 or not owners[0]['start']<=e['start']<e['end']<=owners[0]['end']:raise ValueError('Native layer needs one owning segment.layerIds')
    overlays=[e for f,e in entries(plan) if f in {'companions','editorialScenes'}]
    if any(overlap(a,b) for i,a in enumerate(overlays) for b in overlays[i+1:]):raise ValueError('Only one retained host expression at a time')
    known={e['id'] for f,e in entries(plan) if f!='editorialBeats'}
    for s in plan['orchestration']['segments']:
        refs=s.get('layerIds',[])
        if not isinstance(refs,list) or len(refs)!=len(set(refs)) or any(v not in known for v in refs):raise ValueError('Unknown native layer references')
def enrich_media(p,m):
    m=dict(m)
    if 'crop' in m:m['sourceWidth'],m['sourceHeight']=dimensions(p,m['source'])
    return m
def enriched(p,plan,field,e):
    d=dict(e)
    if field=='screenEffects':
        b=next(b for b in plan['beats'] if b['id']==e['targetBeat']);d['sourceDimensions']=dimensions(p,b.get('image',b.get('video')))
    if field in {'editorialScenes','editorialBeats'}:
        d['content']=dict(d['content'])
        if 'media' in d['content']:d['content']['media']=enrich_media(p,d['content']['media'])
    return d
def build(p,plan,fonts):
    from compile import literal
    styles='\n'.join((p/'assets/glass-lime'/f'{n}.css').read_text(encoding='utf-8') for n in ('common','focus','production'))
    styles=re.sub(r'(?:html,body|body)\{[^}]*\}','',styles)
    fonts+='@font-face{font-family:GLReference;src:url("assets/glass-lime/fonts/reference-roboto.ttf");font-weight:100 900}'
    layers=[]
    for field,e in entries(plan):
        ident=e['id'];duration=e['end']-e['start'];kind={'screenEffects':'screen','companions':'companion'}.get(field,e.get('templateId'));d=enriched(p,plan,field,e)
        body=subprocess.check_output(['node',str(SKILL/'scripts/render_production.mjs')],input=json.dumps(dict(kind=kind,data=d,duration=duration,id=ident)).encode()).decode()
        scripts=''.join(f'<script src="assets/glass-lime/{n}.js"></script>' for n in ('gsap.min','base','focus','glass','production'))
        page=f'''<!doctype html><html><body><template><main id="{ident}" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="30"><style>{fonts}{styles}#{ident}{{position:relative;width:100%;height:100%;background:transparent}}</style><div class="sample-root fine" style="position:absolute;inset:0">{body}</div>{scripts}<script>GLProduction.mount(document.getElementById('{ident}'),'{ident}','{kind}',{literal(d)},{duration});</script></main></template></body></html>'''
        (p/'compositions'/f'{ident}.html').write_text(page,encoding='utf-8');z=20 if field=='editorialBeats' else 32
        layers.append(f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{e["start"]}" data-duration="{duration}" data-track-index="{z}" style="z-index:{z}"></div>')
    return layers
