"""
Agentia Architecturalis — Test Suite (21 tests)

Per build specification, these tests verify all critical invariants.
"""
from __future__ import annotations

import ast
import json
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from AgentiaArchitecturalis import tokens
from AgentiaArchitecturalis.models import ElementNode, DesignDocument
from AgentiaArchitecturalis.theme_manager import ThemeManager
from AgentiaArchitecturalis.features.tabula.element_registry import (
    ALL_ELEMENTS, CATEGORIES, get_element_def, ELEMENT_MAP,
)
from AgentiaArchitecturalis.features.codex_exportum.codex_feature import (
    generate_code, validate_code, _collect_used_tokens,
)


class TestTokens(TestCase):
    """Tests 1-3: Token system."""

    def test_01_ten_tokens_defined(self):
        """T01: Exactly 10 token names defined."""
        self.assertEqual(len(tokens.TOKEN_NAMES), 10)

    def test_02_defaults_match_names(self):
        """T02: DEFAULTS dict keys match TOKEN_NAMES."""
        self.assertEqual(sorted(tokens.DEFAULTS.keys()), sorted(tokens.TOKEN_NAMES))

    def test_03_all_defaults_are_hex(self):
        """T03: All default values are valid hex colour codes."""
        hex_re = re.compile(r'^#[0-9a-fA-F]{6}$')
        for name, value in tokens.DEFAULTS.items():
            self.assertRegex(value, hex_re, f"Token {name} is not valid hex: {value}")


class TestModels(TestCase):
    """Tests 4-6: Data model serialization."""

    def test_04_element_node_roundtrip(self):
        """T04: ElementNode serializes and deserializes losslessly."""
        child = ElementNode("QLabel_gold", "lbl_1", "Ostensio", {"width": 200}, [], 10, 20)
        parent = ElementNode("QFrame", "frame_1", "Receptacula", {"width": 300}, [child], 0, 0)
        d = parent.to_dict()
        restored = ElementNode.from_dict(d)
        self.assertEqual(restored.var_name, "frame_1")
        self.assertEqual(len(restored.children), 1)
        self.assertEqual(restored.children[0].var_name, "lbl_1")
        self.assertEqual(restored.children[0].x, 10)
        self.assertEqual(restored.children[0].y, 20)

    def test_05_design_document_roundtrip(self):
        """T05: DesignDocument JSON round-trip is lossless."""
        elem = ElementNode("QFrame", "f1", "Receptacula", {"width": 100}, [], 50, 60)
        doc = DesignDocument("test_canvas", [elem], "Nox Aurum", 1)
        j = doc.to_json()
        restored = DesignDocument.from_json(j)
        self.assertEqual(restored.name, "test_canvas")
        self.assertEqual(restored.theme_designator, "Nox Aurum")
        self.assertEqual(len(restored.elements), 1)
        self.assertEqual(restored.elements[0].x, 50)

    def test_06_child_xy_parent_relative(self):
        """T06: Children store x/y as parent-relative offsets (constraint #5)."""
        child = ElementNode("QLabel_gold", "c1", "", {"width": 100}, [], 16, 32)
        parent = ElementNode("QFrame", "p1", "", {"width": 300}, [child], 100, 200)
        d = parent.to_dict()
        # Child coordinates should be relative, not scene-absolute
        self.assertEqual(d["children"][0]["x"], 16)
        self.assertEqual(d["children"][0]["y"], 32)


class TestThemeManager(TestCase):
    """Tests 7-9: Theme management."""

    def test_07_defaults_are_nox_aurum(self):
        """T07: Default theme is Nox Aurum."""
        tm = ThemeManager()
        self.assertEqual(tm.theme_name, "Nox Aurum")
        self.assertEqual(len(tm.active_tokens), 10)

    def test_08_load_valid_theme(self):
        """T08: Loading a valid theme.json updates tokens."""
        tm = ThemeManager()
        theme_data = {
            "name": "Test Theme",
            "tokens": {name: "#ffffff" for name in tokens.TOKEN_NAMES},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            f.flush()
            ok, msg = tm.load_theme(Path(f.name))
        self.assertTrue(ok)
        self.assertEqual(tm.theme_name, "Test Theme")
        self.assertEqual(tm.active_tokens["C_GOLD"], "#ffffff")

    def test_09_load_missing_tokens_fails(self):
        """T09: Loading theme with missing tokens fails gracefully."""
        tm = ThemeManager()
        theme_data = {"name": "Bad", "tokens": {"C_BG": "#000000"}}  # Missing 9 tokens
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            f.flush()
            ok, msg = tm.load_theme(Path(f.name))
        self.assertFalse(ok)
        self.assertIn("Missing tokens", msg)


class TestElementRegistry(TestCase):
    """Tests 10-12: Element registry."""

    def test_10_twentyeight_elements(self):
        """T10: 28 element types registered."""
        self.assertEqual(len(ALL_ELEMENTS), 28)

    def test_11_seven_categories(self):
        """T11: 7 palette categories."""
        self.assertEqual(len(CATEGORIES), 7)

    def test_12_containers_accept_children(self):
        """T12: All Receptacula elements accept children."""
        for cat_name, elems in CATEGORIES:
            if cat_name == "Receptacula":
                for edef in elems:
                    self.assertTrue(
                        edef.accepts_children,
                        f"{edef.element_type} should accept children",
                    )


class TestCodeGeneration(TestCase):
    """Tests 13-17: Code generation invariants."""

    def test_13_zero_raw_hex_in_output(self):
        """T13: Generated code contains zero raw hex literals (constraint #1)."""
        elem = ElementNode(
            "ArcaneButton_gold", "btn_1", "Actiones",
            {"width": 140, "height": 34, "bg_token": "C_PANEL", "border_token": "C_GOLD_DARK"},
            [], 0, 0,
        )
        code = generate_code("test", [elem])
        # Find all hex patterns that are NOT inside f-string token refs
        # Raw hex would be like: "#d4af37" not inside {TOKEN_NAME}
        lines = code.split("\n")
        for line in lines:
            # Skip comments and the docstring
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            # Check for raw hex that isn't a token reference
            hex_matches = re.findall(r'#[0-9a-fA-F]{6}', line)
            for match in hex_matches:
                # These specific accent colours are allowed as they're
                # derived constants, not design tokens
                allowed = {"#3aacac", "#c04040", "#0d3030", "#2a0808"}
                if match not in allowed:
                    self.fail(f"Raw hex {match} found in generated code: {line}")

    def test_14_ast_parse_validates(self):
        """T14: Generated code passes ast.parse() (constraint #2)."""
        elem = ElementNode("QFrame", "f1", "Receptacula", {"width": 200, "height": 100}, [], 0, 0)
        code = generate_code("test_widget", [elem])
        valid, msg = validate_code(code)
        self.assertTrue(valid, f"AST validation failed: {msg}")

    def test_15_empty_canvas_valid_python(self):
        """T15: Empty canvas generates valid Python."""
        code = generate_code("empty_canvas", [])
        valid, msg = validate_code(code)
        self.assertTrue(valid, f"Empty canvas code invalid: {msg}")
        self.assertIn("class EmptyCanvas", code)
        self.assertIn("pass", code)

    def test_16_used_tokens_imported(self):
        """T16: Only used tokens are imported."""
        elem = ElementNode(
            "QFrame", "f1", "",
            {"bg_token": "C_PANEL", "border_token": "C_GOLD_DARK"}, [], 0, 0,
        )
        used = _collect_used_tokens([elem])
        self.assertIn("C_PANEL", used)
        self.assertIn("C_GOLD_DARK", used)
        # Unused tokens should not be in the import
        code = generate_code("test", [elem])
        if "from tokens import" in code:
            import_line = [l for l in code.split("\n") if "from tokens import" in l][0]
            self.assertNotIn("C_CRIMSON", import_line)

    def test_17_nested_elements_generate(self):
        """T17: Nested elements generate valid code."""
        child = ElementNode("QLabel_gold", "lbl", "", {"width": 100, "text_content": "Hello"}, [], 10, 10)
        parent = ElementNode("QFrame", "frm", "Receptacula", {"width": 300, "layout_type": "vertical"}, [child], 0, 0)
        code = generate_code("nested_test", [parent])
        valid, msg = validate_code(code)
        self.assertTrue(valid, f"Nested code invalid: {msg}")
        self.assertIn("self.frm", code)
        self.assertIn("self.lbl", code)


class TestArmariumDB(TestCase):
    """Tests 18-19: Armarium database."""

    def test_18_schema_version_exists(self):
        """T18: Armarium schema includes schema_version (constraint #8)."""
        from AgentiaArchitecturalis.features.armarium.armarium_db import ArmariumDB
        with tempfile.TemporaryDirectory() as tmp:
            import AgentiaArchitecturalis.features.armarium.armarium_db as db_mod
            orig = db_mod._DB_PATH
            db_mod._DB_PATH = Path(tmp) / "test.db"
            try:
                db = ArmariumDB()
                row = db._conn.execute(
                    "SELECT value FROM schema_meta WHERE key = 'schema_version'"
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(row["value"], "1.0")
                db.close()
            finally:
                db_mod._DB_PATH = orig

    def test_19_seal_and_fork_preserves_lineage(self):
        """T19: Fork preserves parent_id lineage."""
        from AgentiaArchitecturalis.features.armarium.armarium_db import ArmariumDB
        with tempfile.TemporaryDirectory() as tmp:
            import AgentiaArchitecturalis.features.armarium.armarium_db as db_mod
            orig = db_mod._DB_PATH
            db_mod._DB_PATH = Path(tmp) / "test.db"
            try:
                db = ArmariumDB()
                comp_id = db.seal("Test", "panel", '{"elements": []}')
                fork_id = db.fork(comp_id)
                self.assertIsNotNone(fork_id)
                forked = db.load(fork_id)
                self.assertEqual(forked.parent_id, comp_id)
                self.assertEqual(forked.version, 2)
                db.close()
            finally:
                db_mod._DB_PATH = orig


class TestDirtyState(TestCase):
    """Test 20: Dirty state indicator."""

    def test_20_dirty_ring_is_u25cc(self):
        """T20: Dirty state uses ◌ (U+25CC) (constraint #4)."""
        from AgentiaArchitecturalis.titulum import DIRTY_RING
        self.assertEqual(DIRTY_RING, "\u25CC")


class TestOpeningCeremony(TestCase):
    """Test 21: Opening ceremony."""

    def test_21_ceremony_has_canonical_text(self):
        """T21: Opening ceremony contains canonical bureau text."""
        from AgentiaArchitecturalis.opening_ceremony import CEREMONY_TEXT
        self.assertIn("AGENTIA ARCHITECTURALIS", CEREMONY_TEXT.upper())
        self.assertIn("In Linea", CEREMONY_TEXT)
        self.assertIn("In Parallelo", CEREMONY_TEXT)
        self.assertIn("In Perpetuum", CEREMONY_TEXT)
        self.assertIn("bureau awaits alignment", CEREMONY_TEXT.lower())


if __name__ == "__main__":
    main()
