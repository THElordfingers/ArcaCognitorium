"""
AUCTORITAS SPECTRALIS — v1.0.0
config.py — Configuration manager
Reads ~/.arca/config.json (suite-wide) and manages
per-application preferences stored in ~/.arca/spectralis.json
"""

import json
import os
from pathlib import Path
from typing import Any


# ── Paths ──────────────────────────────────────────────────────────────

ARCA_DIR          = Path.home() / ".arca"
ARCA_CONFIG       = ARCA_DIR / "config.json"
SPECTRALIS_CONFIG = ARCA_DIR / "spectralis.json"
SIGNALS_DIR       = ARCA_DIR / "signals"
THEME_JSON        = ARCA_DIR / "theme.json"
SIGNAL_FILE       = SIGNALS_DIR / "theme_updated"


# ── Defaults ───────────────────────────────────────────────────────────

DEFAULTS: dict[str, Any] = {
    # Colour engine
    "default_harmony":          "Complementary",
    "default_contrast_algo":    "WCAG",
    # Export
    "export_directory":         str(Path.home() / "ArcaCognitorium" / "exports"),
    # Mundana State Bus (interim: filesystem watch)
    "mundana_bus_target":       "",          # empty = not connected
    "signal_file_path":         str(SIGNAL_FILE),
    # UI
    "specularium_default_ctx":  "Instrumentum",
    "lat_en_mode":              "LAT",       # "LAT" or "EN"
    # First-launch ceremony flag
    "inductio_completed":       False,
    # Registry DB path
    "registry_db_path":         str(ARCA_DIR / "chromatic_registry.db"),
}


# ── Loader ─────────────────────────────────────────────────────────────

def _ensure_dirs() -> None:
    ARCA_DIR.mkdir(parents=True, exist_ok=True)
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict[str, Any]:
    """Return merged config: defaults ← suite config ← spectralis config."""
    _ensure_dirs()

    cfg: dict[str, Any] = dict(DEFAULTS)

    # Suite config — read arca_repo_path and any suite-level keys
    if ARCA_CONFIG.exists():
        try:
            suite = json.loads(ARCA_CONFIG.read_text(encoding="utf-8"))
            # Pull export dir from suite config if present
            if "export_directory" in suite:
                cfg["export_directory"] = suite["export_directory"]
        except (json.JSONDecodeError, OSError):
            pass

    # Per-application config overlays everything
    if SPECTRALIS_CONFIG.exists():
        try:
            app_cfg = json.loads(SPECTRALIS_CONFIG.read_text(encoding="utf-8"))
            cfg.update(app_cfg)
        except (json.JSONDecodeError, OSError):
            pass

    return cfg


def save(cfg: dict[str, Any]) -> None:
    """Persist the per-application config."""
    _ensure_dirs()
    SPECTRALIS_CONFIG.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def set_key(key: str, value: Any) -> None:
    cfg = load()
    cfg[key] = value
    save(cfg)


def mark_inductio_complete() -> None:
    set_key("inductio_completed", True)


def inductio_completed() -> bool:
    return bool(get("inductio_completed", False))
