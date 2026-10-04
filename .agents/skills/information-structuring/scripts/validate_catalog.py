"""Check generalized structure coverage and generated SVG correspondence."""

import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from build_catalog import ROOT, documents
from diagrams import diagram


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root=ROOT):
    data=json.loads((root/'references/catalog.json').read_text(encoding='utf-8'))
    samples=data['samples']
    require(data['schema_version']==2,'Expected generalized schema v2')
    require(len(samples)==61,'Expected 61 structures')
    require(Counter(s['kind'] for s in samples)=={'base':48,'variant':11,'principle':2},'Kind counts mismatch')
    require(len({s['id'] for s in samples})==61,'Duplicate IDs')
    require(len({s['name'] for s in samples})==61,'Duplicate names')
    require(sorted(s['type_number'] for s in samples if s['kind']=='base')==list(range(1,49)),'Missing base structures')
    require(Counter(s['type_number'] for s in samples if s['kind']=='variant')=={1:1,2:1,7:1,9:1,19:1,21:1,24:1,25:1,45:3},'Variant mismatch')
    require(Counter(s['group'] for s in samples)=={'要点・全体像を示す':8,'分解する':10,'比べる':11,'変化を見せる':4,'関係と位置で見せる':14,'時間と工程で見せる':7,'構造を地図化する':5,'全型に効く原則':2},'Group counts mismatch')
    require('sources' not in data,'Source assets must not be required')
    for s in samples:
        require(s['type_number'] is None if s['kind']=='principle' else s['type_number'] in range(1,49),'Invalid type number')
        for key in ('id','name','use','layout','encoding','caution','skeleton','diagram_key'):
            require(isinstance(s.get(key),str) and bool(s[key].strip()),f"Missing {key}: {s['id']}")
        require('source' not in s and 'observation_basis' not in s,'Source-specific fields remain')
        require(s['diagram_key']==s['id'],'Diagram key mismatch')
        require(s['preview']==f"assets/examples/{s['id']}.svg",'Preview mismatch')
        require(s['axes'].get('horizontal') and s['axes'].get('vertical'),'Missing axes')
        require(len(s['required_information'])>=2,'Missing input requirements')
        preview=root/s['preview']
        require(preview.resolve().is_relative_to(root.resolve()),'Path outside skill')
        content=preview.read_text(encoding='utf-8')
        parsed=ET.fromstring(content)
        require(parsed.tag=='{http://www.w3.org/2000/svg}svg','Invalid SVG root')
        require(parsed.find('{http://www.w3.org/2000/svg}title').text==s['id']+': '+s['name'],'SVG title mismatch')
        require(content==diagram(s),'Stale or mismatched schematic')
    actual={p.name for p in (root/'assets/examples').iterdir()}
    require(actual=={s['id']+'.svg' for s in samples},'Unexpected or missing example assets')
    require(not (root/'assets/source').exists(),'Original image assets remain')
    md,gallery=documents(data)
    require((root/'references/catalog.md').read_text(encoding='utf-8')==md,'Stale Markdown')
    require((root/'assets/catalog-gallery.html').read_text(encoding='utf-8')==gallery,'Stale HTML')
    print('PASS: 48 base + 11 variants + 2 principles; generic axes; 61 matching SVGs; generated views match')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    validate(parser.parse_args().root)
