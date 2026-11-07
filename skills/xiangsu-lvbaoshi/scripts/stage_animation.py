"""Freeze a selected Lemo source and rendered segment into an Editorial project."""
import argparse
import shutil
from pathlib import Path
from prepare import read, dump, sha
from animation_contract import validate_lemo


def stage(project, ident, source, video, style_id, style_file, build_entry):
    import re
    project, source, video, style_file = [Path(p).resolve() for p in (project, source, video, style_file)]
    if not re.fullmatch('[a-z0-9-]+', ident) or not re.fullmatch('[a-z0-9-]+', style_id):
        raise ValueError('Beat and style IDs use lowercase letters, digits and hyphens')
    if not (project/'input-lock.json').is_file():
        raise ValueError('Prepare the parent project first')
    from animation_contract import local
    for name in ('index.html', 'TREATMENT.md', build_entry):
        local(source, name)
    if not video.is_file() or not style_file.is_file():
        raise ValueError('Rendered video and selected STYLE file must exist')
    target = project/'animations'/ident
    media = project/'assets/animations'/(ident+video.suffix.lower())
    if target.exists() or media.exists() or target.is_relative_to(source):
        raise ValueError('Use a new source/asset destination outside the source directory')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('node_modules', '.git', '__pycache__'))
    shutil.copy2(style_file, target/'lemo-style.md')
    files = {p.relative_to(target).as_posix(): sha(p) for p in sorted(target.rglob('*'))
             if p.is_file() and p.name != 'animation-source.json'}
    dump(target/'animation-source.json', dict(provider='lemo-opuscar', styleId=style_id,
         buildEntry=build_entry, styleFile='lemo-style.md', files=files))
    validate_lemo(target, {'provider':'lemo-opuscar', 'styleId':style_id})
    media.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, media)
    relative = media.relative_to(project).as_posix()
    credits = read(project/'asset-credits.json')
    credits.append(dict(path=relative, sha256=sha(media), sourcePage='generated:lemo-opuscar:'+ident))
    dump(project/'asset-credits.json', credits)
    beat = dict(id=ident, kind='animation', provider='lemo-opuscar', styleId=style_id,
                video=relative, editableSource=target.relative_to(project).as_posix(),
                sourceLabel='Lemo-Opuscar · '+style_id, mediaStart=0)
    if read(project/'input-lock.json').get('profile') == 'mav-editorial-kit/v1':
        beat['title'] = ''  # Baijin's optional material caption is explicit, even when empty.
    return beat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('project','beat','source','video','style','style-file','build-entry'):
        parser.add_argument('--'+key, required=True)
    args = parser.parse_args()
    import json
    print(json.dumps(stage(args.project, args.beat, args.source, args.video,
                           args.style, args.style_file, args.build_entry), ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
