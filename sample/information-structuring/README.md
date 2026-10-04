# 情報整理・可視化の出力サンプル

本スキルが選べる整理目的・配置・テーマ・原図への説明追加を、編集できるDraw.ioで確認するためのサンプル集。全て架空のデータまたは汎用の模式図であり、案件の仕様や専門手法への準拠を表すものではない。図の型を選ぶ順序は「目的 → 情報の意味と軸 → 表現 → テーマ → 配置」とする。

## パターンの分類

| 分類 | 収録内容 | ファイル |
| --- | --- | --- |
| 整理目的 | 概念、分類、分解、比較、依存、時間、業務、状態、因果、リスク、要求トレース、判断、責任、数値、戦略、論証の16ページ | [01-organizing-patterns.drawio](01-organizing-patterns.drawio) |
| カタログ | 48基本構造・11変化形・2共通原則。用途別8ファイル、計61ページ | [対応一覧](index.md)のcatalog区分 |
| テーマ | 同じ情報構造にT01〜T10を適用し、外観と意味を分離する10ページ | [02-theme-comparison.drawio](02-theme-comparison.drawio) |
| 画面説明 | 主要領域・要素の役割・操作説明の3ページ。画像だけで操作順や動作を断定しない | [03-screen-annotations.drawio](03-screen-annotations.drawio) |
| 既存Draw.ioへの注釈 | 原図のID・文字・位置・スタイル・接続を維持し、原図レイヤーをロック | [04-native-annotation.drawio](04-native-annotation.drawio) |
| PlantUMLのSVGへの注釈 | `.puml`と実レンダリングを保持し、説明だけを別レイヤーへ配置 | [05-plantuml-annotation.drawio](05-plantuml-annotation.drawio) |
| PNGへの注釈 | SVGを扱えない場合の代替。原画像を保持し、拡大時の読みやすさに留意 | [06-plantuml-png-annotation.drawio](06-plantuml-png-annotation.drawio) |

計93ページ（原図の別ファイルを除く）。[index.md](index.md)は全ページの名称・ID・テーマ・ファイルへの対応、[manifest.json](manifest.json)は検査用の対応データを持つ。

## 読み方と範囲

整理目的の例は具体的な架空情報に軸を割り当てる例、カタログは配置の骨格を選ぶ例である。同じ型を入力へ適用する場合は、条件・関係名・単位・尺度を実情報から設定する。模式図の高さや位置を事実上の数量として転用しない。

図形・線・文字はDraw.ioで編集できる。曲線と多角形の一部はネイティブの経路・ステンシルとして保持する。注釈例だけは原図画像を単一オブジェクトで保持し、元のPlantUMLや画像内部をDraw.io図形へ変換したとは扱わない。複数ページのファイルは、Draw.io下部のページタブで切り替える。

Markdownは主説明、Draw.ioは補足図、HTMLはスライドのキャンバスであり、形式ごとに別の情報整理法を定義しない。そのため、ここではDraw.ioで確認できる構造に焦点を当てる。大きいマトリクスの全量はTSV／CSVとし、比較・分類の図は小さい例と全体像に限定する。PlantUMLの正本は[sources/sequence.puml](sources/sequence.puml)。Native PlantUMLコンテナの部分実装は環境依存のため、このサンプルは互換性を確認しやすいSVGとPNGを採用する。T05の比較ページはテーマと意味記号の例であり、公式クラウド製品の構成図ではない。

## 更新と再生成

このディレクトリは、ユーザーが指定した版管理するサンプルの保存先である。通常の案件成果物の`output/日時_日本語概要/`とは用途が異なる。サンプルの作成・更新はここへ直接保存し、既存outputを入力として探索しない。

スキルの整理軸・カタログ・テーマ・Draw.io生成・注釈仕様を変更した場合、対応するサンプルと原図・IR・生成コード・対応一覧を同じ変更で更新する。新しい出力パターンは追加し、廃止・統合したパターンは対応一覧で説明する。日本語の指示だけを直した場合も、図の文言に影響がないか点検する。選択肢をこの一覧で閉じない。

生成・検査に使うスクリプトは[scripts/](scripts/)へ保存し、削除しない。同梱補助ツールはスキル側の原本のコピーであり、再生成時に同期する。中間データと原図は[sources/](sources/)、テーマ設定は[references/diagram-themes.json](references/diagram-themes.json)へ保存する。

リポジトリのルートで実行する。Python 3、PlantUMLとJava、Pillow（PNG寸法・一覧画像）を使用する。表示書出しにはDraw.io Desktopが必要。`check_samples.py`のページ番号はDraw.io 27.0.2以降の1始まりを使う。

```powershell
python -X utf8 sample/information-structuring/scripts/build_samples.py
python -X utf8 sample/information-structuring/scripts/check_samples.py
python -X utf8 sample/information-structuring/scripts/check_samples.py --render
```

カタログ・整理目的・テーマのIDの網羅、XMLと接続先、ネイティブ原図の保持、画像ハッシュ、補助ツールの同期を検査する。表示検査はDraw.ioから書き出した`previews/`の全ページを確認し、接続先・ラベル・余白を点検する。機械検査や一覧画像だけを、全ラベルの通常倍率での確認と同一視しない。表示の確認状況は[visual-qa.md](visual-qa.md)に記録する。
