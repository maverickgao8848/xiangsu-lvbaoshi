"""Provenance for online Pixel2All objects and explicitly frozen legacy inputs."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SOURCE_ID = 'pixel2all'
CATALOG_URL = 'https://pixel2all.cn/media/ceramic/catalog.json'
COLLECTION_URL = 'https://pixel2all.cn/objects/'


def source_page_valid(page, source_id=SOURCE_ID):
    url = urlparse(page)
    if url.scheme != 'https' or url.username or url.password:
        return False
    if source_id == 'thiings':
        return url.hostname in {'thiings.co', 'www.thiings.co', 'my.thiings.co'}
    return (url.netloc == 'pixel2all.cn' and url.path.rstrip('/') == '/objects'
            and len(parse_qs(url.query).get('item', [])) == 1
            and re.fullmatch(r'ceramic-[a-z0-9]+(?:-[a-z0-9]+)*', parse_qs(url.query)['item'][0]) is not None)


def validate_credit(project, relative, source_id=SOURCE_ID):
    project = Path(project).resolve()
    file = (project/relative).resolve()
    if not file.is_relative_to(project) or not file.is_file():
        raise ValueError('Object must be a local project file: '+relative)
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    credits_path = project/'asset-credits.json'
    credits = json.loads(credits_path.read_text(encoding='utf-8-sig')) if credits_path.is_file() else []
    matches = [c for c in credits if c.get('path') == relative and c.get('sha256') == digest
               and source_page_valid(c.get('sourcePage', ''), source_id)]
    if source_id == SOURCE_ID:
        matches = [c for c in matches if c.get('sourceId') == SOURCE_ID and
                   c.get('usage') in {'owner', 'personal-noncommercial', 'commercial'} and
                   (c.get('usage') == 'personal-noncommercial' or str(c.get('licenseEvidence') or '').strip())]
    if not matches:
        raise ValueError('Object binding needs matching SHA and '+source_id+' sourcePage/usage evidence: '+relative)
    return matches[0]
