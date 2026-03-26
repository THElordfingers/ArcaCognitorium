"""
core/session.py
Autosave the current composition tree to ~/.config/fenestrium/session.json
on exit, restore on launch.

Write strategy: write to .tmp, then os.replace() for atomicity —
a crash mid-write never corrupts the saved session.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

from core.tree import WidgetNode


CONFIG_DIR  = Path.home() / ".config" / "fenestrium"
SESSION_FILE = CONFIG_DIR / "session.json"
TMP_FILE     = CONFIG_DIR / "session.json.tmp"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save(root: Optional[WidgetNode], selected_uid: Optional[str] = None) -> None:
    """
    Atomically save the current tree to disk.
    Called from App.on_unmount / action_quit.
    """
    _ensure_dir()
    payload = {
        "version":      1,
        "tree":         root.to_dict() if root else None,
        "selected_uid": selected_uid,
    }
    TMP_FILE.write_text(json.dumps(payload, indent=2))
    os.replace(TMP_FILE, SESSION_FILE)


def load() -> tuple[Optional[WidgetNode], Optional[str]]:
    """
    Load the last saved session.
    Returns (root_node, selected_uid) or (None, None) if no session exists
    or the file is corrupt.
    """
    if not SESSION_FILE.exists():
        return None, None
    try:
        payload = json.loads(SESSION_FILE.read_text())
        tree_dict = payload.get("tree")
        root = WidgetNode.from_dict(tree_dict) if tree_dict else None
        return root, payload.get("selected_uid")
    except Exception:
        # Corrupt session — start fresh, don't crash
        return None, None


def clear() -> None:
    """Delete the saved session."""
    SESSION_FILE.unlink(missing_ok=True)
