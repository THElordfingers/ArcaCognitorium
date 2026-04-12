# GNOSIUM EXANIMA — tests/test_vault_scanner.py
# v1.0.0
"""Vault scanner — JSON, YAML, malformed, empty, dual-format."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from Exocognii.GnosiumExanima.entity.vault_scanner import scan_vault
from Exocognii.GnosiumExanima.constants import VAULT_FORMAT_JSON, VAULT_FORMAT_YAML


def _write_json_pkg(root: Path, name: str, payload: dict) -> Path:
    pkg = root / name
    pkg.mkdir(parents=True)
    (pkg / "entity.json").write_text(json.dumps(payload))
    return pkg


def _write_yaml_pkg(root: Path, name: str, role: str, traits: str) -> Path:
    pkg = root / name
    pkg.mkdir(parents=True)
    (pkg / "role.yaml").write_text(role)
    (pkg / "traits.yaml").write_text(traits)
    return pkg


def test_empty_vault(tmp_path: Path) -> None:
    result = scan_vault(tmp_path)
    assert result.packages == []
    assert not result


def test_missing_vault_root(tmp_path: Path) -> None:
    result = scan_vault(tmp_path / "does-not-exist")
    assert result.packages == []


def test_json_package_minimal(tmp_path: Path) -> None:
    _write_json_pkg(tmp_path, "20260401_test_alpha", {
        "entity_id": "alpha",
        "display_name": "ALPHA",
        "role": "Gatekeeper",
        "purpose": "Guards the long silence.",
        "traits": {"verbosity": 0.1, "precision": 0.9},
        "lore_origin": "Arrived before the register was opened.",
    })
    result = scan_vault(tmp_path)
    assert len(result.packages) == 1
    pkg = result.packages[0]
    assert pkg.entity_id == "alpha"
    assert pkg.display_name == "ALPHA"
    assert pkg.source_format == VAULT_FORMAT_JSON
    assert "Gatekeeper" in pkg.role_text
    assert "Guards the long silence" in pkg.role_text
    assert "verbosity" in pkg.traits_text
    assert "Origin" in pkg.lore_text


def test_malformed_missing_role(tmp_path: Path) -> None:
    _write_json_pkg(tmp_path, "bad", {
        "entity_id": "bad",
        "display_name": "BAD",
        "traits": {"verbosity": 0.5},
    })
    result = scan_vault(tmp_path)
    assert result.packages == []
    # Malformed package is dropped and recorded in skipped
    assert len(result.skipped) == 1


def test_yaml_package(tmp_path: Path) -> None:
    pytest.importorskip("yaml")
    _write_yaml_pkg(
        tmp_path, "legacy_pkg",
        role="entity_id: legacy\nname: Legacy\npurpose: testing legacy path\n",
        traits="verbosity: 0.3\nprecision: 0.7\n",
    )
    result = scan_vault(tmp_path)
    assert len(result.packages) == 1
    pkg = result.packages[0]
    assert pkg.entity_id == "legacy"
    assert pkg.source_format == VAULT_FORMAT_YAML


def test_duplicate_id_deduplicated(tmp_path: Path) -> None:
    _write_json_pkg(tmp_path, "first", {
        "entity_id": "dup", "display_name": "First",
        "role": "r", "traits": {"x": 0.5},
    })
    _write_json_pkg(tmp_path, "second", {
        "entity_id": "dup", "display_name": "Second",
        "role": "r", "traits": {"x": 0.5},
    })
    result = scan_vault(tmp_path)
    assert len(result.packages) == 1
