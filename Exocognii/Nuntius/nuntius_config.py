# NUNTIUS — nuntius_config.py
# v1.0
"""Configuus loader for NUNTIUS. Reads ~/.arca/config.json and exposes NuntiusConfig."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

DEFAULT_CONFIG_PATH = Path.home() / ".arca" / "config.json"


class NuntiusConfigError(Exception):
    """Raised when the nuntius block is absent or malformed in Configuus."""


@dataclass
class ConsumerConfig:
    """A single registered consumer."""
    name: str
    url: str


@dataclass
class NuntiusApiConfig:
    """Binding address for the NUNTIUS daemon."""
    host: str = "127.0.0.1"
    port: int = 8730


@dataclass
class NuntiusConfig:
    """Complete resolved NUNTIUS configuration."""
    api: NuntiusApiConfig
    consumers: List[ConsumerConfig]
    consumer_timeout_seconds: float
    log_max_rows: int
    log_db_path: Path


def load_nuntius_config(
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> NuntiusConfig:
    """Load and validate the nuntius block from Configuus. Raises NuntiusConfigError on failure."""
    if not config_path.exists():
        raise NuntiusConfigError(
            f"Configuus not found at {config_path}. "
            "Ensure ~/.arca/config.json exists with a 'nuntius' block."
        )

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise NuntiusConfigError(f"Configuus is not valid JSON: {exc}") from exc

    if "nuntius_api" not in raw:
        raise NuntiusConfigError(
            "Configuus is missing 'nuntius_api' block. "
            "Add: {\"nuntius_api\": {\"host\": \"127.0.0.1\", \"port\": 8730}}"
        )
    if "nuntius" not in raw:
        raise NuntiusConfigError(
            "Configuus is missing 'nuntius' block. "
            "Add consumers, consumer_timeout_seconds, and log_max_rows."
        )

    api_raw = raw["nuntius_api"]
    nuntius_raw = raw["nuntius"]

    api = NuntiusApiConfig(
        host=api_raw.get("host", "127.0.0.1"),
        port=int(api_raw.get("port", 8730)),
    )

    consumers_raw = nuntius_raw.get("consumers", [])
    if not consumers_raw:
        raise NuntiusConfigError(
            "nuntius.consumers is empty. NUNTIUS with zero consumers is a "
            "misconfiguration. Declare at least one consumer in Configuus."
        )

    consumers: List[ConsumerConfig] = []
    for entry in consumers_raw:
        name = entry.get("name", "").strip()
        url = entry.get("url", "").strip()
        if not name:
            raise NuntiusConfigError(f"Consumer entry missing 'name': {entry}")
        if not url.startswith("http"):
            raise NuntiusConfigError(
                f"Consumer '{name}' has invalid url '{url}'. Must start with http."
            )
        consumers.append(ConsumerConfig(name=name, url=url))

    timeout = float(nuntius_raw.get("consumer_timeout_seconds", 2.0))
    log_max_rows = int(nuntius_raw.get("log_max_rows", 10000))

    # DB path: alongside the config file's parent, under .arca/
    log_db_path = config_path.parent / "nuntius_emissions.db"

    return NuntiusConfig(
        api=api,
        consumers=consumers,
        consumer_timeout_seconds=timeout,
        log_max_rows=log_max_rows,
        log_db_path=log_db_path,
    )
