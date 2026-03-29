#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            config.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Config loader for Exvacua Loricum.
Reads ~/.arca/config.json. Falls back to safe defaults.
"""

import json
from pathlib import Path

_CONFIG_FILE = Path.home() / ".arca" / "config.json"
_ARCA_DIR    = Path.home() / ".arca"

_DEFAULTS = {
    "port":                   8731,
    "exvacua_loricum_db":     str(_ARCA_DIR / "exvacua_loricum.db"),
    "exvacua_loricum_store":  str(_ARCA_DIR / "exvacua_loricum"),
    "exvacua_loricum": {
        "interpretus_interval":  600,   # seconds
        "interpretus_threshold": 20,    # pending lorixii count
    },
}


def load_config() -> dict:
    cfg = dict(_DEFAULTS)
    try:
        with _CONFIG_FILE.open() as f:
            raw = json.load(f)
        cfg.update(raw)
        # Merge sub-dict rather than replace
        sub = _DEFAULTS["exvacua_loricum"].copy()
        sub.update(raw.get("exvacua_loricum", {}))
        cfg["exvacua_loricum"] = sub
    except (OSError, json.JSONDecodeError):
        pass

    # Ensure store directory exists
    Path(cfg["exvacua_loricum_store"]).mkdir(parents=True, exist_ok=True)
    return cfg


# Module-level singleton — importable directly
_cfg: dict = {}


def get() -> dict:
    global _cfg
    if not _cfg:
        _cfg = load_config()
    return _cfg
