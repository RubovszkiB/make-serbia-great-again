"""Explicit approved revisions supersede historical archive/hash expectations.

Historical source records remain unchanged. Each exception has an exact digest;
visual replacements are checked against their actual supplied archive as well.
"""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]

def revisions():
    p=ROOT/'docs/approved_runtime_changes.json'
    return json.loads(p.read_text()) if p.exists() else {'scripts':{},'visuals':{}}

def expected_hash(path, historical):
    # Exact later user-approved revisions, without rewriting historical ledgers.
    for file in ['balkan_mini_sources.json','balkan_rearmament_sources.json','yugoslav_politics_sources.json','endgame_sources.json','decision_ux_sources.json']:
        p=ROOT/'docs'/file
        if not p.exists():continue
        later=json.loads(p.read_text())
        digest=later.get('files',{}).get(path,{}).get('after_sha256') if file.startswith('decision_ux') else later.get('deployed_sha256',{}).get(path)
        if digest:return digest
    data=revisions()
    if path in data['scripts']:return data['scripts'][path]
    if path in data['visuals']:return data['visuals'][path]['sha256']
    return historical

def approved_script(path):
    if path in revisions()['scripts']:return True
    p=ROOT/'docs/decision_ux_sources.json'
    return p.exists() and path in json.loads(p.read_text())['files']

def check_current_art(texture, relative):
    record=revisions()['visuals'].get(relative)
    if record:
        data=texture.read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'],relative
        with ZipFile(record['package']) as z:assert data==z.read(record['zip_member'])
        with Image.open(texture) as im:assert list(im.size)==record['size'];im.load()
        return True
    for name in ['balkan_mini_sources.json','balkan_rearmament_sources.json','yugoslav_politics_sources.json','economic_energy_sources.json','endgame_sources.json']:
        source=ROOT/'docs'/name
        if not source.exists():continue
        record=json.loads(source.read_text())['assets'].get(relative)
        if record:
            data=texture.read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'],relative
            assert data[84:88]==record['compression'].encode()
            with Image.open(texture) as im:assert list(im.size)==record['size'];im.load()
            return True
    return False
