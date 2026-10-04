"""Behavior checks for catalog retrieval, hallucination rejection and native XML."""
import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import shape_catalog as sc


class CatalogChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=sc.read(sc.CAT/'shape-catalog.json')

    def test_japanese_alias_and_filters(self):
        rows=sc.search(self.catalog,'データベース',libraries_filter=['flowchart'])
        self.assertEqual(rows[0]['shape_id'],'mxgraph.flowchart.database')
        rows=sc.search(self.catalog,'lambda',domain='cloud_aws',vendor='aws')
        self.assertTrue(rows)
        self.assertTrue(all(r['library']=='aws4' for r in rows))
        self.assertEqual(rows[0]['shape_id'],'mxgraph.aws4.lambda')
        self.assertEqual(sc.search(self.catalog,'存在しない概念zzz'),[])

    def test_unknown_id_not_rendered(self):
        ir=dict(id='bad',metadata=dict(theme='T01',title='拒否'),nodes=[dict(id='x',shape_id='mxgraph.aws4.imaginary_service')])
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'bad.drawio'
            with self.assertRaisesRegex(ValueError,'Unknown/unverified'):
                sc.render(self.catalog,ir,target)
            self.assertFalse(target.exists())

    def test_vendor_requires_input_evidence(self):
        with self.assertRaisesRegex(ValueError,'Vendor shape'):
            sc.resolve(self.catalog,dict(nodes=[dict(id='db',shape_id='mxgraph.aws4.rds')]))

    def test_alias_is_not_an_id(self):
        with self.assertRaises(ValueError): sc.exact(self.catalog,'データベース')

    def test_native_membership_table_and_custom_refs(self):
        sample=sc.ROOT.parents[2]/'sample/information-structuring'
        document=ET.parse(sample/'10-native-capabilities.drawio').getroot()
        sc.validate_xml(document,self.catalog)
        membership=document.find("diagram[@id='native-membership']")
        cells={c.get('id'):c for c in membership.findall('./mxGraphModel/root/mxCell')}
        self.assertEqual(cells['db'].get('parent'),'system')
        table=document.find("diagram[@id='native-table']")
        cells={c.get('id'):c for c in table.findall('./mxGraphModel/root/mxCell')}
        self.assertEqual(cells['responsibility_r0_c0'].get('parent'),'responsibility_r0')
        self.assertEqual(cells['responsibility_r0'].get('parent'),'responsibility')
        reuse=document.find("diagram[@id='native-fragment']")
        cells={c.get('id'):c for c in reuse.findall('./mxGraphModel/root/mxCell')}
        self.assertEqual(cells['reuse__flow'].get('source'),'reuse__entry')
        self.assertEqual(cells['reuse__entry'].get('parent'),'reuse')

    def test_renderer_boundary_revalidates_xml(self):
        doc=ET.fromstring('<mxfile><diagram><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="n" parent="1" style="shape=mxgraph.imagined.icon;"/></root></mxGraphModel></diagram></mxfile>')
        with self.assertRaisesRegex(ValueError,'Unknown/unverified'): sc.validate_xml(doc,self.catalog)
        doc.find('.//mxCell[@id="n"]').set('style','shape=rectangle;')
        doc.find('.//mxCell[@id="n"]').set('parent','missing')
        with self.assertRaisesRegex(ValueError,'Broken parent'): sc.validate_xml(doc,self.catalog)

    def test_compressed_custom_model(self):
        from urllib.parse import quote
        import zlib,base64
        value='<mxGraphModel><root><mxCell id="0"/></root></mxGraphModel>'
        comp=zlib.compressobj(wbits=-15)
        encoded=base64.b64encode(comp.compress(quote(value).encode())+comp.flush()).decode()
        self.assertEqual(sc.decode_model(encoded).tag,'mxGraphModel')

    def test_bad_catalog_rejected(self):
        bad=copy.deepcopy(self.catalog)
        bad['shapes'].append(bad['shapes'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate'): sc.validate(bad)
        bad=copy.deepcopy(self.catalog);bad['shapes'][0]['verified']=False
        with self.assertRaisesRegex(ValueError,'Schema validation'): sc.validate(bad)

    def test_source_discovery_metadata_and_removal_diff(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); assets=root/'assets'; (assets/'nested').mkdir(parents=True)
            (assets/'nested/test.xml').write_text('<shapes name="mxgraph.example"><shape name="Database" w="80" h="80"/></shapes>',encoding='utf-8')
            metadata=root/'metadata.json';sc.write(metadata,dict(rules=[dict(pattern='database',aliases=['データベース'])],shapes={}))
            args=SimpleNamespace(builtin=[str(assets)],custom=[],include=['*.xml'],exclude=[],metadata=str(metadata),destination=str(root/'first'),previous=None)
            sc.generate(args)
            first=sc.read(root/'first/shape-catalog.json')
            self.assertEqual(sc.search(first,'データベース')[0]['shape_id'],'mxgraph.example.database')
            self.assertEqual(sc.read(root/'first/shape-catalog.raw.json')['shapes'][0]['aliases'],[])
            args.previous=str(root/'first/shape-catalog.json');args.destination=str(root/'second');args.exclude=['nested/*']
            sc.generate(args)
            self.assertEqual(sc.read(root/'second/catalog-diff.json')['removed'],['mxgraph.example.database'])
            args.previous=str(root/'first/shape-catalog.json');args.destination=str(root/'first')
            sc.generate(args)
            self.assertEqual(sc.read(root/'first/catalog-diff.json')['removed'],['mxgraph.example.database'])
            sc.write(metadata,dict(shapes={'mxgraph.missing.shape':dict(aliases=['不明'])}))
            with self.assertRaisesRegex(ValueError,'Unknown metadata target'): sc.generate(args)

    def test_custom_image_and_invalid_library(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); assets=root/'custom';assets.mkdir()
            metadata=root/'meta.json';sc.write(metadata,dict(shapes={}))
            lib=ET.Element('mxlibrary');lib.text=json.dumps([dict(title='図',w=20,h=20,data='data:image/svg+xml,'+'<svg xmlns="http://www.w3.org/2000/svg"/>')])
            ET.ElementTree(lib).write(assets/'images.xml',encoding='utf-8')
            args=SimpleNamespace(builtin=[],custom=[str(assets)],include=['*.xml'],exclude=[],metadata=str(metadata),destination=str(root/'catalog'),previous=None)
            sc.generate(args)
            generated=sc.read(root/'catalog/shape-catalog.json')
            self.assertEqual(generated['shapes'][0]['asset_type'],'image')
            ir=dict(id='image',metadata=dict(theme='T01',title='画像'),nodes=[dict(id='image',shape_id=generated['shapes'][0]['id'],x=0,y=0,width=20,height=20)])
            sc.render(generated,ir,root/'image.drawio')
            style=ET.parse(root/'image.drawio').getroot().find('.//mxCell[@id="image"]').get('style')
            self.assertIn('image=data:image/svg+xml,',style)
            self.assertNotIn(';base64,',style)
            (assets/'images.xml').write_text('<invalid/>',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Invalid custom library'): sc.generate(args)


if __name__=='__main__': unittest.main()
