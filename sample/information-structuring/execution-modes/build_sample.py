"""Mode contract samples: same meaning, fast skips optional preview/visual review."""
import hashlib
import argparse
import json
import subprocess
import tempfile
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
SKILL=REPO/'.agents/skills/information-structuring'
sys.path.insert(0,str(SKILL/'scripts'))
import shape_catalog as sc


def build():
    source=BASE.parent/'diagram-vocabulary/examples/DV-031/diagram-ir.json'
    ir=sc.read(source)
    ir['id']='mode-contract'
    ir['metadata']['title']='同じ情報を二つの検査モードで出力する'
    ir['nodes'][0]['label']=ir['metadata']['title']
    sc.write(BASE/'diagram-ir.json',ir)
    catalog=sc.read(SKILL/'references/drawio/shape-catalog.json')
    resolved=sc.render(catalog,ir,BASE/'fast.drawio');sc.write(BASE/'resolved-ir.json',resolved)
    data=(BASE/'fast.drawio').read_bytes();(BASE/'precise.drawio').write_bytes(data)
    for mode in ('fast','precise'):sc.validate_xml(ET.parse(BASE/f'{mode}.drawio').getroot(),catalog)
    # Isolate CLI export from an existing desktop editor session.
    with tempfile.TemporaryDirectory(prefix='drawio-mode-sample-') as profile:
        subprocess.run(['C:/Program Files/draw.io/draw.io.exe','--user-data-dir='+profile,
                        '--export','--format','png','--page-index','1',
                        '--output',str(BASE/'precise.png'),str(BASE/'precise.drawio')],
                       check=True,capture_output=True,timeout=90)
    sc.write(BASE/'input.json',dict(question='受付、確認、回答の順に処理する。この情報をMarkdownとDraw.ioで整理する。',
                                 fictional=True,source=source.relative_to(REPO).as_posix()))
    checks=['input-meaning','xml','shape-ids','parent-and-edge-references']
    manifest=dict(source='input.json',same_meaning=True,git_operations=False,
        samples=[dict(mode='fast',file='fast.drawio',checks=checks,visual_review='not_performed',preview=None),
                 dict(mode='precise',file='precise.drawio',checks=checks,visual_review='pending',preview='precise.png')],
        sha256=hashlib.sha256(data).hexdigest(),maintenance_note='版管理サンプルの改修検査と通常利用の高速モードを区別する')
    sc.write(BASE/'manifest.json',manifest)
    for mode in ('fast','precise'):
        text='# 整理結果\n\n受付 → 確認 → 回答の順で処理する。架空の処理例。\n\n[編集可能な図]('+mode+'.drawio)\n\n'
        if mode=='precise':text+='![図のプレビュー](precise.png)\n\n'
        text+='[根拠と検査状況]('+mode+'-rationale.md)\n'
        (BASE/f'{mode}-result.md').write_text(text,encoding='utf-8',newline='\n')
        rationale=f'# 整理根拠\n\nモード: {mode}\n\n入力原文: 受付、確認、回答の順に処理する。この情報をMarkdownとDraw.ioで整理する。\n\n入力時刻: 取得不可（再利用する架空例）。出所: input.json。\n\n目的: 処理の順序を説明する。軸: sequence。表現: 左から右の基本フロー（DV-031）。テーマ: T01。\n\n受付・確認・回答は同名の図要素に対応し、矢印は次の処理を表す。入力に期間や例外がないため追加しない。\n\n意味・XML・図形ID・所属と接続参照を確認。Git操作なし。\n\n'
        rationale+='詳細な目視検査は未実施。任意のプレビュー生成を省略。\n' if mode=='fast' else '表示検査: 点検待ち。precise.pngを表示して記録する。\n'
        (BASE/f'{mode}-rationale.md').write_text(rationale,encoding='utf-8',newline='\n')
    print('Built identical fast/precise diagrams; only precise preview rendered; visual review pending')


def accept(findings):
    if not findings.strip():raise ValueError('Record the actual visual findings')
    manifest=sc.read(BASE/'manifest.json')
    assert hashlib.sha256((BASE/'precise.drawio').read_bytes()).hexdigest()==manifest['sha256']
    entry=next(e for e in manifest['samples'] if e['mode']=='precise')
    entry['visual_review']='accepted';entry['visual_findings']=findings
    manifest['preview_sha256']=hashlib.sha256((BASE/'precise.png').read_bytes()).hexdigest()
    sc.write(BASE/'manifest.json',manifest)
    path=BASE/'precise-rationale.md'
    path.write_text(path.read_text(encoding='utf-8').replace('表示検査: 点検待ち。precise.pngを表示して記録する。','表示検査: '+findings),encoding='utf-8',newline='\n')
    print('Accepted precise preview; fast remains visually unreviewed in the runtime contract')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--accept-precise',action='store_true');parser.add_argument('--findings',default='')
    args=parser.parse_args()
    if args.accept_precise:accept(args.findings)
    else:build()
