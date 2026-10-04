"""Check reusable fragments and template URLs; optionally render fragment previews."""
import argparse
import copy
import functools
import hashlib
import http.server
import json
import re
import subprocess
import threading
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote
from serve_vocabulary import Handler

BASE = Path(__file__).resolve().parents[1]


def records():
    return json.loads(ET.parse(BASE/'libraries/diagram-vocabulary.xml').getroot().text)


def check_cells(model):
    cells = model.findall('./root/mxCell')
    identifiers = {c.get('id') for c in cells}
    assert len(identifiers) == len(cells)
    for cell in cells:
        for key in ('parent', 'source', 'target'):
            if cell.get(key):
                assert cell.get(key) in identifiers and cell.get(key) != cell.get('id')


def render():
    folder = BASE/'libraries/previews'
    folder.mkdir(exist_ok=True)
    manifest=[]
    for index, record in enumerate(records(), 1):
        model = ET.fromstring(record['xml']); check_cells(model)
        wrapper = ET.Element('mxfile', host='app.diagrams.net')
        page = ET.SubElement(wrapper, 'diagram', id=f'fragment-{index}', name=record['title'])
        page.append(copy.deepcopy(model))
        path = folder/f'fragment-{index:02}.drawio'
        ET.indent(wrapper); ET.ElementTree(wrapper).write(path, encoding='utf-8', xml_declaration=True)
        preview = path.with_suffix('.png')
        subprocess.run(['C:/Program Files/draw.io/draw.io.exe', '--export', '--format', 'png',
                        '--page-index', '1', '--output', str(preview), str(path)],
                       check=True, capture_output=True, timeout=90)
        manifest.append(dict(title=record['title'], file=path.name, preview=preview.name,
                             sha256=hashlib.sha256(preview.read_bytes()).hexdigest()))
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    from PIL import Image, ImageDraw
    sheet=Image.new('RGB',(1200,5*240),'white');draw=ImageDraw.Draw(sheet)
    for index,item in enumerate(manifest):
        pic=Image.open(folder/item['preview']).convert('RGB');pic.thumbnail((570,195))
        x=(index%2)*600+15;y=(index//2)*240+35
        sheet.paste(pic,(x,y));draw.text((x,y-25),f'Fragment {index+1:02}',fill='black')
    sheet.save(folder/'contact-sheet.png')
    print('Rendered 10 fragment previews')


class QuietHandler(Handler):
    def log_message(self,*args): pass


def validate():
    from PIL import Image
    for record in records():check_cells(ET.fromstring(record['xml']))
    for item in json.loads((BASE/'libraries/previews/manifest.json').read_text(encoding='utf-8')):
        preview=BASE/'libraries/previews'/item['preview']
        assert hashlib.sha256(preview.read_bytes()).hexdigest()==item['sha256']
        Image.open(preview).verify()
    configuration=json.loads((BASE/'libraries/configuration.json').read_text(encoding='utf-8'))
    delivery=json.loads((BASE/'libraries/delivery.json').read_text(encoding='utf-8'))
    templates=ET.parse(BASE/'libraries/template-library.xml').getroot()
    assert len(configuration['customTemplates'])==75
    assert configuration['customTemplates']==[{k:v for k,v in t.attrib.items() if k!='clibs'} for t in templates.findall('template')]
    assert all(i.startswith('U') for i in configuration['defaultCustomLibraries'])
    urls=[delivery['template_library'],delivery['custom_library']]
    urls.extend(unquote(i[1:]) for i in configuration['defaultCustomLibraries'])
    urls.extend(c.text[1:] for c in templates.findall('./clibs/add'))
    urls.extend(t.get(key) for t in templates.findall('template') for key in ('url','preview'))
    handler=functools.partial(QuietHandler,directory=str(BASE))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base_path=urlsplit(delivery['base_url']).path
        for url in urls:
            parsed=urlsplit(url);assert parsed.path.startswith(base_path)
            relative=parsed.path[len(base_path):]
            local=f'http://127.0.0.1:{server.server_port}/{relative}'
            with urllib.request.urlopen(local,timeout=10) as response:
                assert response.status==200
                assert response.headers['Access-Control-Allow-Origin']=='*'
                assert response.read()==(BASE/relative).read_bytes()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=3)
    docs=list(BASE.rglob('*.md'))
    docs.append(BASE.parents[2]/'.agents/skills/information-structuring/references/diagram-vocabulary.md')
    for document in docs:
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
            if urlsplit(target).scheme or target.startswith('#'):continue
            assert (document.parent/unquote(target.split('#',1)[0])).exists(),(document,target)
    print(f'Validated 10 fragments and {len(urls)} local HTTP resource references; editor configuration is not installed automatically')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    if args.render:render()
    validate()
