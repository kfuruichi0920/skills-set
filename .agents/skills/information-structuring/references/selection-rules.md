# 整理軸・表現・手法の選択ルール

意味を判定してから表現を選ぶ。キーワードだけで一つの手法に確定せず、入力にある対象・関係・条件と、読者が知りたいことを照合する。16分類の詳細手法候補はframework.mdに収録する。

## 優先して解く問題

1. 同義語や同名異義が整理を妨げるなら、概念整理を先に行う。
2. 条件・例外・出所が不足しているなら、未確定として表示し、確定図へ補完しない。
3. 複数の意味が混在するなら、ファセット分類や別ビューで分ける。
4. 原因・順位・重み・責任・検証対応を確定するための根拠がないなら、一覧や候補表として保持する。
5. 既存61構造に適合しないなら、基本表現、専門手法、独自構成から追加候補を作る。

## 観測から候補を作る

| 整理目的・入力の特徴 | 整理軸 | 基本表現と専門手法の候補 | 採用条件・代替 |
| --- | --- | --- | --- |
| 定義、同義語、上位下位概念が混在 | identity・category・hierarchy・relation | 用語table、概念graph、Taxonomy、Ontology、SKOS | 同じ語を同一対象と断定しない。定義がなければ文脈別の候補表 |
| 雑多な断片、複数のまとまり | category・confidence | list、Affinity Diagram、KJ法、タグ、ファセットmatrix | 分類基準を明示し、重複と未分類を許す。Cluster Analysisには特徴量と尺度が必要 |
| 全体から部分、上位から下位 | hierarchy・part_whole | tree、WBS、PBS、機能分解 | 何を分解するか明示。複数親ならgraphを併用 |
| 複数対象と共通観点 | category・quantity | table、matrix、2×2、Benchmark、map | 尺度を揃える。数値がなければカテゴリ比較 |
| 多対多、相互依存、インターフェース | relation・dependency | graph、DSM、N²、Interface Matrix、CRUD Matrix | 関係種別・方向が必要。密な関係はmatrix、経路を追うならgraph |
| 先行後続、メッセージ、日程 | sequence・time・dependency | sequence、Sequence Diagram、timeline、Gantt、PERT/CPM | 時刻がなくても順序図は可。日程・クリティカルパスには期間・依存が必要 |
| 入力、活動、出力、役割、分岐 | relation・sequence・responsibility | flow、Swimlane、SIPOC、BPMN、DFD | 手続とデータの流れを区別し、分岐条件を保持する |
| 現状態、イベント、条件、次状態 | state・event | state_model、状態遷移table、ECA、Decision Table | 現状態・イベント・条件・動作・次状態を別項目に。不足は未確定 |
| 原因候補、結果、フィードバック | cause・dependency・evidence・confidence | causal graph、Fishbone、5 Why、因果loop、argument | 相関や仮説を確定因果にしない。DAGは循環がない場合のみ |
| 故障、失敗、危険、脅威、影響 | risk・cause・state | Risk Register、FMEA/FTA、Bow-Tie、Threat Model、Safety Case | 初期整理は失敗と影響のtableでもよい。頻度・重大度・対策効果の未根拠採点を避ける |
| 必要性、要求、設計、テストの対応 | purpose・trace・evidence | RTM、Trace Graph、QFD、V-model | 要求・設計・検証IDと関係が必要。名称が似ているだけで対応を生成しない |
| 選択肢、基準、トレードオフ | purpose・evidence・quantity・risk | Decision Matrix、Pugh、AHP、MCDA、QOC、ADR | 情報整理と決定を分ける。重み・比較値がなければ定性比較と未決事項 |
| 人、役割、仕事、責任 | responsibility・hierarchy | RACI、OBS、Stakeholder Map、責任matrix | 責任種別は根拠が必要。未割当を勝手に埋めない |
| 実測値、目標、実績、差、傾向 | quantity・time・confidence | chart、KPI、Dashboard、SPC、EVM | 単位と期間を確認。SPC・EVMは必要な基準データと計算前提がある場合 |
| 目的、成果、能力、施策、成果物 | purpose・dependency・trace | Goal Tree、Impact Map、Theory of Change、Strategy Map | 期待成果への接続は仮説か根拠付きかを区別 |
| 問い、主張、根拠、反論、留保 | evidence・confidence・purpose | argument、IBIS、Toulmin、Claim–Evidence–Reasoning | 説明レイヤとして採用し、情報モデルの対応を保つ |

## 専門手法の扱い

専門手法を選ぶ理由は「名称が有名だから」ではなく、その方法固有の問い・関係・判定条件が必要だからとする。例えば、RACIは仕事と責任種別、FMEAは失敗と影響、RTMは要求と実現・検証対応を追加する。

形が似ている一般図と正式な専門記法を区別する。簡略化したものは「概略」「整理用」と表示する。正式記法、規格準拠、確率・統計計算、最適化を要求された場合は、版・資料・必要データを確認してから実行する。

規格体系の例として、PMにはISO 21502、システムライフサイクルにはISO/IEC/IEEE 15288、システムモデルにはSysML、EAにはTOGAF/ArchiMate、概念体系にはSKOS/ISO 704がある。ここでは対象版や最新性を固定せず、選択時の分野を示す情報として扱う。ユーザー文中の未解決の引用マーカーを検証済み出典として転記しない。

## 複合表現の選択

入力に複数の重要関係がある場合は、主となる表現に補助ビューを付ける。

| 見たいこと | 主表現 | 補助表現 | 接続 |
| --- | --- | --- | --- |
| 構成依存と条件による継続可否 | dependency graph | 状態・条件table、失敗影響table | 対象ID・関係ID |
| 要求の実現と検証範囲 | trace graph / RTM | 根拠・未対応list | 要求ID・設計ID・検証ID |
| 作業日程と責任 | timeline | RACI / 担当table | 作業ID |
| 用語と構成の対応 | 概念graph | 用語table、機能tree | 概念ID・対象ID |
| 観測結果と解釈 | quantitative chart | argument / 根拠table | 測定ID・主張ID |

一つのビューで意味が保てるなら、補助ビューを増やす必要はない。逆に、軸の異なる情報を一枚に押し込めるために条件を捨てない。スライド風キャンバスの各領域や詳細付録へ配置することは、意味構造を選んだ後に考える。
