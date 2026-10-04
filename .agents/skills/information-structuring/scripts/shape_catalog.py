"""Discover real Draw.io assets, search verified shapes, resolve IR and render XML.

Python standard library; schema validation command also needs jsonschema.
Never evaluates JavaScript. Bundled stencils are decoded as data only.
"""
import argparse
import base64
import copy
import fnmatch
import hashlib
import json
import re
import struct
import unicodedata
import zlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, unquote_to_bytes

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / 'references/drawio'
PRIMITIVES = {'rectangle', 'ellipse', 'text', 'image', 'cylinder', 'document',
              'rhombus', 'umlActor', 'cloud', 'hexagon', 'note', 'swimlane',
              'table', 'tableRow', 'partialRectangle', 'line'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def safe_root(path):
    path = Path(path).resolve()
    if 'output' in {p.lower() for p in path.parts}:
        raise ValueError('Existing output is not a catalog discovery root. Copy explicitly authorized assets outside output first.')
    return path


def decode_model(value):
    if not value.lstrip().startswith('<'):
        value = unquote(zlib.decompress(base64.b64decode(value), -15).decode())
    model = ET.fromstring(value)
    if model.tag != 'mxGraphModel':
        raise ValueError('Custom library XML must contain mxGraphModel')
    return model


def asar_assets(path):
    """Read ASAR header and logical files without unpacking or executing them."""
    with path.open('rb') as stream:
        header = struct.unpack('<4I', stream.read(16))
        tree = json.loads(stream.read(header[3]))
        def walk(node, prefix=''):
            for name, item in node.get('files', {}).items():
                logical = prefix+name
                if 'files' in item:
                    yield from walk(item, logical+'/')
                elif not item.get('unpacked') and 'offset' in item:
                    yield logical, item
        files = dict(walk(tree))
        def get(name):
            item = files[name]
            stream.seek(8+header[1]+int(item['offset']))
            return stream.read(item['size'])
        version = json.loads(get('package.json')).get('version', 'unknown')
        for name in sorted(files):
            if '/stencils/' in name and name.endswith('.xml'):
                yield name, get(name), version
            elif name.endswith('/stencils.min.js'):
                script = get(name).decode()
                matches = re.findall(r"f\['([^']+)'\]\s*=\s*'([A-Za-z0-9+/=]+)';", script)
                if not matches:
                    raise ValueError('Unsupported bundled stencil encoding')
                for logical, encoded in matches:
                    yield 'stencils/'+logical, zlib.decompress(base64.b64decode(encoded), -15), version


def discover(root, includes, excludes):
    root = safe_root(root)
    assets = asar_assets(root) if root.suffix == '.asar' else (
        (p.relative_to(root).as_posix(), p.read_bytes(), 'unknown')
        for p in sorted(root.rglob('*.xml')) if 'output' not in {s.lower() for s in p.relative_to(root).parts})
    for name, data, version in assets:
        def matches(pattern):
            return fnmatch.fnmatch(name, pattern) or (pattern.startswith('**/') and fnmatch.fnmatch(name, pattern[3:]))
        if any(matches(p) for p in (includes or ['*.xml'])) and not any(matches(p) for p in excludes):
            yield name, data, version


def generate(args):
    previous = read(args.previous) if args.previous else None
    shapes, libraries, seen, fingerprints, versions = [], {}, set(), {}, set()
    for source_type, roots in [('builtin_stencil', args.builtin), ('custom_library', args.custom)]:
        for root in roots:
            for name, data, version in discover(root, args.include, args.exclude):
                versions.add(version)
                xml = ET.fromstring(data)
                source = f'{Path(root).name}:{name}'
                digest = hashlib.sha256(data).hexdigest()
                fingerprints[source] = digest
                if source_type == 'builtin_stencil':
                    sets = [xml] if xml.tag == 'shapes' else xml.findall('shapes')
                    if not sets:
                        raise ValueError(f'Unsupported stencil: {source}')
                    for group in sets:
                        ns = group.get('name', '').lower()
                        if not ns:
                            raise ValueError(f'Missing namespace: {source}')
                        lib = ns.removeprefix('mxgraph.')
                        libraries.setdefault(lib, dict(id=lib, namespace=ns, source_type=source_type,
                            display_name=lib, domain=[], source_files=[], shape_count=0))
                        if source not in libraries[lib]['source_files']:
                            libraries[lib]['source_files'].append(source)
                        for shape in group.findall('shape'):
                            original = shape.attrib['name']
                            # Draw.io parseStencilSet: spaces -> underscores, then lowercase.
                            canonical = original.replace(' ', '_').lower()
                            identifier = ns+'.'+canonical
                            entry = dict(id=identifier, library=lib, namespace=ns, shape_name=original,
                                canonical_name=canonical, source_type=source_type, source_file=source,
                                source_sha256=digest, width=float(shape.get('w',80)), height=float(shape.get('h',80)),
                                aspect=shape.get('aspect','variable'),
                                connection_points=[dict(c.attrib) for c in shape.findall('./connections/constraint')],
                                tags=re.findall(r'\w+', original.lower()), aliases=[], semantic_categories=[],
                                vendor=None, verified=True, asset_type='shape')
                            if identifier in seen:
                                prior = next(s for s in shapes if s['id'] == identifier)
                                if prior['source_file'] != source:
                                    raise ValueError(f'Conflicting stencil sources: {identifier}')
                                entry['duplicate_definition'] = 'Last definition in same source, matching registry overwrite'
                                shapes.remove(prior)
                                libraries[lib]['shape_count'] -= 1
                            seen.add(identifier); shapes.append(entry); libraries[lib]['shape_count'] += 1
                else:
                    if xml.tag != 'mxlibrary':
                        raise ValueError(f'Invalid custom library: {source}')
                    lib = 'custom:'+Path(root).stem+':'+Path(name).with_suffix('').as_posix()
                    libraries[lib] = dict(id=lib, namespace=lib, display_name=lib, source_type=source_type,
                        domain=[], source_files=[source], shape_count=0)
                    for i, asset in enumerate(json.loads(xml.text or '[]')):
                        identifier = f'{lib}:{i}'
                        if identifier in seen: raise ValueError(f'Duplicate custom ID: {identifier}')
                        seen.add(identifier)
                        if 'xml' in asset:
                            model = decode_model(asset['xml'])
                            cells = model.findall('./root/mxCell')
                            kind = 'fragment' if any(c.get('edge') for c in cells) else 'group'
                        elif 'data' in asset:
                            if not asset['data'].startswith('data:image/'):
                                raise ValueError('Custom images must be embedded image data')
                            kind = 'image'
                        else: raise ValueError(f'Unknown custom entry: {identifier}')
                        title = asset.get('title', str(i))
                        shapes.append(dict(id=identifier, library=lib, namespace=lib, shape_name=title,
                            canonical_name=str(i), source_type=source_type, source_file=source,
                            source_sha256=digest, width=float(asset.get('w',80)), height=float(asset.get('h',80)),
                            aspect='variable', connection_points=[], tags=[], aliases=[], semantic_categories=[],
                            vendor=None, verified=True, asset_type=kind, payload=asset))
                        libraries[lib]['shape_count'] += 1
    raw = dict(catalog_version='1', generated_at=datetime.now(timezone.utc).isoformat(),
        drawio_source_version=','.join(sorted(versions-{'unknown'})) or 'unknown', source_fingerprints=fingerprints,
        libraries=sorted(libraries.values(),key=lambda x:x['id']), shapes=sorted(shapes,key=lambda x:x['id']))
    resolved = copy.deepcopy(raw)
    metadata = read(args.metadata)
    ids = {s['id'] for s in shapes}
    for identifier in metadata.get('shapes', {}):
        if identifier not in ids: raise ValueError(f'Unknown metadata target: {identifier}')
        allowed = {'aliases','semantic_categories','tags','vendor','asset_type','priority','deprecated','recommended_usage'}
        if set(metadata['shapes'][identifier])-allowed:
            raise ValueError(f'Curated metadata may not overwrite verified identity: {identifier}')
    for shape in resolved['shapes']:
        for rule in metadata.get('rules', []):
            if re.search(rule['pattern'], shape['id']):
                for field in ('aliases','semantic_categories','tags'):
                    shape[field] = sorted(set(shape[field]+rule.get(field, [])))
                if rule.get('vendor'): shape['vendor'] = rule['vendor']
        shape.update(metadata.get('shapes', {}).get(shape['id'], {}))
    registry = read(CAT/'library-registry.json')
    for lib in resolved['libraries']:
        lib['domain'] = [d for d, names in registry.items() if any(fnmatch.fnmatch(lib['id'], n) for n in names)]
    validate(resolved)
    out = Path(args.destination)
    write(out/'shape-catalog.raw.json', raw)
    write(out/'shape-catalog.json', resolved)
    write(out/'library-catalog.json', resolved['libraries'])
    if args.previous:
        old = previous
        a,b = ({s['id']:s for s in c['shapes']} for c in (old,resolved))
        la,lb=({s['id'] for s in c['libraries']} for c in (old,resolved))
        write(out/'catalog-diff.json', dict(added=sorted(b.keys()-a.keys()), removed=sorted(a.keys()-b.keys()),
            changed=[i for i in sorted(a.keys()&b.keys()) if a[i]!=b[i]],
            libraries_added=sorted(lb-la), libraries_removed=sorted(la-lb),
            note='Rename/namespace changes appear as removed+added; compare names and source files before migrating.'))
    print(f'Generated {len(shapes)} shapes / {len(libraries)} libraries from {len(fingerprints)} assets')


def validate(catalog):
    import jsonschema
    try:
        jsonschema.validate(catalog,read(CAT/'shape-catalog.schema.json'))
    except jsonschema.ValidationError as error:
        raise ValueError(f'Schema validation failed: {error.message}') from error
    libs={l['id']:l for l in catalog['libraries']}
    if len(libs)!=len(catalog['libraries']): raise ValueError('Duplicate libraries')
    ids=set(); keys=set()
    for shape in catalog['shapes']:
        key=(shape['library'],shape['canonical_name'])
        if shape['id'] in ids or key in keys: raise ValueError('Duplicate ID/canonical key')
        ids.add(shape['id']); keys.add(key)
        if shape['library'] not in libs or not shape['verified']: raise ValueError('Unverified or missing library')
        if shape['width']<=0 or shape['height']<=0: raise ValueError('Invalid dimensions')
    for lib in libs.values():
        if lib['shape_count']!=sum(s['library']==lib['id'] for s in catalog['shapes']):
            raise ValueError('Library count mismatch')


def norm(value):
    return unicodedata.normalize('NFKC',value).casefold().replace('_',' ')


def search(catalog, query, semantic='', domain='', preferred=(), vendor='', limit=8, libraries_filter=()):
    libraries={l['id']:l for l in catalog['libraries']}
    result=[]; q=norm(query)
    for s in catalog['shapes']:
        if not s['verified'] or s.get('deprecated'): continue
        if libraries_filter and s['library'] not in libraries_filter: continue
        if domain and domain not in libraries[s['library']]['domain']: continue
        if vendor and s.get('vendor')!=vendor: continue
        words=[s['shape_name'],s['canonical_name'],*s['aliases'],*s['tags'],*s['semantic_categories'],s['library'],s.get('vendor') or '']
        exact=any(norm(w)==q for w in words)
        token=bool(q) and any(q in norm(w) for w in words)
        meaning=bool(semantic) and semantic in s['semantic_categories']
        if not (exact or token or meaning): continue
        score=(int(meaning),int(s['library'] in preferred),int(bool(domain)),int(bool(vendor)),int(exact),int(token),s.get('priority',0))
        result.append((score,s))
    result.sort(key=lambda x:(tuple(-v for v in x[0]),x[1]['id']))
    return [dict(shape_id=s['id'],library=s['library'],name=s['shape_name'],asset_type=s['asset_type'],
        semantic_categories=s['semantic_categories'],score=list(score),verified=True) for score,s in result[:limit]]


def exact(catalog, identifier):
    match=next((s for s in catalog['shapes'] if s['id']==identifier and s['verified']), None)
    if match is None: raise ValueError(f'Unknown/unverified shape: {identifier}')
    return match


def resolve(catalog, ir):
    result=copy.deepcopy(ir)
    for node in result.get('nodes',[]):
        identifier=node.get('shape_id')
        if identifier:
            s=exact(catalog,identifier)
            if s.get('vendor') and s['vendor']!=node.get('vendor'):
                raise ValueError('Vendor shape requires explicit matching vendor evidence')
            node['resolved']=dict(shape_id=identifier,library=s['library'],verified=True,reason='Explicit catalog candidate')
        elif node.get('primitive'):
            if node['primitive'] not in PRIMITIVES: raise ValueError('Unknown primitive')
            if not node.get('fallback_reason'): raise ValueError('Primitive needs native choice/fallback reason')
            node['resolved']=dict(primitive=node['primitive'],verified=True,reason=node['fallback_reason'])
        else:
            candidates=search(catalog,node['shape_query'],node.get('semantic_type',''),node.get('domain',''),node.get('preferred_libraries',[]),node.get('vendor',''))
            node['candidates']=candidates
            # Deliberately requires planner confirmation to avoid treating rank as semantic proof.
            raise ValueError(f"Select an exact shape_id for {node['id']} from: {candidates}")
    return result


def validate_xml(document, catalog):
    for page in document.findall('diagram'):
        cells=page.findall('./mxGraphModel/root/mxCell'); ids={c.attrib['id'] for c in cells}
        if len(ids)!=len(cells): raise ValueError('Duplicate cell IDs')
        for c in cells:
            for attr in ('parent','source','target'):
                if c.get(attr) and c.get(attr) not in ids: raise ValueError(f'Broken {attr}')
            for token in c.get('style','').split(';'):
                if token.startswith('shape=mxgraph.'): exact(catalog,token[6:])
                elif token.startswith('shape=') and token[6:] not in PRIMITIVES:
                    raise ValueError(f'Unregistered renderer shape: {token}')


def render(catalog, ir, destination):
    from theme_styles import style, theme
    ir=resolve(catalog,ir) # Exact revalidation at renderer boundary.
    selected=ir['metadata']['theme']
    doc=ET.Element('mxfile',host='app.diagrams.net')
    page=ET.SubElement(doc,'diagram',id=ir['id'],name=ir['metadata']['title'])
    model=ET.SubElement(page,'mxGraphModel',page='1',pageWidth=str(ir.get('width',1280)),pageHeight=str(ir.get('height',820)),background=theme(selected)['palette'].get('canvas','#FFFFFF'))
    root=ET.SubElement(model,'root'); ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
    def vertex(n,sty):
        cell=ET.SubElement(root,'mxCell',id=n['id'],value=n.get('label',''),parent=n.get('parent','1'),vertex='1',style=sty)
        ET.SubElement(cell,'mxGeometry',**{k:str(n[k]) for k in ('x','y','width','height')},**{'as':'geometry'})
        return cell
    for n in ir.get('containers',[]):
        vertex(n,style(selected,shape='boundary')+'shape=swimlane;container=1;collapsible=1;startSize=36;horizontal=1;')
    for n in ir['nodes']:
        resolved=n['resolved']; sty=style(selected,shape='label' if resolved.get('primitive')=='text' else 'component',semantic=n.get('role','neutral'))
        if 'shape_id' in resolved:
            s=exact(catalog,resolved['shape_id'])
            if s['source_type']=='custom_library':
                payload=s['payload']
                if 'xml' in payload:
                    fragment=decode_model(payload['xml']); old=fragment.findall('./root/mxCell')
                    mapping={c.get('id'):n['id']+'__'+c.get('id') for c in old if c.get('id') not in ('0','1')}
                    vertex(n,'group;container=1;')
                    for cell in old:
                        if cell.get('id') in ('0','1'): continue
                        cell=copy.deepcopy(cell); cell.set('id',mapping[cell.get('id')])
                        for attr in ('parent','source','target'):
                            if cell.get(attr): cell.set(attr,mapping.get(cell.get(attr),n['id']))
                        root.append(cell)
                    continue
                header, encoded = payload['data'].split(',', 1)
                data = base64.b64decode(encoded) if ';base64' in header else unquote_to_bytes(encoded)
                mime = header.split(';', 1)[0]
                sty+='shape=image;image='+mime+','+base64.b64encode(data).decode()+';imageAspect=1;'
            else:
                sty+='shape='+s['id']+';'
                if s.get('vendor') and not n.get('vendor_style_reason'):
                    raise ValueError('Vendor shape needs explicit identity palette/style rationale')
        else: sty+='shape='+resolved['primitive']+';'
        vertex(n,sty+n.get('style',''))
    for table in ir.get('tables',[]):
        rows=table['rows']; widths=table['column_widths']; height=table.get('row_height',42)
        vertex(dict(id=table['id'],label='',parent=table.get('parent','1'),x=table['x'],y=table['y'],width=sum(widths),height=height*len(rows)),
            'shape=table;container=1;collapsible=0;startSize=0;childLayout=tableLayout;fixedHeader=1;')
        for i,row in enumerate(rows):
            rid=table['id']+f'_r{i}'
            vertex(dict(id=rid,label='',parent=table['id'],x=0,y=i*height,width=sum(widths),height=height),
                'shape=tableRow;container=1;collapsible=0;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;fillColor=none;')
            x=0
            for j,value in enumerate(row):
                vertex(dict(id=rid+f'_c{j}',label=value,parent=rid,x=x,y=0,width=widths[j],height=height),
                    style(selected,shape='component',semantic='primary' if i==0 else 'neutral')+'shape=partialRectangle;top=1;bottom=1;left=1;right=1;')
                x+=widths[j]
    connectors={'flow':'flow','dependency':'dependency','reference':'optional','association':'structural','bidirectional':'mutual','annotation':'secondary'}
    for e in ir.get('edges',[]):
        sty=style(selected,connector=connectors[e['semantic_type']])+'labelBackgroundColor=#FFFFFF;'+e.get('style','')
        cell=ET.SubElement(root,'mxCell',id=e['id'],source=e['source'],target=e['target'],parent=e.get('parent','1'),edge='1',value=e.get('label',''),style=sty)
        geo=ET.SubElement(cell,'mxGeometry',relative='1',**{'as':'geometry'})
        if e.get('waypoints'):
            array=ET.SubElement(geo,'Array',**{'as':'points'})
            for x,y in e['waypoints']: ET.SubElement(array,'mxPoint',x=str(x),y=str(y))
    validate_xml(doc,catalog)
    ET.indent(doc,space='  '); ET.ElementTree(doc).write(destination,encoding='utf-8',xml_declaration=True)
    return ir


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',default=str(CAT/'shape-catalog.json'))
    sub=parser.add_subparsers(dest='command',required=True)
    g=sub.add_parser('generate'); g.add_argument('--builtin',action='append',default=[]); g.add_argument('--custom',action='append',default=[])
    g.add_argument('--include',action='append'); g.add_argument('--exclude',action='append',default=[])
    g.add_argument('--metadata',default=str(CAT/'shape-metadata.json')); g.add_argument('--destination',default=str(CAT)); g.add_argument('--previous')
    s=sub.add_parser('search'); s.add_argument('query'); s.add_argument('--semantic',default=''); s.add_argument('--domain',default=''); s.add_argument('--vendor',default=''); s.add_argument('--library',action='append',default=[]); s.add_argument('--prefer-library',action='append',default=[]); s.add_argument('--limit',type=int,default=8)
    sub.add_parser('validate')
    r=sub.add_parser('render'); r.add_argument('ir'); r.add_argument('destination'); r.add_argument('--resolved-ir',required=True)
    v=sub.add_parser('validate-xml'); v.add_argument('file')
    args=parser.parse_args()
    if args.command=='generate': generate(args); return
    catalog=read(args.catalog); validate(catalog)
    if args.command=='search': print(json.dumps(search(catalog,args.query,args.semantic,args.domain,args.prefer_library,args.vendor,args.limit,args.library),ensure_ascii=False,indent=2))
    elif args.command=='validate':
        print(f"PASS: {len(catalog['shapes'])} verified catalog entries")
    elif args.command=='validate-xml': validate_xml(ET.parse(args.file).getroot(),catalog); print('PASS: XML shape IDs and references')
    elif args.command=='render': write(args.resolved_ir,render(catalog,read(args.ir),args.destination))


if __name__=='__main__': main()
