"""Search Pixel2All metadata; freeze only selected transparent PNGs into a project."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import urllib.request
from urllib.parse import urlsplit, parse_qs

from object_assets import SOURCE_ID, CATALOG_URL, COLLECTION_URL


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url, limit):
    request = urllib.request.Request(url, headers={'User-Agent': 'MAV-Editorial-Pixel2All/1'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.geturl() != url:
            raise ValueError('Unexpected asset redirect: '+response.geturl())
        data = response.read(limit+1)
    if len(data) > limit:
        raise ValueError('Remote asset exceeds size limit')
    return data


def load_catalog():
    raw = fetch(CATALOG_URL, 4*1024*1024)
    catalog = json.loads(raw)
    items = catalog.get('items')
    if catalog.get('schemaVersion') != 1 or not isinstance(items, list) or catalog.get('count') != len(items):
        raise ValueError('Invalid Pixel2All catalog')
    seen = set()
    for item in items:
        ident = item.get('id', '')
        if not re.fullmatch(r'ceramic-[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Invalid/duplicate catalog object ID')
        seen.add(ident)
        preview = urlsplit(item.get('preview', ''))
        version = parse_qs(preview.query, keep_blank_values=True)
        if (preview.scheme or preview.netloc or preview.fragment or
            preview.path != '/media/ceramic/'+ident+'-preview.webp' or
            (preview.query and (set(version) != {'v'} or
             version['v'] != [item.get('sha256', '')[:16]] or
             not re.fullmatch(r'[a-f0-9]{64}', item.get('sha256', ''))))):
            raise ValueError('Unexpected preview URL: '+ident)
    return catalog, digest(raw)


def search(catalog, queries, category=None):
    tokens = [query.strip().casefold() for query in queries if query.strip()]
    results = []
    for item in catalog['items']:
        if category and item['category'] != category:
            continue
        fields = [item['id'], item['name'], item['object'], item['state'], *item.get('tags', []), *item.get('aliases', [])]
        score = sum(3 if token in [f.casefold() for f in fields] else 1
                    for token in tokens if any(token in f.casefold() for f in fields))
        if tokens and not score:
            continue
        results.append({**item, 'sourcePage': COLLECTION_URL+'?item='+item['id'], 'score': score})
    return sorted(results, key=lambda item: (-item['score'], item['id']))


def png_info(data):
    from PIL import Image
    with Image.open(BytesIO(data)) as image:
        if image.format != 'PNG':
            raise ValueError('Selected original must be PNG')
        image.load()
        alpha = image.convert('RGBA').getextrema()[3]
        if alpha[0] == 255 or alpha[1] == 0:
            raise ValueError('Object needs both visible pixels and transparent background')
        return image.width, image.height


def preview_png(data, expected_size):
    from PIL import Image
    with Image.open(BytesIO(data)) as image:
        if image.format != 'WEBP' or max(image.size) != expected_size:
            raise ValueError('Unexpected online preview format/dimensions')
        image.load()
        output = BytesIO()
        image.convert('RGBA').save(output, format='PNG')
    result = output.getvalue()
    png_info(result)
    return result


def local(project, relative):
    target = (project/relative).resolve()
    if not target.is_relative_to(project.resolve()):
        raise ValueError('Object target outside project')
    return target


def read(path, default):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def stage(project, item, catalog_sha, usage='personal-noncommercial', rights_note=None, original=None):
    if usage not in {'owner', 'personal-noncommercial', 'commercial'}:
        raise ValueError('Invalid usage')
    if usage != 'personal-noncommercial' and not (rights_note or '').strip():
        raise ValueError('Owner/commercial use needs actual rights evidence')
    project = Path(project).resolve()
    relative = 'assets/objects/pixel2all/'+item['id']+'.png'
    target = local(project, relative)
    manifest_path = local(project, 'assets/objects/pixel2all/metadata.json')
    credits_path = local(project, 'asset-credits.json')
    manifest = read(manifest_path, {'schemaVersion': 1, 'sourceId': SOURCE_ID, 'items': []})
    credits = read(credits_path, [])
    if manifest.get('schemaVersion') != 1 or manifest.get('sourceId') != SOURCE_ID or not isinstance(manifest.get('items'), list) or not isinstance(credits, list):
        raise ValueError('Invalid existing object manifest/credits')
    acquisition = 'original-import' if original else 'online-preview-converted'
    source_url = None if original else 'https://pixel2all.cn'+item['preview']
    existing = next((x for x in manifest['items'] if x['id'] == item['id']), None)
    # Reuse the frozen online asset without re-downloading it or following catalog changes.
    if existing and not original and existing.get('acquisition') == acquisition:
        if not target.is_file() or digest(target.read_bytes()) != existing['sha256']:
            raise ValueError('Frozen project object changed: '+item['id'])
        if existing.get('usage') != usage or existing.get('licenseEvidence') != rights_note or existing.get('sourceUrl') != source_url:
            raise ValueError('Existing object provenance differs; preserve it and reconcile explicitly')
        from object_assets import validate_credit
        validate_credit(project, relative)
        return {'status': 'unchanged', **existing}
    source_bytes = Path(original).read_bytes() if original else fetch(source_url, 20*1024*1024)
    data = source_bytes if original else preview_png(source_bytes, item['previewSize'])
    width, height = png_info(data)
    if original and (width, height) != (item['width'], item['height']):
        raise ValueError('Original dimensions do not match selected catalog entry')
    record = {'id': item['id'], 'name': item['name'], 'path': relative, 'sourceId': SOURCE_ID,
              'sourcePage': COLLECTION_URL+'?item='+item['id'], 'sourceUrl': source_url,
              'catalogUrl': CATALOG_URL, 'catalogSha256': catalog_sha,
              'sha256': digest(data), 'downloadSha256': digest(source_bytes), 'bytes': len(data),
              'width': width, 'height': height, 'alphaCapable': True,
              'acquisition': acquisition, 'originalDimensions': [item['width'], item['height']],
              'category': item['category'], 'tags': item.get('tags', []), 'aliases': item.get('aliases', []),
              'roles': [item['object'], item['state']], 'usage': usage,
              'licenseUrl': 'https://pixel2all.cn/objects/license', 'licenseEvidence': rights_note,
              'attribution': '素材：像素造物 pixel2all.cn/objects' if usage == 'personal-noncommercial' else None}
    if existing:
        old = {k: v for k, v in existing.items() if k != 'stagedOn'}
        if old == record and target.is_file() and target.read_bytes() == data:
            return {'status': 'unchanged', **existing}
        raise ValueError('Existing object differs; use a new project or reconcile explicitly: '+item['id'])
    if target.exists() or any(c.get('path') == relative for c in credits):
        raise ValueError('Unregistered/conflicting project object: '+relative)
    record['stagedOn'] = datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    target.parent.mkdir(parents=True, exist_ok=True)
    for path in (manifest_path, credits_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    old_manifest = manifest_path.read_bytes() if manifest_path.exists() else None
    old_credits = credits_path.read_bytes() if credits_path.exists() else None
    try:
        target.write_bytes(data)
        manifest['items'].append(record)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        credits_path.write_text(json.dumps(credits+[record], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    except Exception:
        target.unlink(missing_ok=True)
        for path, old in ((manifest_path, old_manifest), (credits_path, old_credits)):
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise
    return {'status': 'staged', **record}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search', action='append', default=[])
    parser.add_argument('--category', choices=('object', 'state', 'metaphor'))
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--id', action='append', default=[])
    parser.add_argument('--project', type=Path)
    parser.add_argument('--file', type=Path, help='Selected original PNG; requires exactly one --id')
    parser.add_argument('--usage', choices=('owner', 'personal-noncommercial', 'commercial'), default='personal-noncommercial')
    parser.add_argument('--rights-note')
    parser.add_argument('--output', type=Path, help='Save search result or staging evidence as JSON')
    args = parser.parse_args()
    if args.file and len(args.id) != 1:
        parser.error('--file requires exactly one --id')
    if args.id and not args.project:
        parser.error('--id requires --project')
    if not (args.list or args.search or args.id):
        parser.error('Use --search, --list or --id with --project')
    catalog, catalog_sha = load_catalog()
    if args.id:
        by_id = {item['id']: item for item in catalog['items']}
        unknown = set(args.id)-by_id.keys()
        if unknown:
            raise ValueError('Unknown catalog ID: '+', '.join(sorted(unknown)))
        result = [stage(args.project, by_id[ident], catalog_sha, args.usage, args.rights_note, args.file)
                  for ident in dict.fromkeys(args.id)]
    else:
        result = {'sourceId': SOURCE_ID, 'catalogUrl': CATALOG_URL, 'catalogSha256': catalog_sha,
                  'queries': args.search, 'checkedOn': datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
                  'items': search(catalog, args.search, args.category)}
    output = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
