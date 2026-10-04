"""Generate neutral schematics and catalog views with the Python standard library."""

import argparse
import html
import json
from pathlib import Path

from diagrams import diagram

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'base': '基本構造', 'variant': '変化形', 'principle': '共通原則'}


def documents(data):
    samples = data['samples']
    md = ['# 表現構造カタログ', '',
          '正本はcatalog.json。build_catalog.pyで生成する。48基本構造・11変化形・2共通原則のIDを維持している。', '',
          '構成図は汎用の領域・役割・関係を示す模式図で、実データの量や出力デザインを規定しない。用途と軸が入力に適合する場合に配置の参考とする。整理方法の選択肢はこの61構造に限定せず、framework.mdとselection-rules.mdから一覧外・複合表現も検討する。', '',
          '| ID | 方法名称 | 区分 | 用途 |', '| --- | --- | --- | --- |']
    for s in samples:
        md.append(f"| [{s['id']}](#{s['id']}) | {s['name']} | {KINDS[s['kind']]} | {s['group']} |")
    cards = []
    current = None
    esc = html.escape
    for s in samples:
        if current != s['group']:
            current = s['group']
            md.extend(['', f'## {current}', ''])
        axes = s['axes']
        md.extend([f'<a id="{s["id"]}"></a>', '', f"### {s['id']}: {s['name']}", '',
                   f"![{s['name']}](../{s['preview']})", '',
                   f"- 使いどころ: {s['use']}",
                   f"- 整理軸: 横＝{axes['horizontal']}、縦＝{axes['vertical']}。{axes['note']}",
                   f"- 配置: {s['layout']}", f"- 記号・情報の対応: {s['encoding']}",
                   f"- 必要な情報: {'、'.join(s['required_information'])}",
                   f"- 注意: {s['caution']}", ''])
        image = s['preview'].removeprefix('assets/')
        cards.append(f'<article id="{esc(s["id"])}" data-group="{esc(s["group"])}">'
                     f'<h2>{esc(s["name"])}</h2><p>{esc(s["id"])} / {KINDS[s["kind"]]} / {esc(s["group"])}</p>'
                     f'<a href="{esc(image)}"><img src="{esc(image)}" alt="{esc(s["name"])}" loading="lazy"></a>'
                     f'<dl><dt>用途</dt><dd>{esc(s["use"])}</dd>'
                     f'<dt>整理軸</dt><dd>{esc(axes["horizontal"])} × {esc(axes["vertical"])}</dd>'
                     f'<dt>配置</dt><dd>{esc(s["layout"])}</dd>'
                     f'<dt>情報の対応</dt><dd>{esc(s["encoding"])}</dd>'
                     f'<dt>注意</dt><dd>{esc(s["caution"])}</dd></dl></article>')
    gallery = '''<!doctype html><html lang="ja"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>情報の表現構造カタログ</title>
<style>
body{font-family:system-ui,sans-serif;color:#222;background:#f7f7f7;margin:24px}
input,select{font:inherit;padding:10px;margin:8px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,390px),1fr));gap:20px}
article{background:white;border:1px solid #bbb;padding:18px}article[hidden]{display:none}h2{font-size:20px}img{width:100%;height:auto}
dt{font-weight:bold;margin-top:10px}dd{margin:0}a{color:inherit}@media print{input,select{display:none}article{break-inside:avoid}}
</style><header><h1>情報の表現構造カタログ</h1>
<p>入力の軸と関係に合わせて構成を選ぶ。構成図の寸法・配色は出力の指定値ではありません。</p>
<label for="query">検索</label><input id="query" type="search" placeholder="例: 時間、比較、論証">
<label for="group">用途</label><select id="group"><option value="">すべて</option>'''
    gallery += ''.join(f'<option>{esc(g)}</option>' for g in dict.fromkeys(s['group'] for s in samples))
    gallery += f'</select><p id="count" aria-live="polite">{len(samples)}件</p></header><main>'
    gallery += '\n'.join(cards)
    gallery += '''</main><script>
const q=document.getElementById('query'),g=document.getElementById('group'),cards=[...document.querySelectorAll('article')];
function filter(){let n=0;for(const c of cards){const yes=(!g.value||c.dataset.group===g.value)&&c.textContent.toLowerCase().includes(q.value.toLowerCase());c.hidden=!yes;if(yes)n++}document.getElementById('count').textContent=n+'件'}
q.addEventListener('input',filter);g.addEventListener('change',filter);
</script></html>\n'''
    return '\n'.join(md)+'\n', gallery


def build(root=ROOT):
    data = json.loads((root/'references/catalog.json').read_text(encoding='utf-8'))
    for s in data['samples']:
        target = root/s['preview']
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(diagram(s),encoding='utf-8',newline='\n')
    md,gallery = documents(data)
    (root/'references/catalog.md').write_text(md,encoding='utf-8',newline='\n')
    (root/'assets/catalog-gallery.html').write_text(gallery,encoding='utf-8',newline='\n')
    print(f"Generated {len(data['samples'])} neutral SVG schematics, Markdown, and HTML")


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    build(parser.parse_args().root)
