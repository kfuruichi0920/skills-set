"""Check coverage, reference integrity and generated framework consistency."""
import json
from pathlib import Path
from build_framework import document

ROOT = Path(__file__).resolve().parents[1]
AXES = set('identity category hierarchy part_whole relation dependency sequence time state event cause purpose responsibility location quantity risk evidence confidence trace'.split())
FORMS = set('list table tree matrix graph sequence timeline state_model flow map quantitative_chart argument'.split())
PURPOSES = set('meaning grouping decomposition comparison relationships timing process state_events causal_analysis risk_failure requirements_trace decision responsibility quantitative strategy explanation'.split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(data['schema_version'] == 1 and data['open_world'] is True, 'Open selection framework required')
    for key, expected in [('axes', AXES), ('forms', FORMS), ('purposes', PURPOSES)]:
        entries = data[key]
        require(len(entries) == len(expected) and {item['id'] for item in entries} == expected, f'{key}: missing or duplicate ID')
    for purpose in data['purposes']:
        require(set(purpose['axes']) <= AXES and purpose['axes'], f"Invalid axes: {purpose['id']}")
        require(set(purpose['forms']) <= FORMS and purpose['forms'], f"Invalid forms: {purpose['id']}")
        for key in ['name', 'question', 'methods', 'signals', 'prerequisites']:
            require(bool(purpose[key]), f"Missing {key}: {purpose['id']}")
    for axis in data['axes']:
        require(all(axis[key] for key in ['name', 'question', 'meaning']), 'Incomplete axis')
    for form in data['forms']:
        require(all(form[key] for key in ['name', 'meaning', 'caution']), 'Incomplete form')
    require(len(data['selection_layers']) == 6 and bool(data['catalog_role']), 'Missing selection layer or catalog role')


if __name__ == '__main__':
    data = json.loads((ROOT / 'references/framework.json').read_text(encoding='utf-8'))
    validate(data)
    require((ROOT / 'references/framework.md').read_text(encoding='utf-8') == document(data), 'Generated framework is stale')
    for relative in ['assets/rationale-template.md', 'assets/storyboard-template.md', 'references/selection-rules.md']:
        require((ROOT / relative).is_file(), f'Missing resource: {relative}')
    print(f"OK: 16 purposes, 19 axes, 12 forms, {sum(len(p['methods']) for p in data['purposes'])} method entries; open selection and rationale resources")
