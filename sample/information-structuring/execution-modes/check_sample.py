"""Check semantic parity and inspectable evidence of mode-specific delivery."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]


def validate():
    manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
    assert not manifest['git_operations']
    fast=(BASE/'fast.drawio').read_bytes();precise=(BASE/'precise.drawio').read_bytes()
    assert fast==precise and hashlib.sha256(fast).hexdigest()==manifest['sha256']
    for entry in manifest['samples']:
        assert entry['checks']==['input-meaning','xml','shape-ids','parent-and-edge-references']
        if entry['mode']=='fast':assert entry['visual_review']=='not_performed' and entry['preview'] is None
        else:assert entry['visual_review']=='accepted' and entry.get('visual_findings')
    assert not (BASE/'fast.png').exists()
    Image.open(BASE/'precise.png').verify()
    assert hashlib.sha256((BASE/'precise.png').read_bytes()).hexdigest()==manifest['preview_sha256']
    for filename in ('fast.drawio','precise.drawio'):
        cells=ET.parse(BASE/filename).findall('.//mxCell');known={c.get('id') for c in cells}
        for cell in cells:
            for key in ('parent','source','target'):
                if cell.get(key):assert cell.get(key) in known and cell.get(key)!=cell.get('id')
    script=REPO/'.agents/skills/information-structuring/scripts/diagram_vocabulary.py'
    for args,count in [([],3),(['--mode','precise'],5),(['--mode','precise','--limit','2'],2)]:
        result=json.loads(subprocess.check_output([sys.executable,'-X','utf8',str(script),*args],cwd=REPO))
        assert len(result['candidates'])==count
    print('PASS: identical meaning/XML, fast preview and visual review omitted, precise preview and review recorded, retrieval limits 3/5/override')


if __name__=='__main__':validate()
