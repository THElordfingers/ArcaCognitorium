"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈   ██████  ██████  ███    ██ ███████ ██  ██████   ▍
🮈  ██      ██    ██ ████   ██ ██      ██ ██        ▍
🮈  ██      ██    ██ ██ ██  ██ █████   ██ ██   ███  ▍
🮈  ██      ██    ██ ██  ██ ██ ██      ██ ██    ██  ▍
🮈   ██████  ██████  ██   ████ ██      ██  ██████   ▍
🮈                                                  ▍
🮈                                                  ▍
🮈                  Python Script                   ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

# =============================================================================
# INCITAMENTUM — config.py
# Version: 2.0
# Arca Cognitorium — Config and history persistence (~/.arca/)
# =============================================================================

import json
from pathlib import Path
from datetime import datetime, timezone

CONFIG_DIR   = Path.home() / '.arca'
CONFIG_FILE  = CONFIG_DIR / 'config.json'
HISTORY_FILE = CONFIG_DIR / 'history.json'
HISTORY_MAX  = 50

DEFAULTS: dict = {
    'repo_url': 'https://raw.githubusercontent.com/lordfingers/ArcaCognitorium/main/',
    'model':    'claude-sonnet-4-5',
}


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load config.json, filling missing keys from DEFAULTS."""
    cfg = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open() as f:
                loaded = json.load(f)
            cfg.update(loaded)
        except (json.JSONDecodeError, OSError):
            pass  # corrupt or unreadable — return defaults silently
    return cfg


def save_config(cfg: dict) -> bool:
    """
    Write cfg to config.json. Creates ~/.arca if needed.
    Returns True on success, False if write fails (logs warning to stderr).
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open('w') as f:
            json.dump(cfg, f, indent=2)
        return True
    except OSError:
        return False


# ── History ───────────────────────────────────────────────────────────────────

def load_history() -> list[dict]:
    """Load history.json. Returns empty list if absent or corrupt."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open() as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def append_history(entry: dict) -> bool:
    """
    Append one history entry, trim to HISTORY_MAX, write back.
    Entry shape: {timestamp, session_key, session_label, prompt, status}
    Returns True on success.
    """
    history = load_history()
    entry.setdefault('timestamp', datetime.now(timezone.utc).isoformat())
    history.append(entry)
    if len(history) > HISTORY_MAX:
        history = history[-HISTORY_MAX:]
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with HISTORY_FILE.open('w') as f:
            json.dump(history, f, indent=2)
        return True
    except OSError:
        return False


def make_history_entry(
    session_key:   str,
    session_label: str,
    prompt:        str,
    status:        str = 'complete',
) -> dict:
    """Construct a well-formed history entry dict."""
    return {
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'session_key':   session_key,
        'session_label': session_label,
        'prompt':        prompt,
        'status':        status,
    }
