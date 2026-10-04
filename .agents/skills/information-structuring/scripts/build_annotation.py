"""Build a layered Draw.io image annotation from an agent-prepared JSON IR."""
import argparse
import base64
import hashlib
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from theme_styles import style, theme

TYPES = {'number_marker', 'leader_line', 'arrow', 'callout', 'highlight', 'region', 'step'}
MIMES = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}


def output_path(path):
    return any(part.lower() == 'output' for part in Path(path).resolve().parts)


def check_source_access(path, allow_output_source=False, current_artifacts=()):
    """Permit only known files created in this task, or explicitly authorized sources."""
    current = {Path(item).resolve() for item in current_artifacts}
    if output_path(path) and Path(path).resolve() not in current and not allow_output_source:
        raise ValueError('Reading existing output requires explicit authorization')


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Coordinates must be finite numbers')
    return value


def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported annotation IR version')
    theme(data['theme'])
    source = data['source']
    for key in ['width', 'height']:
        if number(source[key]) <= 0:
            raise ValueError('Invalid source dimensions')
    display = data['display']
    for key in ['x', 'y', 'width', 'height']:
        number(display[key])
    if display['width'] <= 0 or display['height'] <= 0:
        raise ValueError('Invalid display dimensions')
    canvas = data['canvas']
    if any(number(canvas[key]) <= 0 for key in ['width', 'height']):
        raise ValueError('Invalid canvas dimensions')
    if display['x'] < 0 or display['y'] < 0 or display['x'] + display['width'] > canvas['width'] or display['y'] + display['height'] > canvas['height']:
        raise ValueError('Source does not fit canvas')
    if data.get('annotation_color') and not re.fullmatch(r'#[0-9a-fA-F]{6}', data['annotation_color']):
        raise ValueError('Invalid annotation color')
    if not math.isclose(display['width'] / display['height'], source['width'] / source['height'], rel_tol=0.001):
        raise ValueError('Source aspect ratio must be preserved')
    ids, markers = set(), set()
    for annotation in data['annotations']:
        identifier = annotation['id']
        if not identifier or identifier in ids:
            raise ValueError('Duplicate or empty annotation ID')
        ids.add(identifier)
        if annotation['type'] not in TYPES:
            raise ValueError('Unknown annotation type')
        if annotation.get('semantic', 'primary') not in {'primary', 'warning', 'risk', 'failure', 'success', 'neutral', 'reference'}:
            raise ValueError('Unknown annotation semantic role')
        if annotation['confidence'] not in {'high', 'medium', 'low'} or not annotation['evidence']:
            raise ValueError('Annotation confidence and evidence are required')
        target = annotation['target']
        if not target.get('label') and not target.get('stable_id'):
            raise ValueError('Target needs label or stable ID')
        for key in ['x', 'y', 'width', 'height']:
            if not 0 <= number(target[key]) <= 1:
                raise ValueError('Target outside source')
        if target['x'] + target['width'] > 1 or target['y'] + target['height'] > 1:
            raise ValueError('Target rectangle outside source')
        for key in ['x', 'y']:
            if not 0 <= number(annotation['anchor'][key]) <= 1:
                raise ValueError('Anchor outside source')
            number(annotation['label_position'][key])
        anchor = annotation['anchor']
        if not (target['x'] <= anchor['x'] <= target['x'] + target['width'] and target['y'] <= anchor['y'] <= target['y'] + target['height']):
            raise ValueError('Anchor must point inside the identified target')
        label_x = display['x'] + annotation['label_position']['x'] * display['width']
        label_y = display['y'] + annotation['label_position']['y'] * display['height']
        label_width = number(annotation.get('label_width', 260))
        label_height = number(annotation.get('label_height', 90))
        if label_width <= 0 or label_height <= 0 or label_x < 0 or label_y < 0 or label_x + label_width > canvas['width'] or label_y + label_height > canvas['height']:
            raise ValueError('Explanation label does not fit canvas')
        if annotation.get('marker_position'):
            marker = annotation['marker_position']
            mx = display['x'] + number(marker['x']) * display['width']
            my = display['y'] + number(marker['y']) * display['height']
            if not (14 <= mx <= canvas['width'] - 14 and 14 <= my <= canvas['height'] - 14):
                raise ValueError('Marker does not fit canvas')
        for point in annotation.get('leader_points', []):
            px = display['x'] + number(point['x']) * display['width']
            py = display['y'] + number(point['y']) * display['height']
            if not (0 <= px <= canvas['width'] and 0 <= py <= canvas['height']):
                raise ValueError('Leader waypoint does not fit canvas')
        marker = annotation.get('number')
        if marker is not None:
            marker = str(marker)
            if marker in markers:
                raise ValueError('Duplicate annotation number')
            markers.add(marker)


def build(data, source_path, destination, allow_output_source=False, current_artifacts=()):
    check_source_access(source_path, allow_output_source, current_artifacts)
    validate(data)
    payload = Path(source_path).read_bytes()
    mime = MIMES[Path(source_path).suffix.lower()]
    digest = hashlib.sha256(payload).hexdigest()
    if data['source'].get('sha256') and data['source']['sha256'] != digest:
        raise ValueError('Source version hash mismatch')
    data['source']['sha256'] = digest
    selected = data['theme']
    display = data['display']
    mxfile = ET.Element('mxfile', {'host': 'app.diagrams.net'})
    diagram = ET.SubElement(mxfile, 'diagram', {'id': data['view_id'], 'name': data['purpose']})
    model = ET.SubElement(diagram, 'mxGraphModel', {'page': '1', 'pageWidth': str(data['canvas']['width']), 'pageHeight': str(data['canvas']['height']), 'background': theme(selected)['palette'].get('canvas', '#FFFFFF')})
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    layers = [('1', '00_Source'), ('10', '10_Highlight'), ('20', '20_Annotation'), ('30', '30_Explanation'), ('90', '90_Guide')]
    for identifier, label in layers:
        attributes = {'id': identifier, 'value': label, 'parent': '0'}
        if identifier == '1':
            attributes['style'] = 'locked=1;'
        if identifier == '90':
            attributes['visible'] = '0'
        ET.SubElement(root, 'mxCell', attributes)

    def vertex(identifier, value, parent, vertex_style, x, y, width, height):
        cell = ET.SubElement(root, 'mxCell', {'id': identifier, 'value': value, 'parent': parent, 'vertex': '1', 'style': vertex_style})
        ET.SubElement(cell, 'mxGeometry', {'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height), 'as': 'geometry'})
        return cell

    def transform(position):
        return display['x'] + position['x'] * display['width'], display['y'] + position['y'] * display['height']

    # Draw.io uses the image MIME and base64 payload without a ';base64' style separator.
    embedded = f'data:{mime},' + base64.b64encode(payload).decode('ascii')
    source_style = 'shape=image;imageAspect=1;aspect=fixed;locked=1;movable=0;resizable=0;editable=0;image=' + embedded + ';'
    vertex('source-image', '', '1', source_style, **display)
    for annotation in data['annotations']:
        prefix = 'ann-' + annotation['id']
        target = annotation['target']
        x, y = transform(target)
        ax, ay = transform(annotation['anchor'])
        lx, ly = transform(annotation['label_position'])
        semantic = annotation.get('semantic', 'primary')
        palette = theme(selected)['palette']
        annotation_color = {
            'primary': data.get('annotation_color') or palette.get('primary', palette.get('accent', '#2563EB')),
            'warning': '#D97706', 'risk': '#D97706', 'failure': '#DC2626',
            'success': '#24A148', 'neutral': '#6B7280', 'reference': '#6B7280',
        }[semantic]
        shape_semantic = 'neutral' if semantic == 'reference' else semantic
        marker = str(annotation.get('number', annotation['id']))
        if annotation['type'] in {'highlight', 'region'}:
            highlight = style(selected, shape='boundary', semantic=shape_semantic, logical_boundary=True) + f'strokeColor={annotation_color};'
            vertex(prefix + '-region', annotation['title'] if annotation['type'] == 'region' else '', '10', highlight, x, y, target['width'] * display['width'], target['height'] * display['height'])
        mx, my = transform(annotation.get('marker_position', annotation['anchor']))
        vertex(prefix + '-marker', marker, '20', style(selected, shape='event', semantic=shape_semantic) + f'align=center;whiteSpace=nowrap;fontSize=12;spacing=0;spacingLeft=0;spacingRight=0;aspect=fixed;strokeColor={annotation_color};', mx - 14, my - 14, 28, 28)
        caution = '（推定・要確認）' if annotation['confidence'] == 'low' else ''
        text = marker + ' ' + annotation['title'] + caution + '\n' + annotation.get('description', '')
        label_id = prefix + '-explanation'
        vertex(label_id, text, '30', style(selected, shape='note', semantic='neutral'), lx, ly, annotation.get('label_width', 260), annotation.get('label_height', 90))
        edge = ET.SubElement(root, 'mxCell', {'id': prefix + '-leader', 'value': '注釈', 'parent': '20', 'edge': '1', 'source': label_id, 'style': style(selected, connector='dependency') + f'strokeColor={annotation_color};' + ('endArrow=block;' if annotation['type'] in {'arrow', 'step'} else 'endArrow=none;')})
        geometry = ET.SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        ET.SubElement(geometry, 'mxPoint', {'x': str(ax), 'y': str(ay), 'as': 'targetPoint'})
        if annotation.get('leader_points'):
            points = ET.SubElement(geometry, 'Array', {'as': 'points'})
            for point in annotation['leader_points']:
                px, py = transform(point)
                ET.SubElement(points, 'mxPoint', {'x': str(px), 'y': str(py)})
    for index, block in enumerate(data.get('explanation_blocks', []) + data.get('legend', [])):
        vertex(f'explanation-{index}', block['text'], '30', style(selected, shape='label'), block['x'], block['y'], block['width'], block['height'])
    ET.indent(mxfile, space='  ')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as handle:
        ET.ElementTree(mxfile).write(handle, encoding='utf-8', xml_declaration=True)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ir', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--allow-output-source', action='store_true', help='Use only with explicit user authorization to read the specified output source')
    parser.add_argument('--current-artifact', action='append', type=Path, default=[], help='Exact path of a file created in this task; repeat for IR and source, never designate pre-existing files')
    args = parser.parse_args()
    check_source_access(args.ir, args.allow_output_source, args.current_artifact)
    data = json.loads(args.ir.read_text(encoding='utf-8'))
    source_path = (args.ir.parent / data['source']['path']).resolve()
    result = build(data, source_path, args.destination, args.allow_output_source, args.current_artifact)
    print(json.dumps({'source_sha256': result['source']['sha256'], 'annotations': len(result['annotations']), 'visual_qa': 'pending'}, ensure_ascii=False))
