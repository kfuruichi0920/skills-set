"""Enrich accepted metadata, publish the catalogue and native reuse libraries, validate."""
import argparse
import base64
import copy
import csv
import hashlib
import html
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, urlparse

BASE=Path(__file__).resolve().parents[1]
REPO=BASE.parents[2]
SKILL=REPO/'.agents/skills/information-structuring'
sys.path.insert(0,str(SKILL/'scripts'))
import shape_catalog as sc
from diagram_vocabulary import search
from build_examples import DEFINITIONS

# A visited documentation page and an inspected editable source are different evidence.
REFERENCE_MAP=[1,1,3,14,4,2,8,9,5,6,7,10,11,12,3,13,15,16,17,18,18,19,20,21,22,
               None,23,24,None,24,25,26,27,28,29,30,31,32,32,33,34,33,35,36,37,38,39,40,
               41,42,43,44,46,47,48,48,49,50,51,52,53,54,54,55,56,57,58,56,45,60,
               None,59,10,1,47]
VARIANTS={18:2,20:2,22:21,23:21,28:2,47:33,63:31,67:2}
STRUCTURES={
    'hub-and-spoke':['relation','context'], 'nested-containers':['containment','hierarchy'],
    'component-interface':['responsibility','interface'], 'layered-stack':['hierarchy','dependency'],
    'sequence-lifelines':['sequence','message'], 'state-transition':['state','event','condition'],
    'activity-branch':['flow','condition'], 'entity-relations':['identity','relation','cardinality'],
    'trace-pipeline':['requirement','trace'], 'trace-matrix':['requirement','trace','verification'],
    'role-swimlane':['sequence','responsibility','role'], 'phase-role-grid':['phase','responsibility','flow'],
    'phase-team-grid':['phase','team','responsibility'], 'responsibility-matrix':['work','role','responsibility'],
    'task-time-grid':['time','duration','task','dependency'], 'time-axis':['time','event'],
    'horizon-roadmap':['time','outcome'], 'milestone-gates':['time','condition','decision'],
    'status-columns':['state','work'], 'two-axis-positioning':['quantity','comparison','position'],
    'fishbone':['cause','category','hypothesis'], 'comparison-table':['attribute','comparison'],
    'paired-before-after':['change','comparison'], 'labelled-concept-graph':['definition','relation'],
    'dual-plane':['control','flow','boundary'], 'trust-boundaries':['trust','boundary','control'],
    'quantity-flow':['quantity','flow'], 'funnel':['quantity','condition','filter'],
    'cycle':['sequence','iteration'], 'feedback-loop':['flow','observation','control'],
    'multi-level-zoom':['hierarchy','abstraction','trace'], 'fault-tree':['condition','cause','logic'],
}
NOT_USE={
 'sequence':'実時間の期間や予定日を比較したい場合', 'state':'担当ごとの業務手順だけを説明したい場合',
 'dataflow':'実行の並行性やイベント順を厳密に示したい場合', 'organisation':'組織を越えた多対多の責任割当を示したい場合',
 'raci':'作業の実行順序や完了条件を示したい場合', 'wbs':'依存関係や実時間の予定をこの木だけで示したい場合',
 'timeline':'期間や資源制約を比較したい場合', 'gantt':'論理順序しか分からず期間が与えられていない場合',
 'pert':'資源制約・稼働率・暦を含む完了日を保証したい場合', 'ha':'待機系の存在だけで継続を保証したい場合',
 'fishbone':'相関や候補から原因確定を主張したい場合', 'sankey':'数量が不明、単位が異なる、流量が保存されない場合',
 'venn':'集合間の依存方向や厳密な数量比を説明したい場合', 'screenshot':'表示だけから未確認の動作や操作結果を断定したい場合',
 'matrix':'二軸の尺度や比較対象の粒度が揃わない場合', 'business-model':'九つの論点を列挙するだけで事業の成立を証明したい場合',
 'funnel':'各段階の包含関係や選別条件が不明な場合', 'fault-tree':'論理結合の意味が不明なまま故障確率を算出したい場合',
}

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def enrich(meta,number,assets):
    pattern=meta['composition_pattern']; key=meta['key']
    meta['pattern']=pattern
    meta['variant_of']=f'DV-{VARIANTS[number]:03}' if number in VARIANTS else None
    meta['core']=number in (1,2,4,7,8,12,14,16,17,25,28,29,31,32,33,35,40,43,45,46,48,50,53,55,56,58,63,64,73,74)
    meta['information_structure']=sorted(set(meta['information_structure']+STRUCTURES.get(pattern,[pattern])))
    meta['tags']=sorted(set(meta['tags']+meta['information_structure']))
    if key in NOT_USE: meta['when_not_to_use']=list(dict.fromkeys(meta['when_not_to_use']+[NOT_USE[key]]))
    if meta['visual']['density']=='low-to-medium': meta['visual']['density']='medium' if number in (13,16,33,35,37,38,39,43,47,52,55) else 'low'
    meta['presentation_context']='設計レビュー' if meta['domain'][0] in ('software','infrastructure','security') else '関係者への説明・案の比較'
    ref=REFERENCE_MAP[number-1]
    observation=[]
    if ref:
        asset=assets[f'REF-{ref:03}']
        observation=[dict(asset=asset['id'],source_refs=asset['source_refs'],analysis=asset['analysis'],
             visual_observation=asset['visual_review']['finding'],review_scope=asset['visual_review']['scope'],
             preview='sources/'+asset['preview_path'],original='sources/'+asset['local_path'])]
    if number==26: note='複数地域の境界と複製という抽象構造を公式Architecture Centerから再構成。REF-022をmulti-region原図と扱わない。'
    elif number==39: note='REF-032の行動×段階のグリッドを応用。専用Customer Journey原図を確認したとは扱わない。'
    elif number==60: note='REF-052から流れの分岐を抽出。原図は比例幅の検証根拠ではなく、本例の20=12+8と線幅を独立検査する。'
    elif number==65: note='原図は機能カテゴリの区画。本例では機能と主対象の関係へ独自に再配置した。'
    elif number==66: note='原図はUI断片の説明。独自に描いた架空UIの保持と番号説明へ応用した。'
    else: note='関係の種類と粒度を抽出し、固有データと具体的配置をコピーせず架空の予約サービスへ適応した。'
    meta['source_analysis']=dict(observations=observation,adaptation=note,
          layout_reason='所属は境界、順序は方向、比較は共通位置で読む。説明対象以外の位置や色に意味を作らない。',
          tradeoff='対象数が増えたらOverviewとDetailへ分け、入力に合わせて間隔・折返し・接続点を再計算する。')
    # A source document is not evidence that this independent sample is a formally compliant model.
    meta['notation_scope']='概略の説明パターン。正式な専門記法・分析の完全性を保証しない。'
    meta['editability']=('PlantUML正本を保持。内部SVGは単一オブジェクト。' if meta['external_source']['path']=='source.puml' else '原図SVGを保持。内部は単一オブジェクト、番号と説明はDraw.ioで編集できる。') if meta.get('external_source') else '図形・表・所属・接続・ラベルをDraw.ioで編集できる。'
    return meta

def fragment_model(path,ids):
    model=ET.parse(path).find('./diagram/mxGraphModel'); root=model.find('root')
    all_cells={c.get('id'):c for c in root}; selected=set(ids)
    # Keep descendants, and keep every relationship whose endpoints are both selected.
    changed=True
    while changed:
        added={i for i,c in all_cells.items() if c.get('parent') in selected}
        old=len(selected);selected.update(added);changed=len(selected)!=old
    selected.update(i for i,c in all_cells.items() if c.get('edge')=='1' and c.get('source') in selected and c.get('target') in selected)
    new=ET.Element('mxGraphModel'); nr=ET.SubElement(new,'root');ET.SubElement(nr,'mxCell',id='0');ET.SubElement(nr,'mxCell',id='1',parent='0')
    top=[]
    for i,c in all_cells.items():
        if i not in selected:continue
        child=copy.deepcopy(c)
        if child.get('parent') not in selected:child.set('parent','1');top.append(child)
        nr.append(child)
    positions=[c.find('mxGeometry') for c in top if c.get('vertex')=='1']
    xmin=min(float(g.get('x','0')) for g in positions);ymin=min(float(g.get('y','0')) for g in positions)
    width=max(float(g.get('x','0'))+float(g.get('width','0')) for g in positions)-xmin
    height=max(float(g.get('y','0'))+float(g.get('height','0')) for g in positions)-ymin
    for c in top:
        g=c.find('mxGeometry')
        if g is None:continue
        if c.get('vertex')=='1':g.set('x',str(float(g.get('x','0'))-xmin));g.set('y',str(float(g.get('y','0'))-ymin))
        for point in g.findall('./Array/mxPoint'):point.set('x',str(float(point.get('x'))-xmin));point.set('y',str(float(point.get('y'))-ymin))
    return ET.tostring(new,encoding='unicode'),width,height

def libraries(entries,base_url):
    fragments=[(1,['user','system'],'利用者と主対象'),(20,['outer'],'クラウドの境界'),(25,['active','standby'],'稼働系と待機系'),
       (26,['r0','r1'],'主系と複製先'),(4,['layer0','layer1','layer2'],'三層の依存'),(29,['cp','dp'],'制御とデータ'),
       (1,['legend'],'意味の凡例'),(64,['system','c0','c1','c2'],'外周の説明'),(47,['grid'],'工程とチームの表'),(49,['control'],'対策の注記')]
    records=[];manifest=[]
    for n,ids,title in fragments:
        entry=next(e for e in entries if e['id']==f'DV-{n:03}')
        xml,w,h=fragment_model(REPO/entry['artifact'],ids)
        records.append(dict(title=title,tags=' '.join([entry['key'],entry['composition_pattern'],*entry['domain']]),xml=xml,w=w,h=h))
        manifest.append(dict(title=title,source=entry['id'],selected_cells=ids,kind='fragment'))
    root=ET.Element('mxlibrary');root.text=json.dumps(records,ensure_ascii=False)
    ET.ElementTree(root).write(BASE/'libraries/diagram-vocabulary.xml',encoding='utf-8',xml_declaration=True)
    save(BASE/'libraries/fragment-manifest.json',manifest)
    templates=ET.Element('templates'); clibs=ET.SubElement(templates,'clibs',name='vocabulary-fragments')
    ET.SubElement(clibs,'add').text='U'+base_url+'libraries/diagram-vocabulary.xml'
    for e in entries:
        local='examples/'+e['id']+'/'
        ET.SubElement(templates,'template',section=e['domain'][0],subsection=e['composition_pattern'],
          title=e['title_ja'],name=e['purpose'],url=base_url+local+'example.drawio',preview=base_url+local+'preview.png',
          libs=';'.join(['general','basic',*e['drawio']['libraries']]),clibs='vocabulary-fragments',tags=';'.join(e['tags']))
    ET.indent(templates);ET.ElementTree(templates).write(BASE/'libraries/template-library.xml',encoding='utf-8',xml_declaration=True)
    # Editor customTemplates accepts template objects, not URLs of library XML.
    # URI-based custom library IDs require U + URL encoding.
    custom_templates=[{k:v for k,v in t.attrib.items() if k!='clibs'} for t in templates.findall('template')]
    save(BASE/'libraries/configuration.json',dict(customTemplates=custom_templates,
        defaultCustomLibraries=['U'+quote(base_url+'libraries/diagram-vocabulary.xml',safe='')]))
    save(BASE/'libraries/delivery.json',dict(base_url=base_url,
        template_library=base_url+'libraries/template-library.xml',
        custom_library=base_url+'libraries/diagram-vocabulary.xml'))

def schema():
    props={name:{'type':'string','minLength':1} for name in ('id','key','title_ja','title_en','purpose','pattern','composition_pattern','artifact','artifact_hash','preview_hash')}
    for name in ('domain','diagram_type','source_refs','information_structure','visual_pattern','relationships','when_to_use','when_not_to_use','strengths','limitations','tags'):
        props[name]={'type':'array','items':{'type':'string'},'minItems':0 if name=='relationships' else 1}
    props.update(core={'type':'boolean'},variant_of={'type':['string','null']},
       quality={'type':'object','required':['status','findings','reviewed_at'],'properties':{'status':{'const':'accepted'},'findings':{'type':'string','minLength':10}}},
       layout={'type':'object','required':['primary_axis','grouping','reading_direction']},
       visual={'type':'object','required':['theme','density','hierarchy','emphasis']},
       drawio={'type':'object','required':['libraries','native_features']},source_analysis={'type':'object','required':['observations','adaptation']},
       semantic_shape_requirement={'type':'array'},audience={'type':'array','minItems':1})
    result = dict(type='object',required=['schema_version','entries'],
       properties={'schema_version':{'const':1},'entries':{'type':'array','minItems':40,'items':{'type':'object','required':list(props),'properties':props}}})
    result['$schema']='https://json-schema.org/draft/2020-12/schema'
    return result

def publish(base_url):
    (BASE/'catalog').mkdir(exist_ok=True);(BASE/'libraries').mkdir(exist_ok=True)
    assets={a['id']:a for a in sc.read(BASE/'sources/official-assets.json')['assets']}; entries=[]
    for i in range(1,len(DEFINITIONS)+1):
        folder=BASE/'examples'/f'DV-{i:03}';meta=sc.read(folder/'metadata.yaml')
        if meta['quality']['status']!='accepted':raise ValueError('Review required: '+meta['id'])
        meta=enrich(meta,i,assets);save(folder/'metadata.yaml',meta);entries.append(meta)
        (folder/'README.md').write_text(f"# {meta['title_ja']}\n\n{meta['purpose']}。\n\n[Draw.io](example.drawio) · [SVG](preview.svg) · [情報と採否](metadata.yaml) · [IR](diagram-ir.json)\n\n![プレビュー](preview.png)\n\n採用条件: {meta['when_to_use'][0]}。\n\n不向きな条件: {'、'.join(meta['when_not_to_use'])}。\n\n参照: {', '.join(meta['source_refs'])}（[URL一覧](../../sources/urls.md)）。{meta['source_analysis']['adaptation']}\n\n{meta['editability']}\n\n点検記録: {meta['quality']['findings']}\n",encoding='utf-8',newline='\n')
    data=dict(schema_version=1,source_registry='sample/information-structuring/diagram-vocabulary/sources/source-registry.yaml',entries=entries)
    save(BASE/'catalog/diagram-vocabulary.json',data);save(BASE/'catalog/diagram-vocabulary.schema.json',schema())
    save(SKILL/'references/drawio/diagram-vocabulary.json',data);save(SKILL/'references/drawio/diagram-vocabulary.schema.json',schema())
    libraries(entries,base_url)
    with (BASE/'catalog/index.tsv').open('w',encoding='utf-8-sig',newline='') as stream:
        w=csv.writer(stream,delimiter='\t');w.writerow(['ID','名称','分野','説明パターン','テーマ','Core','派生元','出典','ファイル'])
        for e in entries:w.writerow([e['id'],e['title_ja'],','.join(e['domain']),e['composition_pattern'],e['visual']['theme'],e['core'],e['variant_of'] or '',','.join(e['source_refs']),e['artifact']])
    sources=sc.read(BASE/'sources/source-registry.json')['sources']
    (BASE/'sources/urls.md').write_text('# 参照URL一覧\n\nURLの正本は[source-registry.yaml](source-registry.yaml)。取得状況とライセンスは各項目を参照する。\n\n'+'\n'.join(f"- {s['id']}: [{s['title']}]({s['url']})" for s in sources)+'\n',encoding='utf-8',newline='\n')
    cards=[]
    for e in entries:
        path='examples/'+e['id']+'/'
        cards.append(f'<article data-search="{html.escape(" ".join([e["title_ja"],*e["tags"]]))}"><h2>{e["id"]} {html.escape(e["title_ja"])}</h2><a href="{path}example.drawio"><img loading="lazy" src="{path}preview.png" alt="{html.escape(e["title_ja"])}"></a><p>{html.escape(e["purpose"])}</p><p>{e["visual"]["theme"]} / {e["composition_pattern"]}</p><a href="{path}README.md">採用条件・出典・点検</a></article>')
    (BASE/'gallery.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><title>図解ボキャブラリー</title><style>body{font-family:sans-serif;background:#f8fafc;color:#222;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:24px}article{background:white;border:1px solid #ccc;padding:16px}img{width:100%}h2{font-size:18px}input{width:90%;padding:12px;margin:16px 0}</style><h1>図解サンプルボキャブラリー</h1><p>独自サンプル '+str(len(entries))+'件。名称・分野・構成から検索。クリックでDraw.ioを開く。</p><input id="query" placeholder="依存、状態、swimlane、T01..." aria-label="検索"><main>'+''.join(cards)+'</main><script>query.addEventListener("input",()=>{const q=query.value.toLowerCase();document.querySelectorAll("article").forEach(c=>c.hidden=!c.textContent.toLowerCase().includes(q)&&!c.dataset.search.toLowerCase().includes(q))})</script></html>',encoding='utf-8',newline='\n')
    print(f'Published {len(entries)} examples, {sum(e["core"] for e in entries)} core, {len(VARIANTS)} variants, {len(sources)} sources')

def validate():
    import jsonschema
    from PIL import Image
    data=sc.read(BASE/'catalog/diagram-vocabulary.json');jsonschema.validate(data,sc.read(BASE/'catalog/diagram-vocabulary.schema.json'))
    assert data==sc.read(SKILL/'references/drawio/diagram-vocabulary.json'),'Skill catalogue is stale'
    ids={e['id'] for e in data['entries']}; sources={s['id'] for s in sc.read(BASE/'sources/source-registry.json')['sources']}
    assert len(ids)==len(data['entries'])==len(DEFINITIONS)
    catalog=sc.read(SKILL/'references/drawio/shape-catalog.json')
    for e in data['entries']:
        folder=REPO/e['artifact'];assert folder.is_file()
        assert set(e['source_refs'])<=sources
        assert e['variant_of'] is None or e['variant_of'] in ids
        assert e==sc.read(folder.parent/'metadata.yaml')
        assert hashlib.sha256(folder.read_bytes()).hexdigest()==e['artifact_hash']
        assert hashlib.sha256((folder.parent/'preview.png').read_bytes()).hexdigest()==e['preview_hash']
        Image.open(folder.parent/'preview.png').verify();ET.parse(folder.parent/'preview.svg')
        root=ET.parse(folder).getroot();sc.validate_xml(root,catalog)
        cells=root.findall('.//mxCell');known={c.get('id') for c in cells}
        assert len(known)==len(cells)
        for c in cells:
            for attr in ('parent','source','target'):
                if c.get(attr):assert c.get(attr) in known and c.get(attr)!=c.get('id'),(e['id'],c.attrib)
        if e.get('external_source'):
            source=e['external_source'];assert hashlib.sha256((folder.parent/source['render']).read_bytes()).hexdigest()==source['sha256']
            assert root.find('.//mxCell[@id="source-layer"]').get('style')=='locked=1;'
            style=root.find('.//mxCell[@id="base"]').get('style')
            encoded=style.split('image=data:image/svg+xml,',1)[1].split(';',1)[0]
            assert base64.b64decode(encoded)==(folder.parent/source['render']).read_bytes()
        if e.get('source_preservation'):
            source=e['source_preservation'];original=folder.parent/source['path']
            assert hashlib.sha256(original.read_bytes()).hexdigest()==source['sha256']
            original_cells={c.get('id'):c for c in ET.parse(original).findall('.//mxCell')}
            current_cells={c.get('id'):c for c in cells}
            assert root.find('.//mxCell[@id="source-layer"]').get('style')=='locked=1;'
            for identifier in source['preserved_ids']:
                # Formatting indentation is not a change to a source cell.
                before=ET.canonicalize(ET.tostring(original_cells[identifier],encoding='unicode'),strip_text=True)
                after=ET.canonicalize(ET.tostring(current_cells[identifier],encoding='unicode'),strip_text=True)
                assert before==after,identifier
        if e.get('quantity_check') and 'outputs' in e['quantity_check']: assert sum(e['quantity_check']['outputs'])==e['quantity_check']['input']
        if e.get('quantity_check') and 'widths' in e['quantity_check']:assert len({w/v for w,v in zip(e['quantity_check']['widths'],e['quantity_check']['values'])})==1
    records=json.loads(ET.parse(BASE/'libraries/diagram-vocabulary.xml').getroot().text)
    assert len(records)>=10
    for record in records:
        assert all(k in record for k in ('title','tags','xml','w','h'));sc.validate_xml(ET.fromstring(record['xml']),catalog)
    templates=ET.parse(BASE/'libraries/template-library.xml').findall('template');assert len(templates)==len(ids)
    for template in templates:
        assert all(template.get(k) for k in ('section','title','name','url','preview','tags','libs','clibs'))
        assert urlparse(template.get('url')).scheme in ('http','https')
    for asset in sc.read(BASE/'sources/official-assets.json')['assets']:
        assert hashlib.sha256((BASE/'sources'/asset['local_path']).read_bytes()).hexdigest()==asset['sha256']
        assert asset['license_verified'] and asset['license']=='Apache-2.0'
    cases=[dict(query='複数チームの工程と担当',domain='project-management',composition_pattern='phase-team-grid',expected='DV-047'),
       dict(query='要求と応答の順序',diagram_type='sequence-lifelines',expected='DV-007'),
       dict(query='数量の流れ',composition_pattern='quantity-flow',expected='DV-060')]
    for case in cases:
        expected=case.pop('expected'); assert expected in [c['id'] for c in search(data['entries'],limit=5,**case)]
    assert not search(data['entries'],'zzznomatch999')
    print(f'Validated {len(ids)} samples, XML/shapes/source/image hashes, libraries and retrieval cases')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['publish','validate'])
    parser.add_argument('--base-url',default='http://127.0.0.1:8765/')
    args=parser.parse_args()
    if args.action=='publish':
        if urlparse(args.base_url).scheme not in ('http','https'):parser.error('Use a reachable HTTP(S) catalogue root')
        publish(args.base_url.rstrip('/')+'/')
    else:validate()
