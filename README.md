# 情報整理・可視化

雑多な入力を整理し、適切な表現とその選択根拠を出力するスキル。スライドのフォーマットは、整理した情報を理解しやすく配置するキャンバスの一候補。

- main: 基準となる版。
- dev: スキルの改善と情報整理。

## 使い方

```text
$information-structuring
以下の情報を整理・可視化してください。
目的・読み手: 設計レビューに参加する開発者
素材: ここに文章・メモ・仕様・表などを貼る
```

出力はMarkdownを優先する。補足図はシーケンス図にPlantUML、構造・配置図にDraw.ioを使い、大きな表・マトリクスはMarkdown表ではなくTSV（優先）／CSVにする。これらを主文書にリンクして組み合わせる。未指定時はこの構成を推奨して希望を質問し、HTMLスライドやテーブル中心、その他の明示指定にも従う。

比較・対応・分岐・全体と詳細などを含む情報は、カタログの型と配置を照合し、図の種類に応じてPlantUMLまたはDraw.ioで可視化する。小さな階層・構造・処理順にはASCII図も使える。整理根拠は質問原文・入力時刻（取得できない場合は記録時刻と区別）を含む別の補足Markdownとして添え、成果物は`output/YYYYMMDD_HHMMSS_約20文字の日本語概要/`にまとめて保存する。目的が未指定の場合も仮定を示して整理を進める。

## 構成

整理目的 → 情報の意味と軸 → 基本表現 → 必要な専門手法 → 読み手に合う説明 → キャンバス。

- [スキル](.agents/skills/information-structuring/SKILL.md)
- [16目的・19軸・12基本表現](.agents/skills/information-structuring/references/framework.md)
- [選択規則](.agents/skills/information-structuring/references/selection-rules.md)
- [整理根拠の補足様式](.agents/skills/information-structuring/assets/rationale-template.md)
- [条件付き依存・状態モデルなどの適用例](.agents/skills/information-structuring/references/examples.md)
- [可視化の選び方とASCII図の型](.agents/skills/information-structuring/references/visualization.md)
- [カタログ照合から図制作までの選択手順](.agents/skills/information-structuring/references/catalog-selection.md)
- [Draw.ioの10テーマ・意味記号・配置規則](.agents/skills/information-structuring/references/diagram-themes.md)
- [61構造の配置参考](.agents/skills/information-structuring/assets/catalog-gallery.html)

体系と既存カタログはいずれも閉じた選択肢にしない。新しい軸・整理方法・複合表現を、入力に必要な意味と関係から選べる。専門手法299項目は重複を含む候補索引であり、各手法の正式な分析手順を実装したものではない。

## 検証

Python標準ライブラリで体系・カタログを生成し、網羅性と整合性を検査する。

```powershell
python -X utf8 .agents/skills/information-structuring/scripts/build_framework.py
python -X utf8 .agents/skills/information-structuring/scripts/validate_framework.py
python -X utf8 .agents/skills/information-structuring/scripts/build_catalog.py
python -X utf8 .agents/skills/information-structuring/scripts/validate_catalog.py
python -X utf8 .agents/skills/information-structuring/scripts/validate_themes.py
```

初回抽出は89610da、一般化したスライド案出し版はef2ad6dに保存済み。参考ページはsource.mdに由来情報としてのみ記載し、スキルの利用に参照を必要としない。
