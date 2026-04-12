# GNOSIUM EXANIMA — connectivity/nuntius_emit.py
# v1.0.0
"""
NUNTIUS emission — fire-and-forget event publishing.

NUNTIUS may or may not exist on disk depending on the branch state.
This module attempts to import and call the canonical client; on any
failure it logs to stderr and returns silently. Callers never see the
failure, and conversation flow is never blocked.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any

from .. import __version__
from ..constants import APP_ID

logger = logging.getLogger("gnosium.nuntius")


def emit_event(hint: str, body: dict[str, Any]) -> None:
    """
    Emit a GNOSIUM event to NUNTIUS (if available).

    Args:
        hint:  Routing hint — e.g. "conversation", "session_lifecycle".
        body:  Arbitrary event payload.
    """
    payload = {
        "source_app": APP_ID,
        "source_version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hint": hint,
        "body": body,
    }

    try:
        from Exocognii.Nuntius.nuntius_client import (  # type: ignore
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
    except Exception as exc:  # defensive — never raise from here
        _fallback_log(payload, reason=f"emit failed: {exc}")


def _fallback_log(payload: dict, *, reason: str) -> None:
    print(
        f"[gnosium.nuntius] {reason}: hint={payload.get('hint')}",
        file=sys.stderr,
    )
