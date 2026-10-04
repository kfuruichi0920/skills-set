"""Generate the complete organization framework from its canonical JSON."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def document(data):
    lines = ['# 情報整理の体系', '',
             'framework.jsonを正本として生成した選択用の索引。16目的・19軸・12基本表現は出発点であり、入力に必要な新しい軸・手法・複合表現を追加できる。専門手法の名称は候補であり、正式な実施手順や規格への適合を保証しない。', '',
             '## 選択の順序', '', ' → '.join(data['selection_layers']), '',
             '## 基本軸', '', '| ID | 軸 | 問い | 意味 |', '| --- | --- | --- | --- |']
    for axis in data['axes']:
        lines.append(f"| {axis['id']} | {axis['name']} | {axis['question']} | {axis['meaning']} |")
    lines += ['', '軸を修飾する情報: ' + '、'.join(data['qualifiers']), '',
              '## 基本表現', '', '| ID | 表現 | 意味 | 注意 |', '| --- | --- | --- | --- |']
    for form in data['forms']:
        lines.append(f"| {form['id']} | {form['name']} | {form['meaning']} | {form['caution']} |")
    lines += ['', '## 整理目的と専門手法の候補', '',
              '同じ手法が複数目的に現れるのは、複数の整理軸を持つため。目的を一つに固定する必要はない。', '']
    for index, purpose in enumerate(data['purposes'], 1):
        lines += [f"### {index}. {purpose['name']} ({purpose['id']})", '',
                  f"- 問い: {purpose['question']}",
                  f"- 入力の手掛かり: {purpose['signals']}",
                  f"- 軸: {', '.join(purpose['axes'])}",
                  f"- 基本表現: {', '.join(purpose['forms'])}",
                  f"- 必要な情報・留保: {purpose['prerequisites']}", '',
                  '候補手法: ' + '、'.join(purpose['methods']), '']
    lines += ['## 既存表現との関係', '', data['catalog_role'], '',
              '標準出力は情報整理と可視化案に加え、入力→正規化→整理軸→候補比較→出力要素の対応を残す補足資料。詳しい選択規則はselection-rules.md、記録様式はrationale-template.mdを参照する。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    data = json.loads((ROOT / 'references/framework.json').read_text(encoding='utf-8'))
    (ROOT / 'references/framework.md').write_text(document(data), encoding='utf-8')
