# Draw.ioのネイティブ機能と図形選択

新規Draw.io図の制作時に読む。図の意味・記法・所属・関係を先に決め、テーマは外観へ適用する。既存図・画面の説明追加は[注釈モード](visual-annotation.md)を使い、原図を再構成しない。

図式の候補は[図解ボキャブラリー](diagram-vocabulary.md)で検索する。Diagram Vocabularyは説明パターン、Shape Catalogは部品の実IDを選ぶ資料である。前者の採用後に後者を検索し、対象数・条件・所属・密度に合わせて配置を再設計する。

## 選択と完了条件

1. 説明したい問いから図式を決める。階層、処理、関係、時間、比較、因果、状態を区別する。
2. 入力の意味がUML・SysML・BPMN・ER・ArchiMate・EIPの記法に合うか確認する。形の類似だけでは記法を選ばない。シーケンスはPlantUMLを使う。状態・クラス・活動図もPlantUML＋SVG注釈を候補とする。正式な記法を求められた場合は対象版の一次資料と照合する。
3. 標準の意味図形 → コンテナー・Table・List → 技術・Vendorライブラリ → Custom Library → Fragment・Template → SVG → ラスター画像 → 基本図形の組合せ → 新規Custom Shapeの順に候補を調べる。図式の骨格は既存の表現カタログで、具体的な図形はShape Catalogで選ぶ。
4. [ライブラリ対応](drawio/library-registry.json)を参照して候補を絞り、検索結果だけを読む。対応表にない実ライブラリも検索できる。対応表に記載された候補がインストール版に存在するとは仮定しない。
5. 入力と候補の意味を照合し、正確な`shape_id`をIRへ確定する。検索順位は候補の推薦であり、意味の保証ではない。Aliasは検索用であり、Shape IDとして出力しない。
6. 所属・接続・配置をIRに記録し、解決済みIRを保存してXMLへ変換する。図形IDは確定時とレンダラー入口で検証する。存在しないID・未検証IDは拒否し、確認できる別候補または理由付きの基本図形へ切り替える。
7. 意味と今回のXML・接続参照を検査する。精密モードでは画像へ書き出し、[配置検査](drawio-layout-check.md)を行い、修正後に再表示する。高速モードは[実行モード](execution-modes.md)に従って詳細な表示検査を省く。

正式成果物はNative（適切な意味図形・所属・表・関係線）以上を原則とし、重要な説明図はDesigned（記法・テーマ・配置・注釈・表示と意味の検査・再利用資産）を目標とする。基本図形へのFallbackを選ぶ場合は、未対応の概念・調べた候補・採用理由・検査上の留保を補足に記す。

## 図形カタログの生成・検索

実資産の正本はDraw.ioのStencil XMLとCustom Library。インストール版の`app.asar`には圧縮Stencilが含まれるため、生成ツールはJavaScriptを実行せずデータを展開する。XMLディレクトリも再帰走査できる。既存outputは探索対象にしない。

ツールは[scripts/shape_catalog.py](../scripts/shape_catalog.py)。`--help`と各サブコマンドの`--help`で引数を確認する。以下はリポジトリルートでの例。検証には`jsonschema`を使用する。

```powershell
python -m pip install -r .agents/skills/information-structuring/scripts/requirements-native.txt
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py generate --builtin "C:/Program Files/draw.io/resources/app.asar" --custom .agents/skills/information-structuring/assets/libraries
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py validate
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py search データベース --library flowchart --semantic database
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py search lambda --domain cloud_aws --vendor aws --limit 5
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py render diagram-ir.json result.drawio --resolved-ir resolved-ir.json
python -X utf8 .agents/skills/information-structuring/scripts/shape_catalog.py validate-xml result.drawio
```

保存先・今回作成したファイルの参照範囲・スクリプトの保持は[制作規則](production.md)に従う。呼出時はカタログ・設定・スクリプト・依存一覧・IRを案件の実行フォルダーに保持する。サンプルは[指定保存先](../../../../sample/information-structuring/README.md)へ保存する。

カタログ全件をプロンプトへ投入しない。検索は名称、正規名、Alias、日本語Alias、タグ、意味カテゴリ、ライブラリ、Vendorを対象とする。意味一致 → 推奨ライブラリ → ドメイン → Vendor → 完全名・Alias → 部分一致の順で候補を順位付けする。`--library`は絞込み、`--prefer-library`は順位付けである。一般概念の検索では特定Vendorやサービスを安易に確定しない。

## 正本・更新・出所

- [raw](drawio/shape-catalog.raw.json): 実資産から機械抽出した名称・ID・幅高さ・接続点・出所・SHA256。
- [編集メタデータ](drawio/shape-metadata.json): 日本語Alias、意味カテゴリ、Vendor、推奨用途を付与する正本。ID・出所・verifiedを変更しない。
- [解決済みカタログ](drawio/shape-catalog.json): rawと編集情報の結合結果。LLMは検索を通じて取得する。
- [Schema](drawio/shape-catalog.schema.json)と[Library Catalog](drawio/library-catalog.json): 生成結果の型とライブラリ構成。

Draw.io更新時は旧カタログをoutput外の指定ファイルへ保存し、`generate --previous 旧カタログ --destination 指定先`で差分を作る。追加・削除・定義変更・メタデータ変更・ライブラリ追加削除を確認する。改名・名前空間変更は削除＋追加として出るため、名称と出所で照合する。削除IDを参照するIR・XML・部品を検査し、確認した候補へ移行してサンプルを再生成する。生成時刻、Draw.io版、実資産ハッシュで版を追跡する。

生成ツールは登録規則をDraw.io本体に合わせ、名前の空白を`_`へ置換して小文字化する。同じXML内の重複定義は本体と同じく末尾を採用し、その事実を記録する。別資産間の衝突は拒否する。Schema検査に加え、重複ID・正規キー・所属ライブラリ・編集情報の参照先・XMLのIDと接続先を検証する。

## 所属・表・関係線・外部資産

包含関係は`parent`でコンテナーに所属させ、子座標を親からの相対座標にする。背景矩形との位置の重なりだけで所属を表さない。システム、環境、組織、フェーズ、責任レーンを境界の候補とする。

小さい比較表・責任表・一覧はTable／TableRow／セルの親子構造を使う。Listは項目の意味が同種であり、一覧としての編集が必要な場合に選ぶ。行数・列数が多いマトリクスの全量はTSV／CSVとし、Draw.ioには要点だけを置く。

線はflow、dependency、reference、association、bidirectional、annotationをIRで区別する。包含は線でなく親子関係で表す。記法が線の意味を定める場合はその定義を優先する。ポート・接続点・Waypointを指定し、無関係のノードの横断・ラベル衝突・曖昧な接続先を解消する。

Vendor図形は入力がVendorとサービスを特定している場合に使う。AWS上のDBという記述だけでRDSを確定しない。公式サービス図形の輪郭や識別色をテーマで置換しない。テーマは背景・境界・見出し・注釈・線・文字・余白へ適用する。

Custom Libraryは`mxlibrary`内のJSON配列を読み、XML・SVG・画像・Group・Fragment・Templateを標準Stencilと別名前空間で保持する。XMLは圧縮・非圧縮に対応する。Fragment／Templateは元セルの階層・接続を保持し、挿入時にIDと参照を同時に付け替える。原寸の部品を使い、拡縮が必要なら子座標・接続点・文字を含めて再配置する。外部URL画像は持ち運べる埋込み画像にしてから登録する。

IRには目的・読者・図式・テーマ、ノードの意味・query・確定ID・採用理由、コンテナー所属、表、線の種類、接続先、座標・Waypointを保存する。外部PlantUML／SVG／画面は[注釈IR](visual-annotation.md)へ分離する。原図を意味図形へ置換しない。新規図生成IRと注釈IRは役割を混同しない。

## 検査の根拠

表示検査で、文字切れ・線交差・ノード横断・余白不足・接続先の曖昧さ・領域はみ出しを確認する。意味検査では、DBとStorage、依存とデータ流、BPMN Gatewayと装飾図形、一般概念と特定サービスを区別する。構文検査の合格を記法準拠・表示品質の保証と報告しない。

原図・検索候補・確定ID・カタログ版・採否理由・Fallback・検査した画像・修正内容を補足資料に残す。入力原文と入力時刻は[根拠テンプレート](../assets/rationale-template.md)に従う。

一次資料: [Stencil作成](https://www.drawio.com/docs/tutorials/custom-shapes/)、[Custom Library形式](https://www.drawio.com/docs/reference/format-custom-shape-library/)、[プログラム生成のスタイル](https://www.drawio.com/docs/reference/diagram-generation/style-reference/)。実装時はインストール版の資産・登録処理も照合する。
