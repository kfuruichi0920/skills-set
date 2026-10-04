"""Validate coverage, source locations, crops, and generated documents. Requires Pillow."""

import argparse
from collections import Counter
import json
from pathlib import Path

from PIL import Image, ImageChops

from build_catalog import ROOT, documents


def validate(root=ROOT):
    data = json.loads((root / 'references/catalog.json').read_text(encoding='utf-8'))
    samples = data['samples']
    assert len(samples) == 61, 'Expected 61 samples'
    assert Counter(s['kind'] for s in samples) == {'base': 48, 'variant': 11, 'principle': 2}
    assert len({s['id'] for s in samples}) == 61, 'Duplicate IDs'
    assert len({s['name'] for s in samples}) == 61, 'Duplicate labels'
    base = [s['type_number'] for s in samples if s['kind'] == 'base']
    assert sorted(base) == list(range(1, 49)), 'Base types must cover 01-48 exactly once'
    assert Counter(s['type_number'] for s in samples if s['kind'] == 'variant') == {
        1: 1, 2: 1, 7: 1, 9: 1, 19: 1, 21: 1, 24: 1, 25: 1, 45: 3,
    }, 'Variant coverage mismatch'
    assert Counter(s['group'] for s in samples) == {
        '決めさせる': 8, '分解する': 10, '比べる': 11, '変化を見せる': 4,
        '関係と位置で見せる': 14, '時間と工程で見せる': 7,
        '構造を地図化する': 5, '全型に効く原則': 2,
    }
    expected_rows = {'front': [5, 3, 5, 5, 5, 5, 1], 'back': [4, 6, 6, 2, 6, 1, 5, 2]}
    expected_positions = {(page, row, col) for page, rows in expected_rows.items()
                          for row, count in enumerate(rows, 1) for col in range(1, count + 1)}
    actual_positions = {(s['source']['page'], s['source']['row'], s['source']['column']) for s in samples}
    assert actual_positions == expected_positions, 'Missing or extra source cells'
    originals = {}
    for s in samples:
        for key in ('name', 'use', 'layout', 'encoding', 'caution', 'observation_basis'):
            assert isinstance(s[key], str) and s[key].strip(), f"Empty {key}: {s['id']}"
        number = s['type_number']
        assert number is None if s['kind'] == 'principle' else number in range(1, 49)
        assert s['source']['image'] == data['sources'][s['source']['page']]
        assert (root / s['source']['image']).resolve().is_relative_to(root.resolve())
        assert (root / s['preview']).resolve().is_relative_to(root.resolve())
        source = s['source']['image']
        if source not in originals:
            with Image.open(root / source) as original:
                originals[source] = original.copy()
        original = originals[source]
        l, t, r, b = s['source']['crop']
        assert 0 <= l < r <= original.width and 0 <= t < b <= original.height
        expected = original.crop((l, t, r, b)).convert('RGB')
        with Image.open(root / s['preview']) as preview:
            assert preview.size == expected.size
            assert ImageChops.difference(expected, preview.convert('RGB')).getbbox() is None, s['id']
    md, gallery = documents(data)
    assert (root / 'references/catalog.md').read_text(encoding='utf-8') == md, 'Stale Markdown'
    assert (root / 'assets/catalog-gallery.html').read_text(encoding='utf-8') == gallery, 'Stale HTML'
    print('PASS: 48 base + 11 variants + 2 principles; 61 source cells and exact crops; generated views match')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    validate(parser.parse_args().root)
