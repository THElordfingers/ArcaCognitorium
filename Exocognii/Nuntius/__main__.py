# NUNTIUS — __main__.py
# v1.0
"""Entry point. Loads Configuus, wires dependencies, starts uvicorn."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import uvicorn

from . import nuntius_app
from .nuntius_config import DEFAULT_CONFIG_PATH, NuntiusConfigError, load_nuntius_config
from .nuntius_log import EmissionLog
from .nuntius_registry import ConsumerRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("nuntius")


def main() -> None:
    """Load config, wire dependencies, start uvicorn."""
    try:
        cfg = load_nuntius_config(DEFAULT_CONFIG_PATH)
    except NuntiusConfigError as exc:
        print(f"\n[NUNTIUS] Configuration error — cannot start.\n{exc}\n", file=sys.stderr)
        sys.exit(1)

    registry = ConsumerRegistry(cfg)
    log = EmissionLog(cfg.log_db_path, cfg.log_max_rows)

    # Inject singletons into app module
    nuntius_app.registry = registry
    nuntius_app.emission_log = log
    nuntius_app.config = cfg

    logger.info(
        "NUNTIUS starting on %s:%d — %d consumer(s) registered",
        cfg.api.host,
        cfg.api.port,
        len(cfg.consumers),
    )

    uvicorn.run(
        nuntius_app.app,
        host=cfg.api.host,
        port=cfg.api.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
