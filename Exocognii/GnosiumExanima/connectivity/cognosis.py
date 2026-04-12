# GNOSIUM EXANIMA — connectivity/cognosis.py
# v1.0.0
"""
Cognosis — on-demand HTTP queries to Exvacua Loricum, Perpetuum
Aedificare, and Praesidium. Read-only. No ambient polling.

All calls are short-timeout and never retry. Failures surface as
CognosisError so the caller can render an inline system message in
the conversation.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

logger = logging.getLogger("gnosium.cognosis")

DEFAULT_TIMEOUT = 4.0


class CognosisError(Exception):
    """Generic cognosis query failure — service unreachable or error response."""


class CognosisClient:
    def __init__(
        self,
        *,
        exvacua_loricum_url: str,
        perpetuum_aedificare_url: str,
        praesidium_url: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self._exvacua = exvacua_loricum_url.rstrip("/")
        self._perpetuum = perpetuum_aedificare_url.rstrip("/")
        self._praesidium = praesidium_url.rstrip("/")
        self._timeout = timeout

    def lore_search(self, term: str) -> Any:
        return self._get(f"{self._exvacua}/lore/search", params={"q": term})

    def build_nodes(self) -> Any:
        return self._get(f"{self._perpetuum}/build/nodi")

    def build_recent(self) -> Any:
        return self._get(f"{self._perpetuum}/build/recent")

    def praesidium_search(self, term: str) -> Any:
        return self._get(f"{self._praesidium}/search", params={"q": term})

    def praesidium_status(self) -> Any:
        return self._get(f"{self._praesidium}/status")

    # ── Internal ─────────────────────────────────────────────────
    def _get(self, url: str, params: Optional[dict] = None) -> Any:
        try:
            response = requests.get(url, params=params, timeout=self._timeout)
        except requests.RequestException as exc:
            raise CognosisError(f"{url} unreachable: {exc}") from exc
        if response.status_code >= 400:
            raise CognosisError(
                f"{url} returned HTTP {response.status_code}"
            )
        try:
            return response.json()
        except ValueError:
            return response.text
