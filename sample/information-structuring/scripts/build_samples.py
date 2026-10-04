"""Rebuild tracked Draw.io samples from the skill's current catalogs (no output reads)."""
import base64
import copy
import json
import re
import shutil
import sys
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zlib
from urllib.parse import quote
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
SKILL = REPO / '.agents/skills/information-structuring'
sys.path.insert(0, str(SKILL / 'scripts'))
from diagrams import diagram as skeleton
from theme_styles import style, theme, THEMES
from build_annotation import build as annotate

MANIFEST = []
CELL_ROLES = {}
SAMPLE_BASES = {}


class Page:
    def __init__(self, identifier, title, selected='T01', width=1280, height=820):
        self.element = ET.Element('diagram', id=identifier, name=title)
        self.model = ET.SubElement(self.element, 'mxGraphModel', page='1', pageWidth=str(width), pageHeight=str(height), background=theme(selected)['palette'].get('canvas', '#FFFFFF'))
        self.root = ET.SubElement(self.model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.selected, self.count, self.rects = selected, 0, {}

    def node(self, value, x, y, w=220, h=70, shape='component', role='neutral', extra=''):
        self.count += 1
        identifier = f'n{self.count}'
        cell = ET.SubElement(self.root, 'mxCell', id=identifier, value=value, vertex='1', parent='1', style=style(self.selected, shape=shape, semantic=role)+extra)
        CELL_ROLES[cell] = dict(shape=shape, semantic=role)
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
        self.rects[identifier] = (x, y, w, h)
        return identifier

    def line(self, a, b, label='', kind='flow', points=(), extra=''):
        self.count += 1
        cell = ET.SubElement(self.root, 'mxCell', id=f'e{self.count}', value=label, edge='1', parent='1', style=style(self.selected, connector=kind)+'labelBackgroundColor=#FFFFFF;'+extra)
        CELL_ROLES[cell] = dict(connector=kind)
        geometry = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
        for endpoint, name in ((a, 'source'), (b, 'target')):
            if isinstance(endpoint, str):
                cell.set(name, endpoint)
            else:
                ET.SubElement(geometry, 'mxPoint', x=str(endpoint[0]), y=str(endpoint[1]), **{'as': name+'Point'})
        if points:
            array = ET.SubElement(geometry, 'Array', **{'as': 'points'})
            for x, y in points:
                ET.SubElement(array, 'mxPoint', x=str(x), y=str(y))
        return cell

    def heading(self, title, message, legend):
        self.node(title, 40, 25, 1200, 46,  shape='label', extra='fontSize=24;fontStyle=1;')
        self.node(message, 40, 82, 1200, 70, shape='label')
        self.node('架空の例示データ。案件の事実ではない。\n'+legend, 40, 710, 1200, 80, shape='label', extra='fontSize=14;')


def save(filename, pages, entries):
    document = ET.Element('mxfile', host='app.diagrams.net')
    document.extend(pages)
    path = BASE / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(document, space='  ')
    ET.ElementTree(document).write(path, encoding='utf-8', xml_declaration=True)
    for entry in entries:
        MANIFEST.append(dict(file=filename, **entry))
        page = next(page for page in pages if page.get('id') == entry['id'])
        SAMPLE_BASES[entry['id']] = dict(
            page=copy.deepcopy(page), entry=dict(file=filename, **entry),
            roles={cell.get('id'): CELL_ROLES[cell] for cell in page.findall('./mxGraphModel/root/mxCell') if cell in CELL_ROLES})


def purposes():
    framework = json.loads((SKILL/'references/framework.json').read_text(encoding='utf-8'))
    topics = {
        'meaning': ('T01', '概念と呼称を分け、同義語を共通の概念へ対応付ける。', 'graph'),
        'grouping': ('T10', '問い合わせを対象と状況の独立した軸で整理する。', 'matrix'),
        'decomposition': ('T08', '物理構成で分解する。機能の階層とは混ぜない。', 'tree'),
        'comparison': ('T04', '方式A・Bを同じ評価軸で比較する。結論は条件による。', 'matrix'),
        'relationships': ('T02', '多対多の利用関係と外部境界を示す。', 'graph'),
        'timing': ('T03', '予定の時期と担当を揃える。論理順序だけの図とは区別する。', 'timeline'),
        'process': ('T01', '申請の担当・分岐条件・受渡しを示す。', 'flow'),
        'state_events': ('T08', '状態・イベント・条件を分け、申請の状態変化を示す。', 'state_model'),
        'causal_analysis': ('T09', '障害の観測事実と原因の仮説を分離する。', 'tree'),
        'risk_failure': ('T07', '脅威・影響・予防策を分ける。点数や発生確率は仮定しない。', 'graph'),
        'requirements_trace': ('T02', '要求から設計・検証への対応を共有IDで追う。', 'graph'),
        'decision': ('T04', '選択肢・評価条件・決定を区別し、選定条件を残す。', 'argument'),
        'responsibility': ('T03', '役割ごとに仕事を置き、受渡しの責任を示す。', 'flow'),
        'quantitative': ('T01', '実績・目標・差異を同じ単位で比較する。', 'quantitative_chart'),
        'strategy': ('T04', '目的から成果・施策を展開し、成果を観測する指標を添える。', 'tree'),
        'explanation': ('T09', '主張・根拠・留保を区別し、採用する条件を示す。', 'argument'),
    }
    pages, entries = [], []
    for index, purpose in enumerate(framework['purposes'], 1):
        key = purpose['id']; selected, objective, form = topics[key]
        p = Page(key, f'{index:02} {purpose["name"]}', selected)
        p.heading(purpose['name'], objective, f'{selected} | 青＝主対象。その他の色の意味は要素ラベルに明示。線の名称と向きで関係を読む。')
        if key == 'meaning':
            a=p.node('概念C1\nサービスが利用できない状態',480,300,300,100,role='primary')
            for y,label in [(210,'呼称: サービス停止'),(450,'呼称: 利用不可')]:
                b=p.node(label,80,y); p.line(b,a,'呼称',kind='structural')
            b=p.node('概念C2: 装置の故障\nサービス停止と同義ではない',930,300,260,100)
            p.line(b,a,'原因となり得る',kind='dependency')
        elif key in {'grouping','comparison'}:
            cols=['画面','データ'] if key=='grouping' else ['方式A','方式B']
            rows=['要確認','対応済み'] if key=='grouping' else ['保守性','導入費用']
            values=[['表示が欠ける','項目定義が不明'],['見出しを修正','形式を統一']] if key=='grouping' else [['変更箇所が少ない','変更箇所が多い'],['初期費用が高い','初期費用が低い']]
            for j,col in enumerate(cols): p.node(col,340+j*420,200,380,55,role='primary')
            for i,row in enumerate(rows):
                p.node(row,60,290+i*160,240,120,role='neutral')
                for j in range(2): p.node(values[i][j],340+j*420,290+i*160,380,120)
            p.node('表の全量が大きい場合はTSVへ分け、図は重要な領域・関係だけを示す。',60,640,1140,50,shape='label')
        elif key in {'decomposition','causal_analysis','strategy'}:
            labels = {
                'decomposition':['装置S1（物理構成）','制御基板P1','電源P2','CPU P3','通信IF P4','供給回路P5'],
                'causal_analysis':['観測: 応答時間が増加','仮説H1: 処理が集中','仮説H2: 通信が遅延','観測: 待ち件数が増加','確認待ち: 入力頻度','確認待ち: 通信時間'],
                'strategy':['目的: 利用者の待ち時間を減らす','成果: 受付待ちを短縮','成果: 再申請を減らす','施策: 受付手順を統一','指標: 受付待ち時間','施策: 入力条件を明記'],
            }[key]
            nodes=[p.node(labels[0],470,180,340,80,role='primary')]
            nodes.extend(p.node(labels[i+1],x,345,340,80,role='hypothesis' if key=='causal_analysis' else 'neutral') for i,x in enumerate([180,760]))
            nodes.extend(p.node(labels[i+3],x,540,300,80) for i,x in enumerate([40,470,900]))
            for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5)]:
                p.line(nodes[a],nodes[b],'包含' if key=='decomposition' else ('検討・照合' if key=='causal_analysis' else '展開'),kind='structural' if key=='decomposition' else 'dependency')
        elif key in {'relationships','risk_failure','requirements_trace','decision','explanation'}:
            labels = {
                'relationships':['外部システムE1','受付サービスS1','審査サービスS2','共通データD1'],
                'risk_failure':['脅威T1: 不正な要求','制御C1: 権限を検査','影響I1: 情報の漏えい','制御C2: 監査記録を残す'],
                'requirements_trace':['要求R1: 履歴を保持','設計D1: 履歴保存','試験T1: 保存を確認','要求R2: 操作を追跡'],
                'decision':['条件: 初期費用を抑える','選択肢A: 新規導入','選択肢B: 現行改善','判断: 条件内ならBを採用'],
                'explanation':['主張C1: 手順を統一する','根拠E1: 手順の差がある','留保L1: 対象外の業務がある','判断D1: 対象業務に限定する'],
            }[key]
            nodes=[p.node(labels[i],x,y,350,90,shape='database' if key=='relationships' and i==3 else 'component',role='primary' if i==0 else ('risk' if key=='risk_failure' and i==2 else 'neutral')) for i,(x,y) in enumerate([(70,220),(780,220),(70,515),(780,515)])]
            links = [(0,1,'要求を送る'),(1,2,'審査を依頼'),(1,3,'保存'),(2,3,'参照')] if key=='relationships' else ([(0,1,'予防'),(0,2,'未対処時の影響'),(3,2,'追跡・検知')] if key=='risk_failure' else ([(0,1,'実現'),(1,2,'検証'),(3,1,'実現')] if key=='requirements_trace' else [(0,1,'比較対象'),(0,2,'比較対象'),(2,3,'採用条件を満たす')]))
            if key=='explanation': links=[(1,0,'支持'),(2,0,'適用範囲を限定'),(0,3,'導く')]
            for a,b,label in links:
                points=[(600,265),(600,560)] if (a,b)==(1,2) else []
                p.line(nodes[a],nodes[b],label,kind='dependency',points=points)
        elif key=='timing':
            for j,label in enumerate(['4月','5月','6月']): p.node(label,330+j*280,190,250,50,role='primary')
            for i,label in enumerate(['仕様整理','設計','検証']):
                y=300+i*115; p.node(label,60,y,200,65,shape='label')
                p.node('予定（例示）',330+i*280,y,250,65,shape='process',role='planned')
            p.node('各期間は例示。工程の依存関係は別途確認する。',60,645,1140,45,shape='label')
        elif key in {'process','responsibility'}:
            for i,label in enumerate(['申請者','受付担当','審査担当']):
                p.node(label,40,190+i*160,1200,140,shape='boundary',extra='verticalAlign=top;spacingTop=8;')
            a=p.node('申請を送る',220,240,210,70,shape='process')
            b=p.node('内容を確認する',545,400,210,70,shape='process',role='primary')
            c=p.node('審査する',900,560,210,70,shape='process')
            p.line(a,b,'申請を受渡す',points=[(480,275),(480,435)])
            p.line(b,c,'条件を満たす',points=[(820,435),(820,595)])
            p.line(b,a,'不備: 再提出',kind='failure',points=[(670,175),(325,175)],extra='exitX=0.5;exitY=0;entryX=0.5;entryY=0;')
        elif key=='state_events':
            nodes=[p.node(label,x,320,230,100,shape='process',role='primary' if i==0 else 'neutral') for i,(x,label) in enumerate([(80,'作成中'),(520,'審査中'),(960,'完了')])]
            p.line(nodes[0],nodes[1],'提出 [必須項目あり]')
            p.line(nodes[1],nodes[2],'承認')
            p.line(nodes[1],nodes[0],'差戻し',points=[(635,560),(195,560)],extra='exitX=0.5;exitY=1;entryX=0.5;entryY=1;')
        elif key=='quantitative':
            p.line((200,600),(1180,600),kind='structural'); p.line((200,600),(200,200),kind='structural')
            for i,(label,actual) in enumerate([('4月',30),('5月',20),('6月',10)]):
                x=350+i*280; p.node(f'{actual}分',x,600-actual*10,130,actual*10,role='primary'); p.node(label,x,620,130,45,shape='label')
            p.line((205,400),(1150,400),'目標20分',kind='optional',extra='edgeStyle=none;')
            p.node('指標: 平均受付待ち時間（分）\n実績・目標とも例示値。低い方がよい。',300,160,850,60,shape='label')
        pages.append(p.element)
        entries.append(dict(id=key, category='purpose', name=purpose['name'], theme=selected, form=form, axes=purpose['axes'], reason=objective))
    save('01-organizing-patterns.drawio', pages, entries)


def vector_shape(points):
    """An editable native mxGraph stencil, not an embedded SVG image."""
    xs,ys=zip(*points); x,y=min(xs),min(ys); w,h=max(xs)-x,max(ys)-y
    shape=ET.Element('shape',name='sample-vector',w=str(w or 1),h=str(h or 1),aspect='variable',strokewidth='inherit')
    foreground=ET.SubElement(shape,'foreground'); path=ET.SubElement(foreground,'path')
    for i,(px,py) in enumerate(points): ET.SubElement(path,'move' if i==0 else 'line',x=str(px-x),y=str(py-y))
    ET.SubElement(path,'close'); ET.SubElement(foreground,'fillstroke')
    payload=quote(ET.tostring(shape,encoding='unicode'),safe="~()*!.'-").encode('utf-8')
    compressor=zlib.compressobj(wbits=-15)
    encoded=base64.b64encode(compressor.compress(payload)+compressor.flush()).decode()
    return x,y,w,h,'shape=stencil('+encoded+');'


def catalogs():
    data=json.loads((SKILL/'references/catalog.json').read_text(encoding='utf-8'))
    groups={}
    quantitative={5,6,7,8,9,10,13,14,16,19,21,23,24,25,26,27,28,29,30,31,33}
    for sample in data['samples']:
        selected='T03' if sample['type_number'] in range(35,41) or sample['type_number']==47 else ('T04' if sample['type_number'] in (1,2,3,20,22,32,45) else 'T01')
        p=Page(sample['id'],sample['id']+' '+sample['name'],selected,1000,720)
        svg=ET.fromstring(skeleton(sample)); namespace='{http://www.w3.org/2000/svg}'
        offsetx,offsety=40,30
        vertices=[]; text_items=[]; lines=[]
        for element in svg.find(namespace+'g'):
            tag=element.tag.removeprefix(namespace); a=element.attrib
            if tag=='rect':
                x,y,w,h=[float(a[k]) for k in ('x','y','width','height')]
                node=p.node('',x+offsetx,y+offsety,w,h,role='primary' if a.get('fill')!='white' else 'neutral',extra='dashed=1;' if a.get('stroke-dasharray')!='none' else '')
                vertices.append((node,x,y,w,h,'rect'))
            elif tag=='circle':
                cx,cy,r=[float(a[k]) for k in ('cx','cy','r')]
                node=p.node('',cx-r+offsetx,cy-r+offsety,2*r,2*r,shape='event',extra='fillOpacity=35;')
                vertices.append((node,cx-r,cy-r,2*r,2*r,'circle'))
            elif tag=='text': text_items.append(element)
            elif tag=='line': lines.append(element)
            elif tag=='polygon':
                points=[tuple(map(float,pair.split(','))) for pair in a['points'].split()]
                x,y,w,h,extra=vector_shape(points)
                node=p.node('',x+offsetx,y+offsety,w,h,extra=extra,role='primary')
                vertices.append((node,x,y,w,h,'polygon'))
            elif tag=='path':
                # The catalog has three illustrative curves. Sample the curve as a native polyline.
                coords=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',a['d'])))
                if 'T' in a['d']:
                    start=(coords[0],coords[1]); control=(coords[2],coords[3]); end=(coords[4],coords[5]); end2=(coords[6],coords[7])
                    control2=(2*end[0]-control[0],2*end[1]-control[1]); curves=[(start,control,end),(end,control2,end2)]
                else: curves=[((coords[0],coords[1]),(coords[2],coords[3]),(coords[4],coords[5]))]
                points=[]
                for start,control,end in curves:
                    for i in range(21):
                        t=i/20; points.append(((1-t)**2*start[0]+2*(1-t)*t*control[0]+t*t*end[0]+offsetx,(1-t)**2*start[1]+2*(1-t)*t*control[1]+t*t*end[1]+offsety))
                p.line(points[0],points[-1],kind='optional' if a.get('stroke-dasharray') else 'structural',points=points[1:-1],extra='edgeStyle=none;')
        # Attach centered labels to their native shapes; keep other labels independently editable.
        for element in text_items:
            a=element.attrib; x,y=float(a['x']),float(a['y']); value=element.text or ''; size=float(a['font-size'])
            matches=[v for v in vertices if v[1]<=x<=v[1]+v[3] and v[2]<=y<=v[2]+v[4] and abs(x-(v[1]+v[3]/2))<1 and abs(y-(v[2]+v[4]/2+5))<1]
            if matches and a.get('text-anchor')=='middle':
                v=min(matches,key=lambda v:v[3]*v[4]); cell=p.root.find(f"mxCell[@id='{v[0]}']"); cell.set('value',value); cell.set('style',cell.get('style')+'align=center;fontSize='+str(size)+';')
            else:
                width=min(900,max(40,len(value)*size)); left=x-width/2 if a.get('text-anchor')=='middle' else x
                p.node(value,left+offsetx,y-size+offsety,width+30,size*1.6,shape='label',extra=f'fontSize={size};spacingLeft=0;whiteSpace=nowrap;')
        if sample['type_number']==47:
            for cell in p.root.findall('mxCell'):
                if 'shape=stencil(' in cell.get('style',''):
                    cell.set('style',style(selected,shape='decision')); cell.set('value','判定')
                    CELL_ROLES[cell] = dict(shape='decision', semantic='neutral')
                elif cell.get('value')=='判定' and 'shape=text' in cell.get('style',''):
                    cell.set('value','')
        def anchor(x,y):
            candidates=[v for v in vertices if v[1]-1<=x<=v[1]+v[3]+1 and v[2]-1<=y<=v[2]+v[4]+1]
            return min(candidates,key=lambda v:v[3]*v[4])[0] if candidates else (x+offsetx,y+offsety)
        for element in lines:
            a=element.attrib; x1,y1,x2,y2=[float(a[k]) for k in ('x1','y1','x2','y2')]
            arrow=a.get('marker-end')!='none'; dashed=a.get('stroke-dasharray')!='none'
            kind='dependency' if arrow and dashed else ('flow' if arrow else ('optional' if dashed else 'structural'))
            if sample['type_number']==21 and arrow:
                # The source skeleton has a short illustrative arrow; connect both area objects.
                outer=[v for v in vertices if v[5]=='rect' and v[4]==150]
                left=min(outer,key=lambda v:abs(v[1]+v[3]-x1))
                right=min([v for v in outer if v[1]>left[1]],key=lambda v:v[1])
                p.line(left[0],right[0],kind=kind)
            elif sample['type_number'] in quantitative:
                p.line((x1+offsetx,y1+offsety),(x2+offsetx,y2+offsety),kind=kind,extra='edgeStyle=none;')
            else:
                source,target=anchor(x1,y1),anchor(x2,y2)
                if source==target: source,target=(x1+offsetx,y1+offsety),(x2+offsetx,y2+offsety)
                extra=''
                if sample['type_number']==17:
                    level='0.3' if x2>x1 else '0.7'
                    extra=f'exitY={level};entryY={level};exitX={"1" if x2>x1 else "0"};entryX={"0" if x2>x1 else "1"};'
                points=[]
                if sample['type_number']==47 and dashed and arrow:
                    extra='exitX=0.5;exitY=0;entryX=0.5;entryY=0;'
                    points=[(x1+offsetx,110+offsety),(222.5+offsetx,110+offsety)]
                p.line(source,target,kind=kind,extra=extra,points=points)
        if sample['type_number']==34:
            p=Page(sample['id'],sample['id']+' '+sample['name'],selected,1000,720)
            p.node(sample['name'],40,40,900,45,shape='label',extra='fontSize=22;')
            p.node('対象間で不足を補う対応を、強みから不足への矢印で示す。',40,90,900,50,shape='label')
            a=p.node('対象Aの強み',90,170,300,65,role='primary'); b=p.node('対象Bの強み',570,170,300,65,role='primary')
            c=p.node('対象Aの不足',90,365,300,65); d=p.node('対象Bの不足',570,365,300,65)
            p.line(a,d,'補完',points=[(455,202),(455,397)],extra='exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
            p.line(b,c,'補完',points=[(920,202),(920,470),(60,470),(60,397)],extra='exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
        if sample['id']=='principle-2':
            p=Page(sample['id'],sample['name'],selected,1000,720)
            p.node(sample['name'],40,40,900,45,shape='label',extra='fontSize=22;')
            p.node('同じ向きとずらし量で重ね、各要素のラベルを露出する。',40,90,900,40,shape='label')
            for row in range(3):
                y=145+row*110
                p.node('区分 '+chr(65+row),50,y,130,60,shape='label')
                for i in range(3):
                    p.node('要素 '+chr(65+i),200+i*120,y+i*15,260,65,extra='fontSize=14;spacingLeft=12;')
        p.node('用途: '+sample['use']+'\n整理軸: '+sample['axes']['horizontal']+' × '+sample['axes']['vertical'],40,510,920,65,shape='label')
        p.node('注意: '+sample['caution']+'\n配置参考の模式図。実データへ軸・尺度・関係名を割り当てて使う。',40,590,920,90,shape='label',extra='fontSize=14;')
        n=sample['type_number']
        form='list' if n==1 else ('table' if n in (2,3,4,12,22,45) or sample['id']=='principle-1' else ('tree' if n in (11,18,43,46) else ('timeline' if n in (35,36,37,38) else ('flow' if n in (17,39,40,47) else ('map' if n in (20,41,42,44,48) or sample['id']=='principle-2' else ('matrix' if n in (15,19,32,34) else 'quantitative_chart'))))))
        groups.setdefault(sample['group'],[]).append((p.element,dict(id=sample['id'],category='catalog',name=sample['name'],theme=selected,kind=sample['kind'],form=form,reason=sample['use'])))
    for index,(name,items) in enumerate(groups.items(),1): save(f'catalog/{index:02}.drawio',[item[0] for item in items],[item[1] for item in items])


def themes():
    pages=[]; entries=[]
    for selected,data in THEMES.items():
        p=Page(selected,selected+' '+data['name'],selected)
        p.heading(selected+' '+data['name'],data['use'], '同じ関係構造を各テーマで表示。色は主対象・外部・警告の意味を表す。T05は公式クラウド製品図ではなく意味記号の比較例。')
        boundary=p.node('対象システム（論理境界）',440,180,780,440,shape='boundary',extra='dashed=1;verticalAlign=top;spacingTop=10;')
        a=p.node('外部利用者',65,330,200,110,shape='actor',role='external')
        b=p.node('要求を処理する\n主対象',530,320,250,90,shape='process',role='primary')
        c=p.node('履歴データ',950,310,190,110,shape='database')
        p.line(a,b,'要求'); p.line(b,c,'保存')
        p.node('注意: 権限の条件を確認',550,500,560,75,shape='note',role='warning')
        pages.append(p.element); entries.append(dict(id=selected,category='theme',name=data['name'],theme=selected,reason=data['use']))
    save('02-theme-comparison.drawio',pages,entries)


def annotations():
    source_dir=BASE/'sources'; source_dir.mkdir(exist_ok=True)
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480"><rect width="800" height="480" fill="white"/><g font-family="sans-serif" font-size="22" fill="#222"><rect x="20" y="20" width="760" height="65" fill="#eee"/><text x="40" y="60">申請管理（架空の画面）</text><rect x="20" y="105" width="170" height="350" fill="#f4f4f4"/><text x="40" y="150">申請一覧</text><text x="40" y="200">新規申請</text><rect x="215" y="110" width="560" height="310" fill="white" stroke="#666"/><text x="245" y="155">申請内容</text><rect x="245" y="190" width="490" height="60" fill="white" stroke="#666"/><text x="260" y="230">入力</text><rect x="575" y="330" width="160" height="55" fill="#eee" stroke="#666"/><text x="625" y="367">保存</text></g></svg>'''
    (source_dir/'screen.svg').write_text(svg,encoding='utf-8')
    targets=[('ナビゲーション','申請一覧',.025,.22,.2125,.73,.13,.31),('入力欄','入力',.30625,.3958,.6125,.125,.5,.4583),('保存ボタン','保存',.71875,.6875,.2,.1146,.81875,.745)]
    pages=[]; entries=[]
    for mode in ['orientation','function','workflow']:
        ir=json.loads((SKILL/'assets/annotation-ir-template.json').read_text(encoding='utf-8'))
        ir.update(view_id='screen-'+mode,purpose={'orientation':'画面の主要領域','function':'画面要素の役割','workflow':'操作説明（仮定を明示）'}[mode],audience='初めて利用する人',theme='T01')
        ir['source'].update(path='screen.svg',version='架空の画面v1'); ir['canvas']={'width':1280,'height':850}; ir['annotations']=[]
        for i,(label,text,x,y,w,h,ax,ay) in enumerate(targets,1):
            annotation={'id':f'ANN-{i:03}','number':f'注{i}','type':['region','highlight','callout'][i-1], 'title':label,'description':f'画像上に「{text}」と表示された領域。'+('操作順とクリック後の動作は要確認。' if mode=='workflow' else '表示文字を根拠に説明する。'),'target':{'label':label,'text':text,'x':x,'y':y,'width':w,'height':h},'anchor':{'x':ax,'y':ay},'label_position':{'x':1.075,'y':.04+(i-1)*.32},'label_width':310,'label_height':115,'confidence':'high','evidence':[{'basis':'架空画像上の文字','observed_text':text}]}
            ir['annotations'].append(annotation)
            annotation['marker_position']={'x':x+.015,'y':y-.03}
            annotation['anchor']={'x':x+w-.02,'y':y+h-.02}
        ir['explanation_blocks']=[{'text':ir['purpose']+'\n注番号は説明との対応。処理順ではない。操作後の結果は画像だけから断定しない。','x':60,'y':620,'width':1140,'height':80}]
        ir['legend']=[{'text':'青: 説明対象。破線: 注釈の対応（元図のデータフローではない）。原図はロックし、注釈を別レイヤーで編集する。','x':60,'y':725,'width':1140,'height':70}]
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)/'sample.drawio'; annotate(ir,source_dir/'screen.svg',destination); pages.append(ET.parse(destination).getroot().find('diagram'))
        (source_dir/f'{mode}-ir.json').write_text(json.dumps(ir,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        entries.append(dict(id='screen-'+mode,category='annotation',name=ir['purpose'],theme='T01',reason='原図保持・別レイヤー・番号と図外説明'))
    save('03-screen-annotations.drawio',pages,entries)
    # An existing editable diagram keeps its original IDs/styles/positions on a locked source layer.
    source=Page('native-source','原図: 受付と審査','T02')
    a=source.node('受付',170,280,260,100,role='primary'); b=source.node('審査',820,280,260,100); source.line(a,b,'審査を依頼')
    save('sources/native-source.drawio',[source.element],[])
    source.root.find("mxCell[@id='1']").set('style','locked=1;'); source.root.find("mxCell[@id='1']").set('value','00_Source')
    for identifier,label in [('10','10_Highlight'),('20','20_Annotation'),('30','30_Explanation')]: ET.SubElement(source.root,'mxCell',id=identifier,value=label,parent='0')
    n=source.node('注1 受付の責務\n要求を受け付け、審査へ渡す。',150,520,400,100,shape='note'); source.root.find(f"mxCell[@id='{n}']").set('parent','30')
    e=source.line(n,a,'注釈',kind='dependency'); e.set('parent','20')
    source.element.set('id','native-annotation'); source.element.set('name','既存Draw.ioへの説明追加')
    save('04-native-annotation.drawio',[source.element],[dict(id='native-annotation',category='annotation',name='編集可能な原図の保持',theme='T02',reason='原図のID・文字・位置・関係を保持してレイヤーを追加')])


def sequence():
    source_dir=BASE/'sources'
    puml='''@startuml
skinparam shadowing false
skinparam backgroundColor white
actor "利用者" as User
participant "受付" as Reception
participant "審査担当" as Reviewer
User -> Reception: 申請を送る
Reception -> Reviewer: 審査を依頼する
Reviewer --> Reception: 結果を返す
note over User, Reviewer: 架空の手順。時間間隔は実時間を示さない。
@enduml
'''
    (source_dir/'sequence.puml').write_text(puml,encoding='utf-8')
    for format in ['-tsvg','-tpng']:
        result=subprocess.run(['plantuml',format,str(source_dir/'sequence.puml')],capture_output=True,timeout=60)
        if result.returncode!=0: raise RuntimeError(result.stderr.decode('utf-8',errors='replace'))
    rendered=source_dir/'sequence.svg'; svg=ET.parse(rendered).getroot()
    width=float(svg.get('width').removesuffix('px')); height=float(svg.get('height').removesuffix('px'))
    ir=json.loads((SKILL/'assets/annotation-ir-template.json').read_text(encoding='utf-8'))
    ir.update(view_id='plantuml-svg',purpose='PlantUMLシーケンス図を原図のまま説明する',theme='T02')
    ir['source'].update(path='sequence.svg',width=width,height=height,structured_source='sequence.puml',version='架空の手順v1')
    ir['display']={'x':60,'y':120,'width':width,'height':height}; ir['canvas']={'width':max(1280,width+520),'height':max(850,height+360)}
    # Read the actual rendered text position rather than estimating its target.
    target=next(e for e in svg.iter() if e.tag.endswith('text') and e.text=='申請を送る')
    x,y=float(target.get('x')),float(target.get('y'))
    text_width=float(target.get('textLength'))
    ir['annotations']=[{'id':'SEQ-01','number':'注1','type':'callout','title':'申請の受渡し','description':'利用者から受付へ申請を送る。意味は同梱のPlantUMLソースで確認できる。','target':{'label':'申請を送る','text':'申請を送る','x':x/width,'y':(y-18)/height,'width':100/width,'height':24/height},'anchor':{'x':(x+50)/width,'y':(y-6)/height},'label_position':{'x':1+60/width,'y':.25},'label_width':350,'label_height':120,'confidence':'high','evidence':[{'basis':'sequence.pumlのメッセージ','observed_text':'申請を送る'}]}]
    ir['annotations'][0]['target']['width']=text_width/width
    ir['annotations'][0]['marker_position']={'x':15/width,'y':(y-6)/height}
    ir['annotations'][0]['anchor']={'x':(x+text_width/2)/width,'y':(y-18)/height}
    ir['annotations'][0]['leader_points']=[{'x':1+40/width,'y':(y-18)/height}]
    ir['explanation_blocks']=[{'text':'Mode B: SVGを単一の原図として保持。元の.pumlを編集し再レンダリングする。注釈は別レイヤー。','x':60,'y':height+170,'width':1150,'height':80}]
    ir['legend']=[{'text':'破線の引出線は注釈との対応。シーケンス図の応答矢印とは区別する。','x':60,'y':height+270,'width':1150,'height':60}]
    with tempfile.TemporaryDirectory() as directory:
        destination=Path(directory)/'sequence.drawio'; annotate(ir,rendered,destination)
        save('05-plantuml-annotation.drawio',[ET.parse(destination).getroot().find('diagram')],[dict(id='plantuml-svg',category='annotation',name='PlantUML原図への注釈',theme='T02',form='sequence',reason='PlantUMLソースと実レンダリングを保持し、注釈のみ編集する')])
    (source_dir/'sequence-ir.json').write_text(json.dumps(ir,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    from PIL import Image
    pngwidth,pngheight=Image.open(source_dir/'sequence.png').size
    ir.update(view_id='plantuml-png',purpose='PlantUMLのPNG原図へ説明を追加する')
    ir['source'].update(path='sequence.png',width=pngwidth,height=pngheight,sha256=None)
    ir['display'].update(width=pngwidth,height=pngheight)
    ir['explanation_blocks'][0]['text']='Mode C: PNGを原図として保持。SVGを扱えない環境向けの代替例。拡大時の可読性を確認する。'
    with tempfile.TemporaryDirectory() as directory:
        destination=Path(directory)/'sequence-png.drawio'; annotate(ir,source_dir/'sequence.png',destination)
        save('06-plantuml-png-annotation.drawio',[ET.parse(destination).getroot().find('diagram')],[dict(id='plantuml-png',category='annotation',name='PNG原図への注釈',theme='T02',reason='SVGを扱えない場合のPNG代替。原画像を保持する')])
    (source_dir/'sequence-png-ir.json').write_text(json.dumps(ir,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def style_values(value):
    return dict(token.split('=', 1) for token in value.split(';') if '=' in token)


def theme_cases():
    """Recolor known semantic roles without altering shapes, topology or geometry."""
    configuration=json.loads((BASE/'sources/theme-cases.json').read_text(encoding='utf-8'))
    groups={}; comparison=['# サンプル別のテーマ違い','','図内の情報・配置は同じ。読者・利用目的に応じた別テーマの例を示す。原図への注釈例は原図のスタイルを維持する。','']
    previous=None
    for case in configuration['cases']:
        base=SAMPLE_BASES[case['base_id']]; entry=base['entry']; selected=case['theme']
        if selected==entry['theme']: raise ValueError('Theme case must differ from its base')
        identifier=case['base_id']+'--'+selected
        name=entry['name']+' / '+selected
        if case['base_id'] in {'screen-orientation','plantuml-svg'}:
            irname='orientation-ir.json' if case['base_id']=='screen-orientation' else 'sequence-ir.json'
            ir=json.loads((BASE/'sources'/irname).read_text(encoding='utf-8'))
            ir.update(theme=selected,view_id=identifier)
            source=BASE/'sources'/ir['source']['path']
            with tempfile.TemporaryDirectory() as directory:
                destination=Path(directory)/'theme.drawio'; annotate(ir,source,destination)
                page=ET.parse(destination).getroot().find('diagram')
            (BASE/'sources'/f'{identifier}-ir.json').write_text(json.dumps(ir,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        else:
            page=copy.deepcopy(base['page'])
            model=page.find('mxGraphModel'); model.set('background',theme(selected)['palette'].get('canvas','#FFFFFF'))
            for cell in model.findall('./root/mxCell'):
                if entry['category']=='annotation' and cell.get('parent') not in {'10','20','30'}:
                    continue
                role=base['roles'].get(cell.get('id'))
                if role is not None:
                    original=style_values(cell.get('style',''))
                    target=style_values(style(selected,**role))
                    for key in ('fillColor','strokeColor','fontColor'):
                        if key in target: original[key]=target[key]
                    cell.set('style',';'.join(f'{key}={value}' for key,value in original.items())+';')
                if cell.get('value'):
                    cell.set('value',cell.get('value').replace(entry['theme']+' |',selected+' |'))
        page.set('id',identifier); page.set('name',name)
        category=entry['category']
        filename={'purpose':'07-organizing-theme-cases.drawio','catalog':'08-catalog-theme-cases.drawio','annotation':'09-annotation-theme-cases.drawio'}[category]
        new_entry=dict(id=identifier,category='theme_case',name=name,theme=selected,
                       base_id=case['base_id'],base_file=entry['file'],base_theme=entry['theme'],
                       base_category=category,reason=case['reason'])
        groups.setdefault(filename,[]).append((page,new_entry))
        if previous!=case['base_id']:
            comparison.extend([f"## {entry['name']}（{case['base_id']}）",'',f"元サンプル: [{entry['theme']}]({entry['file']})。",'',f"![元テーマ {entry['theme']}](previews/{case['base_id']}.png)",''])
            previous=case['base_id']
        comparison.extend([f"### {selected}: {THEMES[selected]['name']}",'',case['reason']+'。', '',f"[Draw.ioのページ {identifier}]({filename})",'',f"![{name}](previews/{identifier}.png)",''])
    for filename,items in groups.items(): save(filename,[page for page,_ in items],[entry for _,entry in items])
    (BASE/'theme-cases.md').write_text('\n'.join(comparison).rstrip()+'\n',encoding='utf-8',newline='\n')


def main():
    # Retain the tools used for generation alongside the tracked samples.
    for name in ['diagrams.py','theme_styles.py','build_annotation.py']:
        shutil.copy2(SKILL/'scripts'/name, BASE/'scripts'/name)
    (BASE/'references').mkdir(exist_ok=True)
    shutil.copy2(SKILL/'references/diagram-themes.json', BASE/'references/diagram-themes.json')
    purposes(); catalogs(); themes(); annotations(); sequence()
    theme_cases()
    from build_native_samples import build as native_samples
    MANIFEST.extend(dict(file='10-native-capabilities.drawio', **entry) for entry in native_samples())
    (BASE/'manifest.json').write_text(json.dumps({'schema_version':1,'samples':MANIFEST},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# サンプルの対応一覧','','build_samples.pyでmanifest.jsonと同時に生成する。全て架空のデータまたは配置参考。','','| ID | 名称 | 区分 | テーマ | ファイル |','| --- | --- | --- | --- | --- |']
    for item in MANIFEST:
        lines.append(f"| {item['id']} | {item['name']} | {item['category']} | {item['theme']} | [{item['file']}]({item['file']}) |")
    (BASE/'index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Generated {len(MANIFEST)} sample pages; source files are separate. Existing output was not read.')


if __name__=='__main__': main()
