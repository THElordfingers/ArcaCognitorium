# ─────────────────────────────────────────────────────────────────────────────
# __main__.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
Entry point: python -m MundanaStateBus

Writes PID to /tmp/mundana.pid, installs signal handlers, starts MundanaBus.
"""
import logging
import os
from pathlib import Path

from .mundana_bus import MundanaBus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("mundana")
PID_PATH = Path("/tmp/mundana.pid")


def main() -> None:
    PID_PATH.write_text(str(os.getpid()))
    log.info("Mundana State Bus starting — PID %s", os.getpid())
    bus = MundanaBus()
    bus.install_signal_handlers()   # main thread only
    try:
        bus.start()
    finally:
        PID_PATH.unlink(missing_ok=True)
        log.info("Mundana State Bus exited cleanly")


if __name__ == "__main__":
    main()
