# state.py — Vigilarum Omnia v2
import json, os, tempfile, pathlib

STATE_DIR    = pathlib.Path.home() / ".vigilarum"
STATE_FILE   = STATE_DIR / "state.json"
DISPLAYS_DIR = STATE_DIR / "displays"

def ensure_dirs():
    STATE_DIR.mkdir(exist_ok=True)
    DISPLAYS_DIR.mkdir(exist_ok=True)

def write_state(data: dict):
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def read_state() -> dict | None:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

def state_mtime() -> float:
    try: return STATE_FILE.stat().st_mtime
    except OSError: return 0.0

def display_path(did: int): return DISPLAYS_DIR / f"display_{did}.json"

def read_display(did: int) -> dict:
    try:
        with open(display_path(did), "r", encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict): raise ValueError
        d.setdefault("widgets", []); d.setdefault("columns", 3)
        return d
    except Exception:
        return {"widgets": [], "columns": 3}

def write_display(did: int, cfg: dict):
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=DISPLAYS_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
        os.replace(tmp, display_path(did))
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def toggle_widget(did: int, wid: str) -> bool:
    cfg = read_display(did)
    if wid in cfg["widgets"]:
        cfg["widgets"].remove(wid); write_display(did, cfg); return False
    else:
        cfg["widgets"].append(wid); write_display(did, cfg); return True

def set_columns(did: int, columns: int):
    from data import VALID_COLUMNS
    if columns not in VALID_COLUMNS: return
    cfg = read_display(did); cfg["columns"] = columns; write_display(did, cfg)

def widget_assignments() -> dict:
    from data import MAX_DISPLAYS
    a = {}
    for d in range(1, MAX_DISPLAYS+1):
        for wid in read_display(d)["widgets"]:
            a.setdefault(wid, []).append(d)
    return a

def display_widget_set(did: int) -> set:
    return set(read_display(did)["widgets"])
