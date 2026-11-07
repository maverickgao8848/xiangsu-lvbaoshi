"""Freeze a roughcut, trusted timing and the self-contained 像素·绿宝石 renderer."""
import argparse, hashlib, json, math, shutil, subprocess
from pathlib import Path

SKILL=Path(__file__).resolve().parents[1]
PROFILE='glass-lime-editorial-kit/v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local_file(p,relative):
    if not isinstance(relative,str) or not relative or ':' in relative or '\\' in relative:raise ValueError('Use a project-relative resource path')
    f=(p/relative).resolve()
    if not f.is_relative_to(p.resolve()) or not f.is_file():raise ValueError('Missing/outside resource: '+relative)
    return f
def validate_duration_limit(start,end,max_duration=240):
    if max_duration not in (240,300) or not all(math.isfinite(x) for x in (start,end)) or not 0<end-start<=max_duration:raise ValueError('Duration limit is 240s; explicit --max-duration 300 permits up to 300s')
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(p)]))
def mapped_tokens(alignment,mapping,start,end):
    if mapping.get('schemaVersion')=='mav-talking-head-roughcut-source-map/v1':
        if not isinstance(mapping.get('outputTokens'),list):raise ValueError('Reviewed outputTokens required')
        tokens=[dict(start=round(t['start']-start,4),end=round(t['end']-start,4),text=t['text'],sourceTokenId=t['id']) for t in mapping['outputTokens'] if t['start']>=start-.001 and t['end']<=end+.001 and t['text'].strip()]
    else:
        tokens=[]
        for s in mapping['segments']:
            scale=(s['outputEnd']-s['outputStart'])/(s['sourceEnd']-s['sourceStart'])
            for t in alignment['tokens']:
                if t['start']>=s['sourceStart'] and t['end']<=s['sourceEnd']:
                    a=s['outputStart']+(t['start']-s['sourceStart'])*scale;b=s['outputStart']+(t['end']-s['sourceStart'])*scale
                    if a>=start-.001 and b<=end+.001:tokens.append(dict(start=round(a-start,4),end=round(b-start,4),text=t['text'],sourceTokenId=t['id']))
    return sorted(tokens,key=lambda t:t['start'])
def validate_tokens(tokens,duration):
    previous=0
    for t in tokens:
        if not isinstance(t,dict) or not isinstance(t.get('text'),str) or not t['text'].strip() or any(type(t.get(k)) not in (int,float) or not math.isfinite(t[k]) for k in ('start','end')) or not 0<=t['start']<t['end']<=duration or t['start']<previous-.001:raise ValueError('Invalid/overlapping trusted timing tokens')
        previous=t['end']
def main():
    a=argparse.ArgumentParser(description=__doc__)
    for key in ('source','project','end'):a.add_argument('--'+key,required=True,type=float if key=='end' else str)
    a.add_argument('--start',type=float,default=0);a.add_argument('--max-duration',type=int,choices=(240,300),default=240)
    a.add_argument('--alignment');a.add_argument('--source-map');a.add_argument('--handoff');a.add_argument('--timing',help='Reviewed roughcut-relative {basis,precision,tokens}; times refer to the complete supplied roughcut')
    a.add_argument('--preserve-full-input',action='store_true')
    a.add_argument('--upstream-frame',help='Complete upstream frame; otherwise discover a parent frame before the kit default')
    x=a.parse_args();src=Path(x.source).resolve();p=Path(x.project).resolve()
    if p.exists() and any(p.iterdir()):raise ValueError('Use a new or empty project')
    info=probe(src);duration=float(info['format']['duration']);streams=info['streams']
    if not any(s['codec_type']=='video' for s in streams) or not any(s['codec_type']=='audio' for s in streams):raise ValueError('Roughcut must contain video and original audio')
    if not 0<=x.start<x.end<=duration+.02:raise ValueError('Invalid source range')
    validate_duration_limit(x.start,x.end,x.max_duration)
    if bool(x.alignment)!=bool(x.source_map) or (x.timing and x.alignment):raise ValueError('Use timing or paired alignment/source-map')
    basis='missing trusted timing';precision='none';tokens=[];hashes={}
    if x.handoff:
        handoff=read(x.handoff)
        for key in ('video','timeline','transcript','sourceMap'):
            if handoff.get(key):
                f=local_file(Path(x.handoff).resolve().parent,handoff[key]['path'])
                if sha(f)!=handoff[key]['sha256']:raise ValueError('Handoff hash mismatch: '+key)
                if key=='video' and f!=src:raise ValueError('Wrong handoff video')
                hashes[key]=sha(f)
    if x.timing:
        timing=read(x.timing);basis=timing.get('basis');precision=timing.get('precision')
        if not isinstance(basis,str) or not basis.strip() or precision not in ('word','segment'):raise ValueError('Timing needs declared review basis and word/segment precision')
        validate_tokens(timing['tokens'],duration)
        tokens=[{**t,'start':round(t['start']-x.start,4),'end':round(t['end']-x.start,4)} for t in timing['tokens'] if t['start']>=x.start and t['end']<=x.end]
    elif x.alignment:
        tokens=mapped_tokens(read(x.alignment),read(x.source_map),x.start,x.end);basis='mapped reviewed alignment/source-map';precision='word'
    validate_tokens(tokens,x.end-x.start)
    from orchestration import VERSION as OV
    from effect_planning import VERSION as EV
    # Check the distributable before touching a new project.
    manifest=read(SKILL/'bundle-manifest.json')
    if any(sha(SKILL/f['path'])!=f['sha256'] for f in manifest['files']):raise ValueError('Skill bundle drift; regenerate and review manifest')
    (p/'assets').mkdir(parents=True)
    if x.preserve_full_input:
        video=next(s for s in streams if s['codec_type']=='video')
        if x.start!=0 or abs(x.end-duration)>.001 or (video['width'],video['height'],video['r_frame_rate'])!=(1920,1080,'30/1'):raise ValueError('Full preservation needs the entire canonical 1920x1080/30fps roughcut')
        shutil.copy2(src,p/'assets/source.mp4')
    else:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(x.start),'-i',str(src),'-t',str(x.end-x.start),'-map','0:v:0','-map','0:a:0','-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2','-r','30','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(p/'assets/source.mp4')],check=True)
    shutil.copytree(SKILL/'assets',p/'assets/glass-lime');(p/'assets/vendor').mkdir();shutil.copy2(SKILL/'assets/gsap.min.js',p/'assets/vendor/gsap.min.js')
    dump(p/'words.json',dict(basis=basis,precision=precision,tokens=tokens))
    dump(p/'asset-credits.json',[])
    dump(p/'input-lock.json',dict(profile=PROFILE,duration=round(x.end-x.start,4),maxDurationSec=x.max_duration,sourceStart=x.start,sourceEnd=x.end,originalSourceName=src.name,originalSourceSha256=sha(src),frozenSha256=sha(p/'assets/source.mp4'),wordsSha256=sha(p/'words.json'),source='assets/source.mp4',freezeMethod='copy-full-canonical' if x.preserve_full_input else 'encode-range',handoffHashes=hashes,orchestrationVersion=OV,effectPlanningVersion=EV,objectSourceId='pixel2all',resources={f['path'][7:]:f['sha256'] for f in manifest['files'] if f['path'].startswith('assets/')},gsapSha256=sha(p/'assets/vendor/gsap.min.js')))
    from navigation import DEFAULTS_VERSION
    from roll_transitions import VERSION as RV
    lock=read(p/'input-lock.json');lock['navigationDefaultsVersion']=DEFAULTS_VERSION;lock['rollTransitionsVersion']=RV;dump(p/'input-lock.json',lock)
    from plan import skeleton
    dump(p/'edit-plan.json',skeleton(p))
    from animation_contract import VERSION as AV
    lock=read(p/'input-lock.json');lock['animationRoutingVersion']=AV;dump(p/'input-lock.json',lock)
    from frame_handoff import freeze_frame
    freeze_frame(p,x.upstream_frame,src)
    print(json.dumps(dict(project=str(p),duration=x.end-x.start,tokens=len(tokens),stage='draft; author decisions before compilation')))
if __name__=='__main__':main()
