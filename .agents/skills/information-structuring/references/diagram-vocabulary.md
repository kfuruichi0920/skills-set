# 図解ボキャブラリーから説明パターンを選ぶ

新規Draw.io図の型を選ぶときに読む。Diagram Vocabularyは「何を、どの関係と配置で説明するか」を選ぶ資料であり、Shape Catalogはその構成を描く部品の実IDを選ぶ資料である。テーマの配色だけを変えて説明パターンが増えたとは扱わない。

## 選択手順

1. 説明目的、読み手、入力にある対象・関係・条件、最初に理解すべき点を整理する。
2. [検索ツール](../scripts/diagram_vocabulary.py)でCoreの候補を取得する。高速は原則Top-3、精密はTop-5。目的、分野、読者、意味構造、図の型、構成、視覚パターン、関係、密度、説明場面を検索に使える。全件をプロンプトへ投入しない。
3. 候補の`when_to_use`と`when_not_to_use`を入力と照合する。採用候補のmetadataを読み、構成が不明な場合に実表示プレビューを確認する。高速では用途が合う候補を確定し、不要な候補の展開を続けない。合わなければCore指定を外す。一覧外・複合構成も候補に含める。
4. 主案と代替案の理由を記録する。`variant_of`がある例は派生元と比べ、共通構造と追加条件を分ける。得点は語彙一致の順位であり、適合の確率や品質評価ではない。各検索項目は順位付けの補助であり、厳密なフィルターではない。
5. 入力の情報IDを領域・ノード・関係・注釈へ割り当てる。サンプルの固有データを転用せず、対象数・粒度・所属・条件・文字量・密度から配置を再計算する。線が表す意味を決めてから接続点と経路を設計する。
6. [ネイティブ機能](drawio-native.md)で実在する図形を選び、テーマを意味役割へ適用する。IRから制作し、[実行モード](execution-modes.md)の範囲で検査する。

採用ID、Top-K候補と一致した項目、派生元、見送り理由、変更した構成、入力IDと出力要素、図ファイル・ページを整理根拠へ残す。参照URLの確認状況や原図の観測と、独自に再構成した部分を区別する。

## 検索例

リポジトリルートで実行する。

```powershell
python -X utf8 .agents/skills/information-structuring/scripts/diagram_vocabulary.py "工程と担当" --mode fast --core-only
python -X utf8 .agents/skills/information-structuring/scripts/diagram_vocabulary.py "複数チームの工程と担当" --mode precise --domain project-management --composition-pattern phase-team-grid
python -X utf8 .agents/skills/information-structuring/scripts/diagram_vocabulary.py "要求と応答の順序" --diagram-type sequence-lifelines --limit 3
```

カタログは[diagram-vocabulary.json](drawio/diagram-vocabulary.json)。Schemaは[diagram-vocabulary.schema.json](drawio/diagram-vocabulary.schema.json)。初期版は75例、Core30例、明示した派生8例である。IDは説明例を識別し、75種類の互いに独立した形式を意味しない。

## 実例とライブラリ

[サンプル正本](../../../../sample/information-structuring/diagram-vocabulary/README.md)には各例のDraw.io、PNG・SVG、metadata、入力・解決済みIR、出所、採否条件、点検記録がある。[ギャラリー](../../../../sample/information-structuring/diagram-vocabulary/gallery.html)で実表示を比較できる。PlantUMLの内部は単一のSVGとして保持し、正本の`.puml`を変更する。原図への説明追加では原図保持と注釈の分離を優先する。

Custom Libraryには再利用する部分構造10件、Template Libraryには図全体75件を収録する。前者を挿入する際はセルIDと参照先を同時に付け替える。後者も入力に合わせて配置を変更する。利用環境への自動インストールは行わず、サンプル正本の設定手順を使う。

通常の整理では同梱の分析情報を使い、毎回外部URL全件を取得する必要はない。正式記法、製品仕様、最新のサービス名が判断を左右する場合は対象の一次資料を確認する。スキル単体を移動するときは、利用するサンプル・カタログ・生成用スクリプトも必要に応じて保持する。既存outputを検索して不足するサンプルを補わない。

## 追加・修正の完了条件

参照元を確認し、意味構造と配置を抽出して独自の入力へ適応する。一件ずつ制作 → PNG・SVG書出し → 画像で意味と配置を点検 → 問題修正 → 採用を記録してから次へ進む。生成しただけの例を検索候補へ登録しない。修正した例は採用状態を解除し、再書出し・再点検する。

サンプル・原図・IR・生成コード・metadata・検索カタログ・ライブラリ・一覧を同じ変更で同期する。出所の版と取得状況、確認範囲、利用条件を記録する。原図に存在しない意味や、未確認のページを観測済みと扱わない。
