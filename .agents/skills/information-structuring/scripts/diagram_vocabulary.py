"""Retrieve a small set of reviewed explanation patterns, independently of shapes."""
import argparse
import json
import re
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / 'references/drawio/diagram-vocabulary.json'
FIELDS = ('purpose', 'domain', 'audience', 'information_structure', 'diagram_type',
          'composition_pattern', 'visual_pattern', 'relationships', 'density', 'context')
ALIASES = {
    'チーム': ['team', '担当'], '工程': ['phase', 'process', '工程'],
    '担当': ['responsibility', 'role', 'swimlane', '担当'],
    '時間': ['time', 'timeline', '時間'], '依存': ['dependency', '依存'],
    '境界': ['boundary', 'containment', '境界'], '原因': ['cause', 'fishbone', '因果'],
    '状態': ['state', 'status', '状態'], '比較': ['comparison', 'before-after', '比較'],
    '画面': ['screenshot', 'annotated', '画面'], '処理': ['flow', 'pipeline', '処理'],
    '階層': ['hierarchy', 'layer', '階層'], '要求': ['requirement', 'trace', '要求'],
    '管理職': ['manager', 'executive'], '関係': ['relation', 'graph', '関係'],
    'architecture': ['architecture', '構成', 'software', 'infrastructure'],
}


def terms(value):
    tokens = set(re.findall(r'[a-z0-9]+|[\u3040-\u30ff\u3400-\u9fff]+', str(value).lower()))
    for key, values in ALIASES.items():
        if key in str(value).lower(): tokens.update(values)
    return tokens


def field(entry, name):
    if name == 'density': return entry['visual']['density']
    if name == 'context': return entry.get('presentation_context', entry['audience'])
    return entry.get(name, '')


def search(entries, query='', limit=5, core_only=False, **requirements):
    """A transparent lexical ranking; scores are not probabilities or quality scores."""
    scored = []
    for entry in entries:
        if entry['quality']['status'] != 'accepted': continue
        if core_only and not entry['core']: continue
        matched = []; score = 0
        text = json.dumps({k: field(entry,k) for k in FIELDS}, ensure_ascii=False).lower()
        text += ' ' + ' '.join([entry['title_ja'],entry['title_en'],*entry['tags']]).lower()
        for token in terms(query):
            if token in text: score += 1; matched.append('query:' + token)
        for name, value in requirements.items():
            if not value: continue
            content = str(field(entry, name)).lower()
            hits = [t for t in terms(value) if t in content]
            if hits: score += 3 * len(hits); matched.append(name + ':' + ','.join(sorted(hits)))
        if score or (not query and not any(requirements.values())):
            scored.append((entry,score,matched))
    # Core is preferred only within equal relevance; irrelevant core never suppresses a match.
    scored.sort(key=lambda item: (-item[1],not item[0]['core'],item[0]['id']))
    return [dict(id=e['id'],title=e['title_ja'],pattern=e['composition_pattern'],score=s,
                 matched_fields=m,core=e['core'],variant_of=e['variant_of'],
                 purpose=e['purpose'],when_to_use=e['when_to_use'],when_not_to_use=e['when_not_to_use'],
                 artifact=e['artifact'],metadata=e['artifact'].replace('example.drawio','metadata.yaml'),
                 preview=e['artifact'].replace('example.drawio','preview.png'),source_refs=e['source_refs'])
            for e,s,m in scored[:limit]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='')
    parser.add_argument('--catalog', type=Path, default=DEFAULT)
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--core-only', action='store_true', help='Search core first; expand if its patterns do not fit')
    for name in FIELDS: parser.add_argument('--'+name.replace('_','-'), default='')
    args = parser.parse_args()
    if not 1 <= args.limit <= 20: parser.error('limit must be 1..20')
    data = json.loads(args.catalog.read_text(encoding='utf-8'))
    candidates = search(data['entries'],args.query,args.limit,args.core_only,**{k:getattr(args,k) for k in FIELDS})
    print(json.dumps(dict(candidates=candidates,score_kind='lexical matching, not probability',
                         no_match='カタログ外の構成を検討する' if not candidates else None),ensure_ascii=False,indent=2))
