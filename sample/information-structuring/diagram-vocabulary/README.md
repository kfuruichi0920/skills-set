# Draw.io図解サンプルボキャブラリー

公開例の説明構造を調べ、架空の予約サービス・業務へ再構成した75例。ソフトウェア、システム、クラウド、ネットワーク、セキュリティ、業務、PM、分析、説明・注釈を含む。各例を一件ずつ制作してPNGで個別点検した。

- [実表示ギャラリー](gallery.html): 名前・分野・構成・テーマで検索し、Draw.ioを開く。
- [参照URL一覧](sources/urls.md): 58件。取得状況・確認範囲・利用条件は[Source Registry](sources/source-registry.yaml)。
- [調査結果](sources/research.md): 公式例の構造とライブラリ仕様、確認できなかった参照先。
- [対応一覧TSV](catalog/index.tsv): Excelへ読み込める形式。
- [選択カタログ](catalog/diagram-vocabulary.json): Core30例、明示した派生8例を含む75例。件数は独立形式の数ではない。
- [判断根拠](rationale.md): 入力記録、資料と新規例の関係、検証範囲。

`examples/DV-xxx/`ごとに`example.drawio`、`preview.png`、`preview.svg`、`metadata.yaml`、README、入力・解決済みIR、図形検索記録を保持する。metadataはJSON構文のYAMLで、通常のYAML読込みにも対応する。正式な専門記法や製品構成の完全性を保証する資料ではない。PlantUML例の内部SVGは単一オブジェクトであり、内部をDraw.io図形として編集できるとは扱わない。

## 選び方

目的と情報構造からCoreをTop-K検索し、不足したら全体へ広げる。採用候補の用途、不向きな条件、実表示、原図からの変更を確認する。Shape Catalogから部品を選ぶのは構成を選んだ後である。検索と適応の手順は[スキルの選択規則](../../../.agents/skills/information-structuring/references/diagram-vocabulary.md)。

## Draw.ioへの読込み

[Custom Library](libraries/diagram-vocabulary.xml)は部分構造10件。Draw.ioの「ファイル → ライブラリを開く → デバイス」からXMLを選ぶ。[部分構造の出所](libraries/fragment-manifest.json)を確認して使う。ID、所属、接続先を保ち、入力の要素数に合わせて再配置する。

[部分構造の実表示一覧](libraries/previews/contact-sheet.png)と[個別プレビュー対応](libraries/previews/manifest.json)で、ライブラリから展開した図を確認できる。

[Template Library](libraries/template-library.xml)は図全体75件。外部テンプレートの図・画像・ライブラリはHTTP(S)で取得可能にする必要がある。初期設定はローカル配信先`http://127.0.0.1:8765/`である。リポジトリルートで次を実行する。

```powershell
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/serve_vocabulary.py
```

Draw.ioの「その他 → 設定」で[libraries/configuration.json](libraries/configuration.json)の`customTemplates`と`defaultCustomLibraries`を既存設定に追加する。`customTemplates`は各テンプレートの属性オブジェクトの配列、`defaultCustomLibraries`は`U`とURLエンコードしたURIである。[Draw.io公式の設定仕様](https://www.drawio.com/docs/reference/configure-diagram-editor/)で形式を確認できる。設定とHTTP配信は自動で有効化されない。別ホストを使う場合は下記のpublishへ`--base-url https://ホスト/配信ルート/`を渡して再生成する。Template XML全体を使う場合は`templateFile`へURLを設定できるが、標準テンプレート一覧を置換するため用途を確認する。

同梱サーバーはサンプルのディレクトリだけをlocalhostで配信し、CORSヘッダーを付ける。オンライン版からlocalhostへアクセスする際はブラウザーの接続許可や環境の制約を確認する。今回は設定形式・配信先・XMLと画像の読込みを検査し、エディターの設定は変更していない。

## 再生成と検査

Python 3、[依存一覧](scripts/requirements.txt)、Draw.io Desktop、PlantUMLとJavaを使用する。生成コードのDraw.io実行パスはWindowsの標準インストール先である。参照取得と原図プレビューのコードも[sources/](sources/)へ保持する。

一例の修正後は次の順で行う。`accept`は画像を実際に点検した後に限る。修正した例だけを再生成し、既存outputを参照しない。

```powershell
python -m pip install -r sample/information-structuring/diagram-vocabulary/scripts/requirements.txt
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/build_examples.py build DV-067 --rebuild
# preview.pngを開き、意味・接続先・遮蔽・文字切れ・線と余白を点検する
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/build_examples.py accept DV-067 --findings "実際に確認した内容と修正結果"
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/package_vocabulary.py publish
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/package_vocabulary.py validate
python -X utf8 sample/information-structuring/diagram-vocabulary/scripts/check_delivery.py
```

`build_examples.py`は一件を制作し、直前の例が未点検なら次の新規例を拒否する。再生成は点検状態を解除する。`publish`は全件の採用記録を確認してスキル側カタログ、一覧、ギャラリー、ライブラリを同期する。`validate`はSchema、実図形ID、親子・接続参照、原図保持、画像・XMLハッシュ、数量、検索結果を検査する。`check_delivery.py`はライブラリの構造とHTTP参照を検査する。

## 出所と利用条件

Draw.io公式リポジトリの編集原図60件を固定commit `fab8af896076cecc55deea13bd60ef181fc92292`で取得した。[資産対応とハッシュ](sources/official-assets.json)、[原図の点検範囲](sources/reference-visual-review.json)を保持する。原図はApache-2.0の条件を確認し、同梱のLICENSEを保持する。Webページ全体やベンダーのロゴへ同じライセンスを一律に適用しない。

原図の点検は60件の第1ページの構成と6件の拡大表示であり、全ページ・全細字を確認したとは扱わない。参照原図の固有データは独自例へコピーしていない。専用Customer Journey原図を確認できなかった例、機能タイルを関係図へ適応した例などはmetadataに変更を記録する。参照元の分析と本例の定量検査は別の根拠である。
