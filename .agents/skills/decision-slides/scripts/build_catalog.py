"""Generate local previews and catalog views from catalog.json. Requires Pillow."""

import argparse
import html
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def documents(data):
    samples = data['samples']
    md = [
        '# スライド表現カタログ', '',
        '正本は`catalog.json`。このファイルは`scripts/build_catalog.py`で生成する。', '',
        '48基本型 + 11追加変化形 + 2共通原則 = 61見本。名称は画像のラベルを保存し、配置は視覚読取、用途・記号・注意点は再利用のための解釈を含む。見本の微小な本文や架空数値を実データとして転用しない。', '',
        '見本画像は名称ラベルごと保存している。詳細が読み切れないときは元の2400×3000画像と切り出し位置で確認する。', '',
        '| ID | 型 | 区分 | 方法名称 | 用途グループ |',
        '| --- | --- | --- | --- | --- |',
    ]
    kinds = {'base': '基本型', 'variant': '追加変化形', 'principle': '共通原則'}
    for s in samples:
        number = f"{s['type_number']:02d}" if s['type_number'] else '原則'
        md.append(f"| [{s['id']}](#{s['id']}) | {number} | {kinds[s['kind']]} | {s['name']} | {s['group']} |")
    cards = []
    current = None
    for s in samples:
        if current != s['group']:
            current = s['group']
            md.extend(['', f'## {current}', ''])
        pos = s['source']
        source = f"{pos['page']} 行{pos['row']}・列{pos['column']}、切出し座標{pos['crop']}"
        md.extend([
            f"<a id=\"{s['id']}\"></a>", '', f"### {s['id']}: {s['name']}", '',
            f"![{s['name']}](../{s['preview']})", '',
            f"- 区分: {kinds[s['kind']]}", f"- 使いどころ: {s['use']}",
            f"- 配置・スライド表現: {s['layout']}", f"- 記号・データとの対応: {s['encoding']}",
            f"- 再利用時の注意: {s['caution']}",
            f"- 元見本: [{source}](../{pos['image']})", '',
        ])
        esc = html.escape
        cards.append(
            f'<article id="{esc(s["id"])}" data-group="{esc(s["group"])}">'
            f'<h2>{esc(s["name"])}</h2><p class="meta">{esc(s["id"])} / {esc(s["group"])} / {kinds[s["kind"]]}</p>'
            f'<a href="{esc(s["preview"].removeprefix("assets/"))}"><img src="{esc(s["preview"].removeprefix("assets/"))}" alt="{esc(s["name"])}" loading="lazy"></a>'
            f'<dl><dt>使いどころ</dt><dd>{esc(s["use"])}</dd><dt>配置</dt><dd>{esc(s["layout"])}</dd>'
            f'<dt>記号</dt><dd>{esc(s["encoding"])}</dd><dt>注意</dt><dd>{esc(s["caution"])}</dd></dl>'
            f'<a href="{esc(pos["image"].removeprefix("assets/"))}">元画像: {esc(source)}</a></article>'
        )
    gallery = '''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>スライド表現カタログ — 61見本</title>
<style>
body{font-family:Meiryo,"Yu Gothic",sans-serif;color:#222;background:#f4f7fa;margin:24px}
header{max-width:1100px;margin:auto}input,select{font:inherit;padding:10px;margin:6px 10px 18px 0;max-width:90%}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:20px}
article{background:white;border:1px solid #d9dee3;padding:18px}article[hidden]{display:none}
h2{font-size:20px;color:#1976d2;margin:0}.meta{font-size:13px;color:#52636c}
img{width:100%;height:auto}dt{font-weight:bold;margin-top:10px}dd{margin-left:0}a{color:#145eaa}
@media print{header input,header select{display:none}main{display:block}article{break-inside:avoid;margin-bottom:16px}}
</style>
<header><h1>スライド表現カタログ</h1><p>48基本型・11追加変化形・2共通原則。用途と配置から選び、画像をクリックして見本を確認。</p>
<p>見本の数値・会社は架空。用途・記号・注意は画像を基にした再利用用の解釈を含む。</p>
<label>検索 <input id="query" type="search" placeholder="例: 型、時間、比較"></label>
<label>用途 <select id="group"><option value="">すべて</option>'''
    for group in dict.fromkeys(s['group'] for s in samples):
        gallery += f'<option>{html.escape(group)}</option>'
    gallery += '</select></label><p id="count" aria-live="polite">61件</p></header><main>'
    gallery += '\n'.join(cards)
    gallery += '''</main><script>
const q=document.getElementById('query'),g=document.getElementById('group'),cards=[...document.querySelectorAll('article')];
function filter(){let n=0;for(const c of cards){const yes=(!g.value||c.dataset.group===g.value)&&c.textContent.toLowerCase().includes(q.value.toLowerCase());c.hidden=!yes;if(yes)n++}document.getElementById('count').textContent=n+'件'}
q.addEventListener('input',filter);g.addEventListener('change',filter);
</script></html>\n'''
    return '\n'.join(md) + '\n', gallery


def build(root=ROOT):
    data = json.loads((root / 'references/catalog.json').read_text(encoding='utf-8'))
    originals = {}
    for s in data['samples']:
        output = root / s['preview']
        output.parent.mkdir(parents=True, exist_ok=True)
        source = s['source']['image']
        if source not in originals:
            with Image.open(root / source) as original:
                originals[source] = original.copy()
        originals[source].crop(tuple(s['source']['crop'])).save(output)
    md, gallery = documents(data)
    (root / 'references/catalog.md').write_text(md, encoding='utf-8', newline='\n')
    (root / 'assets/catalog-gallery.html').write_text(gallery, encoding='utf-8', newline='\n')
    print(f"Generated {len(data['samples'])} previews, Markdown, and HTML")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    build(parser.parse_args().root)
