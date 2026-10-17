# 公式XSDの由来と利用範囲

[公式AI生成ドキュメント](https://www.drawio.com/docs/reference/diagram-generation/)が直接案内する[jgraph/drawio-mcp/shared/mxfile.xsd](https://github.com/jgraph/drawio-mcp/blob/e227b9ad530ac22d2a00066c7e6ac3b9583dba74/shared/mxfile.xsd)を無改変で同梱する。MCPの利用は不要。

- XSDヘッダーの版: **1.0**（draw.ioアプリの版とは別）。
- 固定コミット: `e227b9ad530ac22d2a00066c7e6ac3b9583dba74`。
- 取得日: **2026-10-17**。
- SHA-256: `905db85d4e8ebec0e91518cdd62982e0afb3f09ebdcaf9e6b1952957a606639a`。
- 配布元の[LICENSE](https://github.com/jgraph/drawio-mcp/blob/e227b9ad530ac22d2a00066c7e6ac3b9583dba74/LICENSE): Apache-2.0、Copyright 2025 JGraph Ltd。同ライセンスを[LICENSE](LICENSE)に保持。配布元に独立したNOTICEファイルは取得時点でない。図形・アイコンライブラリーは同梱しない。
- 機械可読な記録は[source.json](source.json)。検証時にSHA-256を照合し、不一致なら失敗する。

## 適用範囲

文書ルートは`mxfile`。検証器は単体`mxGraphModel`を包んで適用する。階層・対応属性・属性型を検査する。注釈は圧縮形式にも言及するが、この版の実際の`diagramType`は子`mxGraphModel`のみを受け付けるため、MVPは非圧縮のみ対応する。

ID一意性、必須セル、参照の存在、親循環、役割とgeometryの関係、有限な座標・正の図形寸法、明示矢印キーは追加検査が担当する。描画品質、意味の正しさ、全スタイル、任意のエディターバージョンとの互換性は保証外。公式XSDがまだ表現していないエディター属性もあり、編集済みの既存ファイル全般を検証するツールではない。

## 再取得

通常利用では取得不要。再現する場合だけ次を実行し、記録済みSHA-256と一致することを確認してから配置する。

```sh
curl --fail --location https://raw.githubusercontent.com/jgraph/drawio-mcp/e227b9ad530ac22d2a00066c7e6ac3b9583dba74/shared/mxfile.xsd --output mxfile.xsd
python -c "import hashlib; from pathlib import Path; print(hashlib.sha256(Path('mxfile.xsd').read_bytes()).hexdigest())"
```

更新時は公式リンク・適用形式・ライセンスを再確認し、XSD、LICENSE、source.json、この説明、テストを同時更新する。検証器はリモートスキーマ、XMLのschemaLocation、DTDを取得せず、XIncludeも展開しない。
