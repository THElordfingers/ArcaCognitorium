# Departamentum Documentalis · config.py · v1.1
import json
from pathlib import Path

_CONFIG_PATH = Path.home() / ".arca" / "config.json"
_SELF_DIR = Path(__file__).parent

_DEFAULTS = {
    "db_path":          str(Path.home() / ".arca" / "dd.sqlite"),
    "output_dir":       str(Path.home() / ".arca" / "dd_output"),
    "bureau_i_url":     "http://localhost:8731",
    "node_script_path": str(_SELF_DIR / "node" / "emit_wiz.js"),
    "pandoc_path":      "pandoc",
    "nuntius_api":      "http://localhost:8730",
}

def load() -> dict:
    if _CONFIG_PATH.exists():
        raw = json.loads(_CONFIG_PATH.read_text())
        block = raw.get("departamentum_documentalis", {})
        return {**_DEFAULTS, **block}
    return dict(_DEFAULTS)

CFG = load()
