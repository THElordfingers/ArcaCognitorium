# Auctoritas Spectralis — tests/test_registry.py
# v1.0.0
"""Unit tests for the SQLite chromatic registry."""

import unittest
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from AuctoritasSpectralis.registry import ChromaticRegistry
from AuctoritasSpectralis.constants import MODUS_ARCANUS_DEFAULTS


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self._db_path = Path(self._tmpdir.name) / 'test.db'
        self._reg = ChromaticRegistry(self._db_path)
        self._reg.connect()

    def tearDown(self):
        self._reg.close()
        self._tmpdir.cleanup()

    def _insert_default(self, seal_hash='abc123', designator='Test Palette'):
        return self._reg.insert_palette(
            designator=designator,
            seal_hash=seal_hash,
            tokens=MODUS_ARCANUS_DEFAULTS,
            oklab_bg={'l': 0.1, 'a': 0.0, 'b': 0.0},
            oklab_fg={'l': 0.7, 'a': 0.0, 'b': 0.1},
            wcag_min=8.0, apca_min=60.0,
            passes_aa=True, passes_aaa=False,
            canonical_json='{}', sealed_at='2026-01-01T00:00:00+00:00',
        )

    def test_insert_and_read(self):
        rid = self._insert_default()
        row = self._reg.get_palette(rid)
        self.assertIsNotNone(row)
        self.assertEqual(row['designator'], 'Test Palette')
        self.assertEqual(row['c_gold'], '#d4af37')

    def test_duplicate_seal_raises(self):
        self._insert_default(seal_hash='dupe')
        with self.assertRaises(sqlite3.IntegrityError):
            self._insert_default(seal_hash='dupe')

    def test_list_palettes(self):
        self._insert_default(seal_hash='a')
        self._insert_default(seal_hash='b', designator='Second')
        palettes = self._reg.list_palettes()
        self.assertEqual(len(palettes), 2)
        self.assertEqual(palettes[0]['designator'], 'Second')  # most recent first

    def test_get_tokens_from_row(self):
        rid = self._insert_default()
        row = self._reg.get_palette(rid)
        tokens = self._reg.get_tokens_from_row(row)
        self.assertEqual(tokens['c_bg'], '#050507')


if __name__ == '__main__':
    unittest.main()
