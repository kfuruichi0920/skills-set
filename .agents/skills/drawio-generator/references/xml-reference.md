# XMLの生成契約

一次資料（確認日2026-10-17）:

- [公式AI生成・検証](https://www.drawio.com/docs/reference/diagram-generation/)
- [公式共有XMLリファレンス](https://github.com/jgraph/drawio-mcp/blob/e227b9ad530ac22d2a00066c7e6ac3b9583dba74/shared/xml-reference.md)
- [公式XSDと由来](../schemas/README.md)

この文書はMVPで使う規則の要約であり、公式文書の全文コピーではない。

## 入力と正規化

納品はUTF-8、非圧縮、完全な`mxfile`形式。各`diagram`に一つの`mxGraphModel`、その中に一つの`root`を置く。`diagram`のIDはファイル内で一意。ページ内のセルIDと接続参照はページごとに独立する。

`mxGraphModel`だけのXMLもdraw.ioで使えるが、同梱XSDが宣言する文書ルートは`mxfile`。検証器は単体モデルを`mxfile/diagram`で包んでからXSDを適用する。`--output`を省略した検証は元ファイルを書き換えない。付与するページIDは`page-1`、名前は`Page-1`。複数ページの完全形はそのまま検査する。

Base64/deflate、XMLエスケープされたモデル本文、DOCTYPE/DTD、外部エンティティ、名前空間付き独自形式は対象外。XMLコメントは生成しない。XSD内の注釈は配布元のまま保持する。

## セルと座標

- 最初に`<mxCell id="0"/>`と`<mxCell id="1" parent="0"/>`を置く。これらにvertex/edgeの役割を付けない。
- 図形は`vertex="1" parent="1"`と`mxGeometry x="..." y="..." width="..." height="..." as="geometry"`を持つ。幅・高さは有限の正数。座標の省略値は0。xは右向き、yは下向き。
- 線は`edge="1" parent="1" source="node-a" target="node-b"`と`<mxGeometry relative="1" as="geometry"/>`を持つ。vertexとedgeを両方1にしない。
- ノード接続を基本とする。意図的な未接続端はgeometry内に`<mxPoint x="..." y="..." as="sourcePoint"/>`または`targetPoint`を指定する。
- グループの子は親グループIDをparentに使い、座標は親基準。親参照を循環させない。追加レイヤーはparent=0、役割フラグなし。
- カスタムメタデータが必要な場合は`UserObject`または`object`にIDを置き、内側の`mxCell`にはIDを置かない。参照もラッパーのIDを使う。
- `value`や`label`の`& < > "`はXMLエスケープする。PythonならElementTree等で属性を書き、文字列連結によるXML破損を避ける。

XSD未定義の属性は、エディターが対応していても失敗する場合がある。XSDを黙って改変したり検証を省略したりせず、MVPの対応属性に戻すか、未対応として報告する。
