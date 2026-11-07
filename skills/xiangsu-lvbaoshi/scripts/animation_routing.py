"""Discover the installed 像素 MG workflow; report missing rather than substitute its style."""
import os
import json
import subprocess
from pathlib import Path
from prepare import read, sha

SKILL=Path(__file__).resolve().parents[1]
def repository(project=None):
    """Use the actual content workspace, never the Skill installation depth."""
    if os.environ.get('EDITORIAL_REPO'):
        return Path(os.environ['EDITORIAL_REPO']).expanduser().resolve()
    start=Path(project or Path.cwd()).resolve()
    if start.is_file():start=start.parent
    for root in (start,*start.parents):
        if (root/'.git').exists() or (root/'.agents/skills').is_dir() or (root/'.codex/skills').is_dir() or (root/'5. 素材库').is_dir():
            return root
    return start

def candidates(repo=None, skill_name="xiangsu-mg"):
    repo=Path(repo).resolve() if repo is not None else repository()
    paths=[repo/'.agents/skills/xiangsu-mg/SKILL.md',repo/'.codex/skills/xiangsu-mg/SKILL.md',Path.home()/'.agents/skills/xiangsu-mg/SKILL.md']
    if os.environ.get('CODEX_HOME'):paths.append(Path(os.environ['CODEX_HOME'])/'skills/xiangsu-mg/SKILL.md')
    paths.append(Path.home()/'.codex/skills/xiangsu-mg/SKILL.md')
    if skill_name != 'xiangsu-mg':
        paths = [p.parent.parent/skill_name/'SKILL.md' for p in paths]
    return list(dict.fromkeys(paths))

def discover(project=None, provider="xiangsu-mg"):
    if provider not in {'xiangsu-mg','mav-mg','lemo-opuscar'}:raise ValueError('Unknown animation provider')
    skill_name = 'lemo-opuscar' if provider == 'lemo-opuscar' else 'xiangsu-mg'
    checked=[]
    for path in candidates(repository(project), skill_name):
        checked.append(str(path))
        if path.is_file():
            # Unreadable/invalid installations are not "missing".
            path.read_text(encoding='utf-8-sig')
            return {'provider':'lemo-opuscar' if provider == 'lemo-opuscar' else 'mav-mg','skillPath':str(path),'skillSha256':sha(path),'checkedPaths':checked}
    if provider == 'lemo-opuscar':return {'provider':'missing','checkedPaths':checked,'reason':'Lemo-Opuscar absent at repository and personal locations'}
    return {'provider':'missing','checkedPaths':checked,'reason':'像素 MG absent at repository and personal locations'}

def inherit_frame(project, child, upstream=None, replace=False):
    route=discover(project)
    if route['provider']!='mav-mg':raise ValueError('Install 像素 MG to inherit the upstream frame')
    script=Path(route['skillPath']).parent/'scripts/inherit-frame.mjs'
    args=['node',str(script),'--project',str(child),'--upstream',str(upstream or Path(project)/'frame.md')]
    if replace:args.append('--replace')
    return json.loads(subprocess.check_output(args,text=True,encoding='utf-8'))

def validate_frame(project, child, style_id=None, style_override=None):
    child=Path(child);record=child/'frame-provenance.json'
    lock=read(Path(project)/'input-lock.json')
    if style_override is not None and (not isinstance(style_override,str) or not style_override.strip()):
        raise ValueError('animationStyleOverride must record the user style decision')
    if lock.get('animationRoutingVersion') and not style_override and not record.is_file():
        raise ValueError('New MG must inherit the complete editorial frame')
    if not record.exists():return None
    route=discover(project)
    if route['provider']!='mav-mg':raise ValueError('像素 MG required to verify inherited frame')
    script=Path(route['skillPath']).parent/'scripts/inherit-frame.mjs'
    result=subprocess.run(['node',str(script),'--project',str(child),'--check'],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise ValueError('Inherited MG frame verification failed: '+result.stdout+result.stderr)
    data=json.loads(record.read_text(encoding='utf-8'))
    if style_id and data['styleId']!=style_id:raise ValueError('MG styleId differs from inherited frame provenance')
    if lock.get('animationRoutingVersion') and not style_override:
        parent=Path(project)
        if sha(parent/'frame.md') != data.get('frameSha256'):
            raise ValueError('MG must preserve the complete parent frame bytes')
        resources={r['path']:r['sha256'] for r in data.get('resources',[])}
        for item in read(parent/'frame-resources.json')['resources']:
            if resources.get(item['path']) != item['sha256'] or sha(parent/item['path']) != item['sha256']:
                raise ValueError('MG must inherit the complete parent frame resources')
    return data
