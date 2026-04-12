# LEXIFERIUM · nuntius_emit.py · v1.0.0
"""
NUNTIUS emission — fire-and-forget event publishing.
Canonical pattern.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("lexiferium.nuntius")

APP_ID = "LEXIFERIUM"
APP_VERSION = "1.0"


def emit_event(hint: str, body: dict[str, Any]) -> None:
    payload = {
        "source_app": APP_ID,
        "source_version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hint": hint,
        "body": body,
    }

    try:
        from Exocognii.Nuntius.nuntius_client import (
            NuntiusClient,
            NuntiusDaemonNotRunningError,
        )
    except ImportError:
        _fallback_log(payload, reason="nuntius module unavailable")
        return

    try:
        NuntiusClient().emit(payload)
    except NuntiusDaemonNotRunningError:
        _fallback_log(payload, reason="nuntius daemon not running")
    except Exception as exc:
        _fallback_log(payload, reason=f"emit failed: {exc}")


def _fallback_log(payload: dict, *, reason: str) -> None:
    print(
        f"[lexiferium.nuntius] {reason}: hint={payload.get('hint')}",
        file=sys.stderr,
    )
