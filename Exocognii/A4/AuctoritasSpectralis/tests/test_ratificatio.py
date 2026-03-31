# Auctoritas Spectralis — tests/test_ratificatio.py
# v1.0.0
"""Unit tests for seal generation."""

import unittest
from datetime import datetime

from AuctoritasSpectralis.ratificatio import generate_seal
from AuctoritasSpectralis.constants import MODUS_ARCANUS_DEFAULTS


class TestRatificatio(unittest.TestCase):

    def test_seal_hash_is_64_hex(self):
        seal = generate_seal(MODUS_ARCANUS_DEFAULTS, 'Aureus Profundus')
        self.assertEqual(len(seal['seal_hash']), 64)
        int(seal['seal_hash'], 16)  # should not raise

    def test_timestamp_is_iso8601(self):
        seal = generate_seal(MODUS_ARCANUS_DEFAULTS, 'Aureus Profundus')
        dt = datetime.fromisoformat(seal['sealed_at'])
        self.assertIsNotNone(dt)

    def test_different_timestamps_produce_different_hashes(self):
        seal1 = generate_seal(MODUS_ARCANUS_DEFAULTS, 'Aureus Profundus')
        seal2 = generate_seal(MODUS_ARCANUS_DEFAULTS, 'Aureus Profundus')
        self.assertNotEqual(seal1['seal_hash'], seal2['seal_hash'])

    def test_canonical_json_present(self):
        seal = generate_seal(MODUS_ARCANUS_DEFAULTS, 'Test')
        self.assertIn('c_bg', seal['canonical_json'])


if __name__ == '__main__':
    unittest.main()
