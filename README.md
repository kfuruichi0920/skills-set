# プレゼン資料

任意の情報から重要な軸を抽出し、可視化・スライド化の案を探索するためのリポジトリ。

- main: 基準となる版。
- dev: スキルの改善と資料作成。

## 使い方

Codexでこのリポジトリを開き、$decision-slidesと素材を渡す。

```text
$decision-slides
以下の情報から重要な軸を抽出し、適した可視化・スライド案を比較してください。
素材: ここに文章・メモ・仕様・表などを貼る
```

目的や形式が未指定でも、仮定を明示して案出しを進める。標準出力はMarkdownの「情報整理・抽出軸・表現案の比較・主案のページ構成と図解ラフ」。HTML・編集可能なPowerPointを指定した場合は実ファイルを制作する。

## スキルの骨格

入力の構造化 → 重要な軸の抽出 → 要点と筋道 → 表現案の比較 → ラフ出力と検証。

- [スキル](.agents/skills/decision-slides/SKILL.md)
- [情報整理と表現選択](.agents/skills/decision-slides/references/workflow.md)
- [表現カタログ](.agents/skills/decision-slides/references/catalog.md)
- [汎用の構成図一覧](.agents/skills/decision-slides/assets/catalog-gallery.html)
- [汎用化と検証記録](.agents/skills/decision-slides/references/extraction-audit.md)

48基本構造・11変化形・2共通原則の対応を保持し、元画像の固有名称・企業情報・デザインを汎用構成図へ置き換えている。構成図は概念的なラフで、数値の縮尺や完成デザインを示すものではない。

カタログの正本はcatalog.json。Python標準ライブラリで生成・検証できる。

```powershell
python -X utf8 .agents/skills/decision-slides/scripts/build_catalog.py
python -X utf8 .agents/skills/decision-slides/scripts/validate_catalog.py
```

初回抽出のコミットは89610da。参考ページはスキル内のsource.mdに出典情報としてのみ掲載している。
