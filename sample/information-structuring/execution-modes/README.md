# 高速・精密モードの出力比較

同じ架空入力を使い、情報の意味とXMLを変えずに検査の範囲だけを変える例。通常の利用では案件のoutputへ保存し、Git操作を行わない。このディレクトリはスキル改修用の版管理サンプルである。

| モード | 主文書 | 図 | 根拠と検査 |
| --- | --- | --- | --- |
| 高速 | [fast-result.md](fast-result.md) | [fast.drawio](fast.drawio) | [fast-rationale.md](fast-rationale.md)。詳細な目視検査・任意プレビューは省略 |
| 精密 | [precise-result.md](precise-result.md) | [precise.drawio](precise.drawio) | [precise-rationale.md](precise-rationale.md)。[実画像](precise.png)を表示点検 |

入力は[input.json](input.json)、制作データは[diagram-ir.json](diagram-ir.json)と[resolved-ir.json](resolved-ir.json)、出力対応と検査記録は[manifest.json](manifest.json)。両図は同一バイト列である。高速の検査を省くことは、情報の省略や意図的な配置不良を意味しない。

再生成はリポジトリルートから行う。Python、Pillow、Draw.io Desktopと既存の図形カタログを使う。再生成で精密の表示検査は未完了へ戻る。

```powershell
python -X utf8 sample/information-structuring/execution-modes/build_sample.py
# precise.pngを開いて線・余白・文字・接続先を点検する
python -X utf8 sample/information-structuring/execution-modes/build_sample.py --accept-precise --findings "実際の点検結果"
python -X utf8 sample/information-structuring/execution-modes/check_sample.py
```

検査は同じ意味とXML、高速でのプレビュー省略、精密の点検記録、接続参照、検索Top-Kの高速3件・精密5件・明示上書きを確認する。版管理サンプルの改修検証を、通常利用における高速の目視検査実施と混同しない。
