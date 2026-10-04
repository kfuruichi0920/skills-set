# 図解ボキャブラリーの参照調査

調査日: 2026-10-04（Asia/Tokyo）。URLの正本は `source-registry.yaml`（JSON構文のYAML）で、同内容のJSONとコピー用 `url-list.tsv` を添える。原文にあるSRC-001〜049を維持し、不足する公式ページをSRC-050〜057として追加した。

2026-10-05に[エディター設定仕様](https://www.drawio.com/docs/reference/configure-diagram-editor/)をSRC-058として追加確認した。`customTemplates`はXMLのURL配列でなくテンプレート属性オブジェクトの配列、`defaultCustomLibraries`は`U`付きURLエンコードURIである。初回調査57件と合わせたレジストリは58件。Template XMLとエディター追加設定の形式を区別して生成する。

## 取得と利用条件

[公式の実例一覧](https://www.drawio.com/docs/diagram-types/)は、図の閲覧・編集・原図ダウンロードを案内する。原図は[jgraph/drawio-diagrams](https://github.com/jgraph/drawio-diagrams)の60ファイルを取得した。固定コミットは `fab8af896076cecc55deea13bd60ef181fc92292`。各ファイルの取得URL、SHA256、ページ数、構成要素数、対応SRC、抽出した構成パターンは `official-assets.json` に残す。原図は `official-examples/` に保存した。[固定コミットのLICENSE](https://raw.githubusercontent.com/jgraph/drawio-diagrams/fab8af896076cecc55deea13bd60ef181fc92292/LICENSE)を同梱している。

Apache-2.0の確認対象は、取得したリポジトリ資産である。掲載先の文書全体や、組み込まれた第三者商標・アイコンまで一律の再利用許可と解釈しない。ベンダー・標準団体のページは構造分析に使い、図や文章を複製しない。新規サンプルでは架空の内容、独自のノード・配置・説明を用いる。

57URLへWebツールでアクセスした。56URLは結果を取得できたが、SRC-043 Azure Galleryは本文抽出0行の動的ページ、SRC-049旧OWASP PDFは取得失敗である。OWASPの現在の[Threat Modeling](https://community.owasp.org/Threat_Modeling)を代替SRC-057として追加した。HTTPステータスはWebツールに表示されないため、URLレジストリではnullとし、実際の取得状況をstatusへ記録する。公式ページへの直接urllibアクセスは403だったが、Web経由では本文を取得できた。原図はraw GitHubからHTTP200で取得した。ページ取得と原図ライセンス確認と画像点検を区別する。

## 構成から抽出する知識

- [C4](https://www.drawio.com/docs/diagram-types/c4-modelling/)では、システム全体・実行単位・内部部品の抽象度を分ける。境界と外部要素を識別し、関係に説明を付ける。C4のContainerは実行またはデータ保存するソフトウェア単位であり、単なるDraw.io囲み図形と同義にしない。
- [スイムレーン](https://www.drawio.com/docs/diagram-types/swimlane-diagrams/)では、処理順序に責任軸を重ねる。所有者が変わる接続を引継ぎとして読める配置にする。[Story mapping](https://www.drawio.com/docs/diagram-types/story-mapping/)は顧客の行動と優先順位を整理する。技術実装を同じ粒度で詰め込まない。
- [Azure](https://www.drawio.com/docs/diagram-types/azure-diagrams/)では概要から論理ブロックへ分割し、リージョン等の領域を背景境界として配置する。[ネットワーク](https://www.drawio.com/docs/diagram-types/network-diagrams/)では位置・アクセス境界・サブネットなどの分類目的を選び、接続が通信経路であることを示す。GCPは同ページのGoogle Cloud Platform節とSRC-044を参照する。実装詳細と概要を混ぜない。
- [BPMN](https://www.drawio.com/docs/diagram-types/bpmn-2-0/)のイベント・タスク・ゲートウェイと、通常フローの処理・判断を区別する。[UML](https://www.drawio.com/docs/diagram-types/uml/)各種も、クラス区画、配備境界、状態遷移などの意味を保つ。正式記法を省略したサンプルは概略であると明記する。
- [脅威モデル](https://www.drawio.com/docs/diagram-types/threat-modelling/)ではDFD、処理フロー、攻撃木など説明目的に応じた異なる図を使う。信頼境界と通常の所属境界を混同しない。[NIST Zero Trust](https://www.nist.gov/publications/zero-trust-architecture)および[実装参照](https://pages.nist.gov/zero-trust-architecture/VolumeB/architecture.html)は制御と通信の論理関係を確認する参照先とする。既存企業の製品構成は再現しない。
- [時間軸](https://www.drawio.com/docs/diagram-types/timeline-diagrams/)は節目・期間・工程×担当を別パターンにする。[PERT/依存](https://www.drawio.com/docs/diagram-types/dependency-graphs/)は時間の幅ではなく前後依存を示す。形が似ていても時間と順序を同一視しない。
- [Sankey](https://www.drawio.com/docs/diagram-types/sankey-diagrams/)は流量を幅に対応させる。公式ページは概略図と数値精度が必要な図を区別している。架空サンプルでも保存量、分岐量、幅の整合を検査する。
- [層状インフォグラフィック](https://www.drawio.com/docs/tutorials/infographics-layered-shapes/)からは層の対応と外周Calloutを抽出する。装飾的な3Dや多色は必須ではなく、現在のテーマ規則に合わせて平面化できる。[対話レイヤー](https://www.drawio.com/docs/tutorials/interactive-diagram-layers/)は表示を分ける構成として扱い、情報の意味と外観のテーマを分離する。

以上は説明パターン抽出の判断であり、規格全体への準拠認証ではない。各原図の個別分析は `official-assets.json` のanalysisへ記録した。

## Custom Libraryの正しい形式

[公式Custom Shape Library形式](https://www.drawio.com/docs/reference/format-custom-shape-library/)を確認した。ルートは `<mxlibrary>`。本文はJSON配列で、各項目に `w`、`h` と `xml`または`data`を持たせる。`xml`は`mxGraphModel`の図・グループ・部品を保持できる。`title`は表示名、`tags`は**空白区切り**である。圧縮しないXMLはJSONエスケープに加えてXML本文のエスケープを行う。JSONを作った後、XMLライブラリとしてシリアライズすれば両層のエスケープを管理できる。

Fragmentは一部構成の実Cellを保持する。Templateは図全体の構成である。Custom Libraryへ全体図を入れられるとしても、ボキャブラリーではこの二つの役割を別Metadataとして保つ。

## Template Libraryの正しい形式

[公式Template Library形式](https://www.drawio.com/docs/reference/format-template-library/)を確認した。ルートは `<templates>`。`<template>`に必須の `section`、`url`、`title`を持たせる。任意属性は `subsection`、`name`、`preview`、`libs`、`clibs`、`tags`。**説明は`description`属性でなく`name`属性**へ対応付ける。`libs`と`tags`は**セミコロン区切り**である。外部テンプレートには`preview`を明示する。

`<clibs name="...">`に`<add>`でカスタムライブラリの参照を定義し、テンプレートの`clibs`と対応付ける。設定の`templateFile`は全カタログを置換し、`customTemplates`は追加する。XML宣言が必要である。ローカル相対URLだけでブラウザ利用が成立すると仮定せず、HTTP配信時に解決可能な図・プレビュー・ライブラリURLへ変換する。

## 再実行

```powershell
python -X utf8 sample/information-structuring/diagram-vocabulary/sources/fetch_references.py
python -X utf8 sample/information-structuring/diagram-vocabulary/sources/render_references.py
```

取得はPython標準ライブラリ、プレビュー作成にはDraw.io desktopとPillowが必要。`render_references.py`は保管した編集原図をローカルで書き出す。外部画像をダウンロードする処理は含まない。Draw.io CLIの`--page-index 1`は1ページ目であり、複数ページ全体を確認したとは扱わない。

## 原図の画像点検記録

取得した60原図の第1ページをDraw.io desktopでPNGへ書き出し、12件ずつの接触シート5枚で全件の構成を確認した。さらにAWS（REF018）、BPMN（028）、Storymap（032）、工程×チーム（039）、Sankey（052）、UI説明（057）は個別プレビューを拡大して確認した。点検対象はグルーピング・視覚階層・主要経路・説明の配置であり、全ページ・全ラベルを読んだとは扱わない。個別観測は `reference-visual-review.json` と `official-assets.json` のvisual_reviewへ記録する。

画像を見て抽出内容を修正した。ネットワークREF015は4トポロジーの比較、機能一覧REF056はカテゴリ別タイル配置、層表現REF053は円柱・階段・ピラミッド等の比較である。Sankey REF052第1ページは比例幅の定量例ではなく細線の束による概略であり、新規サンプルの量整合検査は別途必要。UI REF057は画面全体ではなくハンドル・メニュー断片の説明である。これらを汎用パターンへ適用する際、原図にない機能や意味を観測済みとして断定しない。
