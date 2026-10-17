# スタイルの基本

一次資料: [公式Style Reference](https://www.drawio.com/docs/reference/diagram-generation/style-reference/)（確認日2026-10-17）。以下は生成時に使う最小規則。

スタイルは大文字小文字を区別する`key=value;`の列。基本ノードには
`rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;`を使える。
XML属性内のHTMLはXMLエスケープする。外部画像やフォントに依存しない基本図形を優先する。

コネクタの既定値:

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=none;endArrow=none;
```

接続先へ矢印を明示された場合は`endArrow=classic;`、始点側なら`startArrow=classic;`、双方向なら両方に指定する。指定された種類・方向は保つ。何も指定されていない場合は両端none。例から矢印を推測して加えない。

非矩形では図形とperimeterを合わせる。例: `ellipse;perimeter=ellipsePerimeter;`、`rhombus;perimeter=rhombusPerimeter;`。文字色と背景色は十分なコントラストを保つ。色だけで装置の役割を表さずラベルを添える。

XSDはstyleを単なる文字列として扱う。追加検査ではコネクタのstartArrow/endArrowの明示だけを要求し、すべてのキー・値や図形ライブラリーを検証しない。明示矢印かどうかの意味的判断は生成エージェントが行う。
