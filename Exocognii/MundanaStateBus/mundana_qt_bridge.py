# ─────────────────────────────────────────────────────────────────────────────
# mundana_qt_bridge.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
MundanaQtBridge — thread-safe wrapper for PyQt6 subscribers.

The MundanaClient reader loop runs on a background thread. PyQt6 widgets
must not be touched from any thread other than the Qt main thread. This
bridge interposes a QueuedConnection signal between the reader thread
and the application slot, guaranteeing that the application callback
always fires on the main thread.
"""
import logging
from typing import Any

from PyQt6.QtCore import QObject, Qt, pyqtSignal

from .mundana_client import BusDaemonNotRunningError, MundanaClient

log = logging.getLogger("mundana.qt_bridge")


class MundanaQtBridge(QObject):
    """
    Wraps MundanaClient for PyQt6 apps.

    Dispatches inbound bus messages from the reader thread to the Qt main
    thread via a QueuedConnection internal signal, then re-emits the
    caller-supplied qt_signal on the main thread.
    """

    _relay = pyqtSignal(dict)

    def __init__(
        self,
        channel: str,
        qt_signal: Any,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._channel = channel
        self._client = MundanaClient()
        self._relay.connect(
            lambda payload: qt_signal.emit(payload),
            Qt.ConnectionType.QueuedConnection,
        )

    def connect(self) -> None:
        """Connect and subscribe. Raises BusDaemonNotRunningError if absent."""
        self._client.connect()
        self._client.subscribe(self._channel, self.on_bus_message)

    def disconnect(self) -> None:
        """Unsubscribe and disconnect. Safe to call even if never connected."""
        try:
            self._client.unsubscribe(self._channel)
        except Exception:
            pass
        self._client.disconnect()

    def publish(self, payload: dict[str, Any]) -> None:
        """Convenience publish on this bridge's channel."""
        self._client.publish(self._channel, payload)

    def on_bus_message(self, payload: dict) -> None:
        """Called from reader thread. Relays to Qt main thread via QueuedConnection."""
        self._relay.emit(payload)
