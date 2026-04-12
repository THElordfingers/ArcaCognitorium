#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          core/config_loader.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("arx.config_loader")

CONFIG_PATH = Path("~/.arca/config.json").expanduser()


class ConfigLoader:
    """
    Reads ~/.arca/config.json. Exposes typed accessors with documented
    defaults. Missing keys are logged as warnings; defaults are returned.
    All accessors are safe to call before load() only if defaults suffice —
    load() must be called at startup to populate from disk.
    """

    _data: dict = {}
    _loaded: bool = False

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> dict:
        """
        Load config from disk. Returns full dict.
        Logs warning and returns empty dict on missing file or parse error.
        """
        try:
            with open(path, encoding="utf-8") as f:
                cls._data = json.load(f)
            cls._loaded = True
            logger.info("ConfigLoader loaded from %s", path)
        except FileNotFoundError:
            logger.warning(
                "Config file not found at %s — all defaults in effect.", path
            )
            cls._data = {}
        except json.JSONDecodeError as exc:
            logger.warning(
                "Config file at %s is malformed (%s) — all defaults in effect.", path, exc
            )
            cls._data = {}
        return cls._data

    # -------------------------------------------------------------------------
    # API / Authentication
    # -------------------------------------------------------------------------

    @classmethod
    def api_key(cls) -> str:
        """
        Return API key string. Resolves in order:
          1. CLAUDE_API_KEY environment variable
          2. config.json 'api_key' field
        Returns empty string if neither is present.
        """
        env_key = os.environ.get("CLAUDE_API_KEY", "")
        if env_key:
            return env_key
        cfg_key = cls._data.get("api_key", "")
        if not cfg_key:
            logger.warning(
                "CLAUDE_API_KEY not found in environment or config.json."
            )
        return cfg_key

    # -------------------------------------------------------------------------
    # Arx Aedificarix — application-specific block
    # -------------------------------------------------------------------------

    @classmethod
    def _arx(cls) -> dict:
        """Return the arx_aedificarix sub-dict (empty dict if absent)."""
        return cls._data.get("arx_aedificarix", {})

    @classmethod
    def compression_threshold(cls) -> float:
        """
        Fraction of model_context_limit at which compression triggers.
        Default: 0.70
        """
        val = cls._arx().get("compression_threshold", 0.70)
        try:
            return float(val)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid compression_threshold in config — using 0.70."
            )
            return 0.70

    @classmethod
    def model_context_limit(cls) -> int:
        """
        Model context window token limit used for gauge and threshold math.
        Default: 200000
        """
        val = cls._arx().get("model_context_limit", 200_000)
        try:
            return int(val)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid model_context_limit in config — using 200000."
            )
            return 200_000

    @classmethod
    def compression_batch_size(cls) -> int:
        """
        Number of turns compressed per trigger event.
        Default: 20
        """
        val = cls._arx().get("compression_batch_size", 20)
        try:
            return int(val)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid compression_batch_size in config — using 20."
            )
            return 20

    @classmethod
    def db_path(cls) -> Path:
        """
        Override path for arx.db. Default: canonical path beside package.
        """
        val = cls._arx().get("db_path")
        if val:
            return Path(val).expanduser()
        from core.database import DB_PATH
        return DB_PATH

    @classmethod
    def builder_prompt_path(cls) -> Path | None:
        """
        Optional override path for builder_prompt.md.
        Returns None if not configured — PromptLoader uses its own default.
        """
        val = cls._arx().get("builder_prompt_path")
        return Path(val).expanduser() if val else None
