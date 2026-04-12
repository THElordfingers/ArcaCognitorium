# GNOSIUM EXANIMA — prompt/tower_memory.py
# v1.0.0
"""
Read-only access to Tower entity memory.

The Tower maintains per-entity memory.json files at
~/ArcaCognitorium/storage/entities/{entity_id}/memory.json. GNOSIUM
reads these as optional context seeds for the Chamber composite prompt.

GNOSIUM NEVER writes to this path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def read_tower_memory(memory_root: Path, entity_id: str) -> Optional[str]:
    """
    Return a formatted string for inclusion in the entity's prompt block,
    or None if no memory file exists or it cannot be read.
    """
    path = memory_root / entity_id / "memory.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return _format_memory(data)


def _format_memory(data) -> Optional[str]:
    if isinstance(data, str):
        return data.strip() or None
    if not isinstance(data, dict):
        return None
    lines: list[str] = []
    for key in ("summary", "highlights", "recent_interactions", "notes"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            lines.append(f"{key}: {val.strip()}")
        elif isinstance(val, list) and val:
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item}")
    if not lines:
        # Fall back to a compact JSON dump if none of the known keys match
        return json.dumps(data, indent=2)[:2000]
    return "\n".join(lines)
