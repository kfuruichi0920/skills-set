"""Translate a selected theme and explicit semantic roles to Draw.io styles."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'references/diagram-themes.json').read_text(encoding='utf-8'))
THEMES = {theme['id']: theme for theme in DATA['themes']}
SHAPES = {
    'component': {'shape': 'rectangle', 'rounded': '0'},
    'process': {'shape': 'rectangle', 'rounded': '1', 'arcSize': '8'},
    'boundary': {'shape': 'rectangle', 'rounded': '0', 'fillColor': 'none'},
    'database': {'shape': 'cylinder'},
    'document': {'shape': 'document'},
    'decision': {'shape': 'rhombus'},
    'event': {'shape': 'ellipse'},
    'actor': {'shape': 'umlActor'},
    'external_service': {'shape': 'cloud'},
    'policy': {'shape': 'hexagon'},
    'note': {'shape': 'note'},
    'label': {'shape': 'text', 'strokeColor': 'none', 'fillColor': 'none'},
}
CONNECTORS = {
    'flow': {'endArrow': 'block'},
    'structural': {'endArrow': 'none'},
    'dependency': {'dashed': '1', 'endArrow': 'block'},
    'optional': {'dashed': '1', 'dashPattern': '1 4', 'endArrow': 'none'},
    'main_flow': {'endArrow': 'block', 'strokeWidth': '2.5'},
    'main_dependency': {'dashed': '1', 'endArrow': 'block', 'strokeWidth': '2.5'},
    'mutual': {'startArrow': 'block', 'endArrow': 'block'},
    'failure': {'endArrow': 'block'},
    'failure_dependency': {'dashed': '1', 'endArrow': 'block'},
    'secondary': {'endArrow': 'block'},
}
ALIASES = {
    'neutral': ['surface', 'internal', 'neutral', 'light-gray', 'server', 'unknown'],
    'primary': ['primary-light', 'target', 'controlled', 'highlight', 'analysis', 'note-blue'],
    'external': ['external', 'surface-2', 'source'],
    'planned': ['planned'], 'progress': ['progress'],
    'done': ['done', 'success', 'evidence', 'note-green'],
    'success': ['success', 'done', 'evidence', 'trusted', 'note-green'],
    'attention': ['attention', 'warning', 'uncertain', 'note-yellow'],
    'warning': ['warning', 'attention', 'uncertain', 'note-yellow'],
    'risk': ['risk', 'warning'],
    'failure': ['failure', 'error', 'problem', 'critical', 'rejected', 'note-red'],
    'decision': ['decision', 'hypothesis', 'note-purple'],
    'source': ['source'], 'analysis': ['analysis'], 'hypothesis': ['hypothesis'],
    'evidence': ['evidence'], 'uncertain': ['uncertain'], 'rejected': ['rejected'],
    'trusted': ['trusted'], 'controlled': ['controlled'], 'unknown': ['unknown'],
    'threat': ['threat'], 'critical': ['critical'],
    'network': ['network'], 'control': ['control'], 'data': ['network'],
}
FALLBACK = {
    'neutral': '#FFFFFF', 'primary': '#EDF5FF', 'external': '#F2F2F2',
    'planned': '#DCDFE4', 'progress': '#DBEAFE', 'done': '#DCFCE7',
    'success': '#DCFCE7', 'attention': '#FEF3C7', 'warning': '#FEF3C7',
    'risk': '#FCA700', 'failure': '#FEE2E2', 'decision': '#EDE9FE',
    'source': '#E2E8F0', 'analysis': '#DBEAFE', 'hypothesis': '#EDE9FE',
    'evidence': '#DCFCE7', 'uncertain': '#FEF3C7', 'rejected': '#FEE2E2',
    'trusted': '#DCFCE7', 'controlled': '#DBEAFE', 'unknown': '#F3F4F6',
    'threat': '#FEE2E2', 'critical': '#FEE2E2',
    'network': '#DBEAFE', 'control': '#EDE9FE', 'data': '#DBEAFE',
}


def theme(theme_id):
    return THEMES[theme_id]


def palette_value(palette, keys, fallback):
    return next((palette[key] for key in keys if key in palette), fallback)


def readable_text(foreground, background):
    def luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    def contrast(first, second):
        high, low = sorted((luminance(first), luminance(second)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    if contrast(foreground, background) >= 4.5:
        return foreground
    return max(('#161616', '#FFFFFF'), key=lambda candidate: contrast(candidate, background))


def style(theme_id, shape=None, semantic='neutral', connector=None, logical_boundary=False):
    if (shape is None) == (connector is None):
        raise ValueError('Specify exactly one shape or connector')
    palette = theme(theme_id)['palette']
    if semantic not in ALIASES:
        raise ValueError(f'Unknown semantic role: {semantic}')
    primary = palette_value(palette, ['primary', 'accent', 'network', 'progress'], '#2563EB')
    border = palette_value(palette, ['border', 'line', 'secondary', 'gray'], '#666666')
    text = palette_value(palette, ['text', 'navy', 'line'], '#222222')
    values = {'whiteSpace': 'wrap', 'html': '0', 'fontFamily': 'sans-serif',
              'fontSize': '16', 'fontColor': text, 'shadow': '0', 'glass': '0',
              'gradientColor': 'none', 'strokeWidth': '1.5'}
    if shape is not None:
        values.update({'fillColor': palette_value(palette, ALIASES[semantic], FALLBACK[semantic]),
                       'strokeColor': primary if semantic == 'primary' else border,
                       'align': 'left', 'verticalAlign': 'middle', 'spacingLeft': '8'})
        values.update(SHAPES[shape])
        if values['fillColor'] != 'none':
            values['fontColor'] = readable_text(text, values['fillColor'])
        if logical_boundary:
            if shape != 'boundary':
                raise ValueError('Logical boundary applies to boundary shapes only')
            values.update({'dashed': '1', 'strokeWidth': '1'})
    else:
        color = border
        if connector.startswith('failure'):
            color = palette_value(palette, ['failure', 'error', 'problem', 'critical'], '#DC2626')
        elif connector.startswith('main'):
            color = primary
        elif connector == 'secondary':
            color = '#6B7280'
        elif semantic in {'control', 'data', 'network'}:
            color = palette_value(palette, ALIASES[semantic], '#7C3AED' if semantic == 'control' else primary)
        values.update({'edgeStyle': 'orthogonalEdgeStyle', 'rounded': '0',
                       'curved': '0', 'strokeColor': color, 'align': 'center', 'fontSize': '12'})
        values.update(CONNECTORS[connector])
    return ';'.join(f'{key}={value}' for key, value in values.items()) + ';'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=THEMES, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--shape', choices=SHAPES)
    group.add_argument('--connector', choices=CONNECTORS)
    parser.add_argument('--semantic', choices=ALIASES, default='neutral')
    parser.add_argument('--logical-boundary', action='store_true')
    args = parser.parse_args()
    print(style(args.theme, args.shape, args.semantic, args.connector, args.logical_boundary))
