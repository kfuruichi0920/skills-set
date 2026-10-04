"""Record the separately verified editor configuration specification."""
import csv
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
path=BASE/'sources/source-registry.json'
data=json.loads(path.read_text(encoding='utf-8'))
if not any(item['id']=='SRC-058' for item in data['sources']):
    data['sources'].append(dict(id='SRC-058',title='Draw.io editor configuration',provider='draw.io / JGraph',
        url='https://www.drawio.com/docs/reference/configure-diagram-editor/',source_class='drawio-official',
        domains=['設定・再利用'],priority='A',crawl_policy='Public primary-source documentation; structural analysis only.',
        verification=dict(verified_at='2026-10-05',status='web-visited',http_status=None,method='web.open and web.find',
            notes='Verified customTemplates object array and defaultCustomLibraries U + URL-encoded URI. No automatic editor installation tested.'),
        license=None,license_verified=False,license_scope='Analyze configuration; no reproduction license assumed.',
        summary='customTemplatesはテンプレート属性の配列。defaultCustomLibrariesはU付きURLエンコードURI。templateFileは全一覧の置換。',example_links=[]))
data['additional_count']=len(data['sources'])-data['seed_count'];data['source_count']=len(data['sources'])
for name in ('source-registry.json','source-registry.yaml'):
    (BASE/'sources'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
with (BASE/'sources/url-list.tsv').open('w',encoding='utf-8-sig',newline='') as stream:
    writer=csv.writer(stream,delimiter='\t');writer.writerow(['ID','名称','URL','確認状況','確認日','利用条件'])
    for source in data['sources']:
        writer.writerow([source['id'],source['title'],source['url'],source['verification']['status'],
                         source['verification']['verified_at'],source['license_scope']])
source=BASE/'sources/user-specification.txt'
(BASE/'sources/user-input.json').write_text(json.dumps(dict(input_time=None,input_time_status='取得不可',
    recorded_at='2026-10-05T06:36:31+09:00',source='user-specification.txt',sha256=hashlib.sha256(source.read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Registered {len(data["sources"])} URLs and the preserved input hash')
