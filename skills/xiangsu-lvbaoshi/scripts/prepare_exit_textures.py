"""Prepare actual foreground captures for planned local domain-warp exits."""
import argparse,json,re
from pathlib import Path
from prepare import SKILL,read,sha
import content_slots,exit_effects

def prepare(project,plan):
    assets=project/'assets/glass-lime'
    names=('gsap.min','base','focus','flow','extra','material-regions','material','glass','envelope','runtime','domain-warp-exit','editorial')
    for name in names:
        if sha(assets/(name+'.js'))!=sha(SKILL/'assets'/(name+'.js')):
            raise ValueError('Capture needs the matching frozen renderer; prepare a new project: '+name)
    config=read(SKILL/'references/motion.json');settings=config['exitTreatments']['domain-warp']
    css='\n'.join((assets/(name+'.css')).read_text(encoding='utf-8') for name in ('common','focus','flow','extra','material','envelope'))
    frame=project/'frame.md'
    if frame.is_file():css+='\n'+'\n'.join(re.findall(r'```host-layout-css\s*\n([\s\S]*?)```',frame.read_text(encoding='utf-8')))
    fonts=''.join(f'@font-face{{font-family:{family};src:url("assets/glass-lime/fonts/{file}.ttf");font-weight:100 900}}' for family,file in [('GLSans','noto'),('GLNumbers','montserrat'),('GLCaption','oppo')])
    scripts=''.join(f'<script src="assets/glass-lime/{name}.js"></script>' for name in names)
    out=project/'verification/exit-capture';out.mkdir(parents=True,exist_ok=True);manifest={}
    for e in plan.get('effects',[])+plan.get('beats',[]):
        if not e.get('exitMotion'):continue
        if e['exitMotion']!='domain-warp' or e.get('motion') not in ('B','D'):raise ValueError('Local exit currently composes with B/D entrances')
        ident=e['id'];tid=e['templateId'];duration=e['end']-e['start']
        if not re.fullmatch('[a-z0-9-]+',ident) or duration<=settings['durationSec']+1:raise ValueError('Exit needs a safe ID and readable window')
        body=content_slots.render([e],assets)[0]['body'];data={**e['content'],'exitTreatment':'domain-warp'}
        snapshot=duration-settings['durationSec'];sync=''
        if 'confirmAt' in e['content']:
            sync=f"const child=master.getChildren(false,false,true)[0];{json.dumps(e['content']['confirmAt'])}.forEach((at,i)=>{{const path=root.querySelector('.v-checklist-row-'+i+' path');child.killTweensOf(path);const length=path.getTotalLength();master.set(path,{{strokeDasharray:length,strokeDashoffset:length}},0);master.fromTo(path,{{strokeDashoffset:length}},{{strokeDashoffset:0,duration:.42,ease:'power2.out',immediateRender:false}},at);}});"
        page=f'''<!doctype html><html><head><meta charset="utf-8"><base href="../../"><style>{fonts}{css}html,body{{background:transparent!important}}#capture{{width:1920px;height:1080px;background:transparent}}</style>{scripts}</head><body><main id="capture" class="sample-root" data-composition-id="capture-{ident}" data-width="1920" data-height="1080" data-duration="{duration}"><div class="foreground">{body}</div></main><script>const root=document.getElementById('capture');GLEditorial.mount(root,'capture-{ident}','{tid}',{json.dumps(data,ensure_ascii=False)},{duration},'{e['motion']}').then(()=>{{const master=window.__timelines['capture-{ident}'];{sync}master.seek({snapshot},false);window.captureReady=true;}});</script></body></html>'''
        (out/(ident+'.html')).write_text(page,encoding='utf-8')
        manifest[ident]=dict(fingerprint=exit_effects.fingerprint(project,e),snapshotTime=snapshot,templateId=tid,paddingPx=settings['texturePaddingPx'])
    (out/'capture-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return dict(captures=len(manifest),manifest=str(out/'capture-manifest.json'))

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--project',required=True);a.add_argument('--plan',required=True);x=a.parse_args()
    print(json.dumps(prepare(Path(x.project).resolve(),read(Path(x.plan).resolve())),ensure_ascii=True))
