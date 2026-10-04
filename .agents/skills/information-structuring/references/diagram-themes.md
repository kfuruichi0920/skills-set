# Draw.ioのテーマと意味記号

図の型と配置を決めた後、Draw.ioを制作するときに読む。テーマはこの文書とdiagram-themes.jsonで定義する作成用の配色・記号規則であり、Draw.ioに同名の組込みテーマがあることを前提にしない。

## 設計の分離と選択順

情報構造 → 説明したい問い → 図の型 → テーマ → 意味記号 → 配置 → 制作の順に決める。カタログの型は関係の見せ方、テーマは外観、意味記号は色・形・線と意味の対応、配置は方向・階層・位置の割当である。テーマ変更で対象ID、関係、条件、確かさを変えない。

ユーザーのテーマ指定があれば従う。指定がなければ、図の説明目的・読み手・内容を照合し、次の優先順で最初に適合するテーマを選ぶ。複数目的を持つ資料は図ごとに選べるが、テーマの違いと凡例を明示する。

1. 経営層への説明・経営判断 → T04
2. プロジェクト・日程・プロジェクトリスク・Agile → T03
3. クラウド事業者の構成 → T05
4. ネットワーク・通信・インフラ → T06
5. セキュリティ・脅威・Zero Trust → T07
6. ソフトウェア構成・コンポーネント・依存 → T02
7. MBSE・装置・論理／物理構成 → T08
8. 調査・分析・仮説・証拠 → T09
9. ブレーンストーミング・初期構想 → T10
10. その他、または判断材料不足 → T01

読者が経営層でも、図の目的が技術者向けの通信詳細の説明なら、その説明目的を基準にする。語が含まれるだけで判定せず、採用理由を根拠資料へ残す。

## テーマ一覧と配色

配色の正本は[diagram-themes.json](diagram-themes.json)。すべてのパレット色を一つの図で使う必要はない。既存ブランドの正式なデザインシステムへの適合を意味しない。T01は技術文書、T03はプロジェクト管理の考え方を取り入れた汎用テーマとする。

### T01 — Enterprise Technical

- 用途: 技術説明・システム概要・業務構造・設計レビュー
- 表現: Neutral Gray中心、Blueのみ主対象のアクセント。高密度の技術文書向け。

```text
canvas = #FFFFFF
surface = #F4F4F4
surface-2 = #E8E8E8
border = #8D8D8D
text = #161616
text-secondary = #525252
primary = #0F62FE
primary-light = #EDF5FF
success = #24A148
warning = #F1C21B
error = #DA1E28
```

### T02 — Engineering / C4

- 用途: ソフトウェア構成・コンポーネント・依存・要求トレース
- 表現: 境界・形・関係を優先。対象は薄青、内部は白、外部は薄灰。論理境界は破線。

```text
canvas = #FFFFFF
internal = #FFFFFF
target = #E8F1FF
external = #F2F2F2
border = #666666
text = #222222
primary = #2563EB
failure = #DC2626
```

### T03 — Project Management

- 用途: 工程・日程・WBS・リスク・Issue・Agile・判断
- 表現: 予定=灰、進行=青、完了=緑、注意=黄、リスク=橙、問題=赤、判断=紫。状態が不明なら中立。

```text
neutral = #F7F8F9
border = #B3B9C4
text = #172B4D
planned = #DCDFE4
progress = #579DFF
done = #4BCE97
attention = #F5CD47
risk = #FCA700
problem = #F87168
decision = #9F8FEF
```

### T04 — Executive / Consulting

- 用途: 経営層・方針・戦略・投資判断・企画
- 表現: 白・濃紺・灰とアクセント1色。1図1主メッセージ。主張・根拠・結論の確定度を保つ。

```text
canvas = #FFFFFF
navy = #172B4D
gray = #6B7280
light-gray = #F3F4F6
accent = #2563EB
warning = #D97706
```

### T05 — Cloud Architecture

- 用途: クラウド事業者の構成・SaaS・Hybrid Cloud
- 表現: 白背景、薄灰の境界、Region/VPCを破線または薄塗りのコンテナ。サービスは可能なら公式アイコンを使い、固有色は識別に限定。

```text
canvas = #FFFFFF
boundary = #F2F2F2
border = #666666
text = #222222
primary = #2563EB
```

### T06 — Network / Infrastructure

- 用途: ネットワーク・通信・IP・VLAN・Routing・冗長構成
- 表現: 機器は標準アイコン、ネットワークはCloud、ZoneはContainer。物理=実線、論理=破線、制御=紫、データ=青、障害=赤。

```text
network = #2563EB
server = #FFFFFF
device = #F3F4F6
external = #D1D5DB
control = #7C3AED
failure = #DC2626
```

### T07 — Cybersecurity / Zero Trust

- 用途: セキュリティ・IAM・信頼境界・脅威・多層防御
- 表現: 色は製品種別ではなく信頼・リスク・制御状態。Identity=Person/ID、Policy=Hexagon、Control=Shield、Asset=Rectangle、Trust Zone=Container。

```text
trusted = #DCFCE7
controlled = #DBEAFE
unknown = #F3F4F6
warning = #FEF3C7
threat = #FEE2E2
critical = #DC2626
```

### T08 — Blueprint / System Design

- 用途: MBSE・装置・詳細設計・論理／物理構成・インターフェース
- 表現: 極薄の青灰背景、濃い青灰線。階層・境界・接続・ID・型・関係を優先。装飾的な青背景は使わない。

```text
canvas = #F8FAFC
line = #334155
primary = #1D4ED8
secondary = #64748B
highlight = #DBEAFE
```

### T09 — Research / Analysis

- 用途: 技術調査・比較分析・原因分析・仮説・証拠・論文
- 表現: 原資料=灰、分析=青、仮説=紫、根拠支持=緑、不確実=黄、反証=赤。支持・反証は入力の根拠で判定。

```text
neutral = #F8FAFC
source = #E2E8F0
analysis = #DBEAFE
hypothesis = #EDE9FE
evidence = #DCFCE7
uncertain = #FEF3C7
rejected = #FEE2E2
```

### T10 — Whiteboard / Workshop

- 用途: 発想・初期構想・問題発見・Affinity・Workshop
- 表現: 付箋を許可し、まとまりと読む順を保つ。色は問い・仮説・支持・注意など凡例の意味に対応。確定要素は意味に合う技術図形へ移す。

```text
canvas = #FAFAFA
note-yellow = #FFF3BF
note-blue = #D0EBFF
note-green = #D3F9D8
note-red = #FFE3E3
note-purple = #E5DBFF
text = #343A40
```

## 色・形・線の意味

色は意味・状態・注意に割り当てる。部品ごとの識別は形・ラベル・IDで行い、A=青、B=紫、C=緑のような意味のない色分けを行わない。基本はNeutral + Primary + 必要なSemantic 2〜3色以内。色数が増える場合は図を分けるか、ラベル・形・線で補う。主対象、状態、根拠の確かさを同じ色で同時に表す場合は混同しないよう図を分ける。

| 色系統 | 基本意味 |
| --- | --- |
| Blue | 主対象・選択・重要・Primary |
| Green | 正常・完了・許可・Success |
| Yellow | 注意・確認待ち |
| Orange | リスク・警告 |
| Red | エラー・故障・禁止 |
| Purple | 判断・特殊概念・分析上の区別 |
| Gray | 中立・外部・非活動 |
| White | 通常要素 |

テーマ固有の状態対応を使う場合はその凡例を優先する。T09の青は分析、紫は仮説であり、T03の進行中・判断と混同しない。色だけで意味を区別せず、状態名・関係名・凡例を添える。未知の状態を成功色にしない。

| 形 | 意味 |
| --- | --- |
| Rectangle | System・Component・Object |
| Rounded Rectangle | Process・Activity・Function |
| Large Rectangle | Boundary・Scope・Group |
| Cylinder | 永続データ・DB |
| Document | 文書・成果物 |
| Diamond | 判断・条件 |
| Circle | イベント・開始・終了 |
| Person | Actor・User |
| Cloud | 外部サービス・外部システム |
| Hexagon | Rule・Policy・Mechanism |
| Note | 注釈・説明 |

同じ意味は同じ形にする。T06の機器やT07の制御はRouter・Switch・Firewall・Shield等の標準アイコンを使える。T05のクラウドサービスは利用可能な公式アイコンを優先し、AWS Lambda・S3等を単なる名前なしの箱で識別しない。利用できない場合はサービス名を示した代替図形を使い、代替を明記する。アイコンや事業者固有色は識別用に限定する。

| 線 | 意味 |
| --- | --- |
| 実線矢印 | フロー・呼出し・遷移 |
| 実線・矢印なし | 構造上の関係 |
| 破線矢印 | 依存・参照 |
| 点線 | 弱い関係・任意 |
| 太い矢印 | 主フロー・主要な依存（依存は破線を保つ） |
| 双方向矢印 | 相互通信 |
| 赤い矢印 | 障害・例外 |
| 灰色の矢印 | 補助的な関係 |

T02の障害依存は赤い破線、T06の物理接続は実線、論理接続は破線、制御経路は紫、データ経路は青とする。破線を依存と論理接続の両方へ使う場合は関係名を明示する。接続線は直交を基本とし、不要な曲線と交差を避ける。ノード色と線色の意味も凡例で区別する。

## 配置と視覚階層

階層・分解・抽象から具体は上→下、時間・処理・入力から出力は左→右、Context・関係者は中心→周辺、二軸比較はMatrix、役割・組織・システムはSwimlaneを候補とする。型の採用理由と読み手の問いを優先して方向を決める。

図全体／主要領域、グループ／サブシステム／フェーズ、要素／活動の3レベルで視覚階層を設計する。図題・領域見出し・要素ラベルで区別できる。階層を満たすために入力にないグループを捏造しない。さらに詳細が必要ならOverview→Detail→Deep Detailへ分割する。

白または極薄Grayの背景、Sans-serif、左寄せ、一定の余白・整列・文字サイズを基本とする。グラデーション、影、3D、Glass、装飾背景・イラスト・Emojiは使わない。角丸はProcess等の意味がある形だけに小さく適用し、見た目でおおむね0〜8px相当、枠線1〜1.5、主経路2〜2.5を目安とする。長文は本文や注釈へ分け、意味のない図形サイズのばらつきを避ける。テーマはコンパクトな技術図として情報の理解を助けるために使う。

## Draw.io styleへの変換

[theme_styles.py](../scripts/theme_styles.py)は選択済みのテーマIDと意味役割からstyle文字列を生成する。内容の意味やテーマの選択を代行するものではない。色を適用する前に、その意味役割を根拠資料へ記す。

```powershell
python -X utf8 scripts/theme_styles.py --theme T02 --shape component --semantic primary
python -X utf8 scripts/theme_styles.py --theme T02 --shape boundary --logical-boundary
python -X utf8 scripts/theme_styles.py --theme T02 --connector dependency
```

スクリプトのパスはスキルフォルダを基準とする。styleにはfillColor・strokeColor・fontColor・strokeWidth、shape・rounded、shadow=0・glass=0・gradientColor=noneを反映する。接続はedgeStyle=orthogonalEdgeStyle、rounded=0、curved=0を使う。canvasはテーマのcanvas、未定義なら白をmxGraphModelのbackgroundへ反映する。

Draw.ioのarcSizeは通常、角の割合でありpx値ではない。スクリプトの小さいarcSizeを起点とし、表示時に角丸の大きさを確認する。形・公式アイコン・詳細レイアウトは別途指定する。テーマのパレットに意味色がない場合、スクリプトは共通の意味色を使う。採用した意味色・凡例を記録し、パレット全色の自動割当はしない。

## 根拠と品質確認

各図について、説明目的、読み手、先に理解すべき点、図の型・カタログID、テーマIDと選択理由、色・形・線の意味、配置方向、分割の要否を補足資料に残す。判断の要約と検証可能な根拠を記し、内部思考の逐語記録は出力しない。

制作後は、主対象と関係・条件が明確か、意味のない色や装飾がないか、形が揃っているか、主経路を追えるか、交差・余白・整列・文字量が適切かを点検する。コネクターの表示と修正は[配置検査](drawio-layout-check.md)に従う。凡例、ID、補足、全体と詳細の参照を確認する。テーマ変更前後で対象・関係・条件・順序が一致することを確かめる。評価は正確性・明瞭さ・一貫性・追跡可能性・情報密度・認知負荷を優先する。
