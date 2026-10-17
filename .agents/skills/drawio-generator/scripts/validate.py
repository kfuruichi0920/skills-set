#!/usr/bin/env python3
"""Validate uncompressed draw.io XML offline using the pinned official XSD."""

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys

try:
    from lxml import etree
except ImportError:
    print("FAIL [setup] lxml is required: python -m pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)

SKILL_DIR = Path(__file__).resolve().parents[1]
MAX_BYTES = 10 * 1024 * 1024
LIMITATION = "XSD/consistency PASS does not guarantee meaning, layout, style support or editor compatibility."


class NoExternalResources(etree.Resolver):
    def resolve(self, url, public_id, context):
        raise ValueError("External XML resources are forbidden")


def parse_xml(data):
    parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True,
                             recover=False, huge_tree=False)
    parser.resolvers.add(NoExternalResources())
    tree = etree.parse(io.BytesIO(data), parser)
    if tree.docinfo.doctype:
        raise ValueError("DOCTYPE/DTD is forbidden; remove all entity declarations")
    return tree


def load_schema():
    directory = SKILL_DIR / "schemas"
    source = json.loads((directory / "source.json").read_text(encoding="utf-8"))
    data = (directory / "mxfile.xsd").read_bytes()
    if hashlib.sha256(data).hexdigest() != source["sha256"]:
        raise ValueError("Bundled official XSD checksum mismatch; restore the pinned schema")
    return etree.XMLSchema(parse_xml(data))


def normalize(tree):
    """Wrap a bare model, without changing any cells or style instructions."""
    root = tree.getroot()
    if root.tag == "mxGraphModel":
        mxfile = etree.Element("mxfile")
        diagram = etree.SubElement(mxfile, "diagram", id="page-1", name="Page-1")
        diagram.append(root)
        return etree.ElementTree(mxfile)
    if root.tag != "mxfile":
        raise ValueError("Expected mxfile or mxGraphModel root (uncompressed XML only)")
    return tree


def consistency_errors(tree):
    errors = []

    def error(page, node, message):
        cell_id = node.get("id", "?")
        errors.append(f"page={page!r} line={node.sourceline or 0} id={cell_id!r}: {message}")

    page_ids = set()
    for number, diagram in enumerate(tree.getroot().findall("diagram"), 1):
        page = diagram.get("name") or str(number)
        page_id = diagram.get("id")
        if not page_id or page_id in page_ids:
            error(page, diagram, "Page id must be nonempty and unique within the file")
        page_ids.add(page_id)
        model = diagram.find("mxGraphModel")
        if model is None:
            error(page, diagram, "Compressed/text diagrams are unsupported; generate an mxGraphModel child")
            continue
        if (diagram.text or "").strip():
            error(page, diagram, "diagram must contain XML, not compressed/text payload")
        root = model.find("root")
        if root is None:
            continue  # XSD reports the missing root.
        cells = {}
        for item in root:
            if not isinstance(item.tag, str):
                continue
            cell = item if item.tag == "mxCell" else item.find("mxCell")
            if cell is None:
                continue  # XSD reports invalid wrappers.
            cell_id = item.get("id")
            if item is not cell and cell.get("id") is not None:
                error(page, item, "Wrapped mxCell must not have an id; put it on UserObject/object only")
            if not cell_id or cell_id in cells:
                error(page, item, "Cell id must be nonempty and unique within this page")
                continue
            cells[cell_id] = cell

        for required, parent in (("0", None), ("1", "0")):
            cell = cells.get(required)
            if cell is None:
                error(page, root, f"Missing required structural cell id={required!r}")
            elif cell.get("parent") != parent or cell.get("vertex", "0") != "0" or cell.get("edge", "0") != "0":
                error(page, cell, f"Structural cell {required} must have parent={parent!r} and no vertex/edge role")

        for cell_id, cell in cells.items():
            vertex, edge = cell.get("vertex") == "1", cell.get("edge") == "1"
            parent = cell.get("parent")
            if cell_id != "0" and not parent:
                error(page, cell, "parent is required except on root cell 0")
            for attribute in ("parent", "source", "target"):
                reference = cell.get(attribute)
                if reference is not None and reference not in cells:
                    error(page, cell, f"{attribute}={reference!r} does not reference a cell in this page")
            if vertex and edge:
                error(page, cell, "vertex=1 and edge=1 are mutually exclusive")
            if not edge and (cell.get("source") is not None or cell.get("target") is not None):
                error(page, cell, "source/target are only allowed on edge=1 cells")
            if vertex or edge:
                if parent == "0":
                    error(page, cell, "Visible cells must belong to a layer/group, not root 0")
                elif parent in cells and parent != "1":
                    container = cells[parent]
                    if container.get("parent") != "0" and container.get("vertex") != "1" and not (vertex and container.get("edge") == "1"):
                        error(page, cell, "parent must be a layer/group (or an edge for a label vertex)")
            elif cell_id != "0" and parent != "0":
                error(page, cell, "A cell without vertex/edge must be a layer with parent=0")

            geometry = cell.find("mxGeometry")
            if vertex or edge:
                if geometry is None:
                    error(page, cell, "vertex/edge requires mxGeometry")
                    continue
                if geometry.get("as") != "geometry":
                    error(page, cell, 'mxGeometry requires as="geometry"')
            if geometry is not None:
                for element in geometry.iter():
                    for attribute in ("x", "y", "width", "height"):
                        value = element.get(attribute)
                        if value is None:
                            continue
                        try:
                            finite = math.isfinite(float(value))
                        except ValueError:
                            finite = False
                        if not finite:
                            error(page, element, f"{attribute}={value!r} must be a finite number")
                if vertex:
                    for attribute in ("width", "height"):
                        try:
                            valid = math.isfinite(float(geometry.get(attribute, "nan"))) and float(geometry.get(attribute, "nan")) > 0
                        except ValueError:
                            valid = False
                        if not valid:
                            error(page, cell, f"Vertex {attribute} must be a finite positive number")
                if edge:
                    if geometry.get("relative") != "1":
                        error(page, cell, 'Edge mxGeometry requires relative="1"')
                    for endpoint in ("source", "target"):
                        reference = cell.get(endpoint)
                        if reference in cells and cells[reference].get("vertex") != "1":
                            error(page, cell, f"{endpoint} must reference a vertex")
                        if reference is None:
                            point = geometry.find(f"mxPoint[@as='{endpoint}Point']")
                            if point is None or point.get("x") is None or point.get("y") is None:
                                error(page, cell, f"Missing {endpoint}: use a vertex reference or explicit {endpoint}Point x/y")
                    style = dict(token.split("=", 1) for token in cell.get("style", "").split(";") if "=" in token)
                    for arrow in ("startArrow", "endArrow"):
                        if not style.get(arrow):
                            error(page, cell, f"Explicit {arrow} required: use none unless the user requested an arrow")

        # Parent cycles prevent reliable editing even if all references exist.
        finished = set()
        for cell_id in cells:
            chain = set()
            current = cell_id
            while current in cells and current not in finished:
                if current in chain:
                    error(page, cells[current], "parent cycle detected; attach the group to a layer")
                    break
                chain.add(current)
                current = cells[current].get("parent")
            finished.update(chain)
    return errors


def validate(path):
    """Return (report, normalized_tree); never write or fetch resources."""
    report = {"status": "FAIL", "checks": {}, "errors": [], "limitations": LIMITATION}
    try:
        with Path(path).open("rb") as source:
            data = source.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("XML exceeds the 10 MiB input limit")
        tree = parse_xml(data)
        report["checks"]["xml"] = "PASS"
    except (OSError, ValueError, etree.XMLSyntaxError) as exc:
        report["checks"]["xml"] = "FAIL"
        report["errors"].append(f"[xml] {exc}")
        return report, None
    try:
        tree = normalize(tree)
        report["checks"]["normalization"] = "PASS"
    except ValueError as exc:
        report["checks"]["normalization"] = "FAIL"
        report["errors"].append(f"[normalization] {exc}")
        return report, None
    try:
        schema = load_schema()
    except (OSError, ValueError, KeyError, etree.LxmlError) as exc:
        report["checks"]["schema_setup"] = "FAIL"
        report["errors"].append(f"[setup] {exc}")
        return report, None
    valid = schema.validate(tree)
    report["checks"]["xsd"] = "PASS" if valid else "FAIL"
    for issue in schema.error_log:
        report["errors"].append(f"[xsd] line={issue.line} path={issue.path}: {issue.message}")
    errors = consistency_errors(tree)
    report["checks"]["consistency"] = "FAIL" if errors else "PASS"
    report["errors"].extend(f"[consistency] {message}" for message in errors)
    if not report["errors"]:
        report["status"] = "PASS"
    return report, tree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--output", type=Path, help="Write normalized mxfile only on PASS; destination must not exist")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    args = parser.parse_args()
    report, tree = validate(args.file)
    if report["status"] == "PASS" and args.output:
        try:
            # Exclusive creation prevents silently replacing a previous validated file.
            data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True, pretty_print=True)
            with args.output.open("xb") as destination:
                destination.write(data)
            report["output"] = str(args.output)
        except OSError as exc:
            report["status"] = "FAIL"
            report["errors"].append(f"[output] {exc}")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status']}: {args.file}")
        for check, status in report["checks"].items():
            print(f"  {check}: {status}")
        for message in report["errors"]:
            print(f"  {message}")
        print(f"  Note: {LIMITATION}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
