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
    data=revisions()
    if path in data['scripts']:return data['scripts'][path]
    if path in data['visuals']:return data['visuals'][path]['sha256']
    return historical

def approved_script(path):
    return path in revisions()['scripts']

def check_current_art(texture, relative):
    record=revisions()['visuals'].get(relative)
    if record:
        data=texture.read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'],relative
        with ZipFile(record['package']) as z:assert data==z.read(record['zip_member'])
        with Image.open(texture) as im:assert list(im.size)==record['size'];im.load()
        return True
    source=ROOT/'docs/economic_energy_sources.json'
    if source.exists():
        record=json.loads(source.read_text())['assets'].get(relative)
        if record:
            data=texture.read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'],relative
            assert data[84:88]==record['compression'].encode()
            with Image.open(texture) as im:assert list(im.size)==record['size'];im.load()
            return True
    return False
