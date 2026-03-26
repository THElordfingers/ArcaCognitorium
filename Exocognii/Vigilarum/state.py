"""
  ______   _________     _     _________  ________                     
.' ____ \ |  _   _  |   / \   |  _   _  ||_   __  |                    
| (___ \_||_/ | | \_|  / _ \  |_/ | | \_|  | |_ \_|   _ .--.   _   __  
 _.____`.     | |     / ___ \     | |      |  _| _   [ '/'`\ \[ \ [  ] 
| \____) |   _| |_  _/ /   \ \_  _| |_    _| |__/ | _ | \__/ | \ '/ /  
 \______.'  |_____||____| |____||_____|  |________|(_)| ;.__/[\_:  /   
                                                     [__|     \__.' 



VIGILARUM OMNIA — State Manager
Handles reading/writing the shared state file.
All display apps read from this; control app writes to it.
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

STATE_DIR  = Path.home() / ".vigilarum"
STATE_FILE = STATE_DIR / "state.json"
CONFIG_DIR = STATE_DIR / "displays"

def ensure_dirs():
    STATE_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)

def write_state(data: dict):
    """Atomic write — never leaves a partial file."""
    ensure_dirs()
    tmp = STATE_DIR / "state.tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    tmp.replace(STATE_FILE)

def read_state() -> dict | None:
    """Returns None if file missing or unreadable."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return None

def read_display_config(display_id: int) -> dict:
    """
    Returns config for a display.
    Config: { "widgets": [...wid...], "columns": 3 }
    Creates default if missing.
    """
    ensure_dirs()
    path = CONFIG_DIR / f"display_{display_id}.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    # Default: empty widget list, 3 columns
    default = {"widgets": [], "columns": 3}
    write_display_config(display_id, default)
    return default

def write_display_config(display_id: int, config: dict):
    ensure_dirs()
    path = CONFIG_DIR / f"display_{display_id}.json"
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

def list_displays() -> list[int]:
    """Returns sorted list of configured display IDs."""
    ensure_dirs()
    ids = []
    for p in CONFIG_DIR.glob("display_*.json"):
        try:
            n = int(p.stem.split("_")[1])
            ids.append(n)
        except Exception:
            pass
    return sorted(ids)

def assign_widget(display_id: int, wid: str):
    """Add widget to a display. Removes it from all other displays first."""
    all_ids = list_displays()
    # Remove from everywhere
    for did in all_ids:
        cfg = read_display_config(did)
        if wid in cfg["widgets"]:
            cfg["widgets"].remove(wid)
            write_display_config(did, cfg)
    # Add to target (0 = unassigned)
    if display_id > 0:
        cfg = read_display_config(display_id)
        if wid not in cfg["widgets"]:
            cfg["widgets"].append(wid)
        write_display_config(display_id, cfg)

def get_widget_display(wid: str) -> int:
    """Returns display ID widget is assigned to, or 0 if unassigned."""
    for did in list_displays():
        cfg = read_display_config(did)
        if wid in cfg.get("widgets", []):
            return did
    return 0

def set_display_columns(display_id: int, cols: int):
    cfg = read_display_config(display_id)
    cfg["columns"] = cols
    write_display_config(display_id, cfg)                                                     
