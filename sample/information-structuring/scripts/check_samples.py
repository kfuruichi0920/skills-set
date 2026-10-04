"""Validate manifest coverage and references, optionally render every Draw.io page."""
import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
SKILL=BASE.parents[1]/'.agents/skills/information-structuring'


def validate():
    manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))['samples']
    catalog=json.loads((SKILL/'references/catalog.json').read_text(encoding='utf-8'))['samples']
    framework=json.loads((SKILL/'references/framework.json').read_text(encoding='utf-8'))
    themes=json.loads((SKILL/'references/diagram-themes.json').read_text(encoding='utf-8'))['themes']
    for category,expected in [('catalog',{s['id'] for s in catalog}),('purpose',{s['id'] for s in framework['purposes']}),('theme',{s['id'] for s in themes})]:
        actual=[s['id'] for s in manifest if s['category']==category]
        assert set(actual)==expected and len(actual)==len(expected),category
    annotation_ids={s['id'] for s in manifest if s['category']=='annotation'}
    assert annotation_ids=={'screen-orientation','screen-function','screen-workflow','native-annotation','plantuml-svg','plantuml-png'}
    assert {s['form'] for s in manifest if 'form' in s}=={f['id'] for f in framework['forms']},'Basic representation coverage'
    for name in ['diagrams.py','theme_styles.py','build_annotation.py']:
        assert (BASE/'scripts'/name).read_bytes()==(SKILL/'scripts'/name).read_bytes(),f'Stale helper: {name}'
    assert (BASE/'references/diagram-themes.json').read_bytes()==(SKILL/'references/diagram-themes.json').read_bytes()
    tasks=[]
    for filename in sorted({s['file'] for s in manifest}):
        document=ET.parse(BASE/filename).getroot(); pages=document.findall('diagram')
        expected={s['id'] for s in manifest if s['file']==filename}
        assert {p.get('id') for p in pages}==expected,filename
        for index,page in enumerate(pages,1):
            cells=page.findall('./mxGraphModel/root/mxCell'); ids=[c.get('id') for c in cells]
            assert len(ids)==len(set(ids)),page.get('id')
            for cell in cells:
                for attr in ['parent','source','target']:
                    if cell.get(attr): assert cell.get(attr) in ids,(filename,cell.get('id'),attr)
                if cell.get('vertex')=='1':
                    geometry=cell.find('mxGeometry'); assert geometry is not None
                    assert all(float(geometry.get(k,'0'))>=0 for k in ['x','y','width','height']), (filename,cell.get('id'))
            if filename.startswith('catalog/'):
                assert all('shape=image' not in c.get('style','') for c in cells),filename
            tasks.append((filename,index,page.get('id')))
    original=ET.parse(BASE/'sources/native-source.drawio').getroot().findall('./diagram/mxGraphModel/root/mxCell')
    annotated=ET.parse(BASE/'04-native-annotation.drawio').getroot().findall('./diagram/mxGraphModel/root/mxCell')
    by_id={c.get('id'):c for c in annotated}
    def canonical(cell):
        return (cell.tag, cell.attrib, (cell.text or '').strip(), [canonical(child) for child in cell])
    for cell in original:
        if cell.get('vertex') or cell.get('edge'):
            assert canonical(cell)==canonical(by_id[cell.get('id')]),'Native source modified'
    for irpath in [BASE/'sources'/f'{mode}-ir.json' for mode in ['orientation','function','workflow','sequence','sequence-png']]:
        ir=json.loads(irpath.read_text(encoding='utf-8'))
        assert hashlib.sha256((irpath.parent/ir['source']['path']).read_bytes()).hexdigest()==ir['source']['sha256']
    cases=json.loads((BASE/'sources/theme-cases.json').read_text(encoding='utf-8'))['cases']
    variants=[s for s in manifest if s['category']=='theme_case']
    expected={(case['base_id'],case['theme']) for case in cases}
    assert {(s['base_id'],s['theme']) for s in variants}==expected and len(variants)==len(expected)
    assert {s['base_id'] for s in variants if s['base_category']=='purpose'}=={s['id'] for s in framework['purposes']}
    assert {s['theme'] for s in variants}=={s['id'] for s in themes},'All themes must occur in case variants'
    def get_page(filename,identifier):
        return ET.parse(BASE/filename).getroot().find(f"diagram[@id='{identifier}']")
    def styles(value):
        return dict(token.split('=',1) for token in value.split(';') if '=' in token)
    colors={'fillColor','strokeColor','fontColor'}
    for entry in variants:
        base=get_page(entry['base_file'],entry['base_id']); variant=get_page(entry['file'],entry['id'])
        assert {k:v for k,v in base.find('mxGraphModel').attrib.items() if k!='background'}=={k:v for k,v in variant.find('mxGraphModel').attrib.items() if k!='background'},'Canvas geometry changed'
        original=base.findall('./mxGraphModel/root/mxCell'); changed={c.get('id'):c for c in variant.findall('./mxGraphModel/root/mxCell')}
        assert {c.get('id') for c in original}==set(changed),entry['id']
        changed_colors=False
        for cell in original:
            target=changed[cell.get('id')]
            a=dict(cell.attrib); b=dict(target.attrib)
            astyle=styles(a.pop('style','')); bstyle=styles(b.pop('style',''))
            a['value']=a.get('value','').replace(entry['base_theme']+' |',entry['theme']+' |')
            b['value']=b.get('value','')
            assert a==b,(entry['id'],cell.get('id'),'Information or connectivity changed')
            original_geometry=cell.find('mxGeometry'); target_geometry=target.find('mxGeometry')
            if original_geometry is None:
                assert target_geometry is None,(entry['id'],'Unexpected geometry')
            else:
                assert target_geometry is not None,(entry['id'],'Geometry missing')
                assert canonical(original_geometry)==canonical(target_geometry),(entry['id'],'Layout changed')
            assert {k:v for k,v in astyle.items() if k not in colors}=={k:v for k,v in bstyle.items() if k not in colors},(entry['id'],'Shape/line notation changed')
            changed_colors |= any(astyle.get(k)!=bstyle.get(k) for k in colors)
            if entry['base_category']=='annotation' and cell.get('parent')=='1':
                assert astyle==bstyle,(entry['id'],'Source diagram recolored')
        assert changed_colors,entry['id']
        if entry['base_category']=='annotation' and entry['base_id']!='native-annotation':
            irpath=BASE/'sources'/f"{entry['id']}-ir.json"; ir=json.loads(irpath.read_text(encoding='utf-8'))
            assert ir['theme']==entry['theme']
            assert hashlib.sha256((irpath.parent/ir['source']['path']).read_bytes()).hexdigest()==ir['source']['sha256']
    sys.path.insert(0,str(BASE/'scripts'))
    from build_annotation import validate as validate_ir
    bad=json.loads((BASE/'sources/orientation-ir.json').read_text(encoding='utf-8'))
    bad['annotations'][0]['marker_position']={'x':-100,'y':0}
    try: validate_ir(bad)
    except ValueError as error: assert 'Marker does not fit canvas' in str(error)
    else: raise AssertionError('Out-of-canvas marker accepted')
    bad=json.loads((BASE/'sources/sequence-ir.json').read_text(encoding='utf-8'))
    bad['annotations'][0]['leader_points']=[{'x':999,'y':0}]
    try: validate_ir(bad)
    except ValueError as error: assert 'Leader waypoint does not fit canvas' in str(error)
    else: raise AssertionError('Out-of-canvas leader accepted')
    return tasks


def render(tasks, executable, page_ids=()):
    destination=BASE/'previews'; destination.mkdir(exist_ok=True)
    def one(task):
        filename,index,identifier=task
        target=destination/(identifier+'.png')
        result=subprocess.run([executable,'--export','--format','png','--page-index',str(index),'--output',str(target),str(BASE/filename)],capture_output=True,timeout=90)
        if result.returncode!=0 or not target.is_file():
            raise RuntimeError(f'{identifier}: {result.stderr.decode("utf-8",errors="replace")}')
        return identifier
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        selected=[task for task in tasks if not page_ids or task[2] in page_ids]
        assert not page_ids or set(page_ids)=={task[2] for task in selected},'Unknown page ID'
        done=list(pool.map(one,selected))
    # Contact sheets are derived from actual Draw.io exports, never substitute diagrams.
    from PIL import Image, ImageDraw, ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',16)
    for start in range(0,len(tasks),16):
        batch=tasks[start:start+16]; sheet=Image.new('RGB',(1920,4*390),'#e8e8e8'); draw=ImageDraw.Draw(sheet)
        for i,(_,_,identifier) in enumerate(batch):
            preview=Image.open(destination/(identifier+'.png')).convert('RGB'); preview.thumbnail((470,350))
            x=(i%4)*480; y=(i//4)*390
            sheet.paste(preview,(x,y+32)); draw.text((x+8,y+6),identifier,fill='#111',font=font)
        sheet.save(destination/f'contact-{start//16+1:02}.png')
    return done


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--drawio',default='C:/Program Files/draw.io/draw.io.exe')
    parser.add_argument('--page',action='append',default=[],help='Render only the specified changed page ID; repeat as needed')
    parser.add_argument('--theme-cases',action='store_true',help='Render all added theme cases while retaining existing previews')
    args=parser.parse_args(); tasks=validate()
    print(f'PASS: {len(tasks)} pages, coverage, retained tools, XML references, native source preservation, source hashes and theme-case equivalence',flush=True)
    selected=args.page
    if args.theme_cases:
        if selected: parser.error('Choose --theme-cases or --page')
        selected=[s['id'] for s in json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))['samples'] if s['category']=='theme_case']
    if args.render: print(f'Rendered {len(render(tasks,args.drawio,selected))} Draw.io pages',flush=True)
