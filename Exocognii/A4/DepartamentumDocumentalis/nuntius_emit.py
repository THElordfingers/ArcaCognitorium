# Departamentum Documentalis · nuntius_emit.py · v1.0.0
"""
NUNTIUS emission — fire-and-forget event publishing.
Canonical pattern. Replaces the legacy nuntius_client.py.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("dd.nuntius")

APP_ID = "III-DD"
APP_VERSION = "1.1"


def emit_event(hint: str, body: dict[str, Any]) -> None:
    """
    Emit a Bureau III event to NUNTIUS (if available).

    Args:
        hint:  Routing hint — e.g. "document_composed", "mandate_swap",
               "propagatio_migration", "template_created", "template_request".
        body:  Arbitrary event payload.
    """
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
        f"[dd.nuntius] {reason}: hint={payload.get('hint')}",
        file=sys.stderr,
    )
