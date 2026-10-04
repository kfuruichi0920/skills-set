# 情報整理の体系

framework.jsonを正本として生成した選択用の索引。16目的・19軸・12基本表現は出発点であり、入力に必要な新しい軸・手法・複合表現を追加できる。専門手法の名称は候補であり、正式な実施手順や規格への適合を保証しない。

## 選択の順序

整理目的 → 情報の意味・整理軸 → 基本表現 → 必要な専門手法 → 読み手に合う説明方法 → キャンバスと出力形式

## 基本軸

| ID | 軸 | 問い | 意味 |
| --- | --- | --- | --- |
| identity | Identity | 何か | 対象の名前・定義・同一性 |
| category | Category | 何の種類か | 同じ観点での分類・タグ |
| hierarchy | Hierarchy | 何に含まれるか | 上位と下位の包含・抽象化 |
| part_whole | Part-whole | 何から構成されるか | 全体と部分の構成関係 |
| relation | Relation | 何と関係するか | 関連・交換・対応の種類と向き |
| dependency | Dependency | 何に依存するか | 成立・動作に必要な前提 |
| sequence | Sequence | どの順序か | 先行・後続の論理順序 |
| time | Time | いつか | 時点・期間・時間尺度 |
| state | State | どの状態か | 継続する状態と状態遷移 |
| event | Event | 何が起きたか | 変化の契機・出来事 |
| cause | Cause | なぜか | 原因と結果。仮説と裏付けを区別 |
| purpose | Purpose | 何のためか | 目的・成果・達成手段 |
| responsibility | Responsibility | 誰が担うか | 人・役割・活動の割り当て |
| location | Location | どこか | 位置・境界・領域 |
| quantity | Quantity | どの程度か | 量・単位・尺度・分母 |
| risk | Risk | 何が起こり得るか | 失敗・影響・予防・対処 |
| evidence | Evidence | 根拠は何か | 主張を支える出所・観測・資料 |
| confidence | Confidence | どの程度確かか | 確実・推定・未確認とその根拠 |
| trace | Trace | どこからどこへ導出されたか | 入力・概念・要求・設計・検証・表現の対応 |

軸を修飾する情報: 条件、例外、境界、粒度、方向、単位、期間、出所、不確実性

## 基本表現

| ID | 表現 | 意味 | 注意 |
| --- | --- | --- | --- |
| list | List | 項目・要点・未分類事項を並べる | 順序や優先度の意味を明示する |
| table | Table | 対象の属性を同じ項目で並べる | 単位、空欄、不明値を区別する |
| tree | Tree | 階層や一つの切り口による分解を示す | 多対多関係を親子へ押し込めない |
| matrix | Matrix | 二つ以上の観点を交差させる | セルの意味と観点の粒度を揃える |
| graph | Graph | 多対多の関連・依存を示す | 関係の種類、向き、条件を明示する |
| sequence | Sequence | 順序と受け渡しを示す | 論理順序を実時間と混同しない |
| timeline | Timeline | 時点・期間・スケジュールを示す | 期間と依存関係を区別する |
| state_model | State Model | 状態・イベント・条件・動作・次状態を示す | 処理手順と状態遷移を区別する |
| flow | Flow | 入力・処理・出力や流れる情報を示す | 処理・データ・価値の流れを区別する |
| map | Spatial / Map | 位置・境界・領域・被覆を示す | 概念上の配置を物理距離と混同しない |
| quantitative_chart | Quantitative Chart | 数値・分布・傾向を示す | 数値・単位・比較尺度が必要 |
| argument | Argument Structure | 問い・主張・根拠・留保・判断を示す | 事実と解釈と意思決定を区別する |

## 整理目的と専門手法の候補

同じ手法が複数目的に現れるのは、複数の整理軸を持つため。目的を一つに固定する必要はない。

### 1. 意味・概念整理 (meaning)

- 問い: これは何か
- 入力の手掛かり: 同義語・同名異義・定義の混在
- 軸: identity, category, hierarchy, relation
- 基本表現: list, table, tree, graph
- 必要な情報・留保: 名称、定義、対象、用語の使用文脈

候補手法: 用語集 / Glossary、Controlled Vocabulary、Taxonomy、Thesaurus、Ontology、Faceted Classification、Topic Map、Concept Map、Semantic Network、Knowledge Graph、Entity–Relationship Model、Domain Model、Conceptual Data Model、UML Class Diagram、SKOS、ISO 704に基づく用語・概念整理

### 2. 分類・グルーピング (grouping)

- 問い: 何と何が同類か
- 入力の手掛かり: 雑多な断片、共通する観点、複数のタグ
- 軸: category, identity, confidence
- 基本表現: list, table, matrix, tree
- 必要な情報・留保: 情報単位、分類基準、例外・重複の扱い

候補手法: KJ法、Affinity Diagram、Card Sorting、MECE、Cluster Analysis、Tagging、Faceted Classification、Categorization、5W1H / 6W3H、What / Why / How分類、Fact / Opinion / Assumption分類、Must / Should / Could分類、Known / Unknown分類、Internal / External分類、Functional / Non-functional分類

### 3. 分解・階層化 (decomposition)

- 問い: 何から構成されるか
- 入力の手掛かり: 部分、上位・下位、作業・機能・物理構成
- 軸: hierarchy, part_whole, purpose
- 基本表現: tree, list, graph
- 必要な情報・留保: 分解対象、分解観点、親子関係

候補手法: WBS、OBS、CBS、RBS / Risk Breakdown Structure、Resource Breakdown Structure、PBS、System Breakdown Structure、Functional Breakdown Structure、Capability Breakdown、Logical Breakdown、Physical Breakdown、Logic Tree、Issue Tree、Why Tree、How Tree、What Tree、Goal Tree、Objective Tree、Mind Map、Outline、Hierarchical Task Analysis

### 4. 比較・位置付け (comparison)

- 問い: 何がどう違うか
- 入力の手掛かり: 複数対象と共通評価観点
- 軸: category, quantity, location
- 基本表現: table, matrix, map, quantitative_chart
- 必要な情報・留保: 対象、比較観点、共通尺度またはカテゴリ

候補手法: Comparison Table、2×2 Matrix、Multi-dimensional Matrix、Benchmark Matrix、SWOT、PESTLE、BCG Matrix、Ansoff Matrix、Feature Comparison、Architecture Comparison、Technology Radar、Maturity Model、Heat Map、Bubble Chart、Radar Chart、Positioning Map

### 5. 関係・依存整理 (relationships)

- 問い: 何と何が関係するか
- 入力の手掛かり: 多対多、依存、インターフェース、受け渡し
- 軸: relation, dependency, trace
- 基本表現: graph, matrix
- 必要な情報・留保: 関係元・先、関係種別、方向、条件

候補手法: Dependency Graph、Relationship Map、Network Diagram、Knowledge Graph、DSM / Design Structure Matrix、N² Diagram / N-Squared Chart、Dependency Matrix、Interface Matrix、CRUD Matrix、Interaction Matrix、Call Graph、Data Lineage、Dependency Map、Trace Graph、Package Dependency、Module Dependency

### 6. 時間・順序整理 (timing)

- 問い: いつ・どの順に起きるか
- 入力の手掛かり: 時点、期間、先行後続、メッセージ順序
- 軸: time, sequence, dependency, event
- 基本表現: timeline, sequence, graph
- 必要な情報・留保: 時間の有無、順序、期間、依存

候補手法: Timeline、Gantt Chart、Milestone Chart、Roadmap、Release Plan、PERT、CPM、Network Schedule、Sequence Diagram、Timing Diagram、Message Sequence Chart、Event Timeline、Project Calendar、Sprint Plan、Iteration Map

### 7. プロセス整理 (process)

- 問い: どう処理されるか
- 入力の手掛かり: 入力から活動を経て出力、分岐と受け渡し
- 軸: sequence, relation, responsibility, event
- 基本表現: flow, sequence, matrix
- 必要な情報・留保: 入力、活動、出力、役割、分岐条件

候補手法: Flowchart、BPMN、UML Activity Diagram、Swimlane、SIPOC、Value Stream Mapping、Data Flow Diagram、IDEF0、SADT、FFBD、eFFBD、Process Map、Service Blueprint、User Journey、Event Storming、Domain Storytelling、Workflow Diagram

### 8. 状態・イベント整理 (state_events)

- 問い: どの状態で何が起こるか
- 入力の手掛かり: 状態、イベント、条件、遷移、動作
- 軸: state, event, sequence
- 基本表現: state_model, matrix, table, sequence
- 必要な情報・留保: 現状態、イベント、条件、動作、次状態

候補手法: State Machine、State Transition Diagram、State Transition Table、UML State Machine、Event–State Matrix、Event–Condition–Action、Decision Table、Truth Table、Decision Tree、Petri Net、Timing Diagram、Statechart

### 9. 因果・問題分析 (causal_analysis)

- 問い: なぜ起きたか
- 入力の手掛かり: 原因仮説、影響、循環、問題の連鎖
- 軸: cause, event, dependency, evidence, confidence
- 基本表現: tree, graph, argument
- 必要な情報・留保: 出来事、原因候補、条件、証拠、反証

候補手法: 5 Why、Ishikawa / Fishbone、Cause–Effect Diagram、Root Cause Analysis、Fault Tree、Event Tree、Causal Graph、DAG、Causal Loop Diagram、Influence Diagram、Kepner–Tregoe、Barrier Analysis、Change Analysis、Current Reality Tree、Cause–Effect Graph、System Dynamics、Causal Loop、Stock & Flow、Bayesian Network

### 10. リスク・障害整理 (risk_failure)

- 問い: 何が失敗し得るか
- 入力の手掛かり: 故障、失敗、危険、脅威、サービス影響と制御
- 軸: risk, cause, state, dependency, evidence
- 基本表現: table, tree, graph, matrix, argument
- 必要な情報・留保: 対象、失敗・危険、原因、影響、条件、対策

候補手法: Risk Register、RAID Log、Risk Matrix、Risk Breakdown Structure、Risk Heatmap、Risk Burndown、Bow-Tie、FMEA、FMECA、FTA、ETA、RBD、Markov Model、Reliability Block Diagram、HAZOP、STPA、STAMP、Safety Case、GSN、Hazard Log、FRAM、Threat Model、STRIDE、Attack Tree、Attack Graph、Misuse Case、Abuse Case、PASTA、LINDDUN、Threat Matrix

### 11. 要求・トレース整理 (requirements_trace)

- 問い: なぜ必要で、何で実現・検証するか
- 入力の手掛かり: 要求、設計、実現、検証の対応
- 軸: purpose, trace, relation, evidence
- 基本表現: matrix, graph, tree, argument
- 必要な情報・留保: 要求ID、関係種別、設計・検証対象、根拠

候補手法: Requirement Hierarchy、Requirements Traceability Matrix、V-model、Verification Cross Reference Matrix、Requirement × Test Matrix、Requirement × Design Matrix、Use Case、User Story、User Story Mapping、Acceptance Criteria、Gherkin、QFD、House of Quality、KAOS、i*、GRL、Goal Model、SysML Requirement Model、Traceability Graph

### 12. 意思決定整理 (decision)

- 問い: どれを選ぶべきか
- 入力の手掛かり: 選択肢、評価基準、トレードオフ、採否
- 軸: purpose, quantity, risk, evidence, confidence
- 基本表現: matrix, table, argument, tree, quantitative_chart
- 必要な情報・留保: 問い、選択肢、基準、評価根拠、決定状況

候補手法: Decision Matrix、Weighted Scoring、AHP、ANP、MCDA、Pugh Matrix、Pairwise Comparison、Trade Study、Cost–Benefit Analysis、Decision Tree、Expected Value、Utility Analysis、Pareto Analysis、Sensitivity Analysis、Tornado Chart、Scenario Analysis、Monte Carlo Simulation、MoSCoW、WSJF、RICE、ICE、Kano、Cost of Delay、Value / Effort Matrix、ADR / Architecture Decision Record、Decision Log、Assumption Log、QOC / Questions–Options–Criteria

### 13. 責任・組織整理 (responsibility)

- 問い: 誰が何をするか
- 入力の手掛かり: 人・役割・作業・責任・連絡関係
- 軸: responsibility, hierarchy, relation
- 基本表現: matrix, tree, graph, map
- 必要な情報・留保: 役割、作業、責任種別、組織・境界

候補手法: Organization Chart、OBS、RACI、RASCI、Responsibility Assignment Matrix、Stakeholder Map、Power–Interest Grid、Stakeholder Salience Model、Onion Diagram、Communication Matrix、Team Topology Map、Skills Matrix、Resource Matrix、Capability Matrix

### 14. 定量・管理整理 (quantitative)

- 問い: 状態は良いか悪いか
- 入力の手掛かり: 値、目標、実績、差、傾向、分布
- 軸: quantity, time, purpose, confidence
- 基本表現: quantitative_chart, table, tree
- 必要な情報・留保: 測定値、単位、期間、分母、目標・基準の有無

候補手法: KPI、KGI、CSF、GQM、Balanced Scorecard、KPI Tree、Dashboard、Scorecard、EVM、S-Curve、Burndown、Burnup、Cumulative Flow Diagram、Control Chart、Run Chart、Histogram、Pareto Chart、Scatter Plot、Box Plot、Heatmap、Resource Histogram、Capacity Chart、Defect Trend、Milestone Trend Analysis

### 15. 戦略・目的整理 (strategy)

- 問い: 何のために何をするか
- 入力の手掛かり: 目的、成果、能力、施策、成果物の接続
- 軸: purpose, hierarchy, dependency, trace
- 基本表現: tree, graph, map, argument
- 必要な情報・留保: 目的、期待成果、手段、前提、対応根拠

候補手法: Vision → Mission → Goal → Objective、Goal Tree、Strategy Map、Balanced Scorecard、OKR、KPI Tree、Capability Map、Business Capability Map、Value Chain、Value Stream、Business Model Canvas、Lean Canvas、Impact Mapping、Opportunity Solution Tree、Theory of Change、Logic Model、Benefits Dependency Network、Wardley Map、Portfolio Map

### 16. 説明・論証整理 (explanation)

- 問い: どう説明すれば理解できるか
- 入力の手掛かり: 読み手の問い、主張、証拠、留保、説明順序
- 軸: evidence, confidence, purpose, trace
- 基本表現: argument, list, table, graph
- 必要な情報・留保: 読み手、目的、要点、根拠、未確定事項

候補手法: Pyramid Principle、SCQA、PREP、Toulmin Model、Argument Map、IBIS、Claim–Evidence–Reasoning、Issue–Option–Decision、QOC、Overview → Detail、Progressive Disclosure、Abstraction Ladder、Layered Architecture Explanation、C4 Zoom-in、Context → Problem → Mechanism → Consequence、Before / After、As-Is / To-Be、Why / What / How

## 既存表現との関係

既存61構造は基本表現を配置する際の参考。一覧にない方法、複合表現、独自構成を候補に含める。

標準出力は情報整理と可視化案に加え、入力→正規化→整理軸→候補比較→出力要素の対応を残す補足資料。詳しい選択規則はselection-rules.md、記録様式はrationale-template.mdを参照する。
