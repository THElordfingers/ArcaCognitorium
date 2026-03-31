# Auctoritas Spectralis — tests/test_promulgatio.py
# v1.0.0
"""Unit tests for the export engine."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from AuctoritasSpectralis.promulgatio import (
    export_theme_json, export_qss, export_palette_card,
    build_theme_package,
)
from AuctoritasSpectralis.constants import MODUS_ARCANUS_DEFAULTS


class TestPromulgatio(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self._export_dir = Path(self._tmpdir.name)
        self._tokens = MODUS_ARCANUS_DEFAULTS
        self._seal = {
            'seal_hash': 'a' * 64,
            'sealed_at': '2026-01-01T00:00:00+00:00',
            'designator': 'Aureus Profundus',
            'canonical_json': '{}',
        }
        self._oklab = {k: {'l': 0.5, 'a': 0.0, 'b': 0.0} for k in self._tokens}
        self._base_pair = {
            'bg_hex': '#050507', 'bg_oklab': {'l': 0.1, 'a': 0.0, 'b': 0.0},
            'fg_hex': '#d4af37', 'fg_oklab': {'l': 0.7, 'a': 0.0, 'b': 0.1},
        }
        self._summary = {
            'passes_aa': True, 'passes_aaa': False,
            'min_wcag_ratio': 8.0, 'min_apca_lc': 60.0,
            'failing_pairs': [],
        }

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_theme_json_valid(self):
        package = build_theme_package(
            self._tokens, self._oklab, self._base_pair,
            self._seal, self._summary,
        )
        path = export_theme_json(package, self._export_dir)
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertIn('tokens', data)
        self.assertEqual(data['seal_hash'], 'a' * 64)

    def test_qss_not_empty(self):
        path = export_qss(self._tokens, self._export_dir)
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn('#050507', content)

    def test_md_contains_designator(self):
        path = export_palette_card(
            self._tokens, 'Aureus Profundus', 'a' * 64,
            '2026-01-01T00:00:00+00:00', self._summary, self._export_dir,
        )
        content = path.read_text()
        self.assertIn('Aureus Profundus', content)


if __name__ == '__main__':
    unittest.main()
