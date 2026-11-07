"""Hash-bound actual foreground textures for short local domain-warp exits."""
import hashlib,json,re

def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()

def fingerprint(project,entry):
    content=entry['content']
    value={'content':content,'duration':entry['end']-entry['start'],'motion':entry.get('motion','none'),
           'frameSha256':sha(project/'frame.md') if (project/'frame.md').exists() else None,
           'images':{p:sha(project/p) for p in content.get('images',[])}}
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()

def validate(project,plan,config):
    entries=plan['effects']+plan['beats']
    chosen=[e for e in entries if e.get('exitMotion')]
    if not chosen:return
    manifest=json.loads((project/'assets/glass-lime-exits/manifest.json').read_text(encoding='utf-8'))
    credits=json.loads((project/'asset-credits.json').read_text(encoding='utf-8-sig'))
    settings=config['exitTreatments']['domain-warp']
    for e in chosen:
        if e['exitMotion']!='domain-warp' or e.get('motion') not in ('B','D'):raise ValueError('Local domain-warp exit requires an actual B/D template foreground')
        if e['end']-e['start']<=settings['durationSec']+1:raise ValueError('Keep a readable hold before local exit')
        item=manifest.get(e['id'])
        if not item or item.get('fingerprint')!=fingerprint(project,e):raise ValueError('Regenerate exit texture after changing content, frame or media: '+e['id'])
        rel='assets/glass-lime-exits/'+e['id']+'.png';file=project/rel;header=file.read_bytes()[:26]
        if header[:8]!=b'\x89PNG\r\n\x1a\n' or int.from_bytes(header[16:20],'big')!=1920 or int.from_bytes(header[20:24],'big')!=1080 or header[25]!=6:raise ValueError('Exit foreground must be RGBA 1920x1080 PNG')
        if not any(c.get('path')==rel and c.get('sha256')==sha(file) and c.get('sourcePage')=='generated:actual-glass-lime-foreground:'+e['id'] for c in credits):raise ValueError('Exit texture credit/hash mismatch')
        regions=item.get('regions',[])
        if not 1<=len(regions)<=4 or any(set(b)!={'x','y','width','height'} or not 0<=b['x']<b['x']+b['width']<=1920 or not 0<=b['y']<b['y']+b['height']<=1080 for b in regions):raise ValueError('Exit needs valid local foreground regions')

def data(project,entry,config):
    result=dict(entry['content'])
    if not entry.get('exitMotion'):return result
    item=json.loads((project/'assets/glass-lime-exits/manifest.json').read_text(encoding='utf-8'))[entry['id']]
    result.update(exitTreatment='domain-warp',exitTexture='assets/glass-lime-exits/'+entry['id']+'.png',
                  exitRegions=item['regions'],exitSettings=config['exitTreatments']['domain-warp'])
    return result

def cues(entry,config,kit):
    rows=config['cues'][entry['motion']][kit]
    if not entry.get('exitMotion'):return rows
    settings=config['exitTreatments']['domain-warp'];duration=entry['end']-entry['start']
    return [c for c in rows if c['at']<4.7]+[dict(at=6*(duration-settings['durationSec'])/duration,**settings['sound'])]
