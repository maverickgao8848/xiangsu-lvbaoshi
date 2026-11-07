"""Copy selected repository logo variants and provenance into an Editorial project."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def child(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Missing or outside asset: ' + str(relative))
    return path


def stage(repo, project, brands, variant='mark'):
    library = repo / '5. 素材库' / 'logos'
    index = read(library / 'index.json')
    credits_path = project / 'asset-credits.json'
    credits = read(credits_path) if credits_path.exists() else []
    if not isinstance(credits, list):
        raise ValueError('asset-credits.json must be an array')
    copies, additions, output = [], [], []
    for brand in dict.fromkeys(brands):
        category = next((name for name, ids in index['categories'].items() if brand in ids), None)
        if category is None:
            raise ValueError('Brand absent from local index: ' + brand)
        folder = library / category / brand
        manifest_path = child(library, folder.relative_to(library) / 'manifest.json')
        manifest = read(manifest_path)
        if manifest.get('id') != brand or variant not in manifest['variants']:
            raise ValueError('Logo identity/variant mismatch: ' + brand + '/' + variant)
        asset = child(folder, manifest['variants'][variant])
        relative = Path('assets/brands') / brand / asset.name
        targets = [(asset, project / relative),
                   (manifest_path, project / relative.parent / 'manifest.json')]
        for source, target in targets:
            if not target.resolve().is_relative_to(project.resolve()):
                raise ValueError('Logo target outside project')
            if target.exists() and digest(target) != digest(source):
                raise ValueError('Existing project logo differs; keep it and resolve explicitly: ' + str(target))
        source = manifest.get('source', {})
        record = {'path': relative.as_posix(), 'sha256': digest(asset),
                  'sourcePage': source.get('officialReferenceUrl') or source.get('projectUrl') or source.get('packageUrl'),
                  'sourceLibrary': '5. 素材库/logos/index.json', 'brandId': brand,
                  'sourceManifest': (relative.parent / 'manifest.json').as_posix(),
                  'license': source.get('packageLicense'), 'trademarkNote': manifest.get('trademarkNote'),
                  'fallbackNote': manifest.get('fallbackNote')}
        if not record['sourcePage']:
            raise ValueError('Logo manifest has no traceable source: ' + brand)
        copies.extend(targets)
        if not any(c.get('path') == record['path'] and c.get('sha256') == record['sha256'] for c in credits):
            additions.append(record)
        output.append({'brand': brand, 'asset': record['path'], 'sourceManifest': record['sourceManifest'],
                       'fallbackNote': record['fallbackNote']})
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    project.mkdir(parents=True, exist_ok=True)
    credits_path.write_text(json.dumps(credits + additions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--project', type=Path)
    parser.add_argument('--brand', action='append', default=[])
    parser.add_argument('--variant', default='mark')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()
    if args.list:
        print(json.dumps(read(args.repo / '5. 素材库/logos/index.json')['categories'], ensure_ascii=False, indent=2))
    elif args.project and args.brand:
        print(json.dumps(stage(args.repo, args.project, args.brand, args.variant), ensure_ascii=False, indent=2))
    else:
        parser.error('Use --list or --project and at least one --brand')


if __name__ == '__main__':
    main()
