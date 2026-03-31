# Auctoritas Spectralis — tests/test_derivatio.py
# v1.0.0
"""Unit tests for the OKLAB derivation pipeline."""

import re
import unittest

from AuctoritasSpectralis.derivatio import derive_tokens, hex_to_oklab, oklab_to_hex
from AuctoritasSpectralis.constants import DEFAULT_BG, DEFAULT_FG, TOKEN_NAMES

HEX_RE = re.compile(r'^#[0-9a-f]{6}$')


class TestDerivatio(unittest.TestCase):

    def setUp(self):
        self.result = derive_tokens(DEFAULT_BG, DEFAULT_FG)
        self.tokens = self.result['tokens']
        self.oklab = self.result['oklab']

    def test_all_ten_tokens_present(self):
        for name in TOKEN_NAMES:
            self.assertIn(name, self.tokens)

    def test_all_tokens_valid_hex(self):
        for name, val in self.tokens.items():
            self.assertRegex(val, HEX_RE, f'{name} is not valid hex: {val}')

    def test_oklab_lightness_in_range(self):
        for name, coords in self.oklab.items():
            self.assertGreaterEqual(coords['l'], 0.0, f'{name} L below 0')
            self.assertLessEqual(coords['l'], 1.0, f'{name} L above 1')

    def test_no_identical_adjacent_lightness(self):
        entries = sorted(self.oklab.items(), key=lambda x: x[1]['l'])
        for i in range(len(entries) - 1):
            name_a, coords_a = entries[i]
            name_b, coords_b = entries[i + 1]
            self.assertNotAlmostEqual(
                coords_a['l'], coords_b['l'], places=4,
                msg=f'{name_a} and {name_b} have identical lightness'
            )

    def test_roundtrip_hex_oklab(self):
        l, a, b = hex_to_oklab('#d4af37')
        back = oklab_to_hex(l, a, b)
        self.assertEqual(back, '#d4af37')

    def test_bg_is_identity(self):
        self.assertEqual(self.tokens['c_bg'], DEFAULT_BG)

    def test_gold_is_fg_identity(self):
        self.assertEqual(self.tokens['c_gold'], DEFAULT_FG)


if __name__ == '__main__':
    unittest.main()
