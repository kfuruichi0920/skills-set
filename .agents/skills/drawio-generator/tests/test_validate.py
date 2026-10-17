"""Offline acceptance tests for the official XSD and additional checks."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lxml import etree

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("drawio_validate", SKILL / "scripts/validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "candidate.drawio"
        self.tree = etree.parse(str(SKILL / "assets/basic-template.drawio"))

    def cell(self, cell_id):
        return self.tree.find(f".//mxCell[@id='{cell_id}']")

    def check(self, expected="PASS", message=None):
        self.path.write_bytes(etree.tostring(self.tree, encoding="UTF-8"))
        # Validation must never open external resources, including local entities.
        with patch.object(validator.NoExternalResources, "resolve", side_effect=AssertionError("external fetch")):
            report, tree = validator.validate(self.path)
        self.assertEqual(report["status"], expected, report)
        if message:
            self.assertIn(message, "\n".join(report["errors"]))
        return report, tree

    def test_equipment_template(self):
        report, _ = self.check()
        self.assertEqual(report["checks"]["xsd"], "PASS")
        for cell in self.tree.findall(".//mxCell[@edge='1']"):
            self.assertIn("startArrow=none;endArrow=none;", cell.get("style"))

    def test_bare_model_and_explicit_arrow_survive_normalization(self):
        self.cell("link-1").set("style", "startArrow=none;endArrow=classic;")
        model = self.tree.find(".//mxGraphModel")
        expected_model = etree.tostring(model, with_tail=False)
        self.tree = etree.ElementTree(model)
        _, normalized = self.check()
        self.assertEqual(normalized.getroot().tag, "mxfile")
        self.assertEqual(etree.tostring(normalized.find(".//mxGraphModel"), with_tail=False), expected_model)

    def test_cell_ids_are_page_scoped(self):
        page = copy.deepcopy(self.tree.find("diagram"))
        page.set("id", "second")
        self.tree.getroot().append(page)
        self.check()

    def test_duplicate_page_id(self):
        self.tree.getroot().append(copy.deepcopy(self.tree.find("diagram")))
        self.check("FAIL", "Page id")

    def test_duplicate_cell_id(self):
        self.cell("sensor").set("id", "switch")
        report, _ = self.check("FAIL", "unique within this page")
        self.assertIn("page='装置構成'", "\n".join(report["errors"]))

    def test_missing_root_cells(self):
        for cell_id in ("0", "1"):
            with self.subTest(cell_id=cell_id):
                cell = self.cell(cell_id)
                parent = cell.getparent()
                parent.remove(cell)
                self.check("FAIL", "Missing required structural cell")
                parent.append(cell)

    def test_missing_references(self):
        for attribute in ("parent", "source", "target"):
            with self.subTest(attribute=attribute):
                cell = self.cell("link-1")
                original = cell.get(attribute)
                cell.set(attribute, "missing")
                self.check("FAIL", f"{attribute}='missing'")
                cell.set(attribute, original)

    def test_roles_and_geometry(self):
        cell = self.cell("controller")
        cell.set("edge", "1")
        self.check("FAIL", "mutually exclusive")
        del cell.attrib["edge"]
        cell.remove(cell.find("mxGeometry"))
        self.check("FAIL", "requires mxGeometry")

    def test_geometry_marker(self):
        del self.cell("sensor").find("mxGeometry").attrib["as"]
        self.check("FAIL", 'requires as="geometry"')

    def test_invalid_dimensions(self):
        geometry = self.cell("sensor").find("mxGeometry")
        for value in ("0", "-1", "NaN", "INF", "bad", None):
            with self.subTest(value=value):
                if value is None:
                    del geometry.attrib["width"]
                else:
                    geometry.set("width", value)
                self.check("FAIL", "finite positive")

    def test_invalid_coordinates(self):
        self.cell("sensor").find("mxGeometry").set("x", "NaN")
        self.check("FAIL", "finite number")

    def test_parent_cycle(self):
        self.cell("controller").set("parent", "sensor")
        self.cell("sensor").set("parent", "controller")
        self.check("FAIL", "parent cycle")

    def test_edge_geometry_and_arrows(self):
        cell = self.cell("link-1")
        del cell.find("mxGeometry").attrib["relative"]
        cell.set("style", "endArrow=none;")
        self.check("FAIL", 'relative="1"')
        cell.find("mxGeometry").set("relative", "1")
        self.check("FAIL", "Explicit startArrow required")

    def test_unconnected_endpoint_requires_explicit_point(self):
        cell = self.cell("link-1")
        del cell.attrib["target"]
        self.check("FAIL", "Missing target")
        etree.SubElement(cell.find("mxGeometry"), "mxPoint", x="200", y="300", attrib={"as": "targetPoint"})
        self.check()

    def test_endpoint_must_be_vertex(self):
        self.cell("link-1").set("target", "1")
        self.check("FAIL", "target must reference a vertex")

    def test_wrapped_cells(self):
        cell = self.cell("controller")
        parent = cell.getparent()
        wrapper = etree.SubElement(parent, "UserObject", id="controller", label="装置", ip="192.0.2.1")
        del cell.attrib["id"]
        wrapper.append(cell)
        self.check()
        cell.set("id", "inner-id")
        self.check("FAIL", "Wrapped mxCell must not have an id")

    def test_xsd_attribute_type_and_unknown_element(self):
        model = self.tree.find(".//mxGraphModel")
        model.set("grid", "true")
        self.check("FAIL", "[xsd]")
        model.set("grid", "1")
        etree.SubElement(self.tree.getroot(), "unknown")
        self.check("FAIL", "[xsd]")

    def test_compressed_payload(self):
        page = self.tree.find("diagram")
        page.remove(page.find("mxGraphModel"))
        page.text = "BASE64_DEFLATED_DATA"
        self.check("FAIL", "Compressed/text diagrams")

    def test_malformed_xml(self):
        self.path.write_text("<mxfile><diagram></mxfile>", encoding="utf-8")
        report, _ = validator.validate(self.path)
        self.assertEqual(report["checks"]["xml"], "FAIL")
        self.assertIn("line 1", report["errors"][0])

    def test_doctype_entities_are_never_resolved(self):
        for declaration in ('<!ENTITY secret SYSTEM "file:///etc/passwd">',
                            '<!ENTITY secret SYSTEM "https://example.invalid/secret">',
                            '<!ENTITY secret "internal">'):
            with self.subTest(declaration=declaration):
                payload = f'<!DOCTYPE mxfile [{declaration}]><mxfile>&secret;</mxfile>'
                self.path.write_text(payload, encoding="utf-8")
                with patch.object(validator.NoExternalResources, "resolve", side_effect=AssertionError("external fetch")):
                    report, _ = validator.validate(self.path)
                self.assertEqual(report["status"], "FAIL")
                self.assertIn("DOCTYPE/DTD", report["errors"][0])

    def test_utf16_doctype_is_rejected(self):
        self.path.write_bytes('<!DOCTYPE mxfile><mxfile/>'.encode("utf-16"))
        report, _ = validator.validate(self.path)
        self.assertIn("DOCTYPE/DTD", report["errors"][0])

    def test_xinclude_not_expanded(self):
        etree.SubElement(self.tree.getroot(), "{http://www.w3.org/2001/XInclude}include", href="file:///etc/passwd")
        self.check("FAIL", "[xsd]")

    def test_schema_location_not_fetched(self):
        self.tree.getroot().set("{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation", "https://example.invalid/mxfile.xsd")
        self.check()

    def test_schema_checksum_failure(self):
        with patch.object(validator.hashlib, "sha256") as digest:
            digest.return_value.hexdigest.return_value = "wrong"
            self.check("FAIL", "checksum mismatch")

    def test_size_limit_and_missing_file(self):
        self.path.write_bytes(b" " * (validator.MAX_BYTES + 1))
        report, _ = validator.validate(self.path)
        self.assertIn("10 MiB", report["errors"][0])
        report, _ = validator.validate(self.path.with_name("missing.drawio"))
        self.assertEqual(report["status"], "FAIL")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SKILL / "scripts/validate.py"), str(self.path), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_failure_repair_revalidation_and_output(self):
        # Input intent: controller -- switch -- sensor, with no arrows.
        self.cell("link-2").set("target", "sensor-typo")
        self.check("FAIL", "target='sensor-typo'")
        output = Path(self.temp.name) / "diagram.drawio"
        result = self.cli("--output", output, "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
        # The generation agent repairs this known typo using the original intent.
        self.cell("link-2").set("target", "sensor")
        self.check()
        result = self.cli("--output", output, "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(validator.validate(output)[0]["status"], "PASS")
        original = output.read_bytes()
        result = self.cli("--output", output, "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(original, output.read_bytes())


if __name__ == "__main__":
    unittest.main()
