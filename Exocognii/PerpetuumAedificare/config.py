#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            config.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import json
from pathlib import Path

_CONFIG_FILE = Path.home() / ".arca" / "config.json"
_ARCA_DIR    = Path.home() / ".arca"

_DEFAULTS = {
    "port":                        8732,
    "perpetuum_aedificare_db":     str(_ARCA_DIR / "perpetuum_aedificare.db"),
    "perpetuum_aedificare_store":  str(_ARCA_DIR / "perpetuum_aedificare"),
    "perpetuum_aedificare": {
        "aggrexuum_interval":  300,   # seconds
        "aggrexuum_threshold": 10,    # pending captures
        "drift_threshold":     0.65,  # Driftuum Metrica threshold
    },
}


def load_config() -> dict:
    cfg = dict(_DEFAULTS)
    try:
        with _CONFIG_FILE.open() as f:
            raw = json.load(f)
        cfg.update(raw)
        sub = _DEFAULTS["perpetuum_aedificare"].copy()
        sub.update(raw.get("perpetuum_aedificare", {}))
        cfg["perpetuum_aedificare"] = sub
    except (OSError, json.JSONDecodeError):
        pass
    Path(cfg["perpetuum_aedificare_store"]).mkdir(parents=True, exist_ok=True)
    return cfg


_cfg: dict = {}


def get() -> dict:
    global _cfg
    if not _cfg:
        _cfg = load_config()
    return _cfg
