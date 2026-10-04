"""Author one independent example at a time; render, review, accept, then continue.

Build never marks visual review complete. accept is an explicit human/agent action
after viewing the generated PNG, tied to its file hash.
"""
import argparse
import base64
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO=Path(__file__).resolve().parents[4]
BASE=REPO/'sample/information-structuring/diagram-vocabulary'
SKILL=REPO/'.agents/skills/information-structuring'
sys.path.insert(0,str(SKILL/'scripts'))
import shape_catalog as sc
from theme_styles import theme

CATALOG=sc.read(SKILL/'references/drawio/shape-catalog.json')
# id, title, domain, composition, sources, theme, explanation question
DEFINITIONS=[
('context','システムの利用者と外部境界','software','hub-and-spoke',[10,45],'T02','誰が対象システムを利用し、何と連携するか'),
('container','アプリケーションと永続データ','software','nested-containers',[10],'T02','どの実行単位とデータが対象システムに属するか'),
('component','受付APIの責務分割','software','component-interface',[10,13],'T02','一つのAPIをどの責務とインターフェースへ分けるか'),
('layered','依存方向を揃えた三層構造','software','layered-stack',[11],'T08','画面・業務・データの依存方向はどうなっているか'),
('deployment','実行環境と配置対象','software','nested-deployment',[11],'T02','どの環境でどのアプリケーションを実行するか'),
('class','予約と利用者のクラス関係','software','class-association',[12],'T02','予約は誰に属し、どの属性を持つか'),
('sequence','予約要求のやり取り','software','sequence-lifelines',[11],'T02','要求と応答はどの相手へどの順に送られるか'),
('state','予約状態とイベント','software','state-transition',[14],'T02','何を契機に予約の状態が変わるか'),
('activity','受付の処理と条件分岐','software','activity-branch',[11],'T02','確認結果によって処理はどう分岐するか'),
('package','機能パッケージの依存','software','package-dependency',[11],'T02','どの機能群が共通定義に依存するか'),
('usecase','利用者と予約操作','software','actor-usecase',[11],'T02','どの利用者がどの目的で操作するか'),
('dataflow','予約データの入力と保管','software','data-flow',[17],'T01','どのデータがどの処理を通って保管されるか'),
('er','利用者・予約・設備のデータ関係','software','entity-relations',[18],'T02','どのデータのキーが別データに対応するか'),
('requirements','要求・画面・データの対応','software','trace-pipeline',[19],'T08','利用者要求はどの画面とデータで実現されるか'),
('interface','連携先と接続契約の一覧','software','interface-hub',[13],'T02','主システムは何をどの契約で授受するか'),
('traceability','要求・設計・検証のトレース','software','trace-matrix',[15],'T08','要求を何で実現し、何で検証するか'),
('topology','拠点ネットワークの接続','infrastructure','hub-and-spoke',[20],'T06','各拠点はどの経路で接続されるか'),
('logical-network','論理ネットワークの分離','infrastructure','zone-containment',[20],'T06','どの通信領域と経路を論理的に分けるか'),
('physical-network','物理機器と配線','infrastructure','physical-chain',[20],'T06','どの実機をどのケーブルで接続するか'),
('cloud','公開領域と非公開領域','infrastructure','nested-zones',[20],'T05','外部要求はどの境界を通って内部データへ届くか'),
('aws','LambdaとRDSの構成例','infrastructure','vendor-service-flow',[21,41],'T05','明示されたAWSサービスはどう連携するか'),
('azure','Azure VMとSQLの構成例','infrastructure','vendor-service-flow',[50,42],'T05','明示されたAzureサービスはどう連携するか'),
('gcp','GCPの実行環境とDBの構成例','infrastructure','vendor-service-flow',[20,44],'T05','明示されたGCPサービスはどう連携するか'),
('kubernetes','制御プレーンと実行ノード','infrastructure','control-and-workers',[46],'T08','制御対象とアプリケーションの実行場所はどこか'),
('ha','稼働系と待機系の切替条件','infrastructure','active-standby',[20],'T06','障害時にどの条件で待機系へ切り替わるか'),
('multi-region','二つの地域と複製経路','infrastructure','paired-regions',[39,40,44],'T05','どのデータを別地域へ複製するか'),
('rack','ラック内の機器配置','infrastructure','rack-stack',[52],'T06','どの高さにどの機器を置くか'),
('trust','信頼境界と検査点','security','trust-boundaries',[33,47],'T07','どの境界で何を検査するか'),
('control-data','制御判断とデータ通信の分離','security','dual-plane',[47,48],'T07','許可判断と実データの経路はどう異なるか'),
('threat','データフローに脅威を対応付ける','security','threat-overlay',[33,57],'T07','どの処理・境界にどの脅威があるか'),
('basic-flow','受付から回答までの基本フロー','business','left-to-right-pipeline',[27],'T01','入力はどの処理を経て結果になるか'),
('swimlane','担当者ごとの引き渡し','business','role-swimlane',[54],'T03','処理がどの担当からどの担当へ渡るか'),
('cross-functional','工程と担当の交差','business','phase-role-grid',[27],'T03','各工程で誰がどの処理を担当するか'),
('bpmn','承認業務のタスクとゲートウェイ','business','bpmn-exclusive-branch',[16],'T01','承認の条件で業務の経路がどう分かれるか'),
('raci','作業と責任の対応','business','responsibility-matrix',[28],'T03','各作業の実施者と承認者は誰か'),
('organisation','組織の所属関係','business','top-down-hierarchy',[29],'T01','各チームと班はどこへ所属するか'),
('business-model','予約サービスの事業構造','business','business-canvas',[31],'T04','誰に何を提供し、何で支えるか'),
('story-map','利用者行動とリリース範囲','business','story-map-grid',[53],'T10','利用者の行動に対し何を先に提供するか'),
('journey','利用者の接点と困りごと','business','journey-stage-panels',[53],'T09','行動の各段階で何に困り、何を改善するか'),
('roadmap','成果で区切る開発ロードマップ','project-management','horizon-roadmap',[26],'T04','各期間に何を実現するか'),
('timeline','出来事を時点へ配置する','project-management','time-axis',[26],'T03','どの出来事がいつ起きるか'),
('milestone','判断を伴う節目','project-management','milestone-gates',[26],'T03','各節目で何を確認し、誰が判断するか'),
('gantt','作業期間と依存関係','project-management','task-time-grid',[24],'T03','いつどの作業を行い、何の完了を待つか'),
('pert','並行作業の合流と所要日数','project-management','dependency-network',[23],'T03','並行作業はどこで合流し、どの経路が長いか'),
('dependency','成果物同士の依存','project-management','dependency-dag',[23],'T02','どの成果物が次の作業の前提になるか'),
('kanban','タスクの状態と仕掛数','project-management','status-columns',[25],'T03','どのタスクがどの状態にあり、仕掛はいくつか'),
('phase-team','工程ごとのチーム関与','project-management','phase-team-grid',[26],'T03','どのチームがどの工程へ関与するか'),
('wbs','成果物から作業を分解する','project-management','work-breakdown',[56],'T03','完成に必要な成果物と作業は何か'),
('risk','リスクと対策のつながり','project-management','risk-mitigation',[34],'T03','何が起こり得て、何を対策するか'),
('matrix','効果と工数による位置付け','analysis','two-axis-positioning',[31],'T09','各案は同じ二軸でどこに位置するか'),
('swot','内外の要因を四領域で整理する','analysis','swot-quadrants',[31],'T09','強み・弱み・機会・脅威をどう区別するか'),
('pestel','外部環境の六つの観点','analysis','faceted-environment',[31],'T09','どの外部条件が企画に影響するか'),
('fishbone','問題の原因候補を観点別に分ける','analysis','fishbone',[30],'T09','どの観点に原因候補があるか'),
('cause-effect','仮説と結果の因果関係','analysis','causal-chain',[30],'T09','どの仮説がどの結果を説明するか'),
('comparison','同じ評価軸で方式を比較する','analysis','comparison-table',[31],'T09','方式は同じ条件で何が違うか'),
('before-after','変更前後を同じ配置で比べる','analysis','paired-before-after',[31],'T04','同じ対象の何が変わり、何が残るか'),
('decision-tree','条件で選択肢を絞る','analysis','decision-tree',[34],'T09','どの条件ならどの案を選ぶか'),
('concept','概念と関係名を明示する','analysis','labelled-concept-graph',[32],'T09','概念間にはどの種類の関係があるか'),
('venn','集合の共通部分と差分','analysis','overlapping-sets',[55],'T09','何が共通で、何が片方だけに属するか'),
('sankey','数量を保つ流れの分岐','analysis','quantity-flow',[36],'T09','入力数量はどの出力へどれだけ分かれるか'),
('layered-info','能力を積み重ねて説明する','presentation','layered-explanation',[37],'T04','上位の価値はどの基盤に支えられるか'),
('process-steps','段階ごとの成果を示す','presentation','step-panels',[37],'T04','各段階で何を入力し、何を残すか'),
('numbered-flow','番号で読む順を固定する','presentation','numbered-path',[37],'T01','どの順で図を読めばよいか'),
('callout','図の要点を外周で説明する','presentation','callout-cluster',[37],'T01','図のどの箇所にどの説明が対応するか'),
('feature','機能の全体像と対象を対応付ける','presentation','core-and-satellites',[35],'T04','主要機能は誰の何を支えるか'),
('screenshot','原画面を保持した番号付き説明','presentation','annotated-base',[38],'T01','画面のどの領域を何のために使うか'),
('annotated-architecture','構成図を保持した設計意図の説明','presentation','annotated-base',[38],'T02','どの構成要素にどの設計意図が対応するか'),
('executive','主張と根拠を一図にまとめる','presentation','claim-evidence',[35],'T04','判断に必要な主張と根拠は何か'),
('five-c','事業を五つの対象から整理する','analysis','five-factor-context',[31],'T09','顧客・自社・競合・協力者・環境はどう関係するか'),
('gitflow','ブランチの分岐と統合','software','branch-merge-timeline',[22],'T02','変更はどこで分岐し、どこへ統合されるか'),
('funnel','対象数を段階ごとに絞る','analysis','funnel',[35],'T09','候補はどの条件で何件へ絞られるか'),
('cycle','反復する改善の工程','business','cycle',[51],'T03','一巡した結果を次の確認へどう戻すか'),
('feedback','観測結果を判断へ戻す','software','feedback-loop',[17],'T02','出力の観測が次の制御判断へどう影響するか'),
('zoom','全体から部分へ焦点を移す','software','multi-level-zoom',[10,45],'T02','全体のどの部分を次の詳細図で説明するか'),
('fault-tree','障害条件を論理結合で整理する','analysis','fault-tree',[34],'T09','サービス停止にはどの条件の組合せが関わるか'),
]


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Plan:
    def __init__(self, index):
        key,title,domain,composition,refs,selected,question=DEFINITIONS[index-1]
        self.key=key;self.title=title;self.id=f'DV-{index:03}';self.folder=BASE/'examples'/self.id
        self.folder.mkdir(parents=True,exist_ok=True)
        self.retrieval=[]
        self.ir=dict(id=self.id,width=1280,height=900,metadata=dict(title=title,purpose=question,audience='技術者・説明対象者',diagram_type=composition,theme=selected),nodes=[],containers=[],edges=[],tables=[])
        self.meta=dict(id=self.id,key=key,title_ja=title,title_en=key.replace('-',' ').title(),domain=[domain],purpose=question,
            audience=['developer','architect'] if domain in ('software','infrastructure','security') else ['manager','analyst'],
            diagram_type=[composition],composition_pattern=composition,source_refs=[f'SRC-{n:03}' for n in refs],
            information_structure=[],layout=dict(primary_axis='horizontal',grouping=composition,reading_direction='左から右、上から下'),
            drawio=dict(libraries=[],native_features=['connector','semantic-shape']),visual=dict(theme=selected,density='low-to-medium',hierarchy='図の目的 → まとまり → 個別要素',emphasis='主対象と主要経路'),
            visual_pattern=['title-and-short-explanation','neutral-boundaries','semantic-accent','labelled-relations'],relationships=[],
            when_to_use=[question+'を説明したい場合'],when_not_to_use=['入力に示されていない条件・順序・数量を補う場合'],strengths=['関係の種類と粒度を揃えて読める'],limitations=['例示の対象数と配置は案件に応じて再計算する'],
            tags=[key,composition,domain,title],core=index in (1,2,4,12,14,25,28,31,32,35,40,43,45,50,55,56,58,63,64),
            semantic_shape_requirement=[],variant_of=None,quality=dict(status='pending',scores=None),
            example_content='架空の予約サービス・企業・開発計画。実案件のデータではない。',
            artifact=f'sample/information-structuring/diagram-vocabulary/examples/{self.id}/example.drawio')
        self.text('heading',title,40,24,1200,55,26,True)
        self.text('summary',question+'。',40,92,1200,70,18)
        self.text('legend','架空の例。線の意味はラベルで示す。色は主対象・状態・注意を補助する。',40,820,1200,50,14)

    def text(self,i,label,x,y,w=200,h=60,size=18,bold=False,parent='1',extra=''):
        self.ir['nodes'].append(dict(id=i,label=label,x=x,y=y,width=w,height=h,parent=parent,primitive='text',fallback_reason='説明ラベル',style=f'fontSize={size};fontStyle={int(bold)};whiteSpace=wrap;'+extra))
        return i

    def node(self,i,label,x,y,w=180,h=80,kind='process',role='neutral',parent='1',extra='',vendor=None):
        if kind=='umlActor': extra='verticalLabelPosition=bottom;verticalAlign=top;align=center;'+extra
        if kind=='cloud': extra='align=center;spacingLeft=0;'+extra
        if kind=='decision': extra='align=center;spacingLeft=0;'+extra
        if kind in ('process','document','database','decision'):
            result=sc.search(CATALOG,kind,libraries_filter=['flowchart'],limit=5)
            item=next(r for r in result if sc.norm(r['name'])==kind)
            base=dict(shape_id=item['shape_id'],shape_query=kind,semantic_type=kind)
            self.retrieval.append(dict(node=i,query=kind,candidates=result,selected=item['shape_id'],reason='情報の意味に一致する標準図形'))
        elif kind.startswith('mxgraph.'):
            item=sc.exact(CATALOG,kind);base=dict(shape_id=kind,semantic_type=label,vendor=vendor,vendor_style_reason='入力がサービスを明示。識別図形を保持する')
            self.retrieval.append(dict(node=i,query=item['shape_name'],candidates=sc.search(CATALOG,item['shape_name'],libraries_filter=[item['library']],limit=4),selected=kind,reason='明示された図形の意味を照合'))
        else:
            base=dict(primitive=kind,fallback_reason='領域・状態・対象の一般記号。専門記法を主張しない')
        self.ir['nodes'].append(dict(id=i,label=label,x=x,y=y,width=w,height=h,parent=parent,role=role,style=extra,**base))
        self.meta['semantic_shape_requirement'].append(dict(node=i,semantic=base.get('semantic_type',kind)))
        return i

    def box(self,i,label,x,y,w,h,parent='1'):
        self.ir['containers'].append(dict(id=i,label=label,x=x,y=y,width=w,height=h,parent=parent))
        if 'container' not in self.meta['drawio']['native_features']: self.meta['drawio']['native_features'].append('container')
        return i

    def edge(self,a,b,label,kind='flow',points=(),parent='1',extra=''):
        self.ir['edges'].append(dict(id='e'+str(len(self.ir['edges'])),source=a,target=b,label=label,semantic_type=kind,waypoints=list(points),parent=parent,style=extra))
        if kind not in self.meta['relationships']:self.meta['relationships'].append(kind)

    def table(self,i,rows,x=120,y=250,widths=(280,280,280),height=62):
        self.ir['tables'].append(dict(id=i,x=x,y=y,column_widths=list(widths),rows=rows,row_height=height))
        self.meta['drawio']['native_features'].append('table')

    def pipeline(self,labels,y=350,kinds=None):
        n=len(labels);width=180;gap=(1140-n*width)/(n-1) if n>1 else 0
        for i,label in enumerate(labels):
            self.node(f'n{i}',label,60+i*(width+gap),y,kind=kinds[i] if kinds else 'process',role='primary' if i==0 else 'neutral')
            if i:self.edge(f'n{i-1}',f'n{i}','次へ')

    def tree(self,root,branches,leaves=None):
        self.meta['layout']['primary_axis']='vertical'
        self.node('top',root,520,215,220,70,kind='rectangle',role='primary')
        for i,label in enumerate(branches):
            x=110+i*350;self.node(f'b{i}',label,x,390,260,70,kind='rectangle');self.edge('top',f'b{i}','構成する','association')
            if leaves:
                self.node(f'l{i}',leaves[i],x,565,260,80,kind='rectangle');self.edge(f'b{i}',f'l{i}','含む','association')

    def uml(self,source):
        if self.key=='deployment': source='left to right direction\nskinparam nodesep 70\nskinparam ranksep 90\n'+source
        if self.key=='class': source='hide circle\nskinparam classAttributeIconSize 0\n'+source
        source='@startuml\nskinparam monochrome true\nskinparam shadowing false\nskinparam backgroundColor white\nskinparam defaultFontName "Yu Gothic"\nskinparam defaultFontSize 18\n'+source+'\n@enduml\n'
        path=self.folder/'source.puml';path.write_text(source,encoding='utf-8')
        subprocess.run(['plantuml','-charset','UTF-8','-tsvg',str(path.resolve())],check=True,capture_output=True,timeout=90)
        svg=self.folder/'source.svg';root=ET.parse(svg).getroot()
        if 'Syntax Error' in svg.read_text(encoding='utf-8'):raise ValueError('Invalid PlantUML source')
        w=float(re.sub('[^0-9.]','',root.get('width','800')));h=float(re.sub('[^0-9.]','',root.get('height','600')))
        scale=min(1100/w,560/h);dw=w*scale;dh=h*scale
        self.node('base','',(1280-dw)/2,210,dw,dh,kind='image',extra='image=data:image/svg+xml,'+base64.b64encode(svg.read_bytes()).decode()+';locked=1;movable=0;resizable=0;imageAspect=1;')
        self.meta['drawio']['native_features'].append('locked-source-layer')
        self.meta['external_source']=dict(path='source.puml',render='source.svg',sha256=digest(svg),meaning='PlantUMLが記法の正本。SVGは単一の表示オブジェクト')


def compose(p):
    k=p.key
    uml={
    'class':'class 利用者 {\n +利用者ID : String\n +氏名 : String\n}\nclass 予約 {\n +予約ID : String\n +開始日時 : DateTime\n}\n利用者 "1" -- "0..*" 予約 : 登録する',
    'sequence':'actor 利用者\nparticipant 画面\nparticipant 予約API\ndatabase DB\n利用者 -> 画面 : 予約入力\n画面 -> 予約API : 予約要求\n予約API -> DB : 空きを確認\nDB --> 予約API : 確認結果\nalt 空きあり\n予約API -> DB : 予約を登録\n予約API --> 画面 : 受付完了\nelse 空きなし\n予約API --> 画面 : 再選択を依頼\nend',
    'state':'[*] --> 未受付\n未受付 --> 確認中 : 申請\n確認中 --> 受付済 : 空きあり\n確認中 --> 未受付 : 空きなし\n受付済 --> 取消済 : 取消要求\n取消済 --> [*]',
    'activity':'start\n:申請を受信;\n:空きを確認;\nif (空きがある?) then (はい)\n :予約を登録;\nelse (いいえ)\n :再選択を依頼;\nendif\n:結果を通知;\nstop',
    'package':'package 予約業務 {\n [受付]\n [取消]\n}\npackage 共通 {\n [認証]\n [設備定義]\n}\n[受付] ..> [認証] : 利用\n[受付] ..> [設備定義] : 参照\n[取消] ..> [認証] : 利用',
    'usecase':'left to right direction\nactor 利用者\nactor 管理者\nrectangle 予約サービス {\n usecase "空きを探す" as Find\n usecase "予約する" as Book\n usecase "設備を管理する" as Manage\n}\n利用者 --> Find\n利用者 --> Book\n管理者 --> Manage',
    'deployment':'node "公開領域" {\n node "Web実行環境" {\n artifact "予約画面" as Web\n }\n}\nnode "内部領域" {\n node "API実行環境" {\n artifact "予約API" as API\n }\n database "予約DB" as DB\n}\nWeb --> API : HTTPS\nAPI --> DB : SQL',
    }
    if k in uml:p.uml(uml[k]);return
    if k=='context':
        p.node('system','予約サービス\n主対象',500,355,260,100,kind='rectangle',role='primary')
        p.node('user','利用者',80,370,180,90,kind='umlActor');p.node('admin','管理者',1030,370,150,90,kind='umlActor')
        p.node('mail','外部通知サービス',500,620,260,80,kind='cloud',role='external')
        p.edge('user','system','予約する');p.edge('admin','system','設備を管理する');p.edge('system','mail','通知を依頼')
    elif k in ('container','component','cloud','logical-network','trust','kubernetes','multi-region','annotated-architecture'):
        if k=='component':
            p.box('boundary','予約API',100,220,1080,480)
            for i,(a,b) in enumerate([('認証','本人を確認'),('空き検索','設備の空きを確認'),('登録','予約を保存')]):
                p.node(f'n{i}',a+'\n'+b,50+i*340,130,250,110,parent='boundary')
                if i:p.edge(f'n{i-1}',f'n{i}','呼び出す',parent='boundary')
        elif k=='kubernetes':
            p.box('control','制御プレーン',60,240,420,440);p.box('workers','実行ノード群',660,240,540,440)
            p.node('api','APIサーバー',85,120,250,90,parent='control');p.node('node','kubelet',150,115,250,90,parent='workers');p.node('pod','予約アプリ Pod',150,290,250,90,parent='workers')
            p.edge('api','node','状態と指示','bidirectional');p.edge('node','pod','実行を管理',parent='workers')
            p.text('note','制御の意味だけを示す概略図。全内部コンポーネントを網羅しない。',70,715,1150,55)
        elif k=='multi-region':
            for i,title in enumerate(['地域A：主系','地域B：複製先']):
                p.box(f'r{i}',title,70+i*620,230,510,460);p.node(f'app{i}','予約API',40,100,180,80,parent=f'r{i}');p.node(f'db{i}','予約データ',280,100,180,100,kind='database',parent=f'r{i}')
                p.edge(f'app{i}',f'db{i}','SQL',parent=f'r{i}')
            p.edge('db0','db1','非同期複製','dependency',points=[[530,580],[990,580]],extra='exitX=0.5;exitY=1;entryX=0.5;entryY=1;')
            p.text('note','複製先への切替手順と整合性条件は、この概略図だけでは保証しない。',70,730,1130,50)
        else:
            names={'container':('予約システム','利用者向け','業務・データ'), 'cloud':('クラウド環境','公開領域','非公開領域'),'logical-network':('企業ネットワーク','利用者VLAN','サーバーVLAN'),'trust':('処理範囲','未検証の要求','検査後の処理'),'annotated-architecture':('予約システム','画面','業務・データ')}
            outer,left,right=names[k];p.box('outer',outer,60,220,1160,470);p.box('left',left,30,70,360,330,parent='outer');p.box('right',right,520,70,590,330,parent='outer')
            p.node('web','予約画面' if k!='trust' else '外部要求',75,120,200,90,parent='left',role='external' if k=='trust' else 'primary')
            p.node('api','予約API' if k!='trust' else '認証・許可検査',40,120,200,90,parent='right');p.node('db','予約データ',345,120,200,100,kind='database',parent='right')
            p.edge('web','api','HTTPS要求' if k!='logical-network' else 'FW許可経路');p.edge('api','db','SQL',parent='right')
            if k=='annotated-architecture':
                p.text('a1','① 画面と業務を分離',100,710,400,50,bold=True);p.text('a2','② 永続化の責務を分離',730,710,450,50,bold=True)
                p.edge('a1','web','','annotation',extra='exitX=0.5;exitY=0;entryX=0.5;entryY=1;strokeColor=#2563EB;')
                p.edge('a2','db','','annotation',extra='exitX=0.5;exitY=0;entryX=0.5;entryY=1;strokeColor=#2563EB;')
                for n in p.ir['nodes']:
                    if n['id'] in ('a1','a2'):n['style']+='fontColor=#2563EB;'
                    if n['id']=='legend':n['label']='青い線は設計意図の説明先を指す。原図へ通信経路を追加したものではない。'
                p.meta['native_annotation']=True
    elif k=='layered':
        for i,(label,detail) in enumerate([('画面層','入力・表示'),('業務層','空き確認・予約受付'),('データ層','予約の永続化')]):
            p.box(f'layer{i}',label,220,210+i*180,840,135);p.node(f'n{i}',detail,55,48,730,65,parent=f'layer{i}')
            if i:p.edge(f'n{i-1}',f'n{i}','下位層へ依存','dependency')
    elif k=='dataflow':
        p.pipeline(['利用者の入力','予約の確認','予約データ'],kinds=['document','process','database'])
        p.text('note','矢印はデータの移動。処理の実行順序とは分ける。',120,600,1030,70)
        p.ir['edges'][0]['label']='申請データ';p.ir['edges'][1]['label']='確定した予約'
    elif k=='er':
        p.table('users',[['利用者'],['PK 利用者ID'],['氏名']],60,270,[290],64)
        p.table('booking',[['予約'],['PK 予約ID'],['FK 利用者ID'],['FK 設備ID']],490,270,[300],64)
        p.table('resource',[['設備'],['PK 設備ID'],['名称']],940,270,[280],64)
        p.edge('users_r0','booking_r0','1 : 0..*','association');p.edge('resource_r0','booking_r0','1 : 0..*','association')
        p.text('note','PKは主キー、FKは外部キー。利用者と設備の両方を予約が参照する。',90,620,1120,75)
    elif k=='requirements':
        p.pipeline(['REQ-01\n空きを探したい','画面UI-01\n候補を選ぶ','DATA-01\n設備の空き情報'],kinds=['document','rectangle','database'])
        p.ir['edges'][0]['label']='画面へ具体化';p.ir['edges'][1]['label']='参照する'
    elif k=='interface':
        p.node('hub','予約API',490,350,300,110,role='primary')
        for i,(label,x,y) in enumerate([('画面\nHTTPS / JSON',70,270),('認証\nトークン検証',980,270),('通知\n通知要求',490,620)]):
            p.node(f'n{i}',label,x,y,240,100,kind='rectangle');p.edge(f'n{i}','hub','契約を介して接続','association')
    elif k=='traceability':
        p.table('trace',[['要求','設計','検証'],['REQ-01 空き検索','API-01 検索','TEST-01 空き結果'],['REQ-02 予約受付','API-02 登録','TEST-02 重複を防ぐ']],120,260,[320,320,400],90)
        p.text('note','共通IDで導出を追う。対応のない要求や検証は別途一覧化する。',100,660,1150,65)
    elif k in ('topology','physical-network','ha','control-data','threat'):
        if k=='topology':
            p.node('router','中継ネットワーク',500,370,260,90,kind='cloud',role='primary')
            for i,(label,x,y) in enumerate([('拠点A',70,280),('拠点B',1000,280),('業務サーバー',500,650)]):
                p.node(f'n{i}',label,x,y,210,85,kind='rectangle');p.edge(f'n{i}','router','回線接続','association',extra=['entryX=0;entryY=0.5;','entryX=1;entryY=0.5;','entryX=0.5;entryY=1;'][i])
        elif k=='physical-network':
            p.pipeline(['端末 PC-01','スイッチ SW-01','サーバー SV-01'],kinds=['rectangle']*3)
            for e in p.ir['edges']: e['label']='LANケーブル';e['semantic_type']='association'
            p.text('note','機器IDと配線を示す。VLANやアクセス許可の論理条件は別図へ分ける。',100,620,1140,65)
        elif k=='ha':
            p.node('entry','利用要求',60,365,190,90,kind='document');p.node('active','A：稼働系',500,260,260,110,kind='rectangle',role='primary');p.node('standby','B：待機系',500,530,260,110,kind='rectangle');p.node('db','共通データ',1010,365,190,100,kind='database')
            p.edge('entry','active','通常経路');p.edge('active','db','参照・保存');p.edge('entry','standby','A障害時のみ','reference',points=[[350,575]]);p.edge('standby','db','切替後のみ','reference',points=[[900,575]])
            p.text('condition','条件：Bが稼働可能、故障検出済み、切替が承認された場合に継続可能。',80,735,1120,60)
        elif k=='control-data':
            p.box('cp','制御判断',120,210,1040,190);p.box('dp','データ通信',120,485,1040,210)
            p.node('policy','ポリシー判断',430,70,230,85,parent='cp',kind='hexagon',role='primary')
            for i,(label,x) in enumerate([('利用者',40),('アクセス実施点',430),('業務サービス',780)]):p.node(f'n{i}',label,x,90,210,80,parent='dp',kind='rectangle')
            p.edge('n0','n1','データ要求',parent='dp');p.edge('n1','n2','許可時に転送',parent='dp');p.edge('policy','n1','許可・拒否の指示','dependency')
        else:
            p.pipeline(['外部要求','認証・入力検査','予約データ'],kinds=['document','process','database'])
            p.ir['edges'][0]['label']='要求データ';p.ir['edges'][1]['label']='許可された予約'
            p.box('threat','脅威と対策の仮説',160,575,960,160)
            p.text('risk','要求の改ざん → 入力検査\n認証情報の悪用 → 本人確認と監査',35,55,880,85,parent='threat')
            p.edge('threat','n1','検査点へ対応付ける','reference',extra='exitX=0.5;exitY=0;entryX=0.5;entryY=1;')
    elif k in ('aws','azure','gcp'):
        services={'aws':[('mxgraph.aws4.lambda','AWS Lambda','#ED7100','aws'),('mxgraph.aws4.rds','Amazon RDS','#C925D1','aws')],
                  'azure':[('mxgraph.azure.virtual_machine','Azure VM','#0078D4','azure'),('mxgraph.azure.sql_database','Azure SQL Database','#0078D4','azure')],
                  'gcp':[('mxgraph.gcp2.compute_engine','Compute Engine','#4285F4','gcp'),('mxgraph.gcp2.cloud_sql','Cloud SQL','#4285F4','gcp')]}
        # Choose exact existing candidates; never invent an ID if the installed version differs.
        for i,(identifier,label,color,vendor) in enumerate(services[k]):
            if not any(s['id']==identifier for s in CATALOG['shapes']):
                words=label.lower().replace('azure ','').replace('google ','')
                options=sc.search(CATALOG,words,vendor=vendor,limit=12)
                chosen=next((c for c in options if sc.norm(c['name'])==sc.norm(words)),None)
                if not chosen:raise ValueError(f'Confirm actual vendor candidate for {label}: {options}')
                identifier=chosen['shape_id']
            p.node(f's{i}',label,230+i*620,340,180,130,kind=identifier,vendor=vendor,extra=f'verticalLabelPosition=bottom;verticalAlign=top;align=center;fillColor={color};strokeColor=none;')
        p.edge('s0','s1','SQL要求');p.text('note','この例は上記サービスが明示された入力を想定する。一般的なDBを固有サービスと推定しない。',80,640,1150,70)
    elif k=='rack':
        p.box('rack','ラック R-01（模式図）',350,205,580,545)
        for i,(label,height) in enumerate([('パッチパネル',55),('ネットワーク機器',80),('予約サーバー',105),('予備領域',70)]):
            p.node(f'r{i}',label,65,60+i*105,450,height,kind='rectangle',parent='rack')
        p.text('note','配置と空き領域の例。実機のU数・配線長・放熱条件は入力で確認する。',70,760,1160,50)
    elif k in ('basic-flow','process-steps','numbered-flow'):
        labels={'basic-flow':['受付','確認','回答'],'process-steps':['素材を読む','軸を選ぶ','図にする','検証する'],'numbered-flow':['① 入力を確認','② 関係を整理','③ 表現を選ぶ','④ 図を確認']}[k]
        p.pipeline(labels)
        if k=='process-steps':
            for i,label in enumerate(['情報単位','選択理由','図とIR','検査記録']):p.text(f'o{i}','残すもの：'+label,60+i*320,570,235,80,size=17)
    elif k in ('swimlane','cross-functional','phase-team'):
        if k=='swimlane':
            for i,title in enumerate(['依頼者','受付担当','承認担当']):
                p.box(f'l{i}',title,50,205+i*180,1180,140);p.node(f'a{i}',['依頼を入力','内容を確認','承認を判断'][i],100+i*320,55,250,65,parent=f'l{i}')
                if i:p.edge(f'a{i-1}',f'a{i}','引き渡す',points=[[275+(i-1)*320,365+(i-1)*180],[275+i*320,365+(i-1)*180]],extra='exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#172B4D;')
        else:
            headings=['担当 / 工程','準備','設計','検証']
            rows=[headings,['業務担当','要件を整理','条件を確認','受入を確認'],['開発担当','影響を調査','設計・実装','動作を検証'],['運用担当','制約を提示','監視を設計','運用を確認']]
            p.table('grid',rows,80,250,[220,300,300,300],95)
            if k=='cross-functional':
                p.meta['drawio']['native_features'].append('container-table')
                # Table cells become semantic containers; nested steps will be placed during final XML composition.
                p.meta['cell_container']=True
                for row in p.ir['tables'][0]['rows'][1:]:
                    for column in range(1,4): row[column]=''
                for r, labels in enumerate([['要件を整理','条件を確認','受入を確認'],['影響を調査','設計・実装','動作を検証'],['制約を提示','監視を設計','運用を確認']],1):
                    for c,label in enumerate(labels,1):
                        p.node(f'step{r}{c}',label,35,20,230,55,parent=f'grid_r{r}_c{c}')
                p.edge('step11','step22','',points=[[582,392.5],[582,487.5]],parent='1',extra='exitX=1;exitY=0.5;entryX=0;entryY=0.5;strokeColor=#172B4D;')
            p.text('note','工程の順序と担当の分類を分ける。必要な引き渡しだけを関係線で補う。',80,720,1130,60)
            if k=='cross-functional':p.ir['nodes'][-1]['label']='矢印：業務担当が整理した要件を、開発担当の設計へ引き渡す。'
    elif k=='bpmn':
        p.node('start','開始',80,350,60,60,kind='ellipse');p.node('task','申請を確認',260,335,200,90)
        p.node('gate','',630,350,70,70,kind='mxgraph.bpmn.gateway_xor_(data)')
        p.node('yes','承認する',930,240,220,85);p.node('no','差戻しを通知',930,520,220,85)
        p.edge('start','task','');p.edge('task','gate','確認結果')
        p.edge('gate','yes','承認可',points=[[665,282.5]],extra='exitX=0.5;exitY=0;entryX=0;entryY=0.5;')
        p.edge('gate','no','承認不可',points=[[665,562.5]],extra='exitX=0.5;exitY=1;entryX=0;entryY=0.5;')
        p.text('note','排他的分岐の概略。正式なBPMNモデルでは終了・例外・メッセージ意味も定義する。',80,735,1140,65)
    elif k=='raci':
        p.table('raci',[['作業','依頼者','担当者','責任者'],['要求を確定','C','R','A'],['図を制作','C','R','A'],['成果を受入','R','C','A']],130,250,[310,230,230,230],95)
        p.text('key','R：実施、A：最終責任、C：相談。各作業のAは一人とする例。',100,730,1100,60)
    elif k in ('organisation','wbs'):
        p.tree('予約サービス組織' if k=='organisation' else '予約サービスの完成',
            ['業務チーム','開発チーム','運用チーム'] if k=='organisation' else ['要求資料','アプリケーション','運用資料'],
            ['受付班','アプリ開発班','監視班'] if k=='organisation' else ['用語・条件の整理','画面・APIの制作','監視・手順の作成'])
        if k=='organisation':
            for e in p.ir['edges']:e['label']='下位組織'
    elif k=='business-model':
        labels=['協力者\n設備提供者','活動\n予約の仲介','価値\n空きの探索を短縮','顧客関係\n利用案内','顧客\n設備利用者','資源\n設備情報','チャネル\n予約画面','費用\n開発・運用','収益\n利用料の例']
        for i,label in enumerate(labels):
            x=70+(i%3)*395;y=205+(i//3)*185;p.box(f'b{i}',label.split('\n')[0],x,y,360,160);p.text(f't{i}',label.split('\n')[1],25,60,305,70,parent=f'b{i}')
    elif k in ('story-map','journey'):
        rows=[['行動段階','探す','選ぶ','予約する'],['最小の機能','候補一覧','条件の比較','予約受付'],['次の機能','絞込み','お気に入り','変更・取消']] if k=='story-map' else [['段階','探す','選ぶ','予約する'],['接点','検索画面','候補詳細','受付結果'],['困りごと','候補が多い','条件が不明','完了が不明'],['改善案','絞込み','比較欄','通知と状態']]
        p.table('journey',rows,70,235,[235,305,305,305],100)
        p.text('scope','行動の順序を横軸に置く。顧客感情や実測効果は、この架空例から推定しない。',70,730,1160,60)
    elif k in ('roadmap','timeline','milestone'):
        labels={'roadmap':['探索：要求を確定','試行：受付を提供','拡張：運用を改善'],'timeline':['4月：要求を整理','5月：試作を公開','6月：受入を完了'],'milestone':['M1：要求を承認','M2：試作を評価','M3：運用移行を判断']}[k]
        p.pipeline(labels,y=340,kinds=['document']*3 if k=='milestone' else ['rectangle']*3)
        for e in p.ir['edges']:e['label']='次の期間' if k=='roadmap' else '時間の順'
        if k=='roadmap':p.text('condition','日付ではなく成果の到達条件を主に示す。完了条件を満たした後に次へ進む。',80,640,1100,70)
        if k=='milestone':p.text('condition','各節目の判断者：業務責任者。未達なら次工程へ進めず、条件を再確認する。',80,640,1100,70)
    elif k=='gantt':
        p.table('schedule',[['作業 / 週','W1','W2','W3','W4'],['要求整理','実施','実施','',''],['試作','','実施','実施',''],['受入','','','','実施']],70,240,[340,210,210,210,210],95)
        p.text('note','依存：要求の主要条件が確定してから試作、試作完了後に受入。期間は架空の計画値。',80,720,1120,70)
    elif k in ('pert','dependency','risk','cause-effect'):
        if k in ('risk','cause-effect'):
            p.pipeline(['情報が不足','確認漏れの可能性','利用者が再入力'] if k=='risk' else ['条件が曖昧という仮説','受付の確認が増える','回答に時間がかかる'],kinds=['document','process','rectangle'])
            if k=='cause-effect':next(n for n in p.ir['nodes'] if n['id']=='n0')['role']='hypothesis'
            for e in p.ir['edges']:e['label']='起こり得る' if k=='risk' else '仮説の関係'
            p.node('control','対策：必要条件を入力時に確認する',350,615,600,90,kind='note',role='warning')
            p.edge('control','n1','発生を抑える','reference',extra='exitX=0.5;exitY=0;entryX=0.5;entryY=1;')
        else:
            p.node('start','要求を確定' if k=='dependency' else 'A：準備 2日',70,385,215,90,kind='document')
            p.node('up','画面設計' if k=='dependency' else 'B：試作 4日',510,245,240,85)
            p.node('down','API設計' if k=='dependency' else 'C：資料 3日',510,525,240,85)
            p.node('end','結合を検証' if k=='dependency' else 'D：確認 1日',1000,385,220,90)
            connections=[('start','up',[[360,407.5],[360,287.5]],0.25,0.5,'A完了後' if k=='pert' else '要求確定後'),
                         ('start','down',[[360,452.5],[360,567.5]],0.75,0.5,'A完了後' if k=='pert' else '要求確定後'),
                         ('up','end',[[860,287.5],[860,407.5]],0.5,0.25,'B完了後' if k=='pert' else '画面設計後'),
                         ('down','end',[[860,567.5],[860,452.5]],0.5,0.75,'C完了後' if k=='pert' else 'API設計後')]
            for a,b,points,ex,ey,label in connections:p.edge(a,b,label,'dependency',points=points,extra=f'exitX=1;exitY={ex};entryX=0;entryY={ey};strokeColor=#172B4D;')
            if k=='pert':p.text('calc','所要日数の例：A→B→D は7日、A→C→D は6日。資源制約を入れない場合の比較。',80,735,1150,60)
    elif k=='kanban':
        for i,title in enumerate(['予定','対応中（WIP上限2）','完了']):
            p.box(f'col{i}',title,70+i*400,215,350,520)
            labels=[['条件を整理','通知案を検討'],['画面を試作','APIを確認'],['用語を確定']][i]
            for j,label in enumerate(labels):p.node(f'c{i}{j}',label,35,95+j*150,280,100,kind='note',parent=f'col{i}',role=['planned','progress','done'][i])
    elif k in ('matrix','swot'):
        labels=['効果：高 / 工数：小\n案A：入力補助','効果：高 / 工数：大\n案B：連携自動化','効果：低 / 工数：小\n案C：表示修正','効果：低 / 工数：大\n案D：全面改修'] if k=='matrix' else ['内部・有利：強み\n設備情報が揃う','外部・有利：機会\n予約需要の増加','内部・不利：弱み\n受付の属人化','外部・不利：脅威\n競合の増加']
        for i,label in enumerate(labels):p.box(f'q{i}',label.split('\n')[0],100+(i%2)*560,215+(i//2)*250,510,220);p.text(f't{i}',label.split('\n')[1],35,80,430,95,parent=f'q{i}')
        if k=='matrix':p.text('axes','工数は左右、効果は上下の二軸。位置は架空評価であり、実績値ではない。',80,740,1130,60)
    elif k=='pestel':
        p.table('environment',[['観点','確認する条件'],['政治・経済','補助制度・利用料の変化'],['社会・技術','利用習慣・認証技術'],['環境・法律','省資源・個人情報の扱い']],190,230,[350,700],110)
        p.text('note','六つの観点を二つずつ並べた索引。影響の有無と根拠は別途確認する。',80,740,1150,60)
    elif k=='fishbone':
        p.node('effect','回答の遅れ',1010,385,220,100,kind='rectangle',role='primary')
        p.node('spine','',100,431,4,4,kind='ellipse',extra='fillColor=none;strokeColor=none;')
        p.edge('spine','effect','結果','association',extra='edgeStyle=none;endArrow=none;')
        for i,(name,detail,x,y) in enumerate([('人','確認の集中',90,215),('手順','確認項目の不統一',540,215),('情報','条件の不足',90,575),('道具','通知の手作業',540,575)]):
            p.node(f'cause{i}',name+'\n'+detail,x,y,280,100,kind='note')
            p.node(f'joint{i}','',x+330,431,4,4,kind='ellipse',extra='fillColor=none;strokeColor=none;')
            p.edge(f'cause{i}',f'joint{i}','原因候補','association',extra='edgeStyle=none;endArrow=none;')
        p.text('certainty','候補を観点別に整理した図。原因が確定したとは扱わない。',80,745,1100,60)
    elif k=='comparison':
        p.table('compare',[['評価軸','方式A：手作業','方式B：受付自動化'],['導入','すぐ始められる','実装が必要'],['確認','担当者が確認','条件をルール化'],['変更','手順を直す','ルールと実装を直す']],90,235,[320,400,400],105)
    elif k=='before-after':
        for i,title in enumerate(['変更前','変更後']):
            p.box(f'b{i}',title,70+i*640,225,520,460)
            p.node(f'input{i}','申請',30,95,190,85,kind='document',parent=f'b{i}');p.node(f'check{i}','担当者が確認' if i==0 else '条件を自動確認',290,95,195,85,parent=f'b{i}',role='neutral' if i==0 else 'primary');p.edge(f'input{i}',f'check{i}','確認依頼',parent=f'b{i}')
            p.text(f'note{i}','入力と結果は共通。確認の担当だけを変更する。',30,280,455,90,parent=f'b{i}')
    elif k=='decision-tree':
        p.node('choice','条件が定義済みか',495,210,270,100,kind='decision');p.node('defined','ルール化の案',80,510,320,110,kind='rectangle');p.node('unknown','情報を追加調査',830,510,340,110,kind='document')
        p.edge('choice','defined','はい');p.edge('choice','unknown','いいえ');p.text('condition','決定条件は入力の事実で確認する。重み・順位・費用効果を作らない。',90,725,1120,75)
    elif k=='concept':
        p.node('booking','予約',500,355,240,95,kind='rectangle',role='primary')
        for i,(label,x,y,relation) in enumerate([('利用者',70,230,'登録する'),('設備',970,230,'対象となる'),('時間帯',500,620,'指定する')]):
            p.node(f'n{i}',label,x,y,210,85,kind='rectangle')
            if i==2:p.edge('booking',f'n{i}',relation,'association',extra='endArrow=open;')
            else:p.edge(f'n{i}','booking',relation,'association',extra=['entryX=0;entryY=0.5;endArrow=open;','entryX=1;entryY=0.5;endArrow=open;'][i])
        next(n for n in p.ir['nodes'] if n['id']=='legend')['label']='矢印は関係名の主語から対象へ向かう。処理順を示す図ではない。'
    elif k=='venn':
        p.node('a','',210,220,520,460,kind='ellipse',extra='fillColor=none;strokeColor=#2563EB;')
        p.node('b','',510,220,520,460,kind='ellipse',extra='fillColor=none;strokeColor=#64748B;')
        p.text('al','業務条件\n受付の必要情報',250,310,260,220);p.text('both','共通\n本人確認',535,365,170,160,bold=True);p.text('bl','運用条件\n監視・復旧',775,310,220,220)
        p.meta['intentional_overlap']=['a','b'];p.meta['when_not_to_use'].append('厳密な数量比を円の面積から読み取らせたい場合')
    elif k=='sankey':
        p.node('in','受付20件',80,360,250,120,kind='rectangle',role='primary');p.node('accepted','完了12件',880,220,280,100,kind='rectangle');p.node('pending','確認待ち8件',880,580,280,100,kind='rectangle',role='attention')
        p.edge('in','accepted','12件',extra='strokeWidth=12;exitX=1;exitY=0.3;entryX=0;entryY=0.5;');p.edge('in','pending','8件',extra='strokeWidth=8;exitX=1;exitY=0.7;entryX=0;entryY=0.5;')
        p.meta['quantity_check']=dict(input=20,outputs=[12,8],unit='件',width_scale='1px / 件')
        p.text('total','数量の保存：20 = 12 + 8。線幅は件数に比例する架空の例。',80,740,1120,60)
    elif k=='layered-info':
        for i,(label,detail) in enumerate([('利用価値','空きと条件を短時間で把握'),('業務能力','受付・確認・通知'),('基盤','データ・認証・運用')]):
            width=790+i*80
            p.box(f's{i}',label,230-i*40,205+i*195,width,160);p.text(f'd{i}',detail,50,55,width-100,65,parent=f's{i}')
        p.text('principle','積層は依存する能力の説明。立体装飾や面積で数量を表さない。',70,765,1160,55)
    elif k=='callout':
        p.node('system','予約API',500,325,260,135,role='primary')
        for i,(label,x,y) in enumerate([('① 入力条件を検査',50,220),('② 空きを確認',920,220),('③ 結果を通知',475,625)]):
            p.node(f'c{i}',label,x,y,280,100,kind='note');p.edge(f'c{i}','system','','reference',extra=['entryX=0;entryY=0.5;','entryX=1;entryY=0.5;','entryX=0.5;entryY=1;'][i])
        next(n for n in p.ir['nodes'] if n['id']=='legend')['label']='点線は予約APIに対する説明を結ぶ。処理の経路や順序を示す線ではない。'
    elif k=='feature':
        p.node('core','予約サービス',500,340,280,110,kind='rectangle',role='primary')
        for i,(label,x,y) in enumerate([('探索\n候補を見つける',70,230),('比較\n条件を揃える',970,230),('受付\n予約を記録する',70,575),('通知\n結果を知らせる',970,575)]):
            p.node(f'n{i}',label,x,y,240,110,kind='rectangle');p.edge('core',f'n{i}','提供する','association')
    elif k=='screenshot':
        # Independent fictional UI source, not a recreation of a real product screen.
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="850" height="440"><rect width="850" height="440" fill="#f8fafc"/><rect width="850" height="60" fill="#e2e8f0"/><text x="25" y="40" font-size="22">予約管理：架空の画面</text><rect x="20" y="95" width="175" height="315" fill="#ffffff" stroke="#64748b"/><text x="40" y="135" font-size="20">検索条件</text><rect x="225" y="95" width="595" height="220" fill="#ffffff" stroke="#64748b"/><text x="250" y="135" font-size="20">設備の候補一覧</text><rect x="610" y="350" width="210" height="60" fill="#dbeafe" stroke="#2563eb"/><text x="640" y="388" font-size="20">選択して予約</text></svg>'
        (p.folder/'source.svg').write_text(svg,encoding='utf-8')
        p.node('base','',70,220,850,440,kind='image',extra='image=data:image/svg+xml,'+base64.b64encode(svg.encode()).decode()+';locked=1;imageAspect=1;')
        for i,(label,xx,yy) in enumerate([('条件を指定',210,355),('候補を確認',550,355),('予約へ進む',825,552)]):
            p.node(f'num{i}',str(i+1),xx,yy,36,36,kind='ellipse',role='primary',extra='align=center;fontStyle=1;spacingLeft=0;whiteSpace=nowrap;')
            p.text(f'ann{i}',str(i+1)+'：'+label,960,245+i*135,260,100,bold=True)
        p.meta['external_source']=dict(path='source.svg',render='source.svg',sha256=digest(p.folder/'source.svg'),meaning='架空UIの原図を単一オブジェクトで保持')
        p.meta['drawio']['native_features'].append('locked-source-layer')
    elif k=='executive':
        p.box('claim','提案：受付条件を揃える',70,215,1140,160);p.text('claimtext','確認の往復を減らすため、申請時の必要情報を共通化する。',35,60,1070,65,parent='claim')
        for i,(name,detail) in enumerate([('観測','受付条件が担当者で異なる'),('影響の仮説','確認の往復が増える可能性'),('次の確認','必要条件と効果を実測する')]):
            p.box(f'e{i}',name,70+i*390,445,350,240);p.text(f't{i}',detail,25,65,295,130,parent=f'e{i}')
    elif k=='five-c':
        p.node('company','自社：予約仲介',500,365,270,100,kind='rectangle',role='primary')
        for i,(label,x,y) in enumerate([('顧客：設備利用者',70,225),('競合：別の予約手段',975,225),('協力者：設備提供者',70,575),('環境：利用規則',975,575)]):
            p.node(f'f{i}',label,x,y,240,110,kind='rectangle');p.edge(f'f{i}','company','分析対象','association',extra=f'entryX={0 if i%2==0 else 1};entryY={0.25 if i<2 else 0.75};')
    elif k=='gitflow':
        p.box('main','main：リリース基準',70,210,1140,185);p.box('dev','dev：変更を統合',70,435,1140,185)
        for i,(label,x) in enumerate([('基準版',60),('次の基準版',815)]):p.node(f'm{i}',label,x,60,230,75,parent='main',kind='ellipse')
        for i,(label,x) in enumerate([('変更開始',60),('検証済み変更',455),('統合',815)]):p.node(f'd{i}',label,x,60,230,75,parent='dev',kind='ellipse')
        p.edge('m0','m1','版の流れ',parent='main');p.edge('d0','d1','変更・検証',parent='dev');p.edge('d1','d2','統合',parent='dev');p.edge('m0','d0','分岐');p.edge('d2','m1','リリース')
        p.text('scope','ブランチ戦略の例。実際の開発ルールに合わせて分岐・承認条件を変更する。',70,715,1160,65)
    elif k=='funnel':
        for i,(label,width) in enumerate([('候補20件：対象条件で選別',1040),('候補12件：必須条件を確認',624),('候補8件：実行可能性を確認',416)]):
            p.node(f'f{i}',label,(1280-width)/2,225+i*175,width,110,kind='rectangle',role='primary' if i==2 else 'neutral')
            if i:p.edge(f'f{i-1}',f'f{i}','条件を満たす')
        p.text('note','横幅は件数に比例。減った件数の理由は別表で追跡する。',80,755,1130,50)
        p.meta['quantity_check']=dict(values=[20,12,8],widths=[1040,624,416],unit='件',width_scale='52px / 件')
    elif k=='cycle':
        for i,(label,x,y) in enumerate([('計画する',165,220),('試す',845,220),('観測する',845,565),('見直す',165,565)]):p.node(f'n{i}',label,x,y,260,100)
        for a,b,label in [('n0','n1','計画を実行'),('n1','n2','結果を観測'),('n2','n3','結果を評価'),('n3','n0','次の計画へ')]:p.edge(a,b,label)
        p.text('note','反復関係を示す。各工程の実時間や周期はこの配置から推定しない。',80,745,1150,60)
    elif k=='feedback':
        p.pipeline(['判断・制御','対象の処理','結果の観測'],y=320)
        p.edge('n2','n0','観測結果を判断へ戻す','reference',points=[[1110,650],[150,650]],extra='exitX=0.5;exitY=1;entryX=0.5;entryY=1;endArrow=block;dashed=1;dashPattern=6 4;')
        p.text('note','戻りは制御用の情報。通常の処理順や無限ループとは分ける。',80,725,1150,60)
    elif k=='zoom':
        p.box('overview','全体：予約サービス',70,240,460,390);p.node('web','画面',30,110,170,80,parent='overview');p.node('api','API',240,110,170,80,parent='overview',role='primary');p.edge('web','api','要求',parent='overview')
        p.box('detail','詳細：APIの責務',720,240,490,390)
        for i,label in enumerate(['認証','受付','保存']):p.node(f'd{i}',label,35+i*150,145,120,80,parent='detail')
        p.edge('api','detail','この部分を展開','reference',extra='exitX=1;exitY=0.5;entryX=0;entryY=0.6;')
        p.text('note','全体と詳細は同じAPIを別の抽象度で説明する。詳細への線は通信ではない。',80,735,1130,60)
    elif k=='fault-tree':
        p.node('top','予約サービス停止',460,215,360,90,kind='rectangle',role='primary')
        p.node('or','OR',570,385,140,65,kind='rectangle',extra='align=center;spacingLeft=0;')
        p.node('a','API障害',130,555,360,100,kind='rectangle');p.node('b','データへの接続不能',785,555,360,100,kind='rectangle')
        p.edge('a','or','停止条件','association');p.edge('b','or','停止条件','association');p.edge('or','top','いずれかで成立','association')
        p.text('note','論理条件の概略。発生確率・独立性・冗長化の成立は追加情報なしに計算しない。',80,735,1150,60)
    else:raise ValueError(k)


def build(identifier, allow_pending=False):
    index=int(identifier.removeprefix('DV-'))
    if not 1<=index<=len(DEFINITIONS):raise ValueError('Unknown vocabulary ID')
    if index>1 and not allow_pending:
        previous=BASE/'examples'/f'DV-{index-1:03}'/'metadata.yaml'
        if not previous.exists() or sc.read(previous)['quality']['status']!='accepted':
            raise ValueError('Finish rendering and visual review of previous example before creating the next')
    p=Plan(index);compose(p)
    result=sc.render(CATALOG,p.ir,p.folder/'example.drawio')
    doc=ET.parse(p.folder/'example.drawio');root=doc.getroot().find('./diagram/mxGraphModel/root')
    if p.meta.get('external_source'):
        root.insert(2,ET.Element('mxCell',id='source-layer',value='00_Source',parent='0',style='locked=1;'))
        root.insert(3,ET.Element('mxCell',id='annotation-layer',value='20_Annotation',parent='0'))
        root.find("mxCell[@id='base']").set('parent','source-layer')
        for c in root.findall('mxCell'):
            if c.get('vertex')=='1' and c.get('id','').startswith(('num','ann')):c.set('parent','annotation-layer')
        sc.write(p.folder/'annotation-ir.json',dict(source=p.meta['external_source'],purpose=p.ir['metadata']['purpose'],
            audience=p.ir['metadata']['audience'],theme=p.ir['metadata']['theme'],
            annotations=[dict(id=n['id'],label=n['label'],normalized_position=dict(x=(n['x']-70)/850,y=(n['y']-220)/440),
                target_text=['検索条件','設備の候補一覧','選択して予約'][int(n['id'][-1])],confidence='high',source='架空UIの可視文字と元SVG')
                for n in p.ir['nodes'] if n['id'].startswith('num')]))
    if p.meta.get('native_annotation'):
        root.insert(2,ET.Element('mxCell',id='source-layer',value='00_Source',parent='0',style='locked=1;'))
        root.insert(3,ET.Element('mxCell',id='annotation-layer',value='20_Annotation',parent='0'))
        root.find("mxCell[@id='outer']").set('parent','source-layer')
        annotation_ids={'a1','a2',p.ir['edges'][-2]['id'],p.ir['edges'][-1]['id']}
        for c in root:
            if c.get('id') in annotation_ids:c.set('parent','annotation-layer')
            elif c.get('edge')=='1' and c.get('parent')=='1':c.set('parent','source-layer')
        original=copy.deepcopy(doc);original_root=original.getroot().find('./diagram/mxGraphModel/root')
        for c in list(original_root):
            if c.get('id') in annotation_ids:original_root.remove(c)
        ET.indent(original,space='  ');original.write(p.folder/'source.drawio',encoding='utf-8',xml_declaration=True)
        p.meta['source_preservation']=dict(path='source.drawio',sha256=digest(p.folder/'source.drawio'),
            preserved_ids=[c.get('id') for c in original_root if c.get('vertex')=='1' or c.get('edge')=='1'])
        p.meta['drawio']['native_features'].append('locked-source-layer')
    if p.meta.get('cell_container'):
        for c in root.findall('mxCell'):
            if re.fullmatch(r'grid_r[1-3]_c[1-3]',c.get('id','')):
                c.set('style',c.get('style')+'container=1;')
    if p.key=='gantt':
        for c in root.findall('mxCell'):
            if c.get('value')=='実施':c.set('value','予定');c.set('style',c.get('style')+'fillColor=#DCDFE4;fontColor=#172B4D;')
        p.meta['drawio']['native_features'].append('schedule-bars')
    ET.indent(doc,space='  ');doc.write(p.folder/'example.drawio',encoding='utf-8',xml_declaration=True)
    sc.validate_xml(doc.getroot(),CATALOG)
    sc.write(p.folder/'diagram-ir.json',p.ir);sc.write(p.folder/'resolved-ir.json',result);sc.write(p.folder/'retrieval.json',p.retrieval)
    p.meta['information_structure']=sorted(set(['containment' if p.ir['containers'] else 'attributes',*p.meta['relationships']]))
    p.meta['drawio']['libraries']=sorted({sc.exact(CATALOG,n['shape_id'])['library'] for n in p.ir['nodes'] if n.get('shape_id')})
    p.meta['source_analysis']=dict(extracted='関係・分類・配置の説明原理を採用',adaptation='固有データをコピーせず架空の予約サービス・業務へ再構成',review='参照原図の確認範囲はsources/official-assets.jsonとresearch.mdで追跡')
    sc.write(p.folder/'metadata.yaml',p.meta)
    subprocess.run(['C:/Program Files/draw.io/draw.io.exe','--export','--format','png','--page-index','1','--output',str(p.folder/'preview.png'),str(p.folder/'example.drawio')],check=True,capture_output=True,timeout=90)
    subprocess.run(['C:/Program Files/draw.io/draw.io.exe','--export','--format','svg','--page-index','1','--output',str(p.folder/'preview.svg'),str(p.folder/'example.drawio')],check=True,capture_output=True,timeout=90)
    p.meta['artifact_hash']=digest(p.folder/'example.drawio');p.meta['preview_hash']=digest(p.folder/'preview.png');sc.write(p.folder/'metadata.yaml',p.meta)
    (p.folder/'README.md').write_text(f"# {p.title}\n\n{p.meta['purpose']}。\n\n[編集する](example.drawio) · [SVG](preview.svg) · [IR](diagram-ir.json) · [選択した図形](retrieval.json)\n\n![{p.title}](preview.png)\n\n使う場合: {p.meta['when_to_use'][0]}。\n\n使わない場合: {'、'.join(p.meta['when_not_to_use'])}。\n\n出典: {', '.join(p.meta['source_refs'])}（[URL一覧](../../sources/urls.md)）。配置を固定コピーせず、対象数・条件・粒度を入力から再計算する。\n",encoding='utf-8',newline='\n')
    print(json.dumps(dict(id=p.id,title=p.title,preview=str(p.folder/'preview.png'),status='awaiting_visual_review'),ensure_ascii=False))


def accept(identifier, findings):
    folder=BASE/'examples'/identifier;meta=sc.read(folder/'metadata.yaml')
    if not findings.strip():raise ValueError('Record actual visual and meaning findings')
    if digest(folder/'example.drawio')!=meta['artifact_hash'] or digest(folder/'preview.png')!=meta['preview_hash']:raise ValueError('Changed artifact needs render and review')
    meta['quality']=dict(status='accepted',reviewed_at=datetime.now(timezone.utc).isoformat(),findings=findings,scores=None,
        review_scope='個別PNGの表示で、文字・線・配置・意味を確認。規格全体の準拠を保証する検査ではない')
    sc.write(folder/'metadata.yaml',meta)
    print('Accepted '+identifier)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    b=sub.add_parser('build');b.add_argument('id');b.add_argument('--rebuild',action='store_true',help='Rebuild one previously reviewed example; review becomes pending')
    a=sub.add_parser('accept');a.add_argument('id');a.add_argument('--findings',required=True)
    args=parser.parse_args()
    if args.action=='build':build(args.id,args.rebuild)
    else:accept(args.id,args.findings)
