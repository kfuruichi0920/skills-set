# プレゼン資料

意思決定に使うスライドを設計・制作するためのリポジトリ。

## ブランチ

- `main`: 基準となる版。
- `dev`: スキルの改善と資料作成の作業用。

## スキルの使い方

このリポジトリをCodexで開き、`$decision-slides`と資料の素材を渡す。新しいスキルが一覧に反映されない場合は、このフォルダーで新しいチャットを開始する。直接`.agents/skills/decision-slides/SKILL.md`を指定しても使える。

例:

```text
$decision-slides
以下の打合せメモから、部門長が次の施策を判断するための資料を作成してください。
読み手: 部門長
決めたいこと: 試行導入の可否
形式: 編集可能なPowerPoint
枚数: 5枚程度
素材: ここにメモと数値の出所を貼り付ける
```

出力形式を省略した場合はMarkdownの設計図を作成する。HTMLやPowerPointを指定した場合は、設計と検証を含めて完成ファイルを作成する。

工程・規準と見本はスキル内に収録済み。参考ページへのアクセスは制作の前提にしない。

- [工程と規準](.agents/skills/decision-slides/references/workflow.md): 5工程、論理6構造、6文型、12グラフ、検査項目。
- [表現カタログ](.agents/skills/decision-slides/references/catalog.md): 基本48型・追加変化形11件・共通原則2件。
- [見本一覧](.agents/skills/decision-slides/assets/catalog-gallery.html): 全61件の画像と用途。ローカルのブラウザーで開ける。
- [抽出・再点検記録](.agents/skills/decision-slides/references/extraction-audit.md): 網羅性と照合結果。

カタログの正本は`catalog.json`。変更後はPythonとPillowを使い、以下を実行する。

```powershell
python -X utf8 .agents/skills/decision-slides/scripts/build_catalog.py
python -X utf8 .agents/skills/decision-slides/scripts/validate_catalog.py
```

由来と読取範囲は[参考元](.agents/skills/decision-slides/references/source.md)に記録している。
