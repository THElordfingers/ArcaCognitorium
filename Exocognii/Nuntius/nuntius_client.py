# NUNTIUS — nuntius_client.py
# v1.0
"""NuntiusClient — the sole canonical Exocognii emit client. Replaces dual-POST pattern."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from .nuntius_config import DEFAULT_CONFIG_PATH, load_nuntius_config

logger = logging.getLogger(__name__)


class NuntiusDaemonNotRunningError(Exception):
    """Raised when NuntiusClient cannot reach the NUNTIUS daemon."""


class NuntiusClient:
    """
    Client library for all Exocognii apps.
    Import and call .emit(payload_dict) — fire-and-forget.
    Raises NuntiusDaemonNotRunningError if NUNTIUS is not running.
    App function must never be gated on this client's availability.
    """

    def __init__(
        self,
        config_path: Path = DEFAULT_CONFIG_PATH,
    ) -> None:
        """Load Configuus and build the /emit URL. Does not connect on init."""
        cfg = load_nuntius_config(config_path)
        self._url = f"http://{cfg.api.host}:{cfg.api.port}/emit"
        logger.debug("NuntiusClient initialised — endpoint: %s", self._url)

    def emit(self, payload: dict) -> None:
        """
        POST payload to NUNTIUS /emit. Fire-and-forget.
        Raises NuntiusDaemonNotRunningError if service unreachable.
        Caller is responsible for catching and degrading gracefully.

        Example:
            try:
                self._nuntius.emit(involucrum_dict)
            except NuntiusDaemonNotRunningError:
                logger.warning("NUNTIUS not running — observation dropped")
        """
        try:
            response = httpx.post(self._url, json=payload, timeout=5.0)
            if response.status_code not in (200, 202):
                logger.warning(
                    "NuntiusClient: unexpected status %d from NUNTIUS — "
                    "emission may not have been accepted",
                    response.status_code,
                )
        except httpx.ConnectError as exc:
            raise NuntiusDaemonNotRunningError(
                f"Cannot reach NUNTIUS at {self._url}. "
                "Ensure the NUNTIUS daemon is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise NuntiusDaemonNotRunningError(
                f"NUNTIUS timed out at {self._url}."
            ) from exc
