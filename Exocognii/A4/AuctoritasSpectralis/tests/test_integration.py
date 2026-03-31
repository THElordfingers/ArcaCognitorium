# Auctoritas Spectralis — tests/test_integration.py
# v1.0.0
"""End-to-end integration test: compose → derive → audit → ratify → export."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from AuctoritasSpectralis.derivatio import derive_tokens
from AuctoritasSpectralis.scrutinium import build_contrast_matrix, audit_passes
from AuctoritasSpectralis.ratificatio import generate_seal
from AuctoritasSpectralis.registry import ChromaticRegistry
from AuctoritasSpectralis.promulgatio import export_theme_json, build_theme_package


class TestIntegration(unittest.TestCase):

    def test_full_critical_path(self):
        # 1. Set base pair
        bg = '#050507'
        fg = '#d4af37'

        # 2. Derive tokens
        result = derive_tokens(bg, fg)
        tokens = result['tokens']
        oklab = result['oklab']
        self.assertEqual(len(tokens), 10)

        # 3. Build contrast matrix
        matrix = build_contrast_matrix(tokens)
        audit = audit_passes(matrix)
        self.assertIn('passes_aa', audit)

        # 4. Generate seal
        designator = 'Aureus Profundus'
        seal = generate_seal(tokens, designator)
        self.assertEqual(len(seal['seal_hash']), 64)

        # 5. Insert into registry
        tmpdir = TemporaryDirectory()
        db_path = Path(tmpdir.name) / 'test.db'
        reg = ChromaticRegistry(db_path)
        reg.connect()

        rid = reg.insert_palette(
            designator=designator,
            seal_hash=seal['seal_hash'],
            tokens=tokens,
            oklab_bg=oklab.get('c_bg', {'l': 0, 'a': 0, 'b': 0}),
            oklab_fg=oklab.get('c_gold', {'l': 0, 'a': 0, 'b': 0}),
            wcag_min=audit['min_wcag_ratio'],
            apca_min=audit['min_apca_lc'],
            passes_aa=audit['passes_aa'],
            passes_aaa=audit['passes_aaa'],
            canonical_json=seal['canonical_json'],
            sealed_at=seal['sealed_at'],
        )

        # 6. Read back
        palettes = reg.list_palettes()
        self.assertEqual(len(palettes), 1)
        self.assertEqual(palettes[0]['designator'], designator)

        # 7. Export
        export_dir = Path(tmpdir.name) / 'exports'
        base_pair = {
            'bg_hex': bg,
            'bg_oklab': oklab.get('c_bg', {'l': 0, 'a': 0, 'b': 0}),
            'fg_hex': fg,
            'fg_oklab': oklab.get('c_gold', {'l': 0, 'a': 0, 'b': 0}),
        }
        package = build_theme_package(tokens, oklab, base_pair, seal, audit)
        path = export_theme_json(package, export_dir)
        self.assertTrue(path.exists())

        # 8. Validate theme.json
        data = json.loads(path.read_text())
        self.assertEqual(data['designator'], designator)
        self.assertEqual(data['seal_hash'], seal['seal_hash'])
        self.assertIn('tokens', data)
        self.assertEqual(len(data['tokens']), 10)

        # 9. Seal hash matches registry
        row = reg.get_palette(rid)
        self.assertEqual(row['seal_hash'], data['seal_hash'])

        reg.close()
        tmpdir.cleanup()


if __name__ == '__main__':
    unittest.main()
