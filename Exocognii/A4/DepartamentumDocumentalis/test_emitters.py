# Departamentum Documentalis — tests/test_emitters.py
# v1.0.0
"""Tests for Markdown emitter, bureau writer roundtrip, and templates."""

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from DepartamentumDocumentalis.bureau_parser import parse_bureau
from DepartamentumDocumentalis.bureau_writer import write_bureau
from DepartamentumDocumentalis.emitter_md import emit_markdown
from DepartamentumDocumentalis.templates import get_template, list_templates


SAMPLE = """\
---
title: Test Doc
type: expositio
version: 1.0
author: Wizard
theme: wizdoc
---

|h1|Section One|
|body|
Paragraph with **bold** and *italic* text.
|/body|

|bullet|First point|
|bullet|Second point|

|code|python|
def hello():
    pass
|/code|

|table|
|th|Name|Value|
|tr|alpha|1|
|tr|beta|2|
|/table|
"""


class TestMarkdownEmitter(unittest.TestCase):

    def test_emits_title(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('# Test Doc', md)

    def test_emits_headings(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('## Section One', md)

    def test_emits_code_block(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('```python', md)
        self.assertIn('def hello', md)
        self.assertIn('```', md)

    def test_emits_bullets(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('- First point', md)

    def test_emits_bold(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('**bold**', md)

    def test_emits_table(self):
        doc = parse_bureau(SAMPLE)
        md = emit_markdown(doc)
        self.assertIn('alpha', md)
        self.assertIn('beta', md)


class TestBureauWriter(unittest.TestCase):

    def test_roundtrip_preserves_header(self):
        doc = parse_bureau(SAMPLE)
        output = write_bureau(doc)
        doc2 = parse_bureau(output)
        self.assertEqual(doc2.header.title, 'Test Doc')
        self.assertEqual(doc2.header.doc_type, 'expositio')
        self.assertEqual(doc2.header.version, '1.0')

    def test_roundtrip_preserves_node_count(self):
        doc = parse_bureau(SAMPLE)
        output = write_bureau(doc)
        doc2 = parse_bureau(output)
        self.assertEqual(len(doc2.nodes), len(doc.nodes))

    def test_roundtrip_preserves_tags(self):
        doc = parse_bureau(SAMPLE)
        output = write_bureau(doc)
        doc2 = parse_bureau(output)
        tags1 = [n.tag for n in doc.nodes]
        tags2 = [n.tag for n in doc2.nodes]
        self.assertEqual(tags1, tags2)


class TestTemplates(unittest.TestCase):

    def test_list_templates(self):
        templates = list_templates()
        self.assertIn('expositio', templates)
        self.assertIn('dux_tome', templates)
        self.assertIn('build_doc', templates)
        self.assertIn('blank', templates)

    def test_get_template_fills_title(self):
        content = get_template('expositio', title='My App', author='Wizard')
        self.assertIn('My App', content)
        self.assertIn('Wizard', content)

    def test_template_parses(self):
        for tmpl in list_templates():
            content = get_template(tmpl, title='Test', author='W')
            doc = parse_bureau(content)
            self.assertEqual(doc.header.title.split(' ')[0], 'Test')


class TestLibrary(unittest.TestCase):

    def test_record_and_list(self):
        from DepartamentumDocumentalis.library import DocumentLibrary
        with TemporaryDirectory() as tmp:
            lib = DocumentLibrary(Path(tmp) / 'test.db')
            lib.initialize()
            lib.record(title='Test', doc_type='expositio')
            docs = lib.list_documents()
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['title'], 'Test')
            lib.close()


if __name__ == '__main__':
    unittest.main()
