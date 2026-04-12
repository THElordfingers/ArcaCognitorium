#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨ mundana_machinae_bridge.py                                              ⯩
# ⯨                                                      𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ ⯩
#   #
#  ##  mundana_machinae_bridge.py
# ###
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
MUNDANA MACHINAE BRIDGE
═══════════════════════════════════════════════════════════════════════════════
Watches Machinae JSON output files in ~/.arca/ and publishes changes to the
Mundana State Bus. Zero modifications to any Machina required.

Each Machina already writes its state to ~/.arca/<name>.json via its write()
method. This bridge watches those files for changes and publishes the content
to the corresponding Mundana channel.

Usage:
    python3 mundana_machinae_bridge.py
    python3 mundana_machinae_bridge.py --interval 5   # poll every 5 seconds

Requires:
    - Mundana State Bus running at /tmp/mundana.sock
    - MundanaClient importable from Exocognii.MundanaStateBus

Part of MundanaStateBus package. Run: python3 -m MundanaStateBus.mundana_machinae_bridge
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[mundana-bridge] %(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mundana.bridge")

# ── Channel mapping ───────────────────────────────────────────────────────
# Machina JSON filename → Mundana channel name

MACHINA_MAP: dict[str, str] = {
    "machina_caelestis.json":     "mundana.caelestis",
    "machina_circadiana.json":    "mundana.circadiana",
    "machina_horologica.json":    "mundana.horologica",
    "machina_meteorologica.json": "mundana.meteorologica",
    "machina_solaris.json":       "mundana.solaris",
    "machina_tidalis.json":       "mundana.tidalis",
}

ARCA_DIR = Path.home() / ".arca"


def _file_hash(path: Path) -> str | None:
    """Return SHA-256 of file contents, or None if unreadable."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, IOError):
        return None


def _load_json(path: Path) -> dict | None:
    """Read and parse JSON file, returning None on any failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, IOError, json.JSONDecodeError) as e:
        log.warning("Failed to read %s: %s", path.name, e)
        return None


def run_bridge(interval: float = 3.0) -> None:
    """
    Main loop. Polls Machinae JSON files, publishes changes to Mundana.
    Gracefully degrades if Mundana is not running.
    """
    # ── Import MundanaClient ──────────────────────────────────────────
    try:
        from .mundana_client import MundanaClient, BusDaemonNotRunningError
    except ImportError:
        # Fallback for standalone execution
        exocognii_path = Path.home() / "ArcaCognitorium" / "Exocognii"
        if str(exocognii_path) not in sys.path:
            sys.path.insert(0, str(exocognii_path))
        try:
            from MundanaStateBus.mundana_client import (
                MundanaClient,
                BusDaemonNotRunningError,
            )
        except ImportError:
            log.error("Cannot import MundanaClient.")
            sys.exit(1)

    # ── Connect to bus ────────────────────────────────────────────────
    client = MundanaClient()
    bus_alive = False
    try:
        client.connect()
        bus_alive = True
        log.info("Connected to Mundana State Bus")
    except BusDaemonNotRunningError:
        log.warning("Mundana not running — will retry on each cycle")

    # ── State tracking ────────────────────────────────────────────────
    last_hashes: dict[str, str] = {}

    log.info(
        "Bridge running — watching %d Machinae, polling every %.1fs",
        len(MACHINA_MAP), interval,
    )
    log.info("Watching: %s", ARCA_DIR)

    try:
        while True:
            for filename, channel in MACHINA_MAP.items():
                path = ARCA_DIR / filename
                if not path.exists():
                    continue

                current_hash = _file_hash(path)
                if current_hash is None:
                    continue

                # Skip if unchanged
                if last_hashes.get(filename) == current_hash:
                    continue

                last_hashes[filename] = current_hash
                payload = _load_json(path)
                if payload is None:
                    continue

                # Publish
                if not bus_alive:
                    try:
                        client.connect()
                        bus_alive = True
                        log.info("Reconnected to Mundana")
                    except BusDaemonNotRunningError:
                        continue

                try:
                    client.publish(channel, payload)
                    log.info("Published %s → %s", filename, channel)
                except BusDaemonNotRunningError:
                    bus_alive = False
                    log.warning("Mundana lost — will retry")
                except Exception as e:
                    log.warning("Publish failed for %s: %s", channel, e)

            time.sleep(interval)

    except KeyboardInterrupt:
        log.info("Bridge stopped")
    finally:
        if bus_alive:
            try:
                client.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mundana Machinae Bridge — publishes Machinae state to the bus"
    )
    parser.add_argument(
        "--interval", type=float, default=3.0,
        help="Poll interval in seconds (default: 3.0)"
    )
    args = parser.parse_args()
    run_bridge(interval=args.interval)
