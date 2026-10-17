# 受け入れ検査

リポジトリのルートで実行する（Python 3.10以上）。

```sh
python -m pip install -r .agents/skills/drawio-generator/requirements.txt
python -m unittest discover -s .agents/skills/drawio-generator/tests -v
python .agents/skills/drawio-generator/scripts/validate.py .agents/skills/drawio-generator/assets/basic-template.drawio --json
```

テストはPython標準unittestとlxmlを使用し、ネットワークやdraw.ioのインストールを必要としない。正常な装置3台・線2本、単体モデル正規化、複数ページ、ラッパー、明示矢印保持、XSD型違反、XML破損、ID重複、欠落参照・寸法、親循環、危険なXML、出力保護を検査する。DTD/エンティティの拒否はUTF-16でも確認し、外部リソースのresolverが呼ばれたら失敗させる。

## 修正・再検証の例

入力は「制御装置—スイッチ—センサー、矢印なし」。生成ミスとして`link-2`のtargetを`sensor-typo`にすると、検証器は次のような診断を返し、終了コード1となる。

```text
[consistency] page='装置構成' line=... id='link-2': target='sensor-typo' does not reference a cell in this page
```

エージェントは入力とセル一覧から正しい接続先が`sensor`であると判断し、生成コードまたはXMLを修正して同じコマンドを再実行する。XML/XSD/整合性がPASSになった時だけ完全形を納品する。`test_failure_repair_revalidation_and_output`はこの1回修正の流れを再現する。テスト内の既知誤記修正はLLM自体の自動実行試験ではなく、手順の回帰試験。一般の修正判断はSKILL.mdに従うエージェントが担う。

## draw.ioでの表示・編集確認（手動受け入れ）

1. `assets/basic-template.drawio`をdraw.io Desktopまたは[Web版](https://app.diagrams.net/)の「ファイル → 開く」で選択する。
2. 「装置構成」ページに制御装置・スイッチ・センサーと線2本があること、線の両端に矢印がないことを確認する。
3. 制御装置を移動し、線の端が追従することを確認する。ラベルを変更し、別々の図形として編集できることを確認する。
4. 線の端を別ノードへ付け替える。別名保存し、再度開いて編集状態が保持されていることを確認する。
5. 実施日・エディターの版・OS・確認結果を記録する。元の版管理テンプレートは上書きしない。保存で圧縮された図はこの非圧縮XML検証器の対象外なので、再検証時は非圧縮で保存する。

XSD PASSと描画・編集確認は別結果として報告する。未実施なら未実施と明記する。

## 実装時の確認記録（2026-10-17）

- Python 3.12.14 / lxml 6.1.1、Linuxで上記unittest全26件がPASS。
- 基本テンプレートはXML・正規化・公式XSD・追加整合性の全項目PASS。
- draw.ioでの実表示・編集・保存後再オープンは未実施。このセッションではdraw.io Desktopと接続ブラウザーの操作ツールを利用できなかったため、上記手動受け入れを残す。
