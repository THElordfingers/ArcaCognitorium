# Departamentum Documentalis — tests/test_integration.py
# v1.0.0
"""End-to-end: scaffold → parse → roundtrip → emit .md → emit .wiz."""

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from DepartamentumDocumentalis.templates import get_template
from DepartamentumDocumentalis.bureau_parser import parse_bureau
from DepartamentumDocumentalis.bureau_writer import write_bureau
from DepartamentumDocumentalis.emitter_md import emit_markdown, emit_to_file
from DepartamentumDocumentalis.library import DocumentLibrary


class TestIntegration(unittest.TestCase):

    def test_full_pipeline_md(self):
        """Scaffold → parse → write → reparse → emit .md → validate."""
        # 1. Scaffold
        content = get_template('expositio', title='Integration Test', author='Wizard')
        self.assertIn('Integration Test', content)

        # 2. Parse
        doc = parse_bureau(content)
        self.assertEqual(doc.header.title, 'Integration Test \u2014 Expositio')
        self.assertGreater(len(doc.nodes), 0)

        # 3. Roundtrip
        written = write_bureau(doc)
        doc2 = parse_bureau(written)
        self.assertEqual(len(doc2.nodes), len(doc.nodes))

        # 4. Emit .md
        md = emit_markdown(doc2)
        self.assertIn('# Integration Test', md)
        self.assertIn('## Identity', md)

        # 5. Write to file
        with TemporaryDirectory() as tmp:
            md_path = Path(tmp) / 'test.md'
            emit_to_file(doc2, md_path)
            self.assertTrue(md_path.exists())
            content = md_path.read_text()
            self.assertIn('Integration Test', content)

    def test_library_integration(self):
        """Record a compiled document in the library."""
        with TemporaryDirectory() as tmp:
            lib = DocumentLibrary(Path(tmp) / 'test.db')
            lib.initialize()

            rid = lib.record(
                title='Test Doc', doc_type='expositio',
                source_path='/tmp/test.bureau',
                wiz_path='/tmp/test.wiz',
                md_path='/tmp/test.md',
                version='1.0', author='Wizard',
            )
            self.assertIsNotNone(rid)

            docs = lib.list_documents()
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['title'], 'Test Doc')
            self.assertEqual(docs[0]['doc_type'], 'expositio')

            lib.close()

    def test_wiz_emitter_available(self):
        """Verify the Node.js emitter script exists."""
        from DepartamentumDocumentalis.emitter_wiz import _get_emitter_script
        script = _get_emitter_script()
        self.assertTrue(script.exists(), f"Emitter script missing: {script}")


if __name__ == '__main__':
    unittest.main()
