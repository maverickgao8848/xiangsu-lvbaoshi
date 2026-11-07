"""Validate and compile authored 像素·绿宝石 full-film decisions into HyperFrames."""
import argparse,html,json,math,re,subprocess
from pathlib import Path
from prepare import SKILL,PROFILE,read,dump,sha,local_file,probe,validate_duration_limit,validate_tokens
from captions import captions
import orchestration,effect_planning,animation_insert,animation_routing,content_slots
from animation_contract import provider as animation_provider, credit_source, selected_routes
import scene_kit
import exit_effects
import production_layers
import navigation
import material_display
import roll_transitions

def esc(s):return html.escape(str(s),quote=True)
def literal(s):return json.dumps(s,ensure_ascii=False).replace('<','\\u003c')
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def credit(p,relative,source=None):
    f=local_file(p,relative)
    if not any(c.get('path')==relative and c.get('sha256')==sha(f) and isinstance(c.get('sourcePage'),str) and c['sourcePage'].strip() and (source is None or c['sourcePage']==source) for c in read(p/'asset-credits.json')):raise ValueError('Missing/mismatched frozen media credit: '+relative)
    return f
def validate(p,plan):
    lock=read(p/'input-lock.json');d=lock['duration'];validate_duration_limit(0,d,lock['maxDurationSec'])
    plan=roll_transitions.resolve(navigation.effective_plan(plan,lock),lock)
    if set(plan)-{'id','profile','duration','beats','effects','captions','hostFinish','orchestration','mg','soundCues','screenEffects','companions','editorialScenes','navigation','rollTransitions','animationStyleOverride'}:raise ValueError('Unknown/retired plan fields; use current 像素·绿宝石 plan-format.md')
    if lock['profile']!=PROFILE or plan.get('profile')!=PROFILE or not finite(plan.get('duration')) or abs(plan['duration']-d)>.001:raise ValueError('Profile/source duration mismatch')
    if not re.fullmatch('[a-z0-9-]+',plan.get('id','')):raise ValueError('Invalid composition id')
    if sha(p/'assets/source.mp4')!=lock['frozenSha256'] or sha(p/'words.json')!=lock['wordsSha256']:raise ValueError('Frozen source/timing changed; prepare a new project')
    if sha(p/'assets/vendor/gsap.min.js')!=lock['gsapSha256']:raise ValueError('Frozen GSAP changed')
    for rel,digest in lock['resources'].items():
        if sha(local_file(p/'assets/glass-lime',rel))!=digest:raise ValueError('Frozen renderer changed: '+rel)
        if not (SKILL/'assets'/rel).is_file() or sha(SKILL/'assets'/rel)!=digest:raise ValueError('Skill renderer changed; prepare a new project rather than mix renderer versions')
    summary=orchestration.validate(plan,lock)
    effect_planning.audit(plan,required=True,project=p,lock=lock)
    words=read(p/'words.json');validate_tokens(words['tokens'],d)
    if not words['tokens']:raise ValueError('Trusted reviewed timing required for narration compilation')
    cues=captions(words['tokens'],plan.get('captions'),d)
    material_display.validate(p,plan)
    finish=plan.get('hostFinish',{'enabled':False})
    if not isinstance(finish,dict) or set(finish)-{'enabled','preset'} or type(finish.get('enabled')) is not bool or finish.get('preset','soft-edge-v1')!='soft-edge-v1':raise ValueError('Invalid hostFinish')
    cat={x['id']:x for x in read(SKILL/'references/effect-catalog.json')};motion=read(SKILL/'references/motion.json')
    items=plan['beats']+plan['effects'];ids={plan['id']}
    previous=0;glass=[]
    for b in plan['beats']:
        if b['start']<previous-.001:raise ValueError('Overlapping/out-of-order beats')
        previous=b['end']
    for e in items:
        if not isinstance(e,dict) or not re.fullmatch('[a-z0-9-]+',e.get('id','')) or e['id'] in ids:raise ValueError('Duplicate/invalid scene id')
        ids.add(e['id'])
        if not all(finite(e.get(k)) for k in ('start','end')) or not 0<=e['start']<e['end']<=d:raise ValueError('Invalid scene range')
        if e['end']-e['start']<.8:raise ValueError('Reading window too short')
        if e in plan['effects'] or e.get('kind') in {'evidence','explanation','material'}:
            if set(e)-{'id','kind','start','end','templateId','content','motion','sound','sourceLabel','sourceUrl','stillReason','exitMotion'}:raise ValueError('Unknown template fields')
            tid=e.get('templateId');content=e.get('content')
            if tid not in cat or not isinstance(content,dict):raise ValueError('Template/content required')
            if set(content)-{'title','definition','note','old','question','second','fine','source','regions','object','text','images'}:raise ValueError('Unsupported template content fields')
            if e in plan['effects'] and cat[tid]['bg']!='host':raise ValueError('Grid templates are full-picture beats, not host overlays')
            if e in plan['effects'] and any(e['start']<b['end'] and e['end']>b['start'] for b in plan['beats'] if b['kind']=='animation'):raise ValueError('Editorial effects may not decorate complete 像素 MG frames')
            selected=e.get('motion','none')
            if selected not in ['none']+[v['id'] for v in motion['variants']] or (tid=='L30' and selected!='none'):raise ValueError('Unsupported motion/template combination')
            if e.get('sound','auto') not in ('auto','mute','camera','electronic'):raise ValueError('Unknown sound kit')
            for name in ('text','images'):
                if not isinstance(content.get(name),list) or any(not isinstance(v,str) or not v.strip() for v in content[name]):raise ValueError('Production content needs explicit text and images arrays')
            for image in content['images']:credit(p,image)
            if tid=='L24' and not content.get('object'):raise ValueError('L24 production needs a real object/logo rather than its demonstration SVG')
            if content.get('object'):
                if cat[tid]['bg']!='host' or content['object'] not in content['images']:raise ValueError('Host companion object must bind its actual image slot')
                credit(p,content['object'])
            if e.get('kind')=='evidence' or tid in {'L17','L18','L19','L31'}:
                if not e.get('sourceLabel') or not e.get('sourceUrl'):raise ValueError('Evidence/source template needs a real source label and URL')
                for image in content['images']:credit(p,image,e['sourceUrl'])
            if any(c.get('path') in content['images'] and c.get('sourceMediaType')=='video' for c in read(p/'asset-credits.json')) and not e.get('stillReason'):raise ValueError('A still extracted from supplied video needs its explicit reading purpose')
            if tid=='L31':
                f=credit(p,content.get('source'));header=f.read_bytes()[:24]
                if header[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('L31 source must be PNG')
                w=int.from_bytes(header[16:20],'big');h=int.from_bytes(header[20:24],'big')
                if (w,h)!=(1920,640):raise ValueError('L31 currently supports a 1920x640 source; prepare an explicit crop and recompute regions')
                if not content.get('regions') or any(set(r)!={'x','y','width','height','group'} or any(not finite(v) for v in r.values()) or not 0<=r['x']<r['x']+r['width']<=w or not 0<=r['y']<r['y']+r['height']<=h or r['group']<0 or int(r['group'])!=r['group'] for r in content['regions']):raise ValueError('Invalid source-pixel highlight regions')
                if len(content['images'])!=len(content['regions'])+1 or any(v!=content['source'] for v in content['images']):raise ValueError('L31 must preserve original pixels in every highlight copy')
            glass.append(e)
        elif e.get('kind')=='editorial':
            if e.get('templateId') not in {'R04','R05'}:raise ValueError('Editorial main pictures use R04/R05')
        elif e.get('kind')=='interface' and 'config' in e:
            if set(e)-{'id','kind','start','end','sceneId','config','sourceLabel'} or not e.get('sourceLabel'):raise ValueError('Native Scene Kit needs an explicit source/simulation label; unsupported decoration')
            scene=scene_kit.prepare(p,e)
            for image in content_slots.slots(scene['html'])['images']:
                if not image.startswith('data:image/'):credit(p,image)
        elif e.get('kind') in {'animation','media','broll','screen','interface'}:
            allowed={'id','kind','start','end','video','image','mediaStart','sourceLabel','sourceUrl','editableSource','sceneId','display','provider','styleId'}
            if set(e)-allowed:raise ValueError('Frozen full-picture video owns its pixels; unsupported decoration')
            if 'image' in e:
                if e['kind'] not in {'screen','media','broll'} or 'video' in e or 'mediaStart' in e:raise ValueError('Still source is exclusive and only supported for screen/media/broll')
                f=credit(p,e['image'])
                if f.suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}:raise ValueError('Invalid still source format')
                production_layers.dimensions(p,e['image'])
                if not e.get('sourceLabel'):raise ValueError('Still source needs its actual source label')
                continue
            f=credit(p,e.get('video'),credit_source(e) if e['kind']=='animation' else None)
            info=probe(f);stream=next((s for s in info['streams'] if s['codec_type']=='video'),None);offset=e.get('mediaStart',0)
            if not stream or not finite(offset) or offset<0 or offset+e['end']-e['start']>float(info['format']['duration'])+.001:raise ValueError('Source video window too short')
            if not e.get('sourceLabel'):raise ValueError('Video needs its actual source label')
            if e['kind']=='interface':
                if e.get('sceneId') not in {'S01','S03','S12'}:raise ValueError('Scene Kit supports S01/S03/S12')
                source=(p/e.get('editableSource','')).resolve()
                if not source.is_relative_to((p/'interfaces').resolve()) or not (source/'index.html').is_file():raise ValueError('Interface needs editable source under interfaces/')
        else:raise ValueError('Unsupported main-picture kind')
    for a in plan['effects']:
        if any(a['id']!=b['id'] and a['start']<b['end'] and a['end']>b['start'] for b in plan['effects']):raise ValueError('Only one 像素·绿宝石 foreground window at a time; pair objects inside its declared image slots')
    production_layers.validate(p,plan,credit,ids)
    navigation.validate(p,plan,ids)
    roll_transitions.validate(p,plan,lock)
    animation_insert.validate(p,plan)
    route=selected_routes(p,plan) or None
    if any(b['kind']=='animation' and animation_provider(b)=='xiangsu-mg' for b in plan['beats']):
        mg_route=route['xiangsu-mg']
        if mg_route['provider']!='mav-mg':raise ValueError('Install xiangsu-mg; 像素·绿宝石 does not silently substitute another MG renderer')
        mg=plan.get('mg',{});provider=Path(mg_route['skillPath']).parent
        styles={f.parent.name for f in (provider/'assets/styles').glob('*/metadata.json')}
        if not isinstance(mg,dict) or not isinstance(mg.get('styleId'),str) or not mg['styleId']:raise ValueError('Confirm a 像素 MG style')
        for b in plan['beats']:
            if b['kind']=='animation' and animation_provider(b)=='xiangsu-mg':
                source=p/b['editableSource']
                inherited=animation_routing.validate_frame(p,source,mg['styleId'],plan.get('animationStyleOverride'))
                if mg['styleId'] not in styles and not inherited:raise ValueError('Custom MG style needs verified upstream frame provenance')
                if not (source/'BRIEF.md').is_file() or mg['styleId'] not in (source/'BRIEF.md').read_text(encoding='utf-8'):raise ValueError('Animation BRIEF must retain the selected 像素 MG style')
    exit_effects.validate(p,plan,read(SKILL/'references/motion.json'))
    rendered=content_slots.render(glass,p/'assets/glass-lime')
    for e,result in zip(glass,rendered):
        slots=content_slots.slots(result['body'])
        if any(len(e['content'][k])!=len(slots[k]) for k in ('text','images')):raise ValueError('Template slot count mismatch: '+e['id'])
    for cue in plan.get('soundCues',[]):
        if set(cue)!={'id','file','at','duration','volume'} or cue['id'] in ids or not re.fullmatch('[a-z0-9-]+',cue['id']) or not all(finite(cue[k]) for k in ('at','duration','volume')) or not 0<=cue['at']<cue['at']+cue['duration']<=d or not 0<=cue['volume']<=1:raise ValueError('Invalid authored sound cue')
        credit(p,cue['file']);ids.add(cue['id'])
        if cue['duration']>float(probe(p/cue['file'])['format']['duration'])+.001:raise ValueError('Sound cue exceeds actual file')
    return lock,summary,cues,glass,rendered,route

def caption_layers(p,cues,plan,fonts,styles):
    """Group unchanged cues into small native sub-compositions for Studio."""
    result=[]
    caption_style=re.search(r'\.mav-subtitle\s*\{[^}]*\}',styles)
    if cues and not caption_style:raise ValueError('Frozen caption style missing')
    for offset in range(0,len(cues),16):
        group=cues[offset:offset+16];start=group[0]['start'];end=group[-1]['end'];duration=round(end-start,4)
        ident=f'mav-captions-{offset//16:02d}';nodes=[]
        for i,c in enumerate(group,offset):
            on_media=any(c['start']<b['end'] and c['end']>b['start'] for b in plan['beats'])
            declarations=['background:rgba(48,49,52,.72)'] if on_media else []
            phases=[e for e in plan.get('editorialScenes',[]) if e['templateId']=='R03' and c['start']<e['end'] and c['end']>e['start']]
            if phases:
                top=min(r['y']-(76 if r.get('caption') else 0) for e in phases for r in e['content']['items'])
                declarations.append(f'bottom:{1080-top+24}px')
            finish=' style="'+(';'.join(declarations))+'"' if declarations else ''
            nodes.append(f'<div id="caption-{i}" class="clip" data-start="{round(c["start"]-start,4)}" data-duration="{round(c["end"]-c["start"],4)}" data-track-index="50" style="z-index:50"><span class="mav-subtitle"{finish}>{esc(c["text"])}</span></div>')
        page=f'''<!doctype html><html lang="zh-CN"><body><template><main id="{ident}" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="30"><style>{fonts}{caption_style.group() if caption_style else ''}#{ident}{{position:relative;width:1920px;height:1080px;background:transparent}}#{ident} .clip{{position:absolute;inset:0}}</style>{''.join(nodes)}<script src="assets/vendor/gsap.min.js"></script><script>window.__timelines=window.__timelines||{{}};window.__timelines['{ident}']=gsap.timeline({{paused:true}}).to({{}},{{duration:{duration}}});</script></main></template></body></html>'''
        (p/'compositions'/f'{ident}.html').write_text(page,encoding='utf-8')
        result.append(f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{start}" data-duration="{duration}" data-track-index="50" style="z-index:50"></div>')
    return result

def build(p,plan,checked):
    lock,summary,cues,glass,rendered,route=checked;d=plan['duration'];p.joinpath('compositions').mkdir(exist_ok=True)
    plan=roll_transitions.resolve(navigation.effective_plan(plan,lock),lock)
    cat={x['id']:x for x in read(SKILL/'references/effect-catalog.json')};config=read(SKILL/'references/motion.json')
    styles='\n'.join((p/'assets/glass-lime'/f'{n}.css').read_text(encoding='utf-8') for n in ['common','focus','flow','extra','material','envelope'])
    # HTML/body rules scope to a sub-composition's stage; a host overlay must stay transparent.
    substyles=re.sub(r'(?:html,body|body)\{[^}]*\}','',styles)
    fonts=''.join(f'@font-face{{font-family:{family};src:url("assets/glass-lime/fonts/{file}.ttf");font-weight:100 900}}' for family,file in [('GLSans','noto'),('GLNumbers','montserrat'),('GLCaption','oppo')])
    scripts=''.join(f'<script src="assets/glass-lime/{n}.js"></script>' for n in ['gsap.min','base','focus','flow','extra','material-regions','material','glass','envelope','runtime','domain-warp-exit','editorial'])
    layers=[];sounds=[]
    for e,result in zip(glass,rendered):
        ident=e['id'];duration=e['end']-e['start'];tid=e['templateId'];bg=cat[tid]['bg'];motion=e.get('motion','none')
        render_data=exit_effects.data(p,e,config)
        bgclass='grid' if bg=='grid' else 'transparent'
        page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"></head><body><template><main id="root" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="30"><style>{fonts}{substyles}.background.transparent{{background:transparent}}#root{{position:relative;width:1920px;height:1080px;background:transparent}}</style>{scripts}<div id="{ident}-content" class="sample-root"><div class="background {bgclass}"></div><div class="foreground">{result['body']}</div></div><script>GLEditorial.mount(document.getElementById('{ident}-content'),'{ident}','{tid}',{literal(render_data)},{duration},'{motion}');</script></main></template></body></html>'''
        (p/'compositions'/f'{ident}.html').write_text(page,encoding='utf-8')
        z=30 if e in plan['effects'] else 20
        layers.append(f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{e["start"]}" data-duration="{duration}" data-track-index="{z}" style="z-index:{z}"></div>')
        kit=e.get('sound','auto');variant=next((v for v in config['variants'] if v['id']==motion),None)
        kit=variant['kit'] if kit=='auto' and variant else kit
        if variant and kit not in ('mute','auto'):
            for i,c in enumerate(exit_effects.cues(e,config,kit)):
                at=e['start']+c['at']*duration/6;length=min(config['sfxDuration'][c['file']],e['end']-at)
                sounds.append(dict(id=f'{ident}-sfx-{i}',file=c['file'].replace('assets/','assets/glass-lime/',1),at=at,duration=length,volume=c['volume']*config['masterVolume']))
    for b in plan['beats']:
        if b in glass or b['kind']=='editorial':continue
        ident=b['id'];duration=b['end']-b['start']
        if material_display.selected(b):
            layers.append(material_display.compile_one(p,b,fonts,handoff=roll_transitions.owns_entry(plan,b)))
            continue
        if b['kind']=='animation':
            layers.append(animation_insert.compile_one(p,b))
            continue
        if b['kind']=='interface' and 'config' in b:
            q=scene_kit.prepare(p,b);kit=p/'assets/glass-lime/component-kit'
            sceneCSS=(kit/'scene.css').read_text(encoding='utf-8').replace('assets/component-kit/','assets/glass-lime/component-kit/').replace('JetBrains Mono','GLTerminal').replace('EB Garamond','GLNumbers')
            sceneCSS+=''.join(f'@font-face{{font-family:"GLTerminal";src:url("assets/glass-lime/component-kit/fonts/JetBrainsMono-{weight}.woff2");font-weight:{weight}}}' for weight in (400,700))
            page=f'''<!doctype html><html><body><template><main id="root" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="30"><style>{fonts}{substyles}{q['fonts']}{sceneCSS}#root{{position:relative;width:1920px;height:1080px}}.gl-interface-stage{{position:absolute;left:240px;top:135px;width:1440px;height:810px;overflow:hidden;border-radius:30px}}.component-interface{{width:1280px;height:720px;transform:scale(1.125);transform-origin:0 0}}.gl-interface-source{{position:absolute;left:240px;bottom:70px;font:24px GLSans;color:#dddeda}}</style><div class="background grid"></div><div class="gl-interface-stage"><div id="{ident}-interface" class="component-interface">{q['html']}</div></div><p class="gl-interface-source">{esc(b['sourceLabel'])}</p><script src="assets/vendor/gsap.min.js"></script><script>document.fonts.ready.then(()=>{{const root=document.getElementById('{ident}-interface');const child=((document,window)=>({q['install']})({literal(q['config'])},{literal(q['sequence'])}))({{querySelector:s=>root.querySelector(s)}},{{__timelines:{{}}}});const tl=gsap.timeline({{paused:true}}).add(child.paused(false),0);tl.to({{}},{{duration:.01}},{duration}-.01);window.__timelines=window.__timelines||{{}};window.__timelines['{ident}']=tl;}});</script></main></template></body></html>'''
            source=p/'interfaces'/ident;source.mkdir(parents=True,exist_ok=True)
            sourcePage=page.replace('<template>','').replace('</template>','').replace('assets/vendor/','../../assets/vendor/').replace('assets/glass-lime/component-kit/','../../assets/glass-lime/component-kit/')
            (source/'index.html').write_text(sourcePage,encoding='utf-8');dump(source/'scene-input.json',dict(sceneId=b['sceneId'],config=b['config'],sourceLabel=b['sourceLabel']))
        else:
            media=f'<img id="{ident}-image" src="{esc(b["image"])}" alt="">' if 'image' in b else f'<video id="{ident}-video" class="clip" src="{esc(b["video"])}" data-start="0" data-duration="{duration}" data-media-start="{b.get("mediaStart",0)}" muted playsinline></video>'
            page=f'''<!doctype html><html><body><template><main id="{ident}" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="30"><style>#{ident}{{width:100%;height:100%;position:relative;background:#08090b}}#{ident} video,#{ident} img{{width:100%;height:100%;object-fit:contain}}</style>{media}<script src="assets/vendor/gsap.min.js"></script><script>window.__timelines=window.__timelines||{{}};window.__timelines['{ident}']=gsap.timeline({{paused:true}}).to({{}},{{duration:{duration}}});</script></main></template></body></html>'''
        (p/'compositions'/f'{ident}.html').write_text(page,encoding='utf-8')
        layers.append(f'<div id="slot-{ident}" class="clip" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{b["start"]}" data-duration="{duration}" data-track-index="20" style="z-index:20"></div>')
    layers.extend(production_layers.build(p,plan,fonts))
    nav_layer,nav_info=navigation.build(p,plan,fonts)
    if nav_layer:layers.append(nav_layer)
    # Each host span owns the finish; complete media/MG pixels remain untouched.
    if plan.get('hostFinish',{}).get('enabled'):
        for i,s in enumerate(plan['orchestration']['segments']):
            if s['scenario']=='host':layers.append(f'<div id="finish-{i}" class="clip" data-start="{s["start"]}" data-duration="{s["end"]-s["start"]}" data-track-index="10" style="z-index:10;pointer-events:none;background:url(assets/glass-lime/host-edge-shadow/soft-edge-v1.png) 0 0/100% 100%"></div>')
    layers.extend(caption_layers(p,cues,plan,fonts,styles))
    for index,cue in enumerate(sounds+plan.get('soundCues',[])):layers.append(f'<audio id="{cue["id"]}" src="{esc(cue["file"])}" data-start="{cue["at"]}" data-duration="{cue["duration"]}" data-volume="{cue["volume"]}" data-track-index="{60+index}"></audio>')
    roll_layers,roll_motion,roll_css,roll_script=roll_transitions.compile_layers(p,plan)
    layers.extend(roll_layers)
    source=f'<video id="host-source" class="clip host-source" src="assets/source.mp4" data-start="0" data-duration="{d}" data-has-audio="true" playsinline></video>'
    assembled=roll_transitions.assemble(source,layers,plan)
    ident=plan['id'];page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>像素·绿宝石 Editorial</title><style>{fonts}{styles}{roll_css}#{ident}{{position:relative;width:1920px;height:1080px;overflow:hidden}}.clip{{position:absolute;inset:0}}.host-source{{width:1920px;height:1080px;object-fit:contain}}</style></head><body><main id="{ident}" data-composition-id="{ident}" data-width="1920" data-height="1080" data-duration="{d}" data-fps="30">{assembled}</main><script src="assets/vendor/gsap.min.js"></script>{roll_script}<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}}).to({{}},{{duration:{d}}});{roll_motion}window.__timelines['{ident}']=tl;</script></body></html>'''
    (p/'index.html').write_text(page,encoding='utf-8');dump(p/'captions.json',cues)
    dump(p/'package.json',dict(name='glass-lime-film',private=True,scripts={'check':'npx --yes hyperframes@0.8.192 check','dev':'npx --yes hyperframes@0.8.192 preview --background','render':'npx --yes hyperframes@0.8.192 render'}))
    dump(p/'build-report.json',dict(profile=PROFILE,duration=d,planSha256=sha(p/'edit-plan.json') if (p/'edit-plan.json').is_file() else None,sourceSha256=lock['frozenSha256'],templateInstances=len(glass),nativeSoundCues=sounds,orchestration=summary,animationRoute=route,navigation=nav_info,visualApproval='pending',status='compiled; run HyperFrames check and review the real representative segment'))
    orchestration.write(p,plan,summary);animation_insert.record(p,plan)
    material_display.record(p,plan)
    roll_transitions.record(p,plan)

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--project',required=True);a.add_argument('--plan',required=True);a.add_argument('--validate-only',action='store_true');x=a.parse_args();p=Path(x.project).resolve();plan=read(x.plan)
    checked=validate(p,plan)
    if not x.validate_only:build(p,plan,checked)
    print(json.dumps(dict(ok=True,stage='validated' if x.validate_only else 'compiled',segments=checked[1]['segments'],templates=len(checked[3]))))
if __name__=='__main__':main()
