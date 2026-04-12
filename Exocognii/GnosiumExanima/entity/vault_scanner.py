# GNOSIUM EXANIMA — entity/vault_scanner.py
# v1.0.0
"""
Vault scanner — reads entity packages from disk.

Supports two on-disk formats:

  1. EntitexRefined (primary): one subdirectory per entity containing
     entity.json plus an optional portrait.png. The JSON carries
     `entity_id`, `display_name`, `role` (or `purpose`), a `traits` dict,
     and `lore_*` fields.

  2. Legacy Entitex staged (fallback): subdirectory containing
     role.yaml, traits.yaml, and optional lore.yaml + portrait.png.

Malformed or incomplete packages are skipped with a warning logged to
stderr. The scanner never raises on a bad package — it only raises if
the vault root itself is unreadable.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from ..constants import VAULT_FORMAT_JSON, VAULT_FORMAT_YAML
from .models import EntityPackage

try:
    import yaml  # type: ignore
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ─── Result envelope ───────────────────────────────────────────────
@dataclass
class VaultScanResult:
    packages: list[EntityPackage]
    skipped: list[tuple[Path, str]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.packages)

    def by_id(self) -> dict[str, EntityPackage]:
        return {p.entity_id: p for p in self.packages}


# ─── Public entry point ────────────────────────────────────────────
def scan_vault(*roots: Path) -> VaultScanResult:
    """
    Scan one or more vault roots. Returns the union of discovered packages,
    deduplicated by entity_id (first wins — primary roots should come first).
    """
    result = VaultScanResult(packages=[])
    seen: set[str] = set()

    for root in roots:
        if not root or not root.exists() or not root.is_dir():
            continue
        for pkg_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            pkg = _load_package(pkg_dir)
            if pkg is None:
                result.skipped.append((pkg_dir, "unrecognised or malformed package"))
                continue
            if pkg.entity_id in seen:
                continue
            seen.add(pkg.entity_id)
            result.packages.append(pkg)

    # Stable ordering: by display_name, case-insensitive
    result.packages.sort(key=lambda p: p.display_name.casefold())
    return result


# ─── Loader dispatch ───────────────────────────────────────────────
def _load_package(pkg_dir: Path) -> Optional[EntityPackage]:
    try:
        json_path = pkg_dir / "entity.json"
        if json_path.exists():
            return _load_json_package(pkg_dir, json_path)

        role_path = pkg_dir / "role.yaml"
        traits_path = pkg_dir / "traits.yaml"
        if role_path.exists() and traits_path.exists():
            if not _HAS_YAML:
                _warn(pkg_dir, "legacy YAML package found but PyYAML not installed")
                return None
            return _load_yaml_package(pkg_dir, role_path, traits_path)

        return None
    except Exception as exc:
        _warn(pkg_dir, f"load failure: {exc}")
        return None


# ─── JSON loader (EntitexRefined) ──────────────────────────────────
def _load_json_package(pkg_dir: Path, json_path: Path) -> Optional[EntityPackage]:
    data = json.loads(json_path.read_text(encoding="utf-8"))

    entity_id = data.get("entity_id") or _derive_id_from_dir(pkg_dir)
    display_name = (
        data.get("display_name")
        or data.get("title")
        or entity_id.replace("_", " ").title()
    )

    # Combine the short role title with the longer purpose/function block
    role_parts: list[str] = []
    for key in ("role", "title"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            role_parts.append(val.strip())
            break
    for key in ("purpose", "function"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            role_parts.append(val.strip())
            break
    role_text = "\n\n".join(role_parts)

    traits_text = _format_traits(data.get("traits"), data.get("personality"))
    lore_text = _format_lore(data)

    if not role_text.strip() or not traits_text.strip():
        _warn(pkg_dir, "missing role or traits content")
        return None

    return EntityPackage(
        entity_id=entity_id,
        display_name=display_name,
        source_path=pkg_dir,
        source_format=VAULT_FORMAT_JSON,
        role_text=role_text,
        traits_text=traits_text,
        lore_text=lore_text,
        portrait_path=_find_portrait(pkg_dir),
        raw=data,
    )


def _format_traits(traits, personality: Optional[str]) -> str:
    parts: list[str] = []
    if isinstance(traits, dict) and traits:
        parts.append("Disposition axes (0.0–1.0):")
        for key, val in traits.items():
            parts.append(f"  - {key}: {val}")
    if isinstance(personality, str) and personality.strip():
        if parts:
            parts.append("")
        parts.append(personality.strip())
    return "\n".join(parts)


def _format_lore(data: dict) -> str:
    """Collect lore_* fields into a prose block, in canonical order."""
    order = ("lore_origin", "lore_nature", "lore_relationship", "lore_aura")
    labels = {
        "lore_origin": "Origin",
        "lore_nature": "Nature",
        "lore_relationship": "Relation to the Wizard",
        "lore_aura": "Aura",
    }
    chunks: list[str] = []
    for key in order:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            chunks.append(f"{labels[key]}: {val.strip()}")
    return "\n\n".join(chunks)


# ─── YAML loader (legacy Entitex staged) ───────────────────────────
def _load_yaml_package(
    pkg_dir: Path,
    role_path: Path,
    traits_path: Path,
) -> Optional[EntityPackage]:
    role = yaml.safe_load(role_path.read_text(encoding="utf-8")) or {}
    traits = yaml.safe_load(traits_path.read_text(encoding="utf-8")) or {}
    lore_path = pkg_dir / "lore.yaml"
    lore = {}
    if lore_path.exists():
        lore = yaml.safe_load(lore_path.read_text(encoding="utf-8")) or {}

    entity_id = (
        role.get("entity_id")
        or role.get("id")
        or _derive_id_from_dir(pkg_dir)
    )
    display_name = (
        role.get("display_name")
        or role.get("name")
        or entity_id.replace("_", " ").title()
    )

    role_text = _yaml_block_to_text(role, skip={"entity_id", "id", "display_name", "name"})
    traits_text = _yaml_block_to_text(traits)
    lore_text = _yaml_block_to_text(lore) if lore else ""

    if not role_text.strip() or not traits_text.strip():
        _warn(pkg_dir, "missing role or traits content in YAML package")
        return None

    return EntityPackage(
        entity_id=entity_id,
        display_name=display_name,
        source_path=pkg_dir,
        source_format=VAULT_FORMAT_YAML,
        role_text=role_text,
        traits_text=traits_text,
        lore_text=lore_text,
        portrait_path=_find_portrait(pkg_dir),
        raw={"role": role, "traits": traits, "lore": lore},
    )


def _yaml_block_to_text(block, skip: Optional[set[str]] = None) -> str:
    skip = skip or set()
    if isinstance(block, str):
        return block.strip()
    if not isinstance(block, dict):
        return ""
    lines: list[str] = []
    for key, val in block.items():
        if key in skip:
            continue
        if isinstance(val, (list, tuple)):
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item}")
        elif isinstance(val, dict):
            lines.append(f"{key}:")
            for sub_k, sub_v in val.items():
                lines.append(f"  {sub_k}: {sub_v}")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


# ─── Helpers ───────────────────────────────────────────────────────
def _first_nonempty(*candidates) -> Optional[str]:
    for c in candidates:
        if isinstance(c, str) and c.strip():
            return c
    return None


def _derive_id_from_dir(pkg_dir: Path) -> str:
    """Fallback id from dir name, stripping leading timestamp prefixes."""
    name = pkg_dir.name
    for i, ch in enumerate(name):
        if ch == "_" and i > 0 and name[:i].replace("_", "").isdigit():
            tail = name[i + 1:]
            if tail:
                return tail
    return name


def _find_portrait(pkg_dir: Path) -> Optional[Path]:
    for candidate in ("portrait.png", "portrait.jpg", "portrait.webp"):
        p = pkg_dir / candidate
        if p.exists():
            return p
    return None


def _warn(pkg_dir: Path, reason: str) -> None:
    print(f"[gnosium.vault] skipped {pkg_dir.name}: {reason}", file=sys.stderr)
