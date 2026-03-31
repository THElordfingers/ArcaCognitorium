# Agentia Architecturalis — tests/test_theme_loader.py
# v1.0.0
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from AgentiaArchitecturalis.theme_loader import (
    load_theme, validate_theme, get_active_tokens, reset_to_defaults,
)
from AgentiaArchitecturalis.constants import MODUS_ARCANUS_DEFAULTS, TOKEN_NAMES


class TestThemeLoader(unittest.TestCase):
    def setUp(self):
        reset_to_defaults()
        self._tmp = TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()
        reset_to_defaults()

    def _write_theme(self, data, name='theme.json'):
        path = Path(self._tmp.name) / name
        path.write_text(json.dumps(data))
        return path

    def test_valid_theme_loads(self):
        data = {'tokens': dict(MODUS_ARCANUS_DEFAULTS), 'designator': 'Test'}
        path = self._write_theme(data)
        tokens = load_theme(path)
        for key in TOKEN_NAMES:
            self.assertIn(key, tokens)

    def test_missing_key_raises(self):
        incomplete = dict(MODUS_ARCANUS_DEFAULTS)
        del incomplete['c_gold']
        data = {'tokens': incomplete}
        path = self._write_theme(data)
        with self.assertRaises(ValueError) as ctx:
            load_theme(path)
        self.assertIn('c_gold', str(ctx.exception))

    def test_defaults_without_load(self):
        tokens = get_active_tokens()
        self.assertEqual(tokens, MODUS_ARCANUS_DEFAULTS)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_theme(Path('/nonexistent/theme.json'))

if __name__ == '__main__':
    unittest.main()
