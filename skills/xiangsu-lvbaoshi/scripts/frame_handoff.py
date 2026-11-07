"""Freeze the complete upstream frame and its actual visual dependencies."""
import hashlib,json,shutil
from pathlib import Path
SKILL=Path(__file__).resolve().parents[1]
def freeze_frame(project, upstream=None, source=None):
    p=Path(project)
    if (p/'frame.md').exists():return
    if upstream is None:
        for directory in p.resolve().parents:
            if (directory/'frame.md').is_file():upstream=directory/'frame.md';break
            if (directory/'.git').exists():break
    if upstream is None and source is not None:
        folder=Path(source).resolve().parent
        for directory in (folder,*folder.parents):
            if (directory/'frame.md').is_file():upstream=directory/'frame.md';break
            if (directory/'.git').exists():break
    if upstream is not None:
        from animation_routing import inherit_frame
        return inherit_frame(p,p,upstream)
    declarations=json.loads((SKILL/'assets/frame/resources.json').read_text(encoding='utf-8'))['resources']
    files=[i['path'] for i in declarations]
    for item in declarations:
        r=item['path']
        source=SKILL/'assets'/r.removeprefix('assets/glass-lime/');target=p/r
        if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Declared frame resource changed: '+r)
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copyfile(source,target)
        if target.read_bytes()!=source.read_bytes():raise ValueError('Frame resource differs: '+r)
    (p/'frame.md').write_bytes((SKILL/'assets/frame/FRAME.md').read_bytes())
    resources=[dict(path=r,sha256=hashlib.sha256((p/r).read_bytes()).hexdigest()) for r in files]
    (p/'frame-resources.json').write_text(json.dumps(dict(styleId='glass-lime-extracted',resources=resources),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
