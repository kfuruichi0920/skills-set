"""Validate theme coverage, style generation and the editable Draw.io example."""
import re
import xml.etree.ElementTree as ET
from theme_styles import DATA, ROOT, THEMES, SHAPES, CONNECTORS, ALIASES, style


def require(condition, message):
    if not condition:
        raise ValueError(message)


def properties(value):
    return dict(part.split('=', 1) for part in value.split(';') if '=' in part)


def validate():
    expected = {f'T{index:02}' for index in range(1, 11)}
    require(len(DATA['themes']) == 10 and set(THEMES) == expected, 'Missing or duplicate theme')
    require(DATA['default_theme'] == 'T01', 'Invalid default theme')
    require(DATA['selection_order'] == ['T04', 'T03', 'T05', 'T06', 'T07', 'T02', 'T08', 'T09', 'T10', 'T01'], 'Invalid selection precedence')
    for theme_id, theme in THEMES.items():
        require(all(theme[field] for field in ['name', 'use', 'character', 'palette']), f'Incomplete {theme_id}')
        require(all(re.fullmatch(r'#[0-9A-Fa-f]{6}', value) for value in theme['palette'].values()), 'Invalid palette color')
        for shape in SHAPES:
            for semantic in ALIASES:
                values = properties(style(theme_id, shape=shape, semantic=semantic))
                require(values['shadow'] == '0' and values['gradientColor'] == 'none', 'Decorative style')
        require(properties(style(theme_id, shape='component'))['rounded'] == '0', 'Component rounded by default')
        require(properties(style(theme_id, shape='decision'))['shape'] == 'rhombus', 'Decision notation lost')
        for connector in CONNECTORS:
            values = properties(style(theme_id, connector=connector))
            require(values['edgeStyle'] == 'orthogonalEdgeStyle' and values['curved'] == '0', 'Unexpected edge layout')
        require(properties(style(theme_id, connector='dependency'))['dashed'] == '1', 'Dependency notation lost')
        require(properties(style(theme_id, connector='structural'))['endArrow'] == 'none', 'Structure given flow notation')
    path = ROOT / 'assets/drawio-examples/catalog-layouts.drawio'
    diagrams = ET.parse(path).getroot().findall('diagram')
    require(len(diagrams) == 2, 'Missing Draw.io example page')
    for diagram in diagrams:
        cells = diagram.findall('mxGraphModel/root/mxCell')
        ids = [cell.get('id') for cell in cells]
        require(len(ids) == len(set(ids)), 'Duplicate Draw.io cell')
        require('theme-legend' in ids, 'Missing theme legend')
        for cell in cells:
            for key in ['parent', 'source', 'target']:
                require(not cell.get(key) or cell.get(key) in ids, f'Unknown {key}')
            if cell.get('vertex') == '1' or cell.get('edge') == '1':
                require(cell.find('mxGeometry') is not None, 'Missing geometry')
                values = properties(cell.get('style', ''))
                require(values.get('shadow') == '0' and values.get('glass') == '0', 'Example not themed')
    print('OK: 10 themes; selection precedence; semantic shape/connector styles; 2 themed Draw.io pages')


if __name__ == '__main__':
    validate()
