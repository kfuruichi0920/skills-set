# 出典情報

既存図への説明追加は、ユーザー提示のVisual Annotation / Explanation仕様を取り込んだ。入力・モード・レイヤー・確かさ・正規化座標・IR・複数View・更新時の照合・視覚検査をvisual-annotation.mdへ収録する。[公式PlantUML挿入仕様](https://www.drawio.com/docs/manual/insert/insert_plantuml/)でNativeコンテナのソース編集と部分実装の制約、[画像挿入](https://www.drawio.com/docs/manual/insert/add-images/)と[レイヤー](https://www.drawio.com/docs/manual/layers/)で原画像と注釈の分離の参照先を確認した。Native対応は利用する環境ごとに検査する。

Draw.ioの10テーマ、配色、選択順、意味記号と品質観点はユーザー提示のTheme Catalogを取り込んだ。diagram-themes.jsonに配色の正本、diagram-themes.mdに運用規則を収録する。[Draw.io公式style reference](https://www.drawio.com/docs/reference/diagram-generation/style-reference/)でstyle生成の参照先を確認した。これらは本スキルの作成用テーマであり、ブランドの正式テーマやDraw.ioの組込みテーマではない。

ASCII図は、同じtechnical-writingの`references/ascii-diagrams.md`から、共通記号と8つの型（構成、層、包含、処理順、定義と実体、正本と派生、やり取り、レコード）を一般化し、visualization.mdへ収録した。切替先は本スキルの出力方針に合わせDraw.io等とする。元の資料への実行時依存はない。

日本語の記述規則は、ユーザー指定の`C:/git/cdx/d2d/.agents/skills/technical-writing/SKILL.md`を参考に、正確性・一意性・検証可能性、用語の統一、記述の役割の分離、図と情報の意味境界を抽出した。D2D固有の文書配置・識別子体系・検査コマンドは適用しない。必要な規則はjapanese-writing.mdに記載してあり、実行時に元スキルを読む必要はない。

参考ページ: https://note.com/uchita_success/n/na5babdc58b0e

ユーザー提供の工程図と表現一覧から、情報構造・配置の考え方を抽出した。出典は由来を示す情報であり、実行時に参照する必要はない。

初回の抽出結果はGitコミット89610daに保存した。現行版では固有名称・会社名・架空の実数・固定配色・固定寸法・作者の検査実績を運用情報から除き、汎用の役割と構成図へ置き換えた。元画像は現行スキルに同梱しない。


一般化した可視化・スライド案出し版はdevのef2ad6dに保存した。その後、ユーザー提示の「情報整理」体系を取り込み、情報整理・可視化へ目的を改めた。

取り込んだ情報は16整理目的、19個の明示された基本軸、12基本表現、各目的の専門手法候補、意味判定から説明方法までの選択順序。framework.jsonとframework.mdに全候補を記載し、選択規則・実行手順・根拠記録はスキル内で定義する。

提供文中の引用プレースホルダーには参照先がなく、規格の版・採択時期に関する記述も今回の整理では確認していない。これらを検証済みの出典や運用上の前提として採用しない。正式記法や規格への適合を求められる実案件では、対象版と一次資料を確認する。

PlantUMLシーケンス図の例は[公式の構文説明](https://plantuml.com/sequence-diagram)で参加者・別名・メッセージの記法を確認した。使用する例と運用規則はvisualization.md・production.mdに収録している。

## Draw.ioネイティブ機能の統合（2026-10-04）

ユーザー添付「LLM図解Skill — Draw.io Native機能活用・Shape Catalog統合仕様」に基づき、実Stencilの抽出・検索・解決済みIR・XML検証・ネイティブ機能選択・再利用資産を追加した。資産版はDraw.io Desktop 31.5.2。登録規則とTable／TableRowの設定は同版のapp.min.jsを照合した。生成カタログの出所とハッシュはreferences/drawioのrawへ保存する。サンプルと検査記録はsample/information-structuringを参照する。
