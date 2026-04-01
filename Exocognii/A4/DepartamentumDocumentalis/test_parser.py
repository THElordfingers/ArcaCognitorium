# Departamentum Documentalis — tests/test_parser.py
# v1.0.0
"""Unit tests for the .bureau parser."""

import unittest
from DepartamentumDocumentalis.bureau_parser import parse_bureau, parse_inline


class TestInlineParsing(unittest.TestCase):

    def test_plain_text(self):
        spans = parse_inline('Hello world')
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].text, 'Hello world')
        self.assertFalse(spans[0].bold)

    def test_bold(self):
        spans = parse_inline('This is **bold** text')
        self.assertEqual(len(spans), 3)
        self.assertTrue(spans[1].bold)
        self.assertEqual(spans[1].text, 'bold')

    def test_italic(self):
        spans = parse_inline('This is *italic* text')
        self.assertTrue(any(s.italic for s in spans))

    def test_inline_code(self):
        spans = parse_inline('Use `hello()` here')
        self.assertTrue(any(s.code for s in spans))

    def test_color_token(self):
        spans = parse_inline('This is {{c_gold|golden}} text')
        colored = [s for s in spans if s.color_token]
        self.assertEqual(len(colored), 1)
        self.assertEqual(colored[0].color_token, 'c_gold')
        self.assertEqual(colored[0].text, 'golden')


class TestBureauParser(unittest.TestCase):

    def test_header_parsing(self):
        text = "---\ntitle: Test\ntype: blank\nversion: 2.0\n---\n"
        doc = parse_bureau(text)
        self.assertEqual(doc.header.title, 'Test')
        self.assertEqual(doc.header.doc_type, 'blank')
        self.assertEqual(doc.header.version, '2.0')

    def test_single_tags(self):
        text = "|h1|Section One|\n|h2|Sub Section|\n|bullet|A point|\n"
        doc = parse_bureau(text)
        self.assertEqual(len(doc.nodes), 3)
        self.assertEqual(doc.nodes[0].tag, 'h1')
        self.assertEqual(doc.nodes[0].content, 'Section One')
        self.assertEqual(doc.nodes[2].tag, 'bullet')

    def test_body_block(self):
        text = "|body|\nParagraph text here.\nMore text.\n|/body|\n"
        doc = parse_bureau(text)
        self.assertEqual(len(doc.nodes), 1)
        self.assertEqual(doc.nodes[0].tag, 'body')
        self.assertIn('Paragraph', doc.nodes[0].content)

    def test_code_block(self):
        text = "|code|python|\ndef hello():\n    pass\n|/code|\n"
        doc = parse_bureau(text)
        self.assertEqual(len(doc.nodes), 1)
        self.assertEqual(doc.nodes[0].tag, 'code')
        self.assertEqual(doc.nodes[0].meta['lang'], 'python')
        self.assertIn('def hello', doc.nodes[0].content)

    def test_table(self):
        text = "|table|\n|th|A|B|\n|tr|1|2|\n|tr|3|4|\n|/table|\n"
        doc = parse_bureau(text)
        self.assertEqual(len(doc.nodes), 1)
        tbl = doc.nodes[0]
        self.assertEqual(tbl.tag, 'table')
        self.assertEqual(len(tbl.children), 3)  # 1 header + 2 rows
        self.assertEqual(tbl.children[0].tag, 'th')
        self.assertEqual(len(tbl.children[0].children), 2)  # 2 cells

    def test_break(self):
        text = "|break|\n"
        doc = parse_bureau(text)
        self.assertEqual(doc.nodes[0].tag, 'break')

    def test_full_document(self):
        text = """\
---
title: Full Test
type: expositio
version: 1.0
author: Wizard
theme: wizdoc
---

|h1|Identity|
|bullet|Name: Test App|
|bullet|Version: 1.0|

|h1|Purpose|
|body|
This is the purpose section with **bold** text.
|/body|

|code|python|
x = 42
|/code|

|table|
|th|Key|Value|
|tr|a|1|
|/table|

|break|
|h2|Final Section|
"""
        doc = parse_bureau(text)
        self.assertEqual(doc.header.title, 'Full Test')
        self.assertGreater(len(doc.nodes), 5)
        tags = [n.tag for n in doc.nodes]
        self.assertIn('h1', tags)
        self.assertIn('bullet', tags)
        self.assertIn('body', tags)
        self.assertIn('code', tags)
        self.assertIn('table', tags)
        self.assertIn('break', tags)


if __name__ == '__main__':
    unittest.main()
