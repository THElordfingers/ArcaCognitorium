"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈                   ██████  ██████  ███    ██ ███████ ██  ██████  ██    ██ ██    ██ ███████ ▍
🮈                  ██      ██    ██ ████   ██ ██      ██ ██       ██    ██ ██    ██ ██      ▍
🮈                  ██      ██    ██ ██ ██  ██ █████   ██ ██   ███ ██    ██ ██    ██ ███████ ▍
🮈                  ██      ██    ██ ██  ██ ██ ██      ██ ██    ██ ██    ██ ██    ██      ██ ▍
🮈                   ██████  ██████  ██   ████ ██      ██  ██████   ██████   ██████  ███████ ▍
🮈                                                                                           ▍
🮈                                                                                           ▍
🮈           Python Script           ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
🮈      PRAESIDIUM · configuus.py                                                   ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              configuus.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · configuus.py
# ~/.arca/config.json loader with typed accessors.
# version: 1.0.0
"""

import json
from pathlib import Path


class ConfigError(Exception):
    pass


class Configuus:
    """
    Loads ~/.arca/config.json and exposes typed property accessors.
    Raises ConfigError on missing required keys.
    Call Configuus() once at startup; pass instance to modules that need it.

    Minimum required config.json:
    {
        "arca_repo_path": "/home/lordfingers/ArcaCognitorium",
        "praesidium_api": "http://localhost:8300",
        "exvacua_loricum_api": "http://localhost:8301",
        "perpetuum_aedificare_api": "http://localhost:8302"
    }
    """

    REQUIRED_KEYS = (
        "arca_repo_path",
    )

    def __init__(self, path: Path | None = None):
        self._path = path or (Path.home() / ".arca" / "config.json")
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            # Create minimal config with sensible defaults on first run
            self._path.parent.mkdir(parents=True, exist_ok=True)
            defaults = {
                "arca_repo_path": str(Path.home() / "ArcaCognitorium"),
                "praesidium_api": "http://localhost:8300",
                "exvacua_loricum_api": "http://localhost:8301",
                "perpetuum_aedificare_api": "http://localhost:8302",
            }
            self._path.write_text(json.dumps(defaults, indent=2))
            self._data = defaults
            return

        try:
            self._data = json.loads(self._path.read_text())
        except json.JSONDecodeError as e:
            raise ConfigError(f"Malformed config at {self._path}: {e}") from e

        for key in self.REQUIRED_KEYS:
            if key not in self._data:
                raise ConfigError(f"Required key '{key}' missing from {self._path}")

    @property
    def arca_repo_path(self) -> Path:
        return Path(self._data["arca_repo_path"])

    @property
    def praesidium_api(self) -> str:
        return self._data.get("praesidium_api", "http://localhost:8300")

    @property
    def exvacua_loricum_api(self) -> str:
        return self._data.get("exvacua_loricum_api", "http://localhost:8301")

    @property
    def perpetuum_aedificare_api(self) -> str:
        return self._data.get("perpetuum_aedificare_api", "http://localhost:8302")

    def claudebox_path(self) -> Path:
        """Returns arca_repo_path / claudebox — canonical ClaudeBox location."""
        return self.arca_repo_path / "claudebox"

    def get(self, key: str, default=None):
        """Escape hatch for arbitrary config keys."""
        return self._data.get(key, default)

