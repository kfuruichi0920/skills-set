"""Fetch pinned editable references; no remote image downloads. Python 3.12 stdlib."""
from pathlib import Path
import urllib.request,urllib.error,json,re,hashlib,concurrent.futures,xml.etree.ElementTree as ET,base64,zlib,urllib.parse
ROOT=Path(__file__).resolve().parent
SHA="fab8af896076cecc55deea13bd60ef181fc92292"
DATE="2026-10-04"
ASSETS=[
("blog/C4.drawio",[10,45],"system-context / container / component / class","抽象度ごとに複数ページを分離し、対象境界と外部依存を示す"),
("examples/uml-class-example.drawio",[12],"class","クラスの名前・属性・操作を区画で分離し関連で結ぶ"),
("examples/uml-component-example.drawio",[13],"component","部品の提供・要求インターフェースを接続する"),
("examples/uml-deployment-example.drawio",[11],"deployment","実行環境の境界に配備物を配置する"),
("examples/uml-activity-example.drawio",[11],"activity","開始・判断・分岐・終了を区別する"),
("examples/uml-package-example.drawio",[11],"package","パッケージ包含と依存線を区別する"),
("examples/uml-use-case-example.drawio",[11],"use-case","利用者とシステム境界内の機能を関連づける"),
("examples/sequence-diagram-examples.drawio",[11],"sequence","参加者の横配置とメッセージの縦順序を分離する"),
("blog/uml-state-diagram-smart-lock.drawio",[14],"state-machine","状態ノードとイベント・条件付き遷移を結ぶ"),
("blog/data-flow.drawio",[17],"data-flow","外部主体・処理・保存先・データ名を区別する"),
("blog/er-diagram-library.drawio",[18],"entity-relationship","行を持つ実体テーブルを多重度付き関係で結ぶ"),
("blog/requirements-flow.drawio",[19],"requirements-flow / interface","要求・画面・データの異種要素を関連で束ねる"),
("examples/sysml-requirements-diagram.drawio",[15],"requirements","要求IDと要求内容を分け、導出・充足関係を識別する"),
("examples/sysml-block-definition-diagram.drawio",[15],"system-breakdown","ブロック構成と型の関係を階層的に表す"),
("templates/network/topology_1.xml",[20],"network-topology","中心の接続装置から機器へ枝分かれする"),
("templates/network/lan_1.xml",[20],"logical-network","LANの領域・機器・接続を分離する"),
("examples/bus-topology-example.drawio",[20],"physical-network","共通バスと機器への接続点を表す"),
("examples/aws-simple-architecture.drawio",[21],"aws / cloud","サービス識別図形とリージョン境界でクラウド構成を示す"),
("blog/azure-architecture-example.drawio",[50],"azure","サービスと領域を階層化し、通信経路を結ぶ"),
("templates/gcp/internet_of_things_sensor_stream_ingest_and_processing.xml",[20,44],"gcp","センサーから収集・処理・保存の流れを段階化する"),
("templates/gcp/dev_test_jenkins_in_k8s.xml",[20,46],"kubernetes","コンテナー処理と外部開発サービスの境界を分ける"),
("templates/gcp/backup_and_archive_disaster_recovery_with_application_replication.xml",[20,44],"ha / multi-region","主系と複製先を並列領域で分ける"),
("examples/rack-diagram-simple-server.drawio",[52],"rack","ラックの物理位置を縦方向のスロットで表す"),
("blog/threat-modelling.drawio",[33],"trust-boundary / threat-model","データ経路と信頼境界を重ねて脅威の位置を示す"),
("templates/basic/flowchart.xml",[1],"basic-flow","処理矩形と判断菱形の区別で分岐を示す"),
("templates/basic/swimlanes.xml",[54],"swimlane","処理順序に担当レーンを重ねる"),
("templates/flowcharts/cross_functional_flowchart_1.xml",[27],"cross-functional","工程と担当の交差で引継ぎを可視化する"),
("examples/bpmn-example.drawio",[16],"bpmn","イベント・タスク・ゲートウェイの専用記法を使う"),
("blog/website-roles-products.drawio",[28],"roles-responsibility","役割と担当領域の対応を分けて示す"),
("templates/basic/orgchart.xml",[29],"organisation","親子の責任系統を上から下へ分岐する"),
("examples/business-model-canvas-table.drawio",[1],"business-model","複数の事業観点を区画化したキャンバスに配置する"),
("blog/story-map.drawio",[53],"story-map / customer-activities","ユーザー行動の横順序と優先度の縦構造を分ける"),
("examples/timeline-example.drawio",[26],"roadmap / milestone","時間軸上に節目と説明を配置する"),
("examples/timeline-infographic-shapes-vertical.drawio",[26],"vertical-timeline","縦の時間軸と左右の説明を対応づける"),
("examples/gantt-table.drawio",[24],"gantt","タスク行と日程列に期間バーを重ねる"),
("templates/business/pert_1.xml",[23],"pert","作業の前後関係と分岐・合流をネットワークで示す"),
("examples/gemfile-dependency-graph.drawio",[23],"dependency","複数の依存先を有向グラフとして配置する"),
("examples/kanban-examples.drawio",[25],"kanban","状態列と作業カードで滞留を示す"),
("blog/project-phase-timeline.drawio",[26],"phase-team","工程期間と担当を同じ時間軸で比較する"),
("templates/charts/work_breakdown_structure.xml",[56],"work-breakdown","成果物や仕事を階層分解する"),
("blog/probability-tree.drawio",[34],"risk / decision-tree","条件分岐を枝の経路として明示する"),
("templates/business/ansoff_matrix.xml",[31],"2x2","独立する二軸を四象限に交差させる"),
("examples/SWOT.xml",[31],"swot","内外と正負の観点を四区画に整理する"),
("examples/pestel-analysis.drawio",[31],"pestel","六つの外部環境要因を独立領域として配置する"),
("examples/5c-marketing-analysis.drawio",[31],"5c","市場の五観点を比較できるまとまりへ配置する"),
("examples/ishikawa-fishbone-examples.drawio",[30],"fishbone","結果へ向かう主軸に原因分類を枝として付加する"),
("templates/engineering/fault_tree_1.xml",[34],"cause-effect / fault-tree","望ましくない事象を論理条件へ分解する"),
("templates/education/compare_diagram.xml",[35],"comparison / before-after","同じ基準の左右配置で差異を示す"),
("templates/other/decision_tree_1.xml",[34],"decision-tree","判断と選択枝を階層化する"),
("blog/concept-maps.drawio",[32],"concept-map","概念同士を関係ラベル付きで接続する"),
("examples/VennDiagram.xml",[55],"venn","集合領域の重なりで共通部分を示す"),
("blog/sankey-diagrams.drawio",[36],"sankey","流れの量を幅で符号化する"),
("blog/infographic-shape-library-layers.drawio",[37],"layered-infographic","層と外周説明の対応を揃える"),
("examples/infographic-project-steps.drawio",[37],"process-steps / numbered-flow","繰返し形状の配置で工程の順番を示す"),
("templates/other/callouts_1.xml",[37],"callout","対象と図外説明を引出線で対応づける"),
("blog/diagram-integrations.drawio",[1],"feature-overview","中心概念の周囲に関連機能を配置する"),
("blog/board-visual-tutorial.drawio",[4],"annotated-screenshot","画面領域と外周の説明を対応づける"),
("blog/layers-how-they-work.drawio",[38],"interactive-layers","重ねる説明要素をレイヤー単位で管理する"),
("templates/other/cycle_1.xml",[51],"circular-process","繰返しの終端を次周期の先頭へ戻す"),
("blog/gitflow-examples.drawio",[22],"gitflow","並行する枝と合流を時間順序で示す")]
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'ReferenceResearch/1.0'})
 with urllib.request.urlopen(req,timeout=30) as r:return r.read(),r.status,r.url

def main():
 target=ROOT/'official-examples';target.mkdir(exist_ok=True)
 lic,_,_=get(f'https://raw.githubusercontent.com/jgraph/drawio-diagrams/{SHA}/LICENSE')
 (target/'LICENSE').write_bytes(lic)
 def fetch(item):
  path,refs,patterns,observation=item
  url=f'https://raw.githubusercontent.com/jgraph/drawio-diagrams/{SHA}/{path}'
  data,status,final=get(url); out=target/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  root=ET.fromstring(data); pages=root.findall('diagram') if root.tag=='mxfile' else [root]
  stats=[]
  for pg in pages:
   model=pg.find('mxGraphModel')
   if model is None:
    if pg.tag=='mxGraphModel':model=pg
    elif pg.text and pg.text.strip():
     try:model=ET.fromstring(urllib.parse.unquote(zlib.decompress(base64.b64decode(pg.text),-15).decode()))
     except Exception:pass
   stats.append({'name':pg.get('name','Page-1'),'vertices':sum(c.get('vertex')=='1' for c in model.iter('mxCell')) if model is not None else None,'edges':sum(c.get('edge')=='1' for c in model.iter('mxCell')) if model is not None else None})
  return {'id':'REF-'+str(ASSETS.index(item)+1).zfill(3),'source_refs':['SRC-'+str(n).zfill(3) for n in refs]+['SRC-002'],'repository_path':path,'url':url,'original_url':'https://github.com/jgraph/drawio-diagrams/blob/dev/'+path,'local_path':'official-examples/'+path,'repository_commit':SHA,'sha256':hashlib.sha256(data).hexdigest(),'http_status':status,'verified_at':DATE,'license':'Apache-2.0','license_verified':True,'license_scope':'Repository LICENSE at pinned commit; embedded third-party names/icons may carry separate trademark or use conditions.','page_count':len(pages),'pages':stats,'patterns':patterns.split(' / '),'analysis':observation,'analysis_basis':'official documentation + editable XML; image review separately recorded','visual_review':'pending'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:assets=list(pool.map(fetch,ASSETS))
 review_file=ROOT/'reference-visual-review.json'
 if review_file.exists():
  reviews={x['asset_id']:x for x in json.loads(review_file.read_text(encoding='utf-8'))['reviews']}
  for asset in assets:
   if asset['id'] in reviews:
    asset['analysis']=reviews[asset['id']]['analysis'];asset['visual_review']=reviews[asset['id']]['visual_review']
 (ROOT/'official-assets.json').write_text(json.dumps({'repository_commit':SHA,'license_file':'official-examples/LICENSE','assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Fetched',len(assets),'editable assets')
if __name__=='__main__':main()
