"""Inspect or explicitly refresh the local distributable manifest after a reviewed change."""
import argparse
from prepare import SKILL, read, dump, sha


def inventory():
    paths = [SKILL/'SKILL.md', SKILL/'asset-credits.json']
    for folder in ('agents','assets','references','scripts'):
        paths.extend(p for p in (SKILL/folder).rglob('*') if p.is_file() and
                     '__pycache__' not in p.parts and p.suffix != '.pyc')
    return [dict(path=p.relative_to(SKILL).as_posix(), sha256=sha(p)) for p in sorted(set(paths))]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Record the inspected local source as the current bundle')
    args=parser.parse_args()
    manifest=read(SKILL/'bundle-manifest.json')
    current=inventory()
    old={f['path']:f['sha256'] for f in manifest['files']}
    new={f['path']:f['sha256'] for f in current}
    changes=sorted(p for p in old.keys() | new.keys() if old.get(p)!=new.get(p))
    print('\n'.join(changes) or 'Bundle matches local files')
    if args.write:
        dump(SKILL/'bundle-manifest.json',{**manifest,'files':current})
    elif changes:
        raise SystemExit(1)


if __name__=='__main__':
    main()
