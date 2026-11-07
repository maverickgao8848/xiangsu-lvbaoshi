"""Use frozen Scene Kit content/sequence contracts with a 像素·绿宝石 outer stage."""
import json,subprocess
from pathlib import Path
from prepare import read,sha
def prepare(p,beat):
    kit=p/'assets/glass-lime/component-kit';manifest=read(kit/'manifest.json')
    if any(sha(kit/name)!=digest for name,digest in manifest['hashes'].items()):raise ValueError('Frozen Scene Kit changed')
    if beat.get('sceneId') not in {'S01','S03','S12'} or not isinstance(beat.get('config'),dict) or not isinstance(beat['config'].get('content'),dict):raise ValueError('Scene Kit needs explicit supported sceneId/config.content')
    return json.loads(subprocess.check_output(['node',str(kit/'prepare.mjs')],input=json.dumps(dict(kind='interface',sceneId=beat['sceneId'],config=beat['config'],duration=beat['end']-beat['start'])).encode()))
