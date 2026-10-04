"""Generate native-capability samples via real catalog retrieval and resolved IR."""
import copy
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
SKILL=BASE.parents[1]/'.agents/skills/information-structuring'
sys.path.insert(0,str(SKILL/'scripts'))
import shape_catalog as sc


def build():
    catalog=sc.read(SKILL/'references/drawio/shape-catalog.json')
    irs=[]; retrieval=[]
    def base(identifier,title,message,selected='T01'):
        ir=dict(id=identifier,metadata=dict(title=title,purpose=message,audience='技術者',diagram_type='native',theme=selected),nodes=[],edges=[],containers=[],tables=[])
        ir['nodes'].append(dict(id='heading',label=title,x=40,y=25,width=1180,height=50,primitive='text',fallback_reason='ページ見出し',style='fontSize=26;fontStyle=1;'))
        ir['nodes'].append(dict(id='summary',label=message,x=40,y=92,width=1180,height=70,primitive='text',fallback_reason='説明文'))
        ir['nodes'].append(dict(id='legend',label='架空の例。入力に示された意味だけを図形・所属・線で表現する。',x=40,y=720,width=1180,height=55,primitive='text',fallback_reason='凡例',style='fontSize=14;'))
        irs.append(ir);return ir
    def node(ir,identifier,label,query,library,x,y,w=160,h=100,**extra):
        candidates=sc.search(catalog,query,libraries_filter=[library],limit=5)
        exact=[c for c in candidates if sc.norm(c['name'])==sc.norm(query)]
        if not exact: raise ValueError(f'Exact sample candidate missing: {query}/{library}')
        chosen=exact[0]
        retrieval.append(dict(page=ir['id'],node=identifier,query=query,candidates=candidates,selected=chosen['shape_id'],reason='入力が候補の概念を明示している例'))
        ir['nodes'].append(dict(id=identifier,label=label,x=x,y=y,width=w,height=h,shape_query=query,
            shape_id=chosen['shape_id'],semantic_type=query,library=library,**extra))
    def edge(ir,a,b,label,kind='flow',**extra):
        ir['edges'].append(dict(id='edge'+str(len(ir['edges'])),source=a,target=b,label=label,semantic_type=kind,**extra))
    ir=base('native-flow','フローチャート：処理・判定・文書・DBを区別','受付から記録までを標準の意味図形で表す。判定の条件は線に残す。')
    for a,label,query,x in [('request','申請書','document',70),('check','内容確認','process',330),('decision','条件を満たす','decision',590),('db','受付記録','database',870)]:
        node(ir,a,label,query,'flowchart',x,310)
    edge(ir,'request','check','確認対象');edge(ir,'check','decision','判定');edge(ir,'decision','db','はい')
    ir['nodes'].append(dict(id='return',label='修正依頼',x=590,y=540,width=160,height=70,primitive='rectangle',fallback_reason='組織固有の連絡先を表す通常要素'))
    edge(ir,'decision','return','いいえ',style='exitX=0.5;exitY=1;entryX=0.5;entryY=0;')

    ir=base('native-membership','コンテナー：所属を親子関係として保持','子要素の座標は所属コンテナーからの相対座標。依存は破線で示す。','T02')
    ir['containers']=[dict(id='system',label='対象システム',x=60,y=220,width=680,height=390)]
    node(ir,'api','受付処理','process','flowchart',50,120,parent='system')
    node(ir,'db','永続データ','database','flowchart',400,120,parent='system')
    node(ir,'external','外部文書','document','flowchart',940,340)
    edge(ir,'api','db','参照する','dependency',parent='system')
    edge(ir,'external','api','入力',waypoints=[[1020,280],[190,280]],style='exitX=0.5;exitY=0;entryX=0.5;entryY=0;')

    ir=base('native-table','ネイティブTable：少量の責任一覧','表・行・セルの親子構造で編集できる。大きなマトリクスの本体はTSVへ分ける。','T03')
    ir['tables']=[dict(id='responsibility',x=110,y=260,column_widths=[280,250,250],rows=[['作業','担当','確認者'],['入力の整理','分析担当','依頼者'],['図解の確認','図解担当','レビュー担当'],['承認','依頼者','責任者']])]

    ir=base('native-aws','Vendor図形：明示されたAWSサービスを選ぶ','この例の入力は「AWS LambdaがAmazon RDSを利用する」。一般的なDBをRDSと推定しない。','T05')
    node(ir,'lambda','AWS Lambda','lambda','aws4',180,300,vendor='aws',vendor_style_reason='AWSサービスの識別色を保持する',style='verticalLabelPosition=bottom;verticalAlign=top;align=center;fillColor=#ED7100;strokeColor=none;')
    node(ir,'rds','Amazon RDS','rds','aws4',750,300,vendor='aws',vendor_style_reason='AWSサービスの識別色を保持する',style='verticalLabelPosition=bottom;verticalAlign=top;align=center;fillColor=#C925D1;strokeColor=none;')
    edge(ir,'lambda','rds','SQL要求')

    ir=base('native-eip','EIP：内容に応じた振り分けと集約','メッセージ内容による振り分けと、関連メッセージの集約をEIP図形で区別する。','T02')
    node(ir,'router','内容による振り分け','content_based_router','eip',200,310,style='verticalLabelPosition=bottom;verticalAlign=top;align=center;labelWidth=240;')
    node(ir,'aggregate','関連メッセージの集約','aggregator','eip',810,310,style='verticalLabelPosition=bottom;verticalAlign=top;align=center;labelWidth=260;')
    edge(ir,'router','aggregate','関連メッセージ')

    custom=[s for s in catalog['shapes'] if s['source_type']=='custom_library']
    for kind,title in [('fragment','再利用Fragment：受付と記録'),('template','再利用Template：全体と詳細の配置')]:
        ir=base('native-'+kind,title,'Custom Libraryから取得した構造・配置を再利用する。元セルのIDはインスタンスごとに再採番する。')
        asset=next(s for s in custom if s['asset_type']==kind)
        ir['nodes'].append(dict(id='reuse',label='',x=100,y=240,width=asset['width'],height=asset['height'],shape_id=asset['id']))

    document=ET.Element('mxfile',host='app.diagrams.net');entries=[];used=set()
    for ir in irs:
        path=BASE/'sources'/f"{ir['id']}-ir.json";sc.write(path,ir)
        temporary=BASE/'sources'/f"{ir['id']}.drawio"
        resolved=sc.render(catalog,ir,temporary);sc.write(BASE/'sources'/f"{ir['id']}-resolved.json",resolved)
        document.append(ET.parse(temporary).getroot().find('diagram'))
        temporary.unlink() # intermediate only; all generation code and IR are retained.
        used.update(n['shape_id'] for n in ir['nodes'] if n.get('shape_id'))
        entries.append(dict(id=ir['id'],name=ir['metadata']['title'],category='native',theme=ir['metadata']['theme']))
    ET.indent(document,space='  ');ET.ElementTree(document).write(BASE/'10-native-capabilities.drawio',encoding='utf-8',xml_declaration=True)
    sc.write(BASE/'sources/native-retrieval.json',retrieval)
    snapshot=copy.deepcopy(catalog);snapshot['shapes']=[s for s in catalog['shapes'] if s['id'] in used]
    libs={s['library'] for s in snapshot['shapes']};snapshot['libraries']=[copy.deepcopy(l) for l in catalog['libraries'] if l['id'] in libs]
    for lib in snapshot['libraries']: lib['shape_count']=sum(s['library']==lib['id'] for s in snapshot['shapes'])
    sc.write(BASE/'references/drawio/shape-catalog.json',snapshot)
    for name in ['shape-catalog.schema.json','library-registry.json','shape-metadata.json']:
        shutil.copyfile(SKILL/'references/drawio'/name,BASE/'references/drawio'/name)
    shutil.copyfile(SKILL/'scripts/shape_catalog.py',BASE/'scripts/shape_catalog.py')
    shutil.copyfile(SKILL/'scripts/requirements-native.txt',BASE/'scripts/requirements-native.txt')
    (BASE/'sources/libraries').mkdir(exist_ok=True)
    shutil.copyfile(SKILL/'assets/libraries/reusable.xml',BASE/'sources/libraries/reusable.xml')
    lines=['# Draw.ioネイティブ機能のサンプル','','[7ページのDraw.io](10-native-capabilities.drawio)。ページタブで切り替える。全て架空の例。','']
    for ir in irs:
        lines.extend([f"## {ir['metadata']['title']}",'',ir['metadata']['purpose'],'',f"テーマ: {ir['metadata']['theme']}。IR: [入力](sources/{ir['id']}-ir.json)／[解決済み](sources/{ir['id']}-resolved.json)。",'',f"![{ir['metadata']['title']}](previews/{ir['id']}.png)",''])
    (BASE/'native-capabilities.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8',newline='\n')
    return entries


if __name__=='__main__': build()
