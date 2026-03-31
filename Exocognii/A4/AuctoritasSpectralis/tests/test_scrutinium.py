# Auctoritas Spectralis — tests/test_scrutinium.py
# v1.0.0
"""Unit tests for the contrast engine."""

import unittest

from AuctoritasSpectralis.derivatio import derive_tokens
from AuctoritasSpectralis.scrutinium import (
    compute_wcag_ratio, compute_apca_lc, build_contrast_matrix,
    audit_passes, simulate_cvd,
)
from AuctoritasSpectralis.constants import DEFAULT_BG, DEFAULT_FG


class TestScrutinium(unittest.TestCase):

    def setUp(self):
        result = derive_tokens(DEFAULT_BG, DEFAULT_FG)
        self.tokens = result['tokens']

    def test_gold_on_bg_passes_aa(self):
        ratio = compute_wcag_ratio(self.tokens['c_gold'], self.tokens['c_bg'])
        self.assertGreaterEqual(ratio, 4.5, 'C_GOLD on C_BG should pass AA')

    def test_gold_dim_on_panel_ratio_above_one(self):
        ratio = compute_wcag_ratio(self.tokens['c_gold_dim'], self.tokens['c_panel'])
        self.assertGreater(ratio, 1.0)

    def test_cvd_deuteranopia_returns_valid_hex(self):
        sim = simulate_cvd(self.tokens['c_crimson'], 'deuteranopia')
        self.assertRegex(sim, r'^#[0-9a-f]{6}$')
        self.assertNotEqual(sim, self.tokens['c_crimson'])

    def test_wcag_ratio_black_white(self):
        ratio = compute_wcag_ratio('#ffffff', '#000000')
        self.assertAlmostEqual(ratio, 21.0, places=0)

    def test_apca_returns_float(self):
        lc = compute_apca_lc('#d4af37', '#050507')
        self.assertIsInstance(lc, float)

    def test_contrast_matrix_not_empty(self):
        matrix = build_contrast_matrix(self.tokens)
        self.assertGreater(len(matrix), 0)

    def test_audit_returns_required_keys(self):
        matrix = build_contrast_matrix(self.tokens)
        audit = audit_passes(matrix)
        for key in ['passes_aa', 'passes_aaa', 'min_wcag_ratio', 'min_apca_lc', 'failing_pairs']:
            self.assertIn(key, audit)


if __name__ == '__main__':
    unittest.main()
