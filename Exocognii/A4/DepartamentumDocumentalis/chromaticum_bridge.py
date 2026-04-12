# Departamentum Documentalis · chromaticum_bridge.py · v1.1
import requests
from DepartamentumDocumentalis.config import CFG

_CACHE: dict = {}
_FALLBACK = {
    "void": "#050507", "obsidian": "#0a0a12", "aurum": "#d4af37",
    "parchment": "#c8b88a", "ash": "#2a2a3a", "ember": "#8b4513",
    "ghost": "#e8e8f0", "rune": "#6a5acd", "smoke": "#555566", "nil": "#000000",
}

def get_chromatica_list() -> list:
    try:
        r = requests.get(f"{CFG['bureau_i_url']}/chromatica", timeout=3)
        if r.ok:
            return r.json().get("names", [])
    except Exception:
        pass
    return list(_CACHE.keys()) or ["ModusArcanus"]

def get_theme_snapshot(chromaticum_name: str) -> dict:
    try:
        r = requests.get(f"{CFG['bureau_i_url']}/chromatica/{chromaticum_name}", timeout=3)
        if r.ok:
            data = r.json()
            _CACHE[chromaticum_name] = data
            return data
    except Exception:
        pass
    return _CACHE.get(chromaticum_name, dict(_FALLBACK))
