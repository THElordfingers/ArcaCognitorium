# ─────────────────────────────────────────────────────────────────────────────
# __init__.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
MundanaStateBus — public API surface.

Exocognii apps import from here only:
    from MundanaStateBus import MundanaClient, MundanaQtBridge
    from MundanaStateBus import BusChannelError, BusDaemonNotRunningError
    from MundanaStateBus import CHANNELS
"""
from .mundana_channels import CHANNELS, BusChannelError, validate_channel
from .mundana_client import (
    BusConnectionLostError,
    BusDaemonNotRunningError,
    MalformedPayloadError,
    MundanaClient,
)

# MundanaQtBridge requires PyQt6 — only available in Exocognii app venvs.
# Import lazily so the core library works in non-Qt contexts (tests, CLI tools).
try:
    from .mundana_qt_bridge import MundanaQtBridge
    _QT_AVAILABLE = True
except ImportError:
    MundanaQtBridge = None  # type: ignore[assignment,misc]
    _QT_AVAILABLE = False

__all__ = [
    "CHANNELS",
    "BusChannelError",
    "BusConnectionLostError",
    "BusDaemonNotRunningError",
    "MalformedPayloadError",
    "MundanaClient",
    "MundanaQtBridge",
    "validate_channel",
    "_QT_AVAILABLE",
]
__version__ = "1.0.0"
