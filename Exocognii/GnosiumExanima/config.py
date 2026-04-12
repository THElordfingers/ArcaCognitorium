# GNOSIUM EXANIMA — config.py
# v1.0.0
"""
Bridge to PRAESIDIUM Configuus with GNOSIUM-specific keys.

Reads ~/.arca/config.json via Configuus. Adds typed accessors for the
gnosium.* namespace used by the distillation and token-budget subsystems.
"""

from __future__ import annotations

from pathlib import Path

from .constants import (
    DEFAULT_DISTILLATION_THRESHOLD,
    DEFAULT_SYSTEM_PROMPT_TOKEN_CEILING,
    DEFAULT_MUNDANA_POLL_SECONDS,
)


class GnosiumConfig:
    """Thin wrapper over PRAESIDIUM.Configuus with gnosium.* accessors."""

    def __init__(self, configuus=None):
        if configuus is None:
            from Exocognii.Praesidium.configuus import Configuus
            configuus = Configuus()
        self._cfg = configuus

    # ── PRAESIDIUM passthroughs ───────────────────────────────────
    @property
    def arca_repo_path(self) -> Path:
        return self._cfg.arca_repo_path

    @property
    def claudebox_path(self) -> Path:
        return self._cfg.claudebox_path()

    @property
    def praesidium_api(self) -> str:
        return self._cfg.praesidium_api

    @property
    def exvacua_loricum_api(self) -> str:
        return self._cfg.exvacua_loricum_api

    @property
    def perpetuum_aedificare_api(self) -> str:
        return self._cfg.perpetuum_aedificare_api

    # ── GNOSIUM-specific keys (nested under "gnosium" or flat) ────
    def _gnosium(self, key: str, default):
        # Support both {"gnosium": {"key": ...}} and "gnosium.key" flat form
        nested = self._cfg.get("gnosium", None)
        if isinstance(nested, dict) and key in nested:
            return nested[key]
        return self._cfg.get(f"gnosium.{key}", default)

    @property
    def distillation_threshold(self) -> int:
        return int(self._gnosium("distillation_threshold",
                                 DEFAULT_DISTILLATION_THRESHOLD))

    @property
    def system_prompt_token_ceiling(self) -> int:
        return int(self._gnosium("system_prompt_token_threshold",
                                 DEFAULT_SYSTEM_PROMPT_TOKEN_CEILING))

    @property
    def mundana_poll_seconds(self) -> int:
        return int(self._gnosium("mundana_poll_seconds",
                                 DEFAULT_MUNDANA_POLL_SECONDS))

    # ── Derived paths ─────────────────────────────────────────────
    @property
    def vault_path_primary(self) -> Path:
        return self.arca_repo_path / "Exocognii" / "EntitexRefined" / "vault"

    @property
    def vault_path_legacy(self) -> Path:
        return self.arca_repo_path / "Exocognii" / "Entitex" / "staged"

    @property
    def tower_entity_memory_root(self) -> Path:
        return self.arca_repo_path / "storage" / "entities"

    @property
    def gnosium_storage(self) -> Path:
        p = self.arca_repo_path / "Exocognii" / "GnosiumExanima" / "storage"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def sqlite_path(self) -> Path:
        return self.gnosium_storage / "gnosium.db"

    @property
    def window_state_path(self) -> Path:
        return self.gnosium_storage / "window_state.json"

    @property
    def mundana_state_file(self) -> Path:
        return Path.home() / ".arca" / "mundana_state.json"
