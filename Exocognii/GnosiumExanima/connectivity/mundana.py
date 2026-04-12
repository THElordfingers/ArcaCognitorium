# GNOSIUM EXANIMA — connectivity/mundana.py
# v1.1.0
"""
Mundana state watcher — hybrid bus subscription + file polling.

Tries to subscribe to Mundana State Bus channels via MundanaQtBridge
for real-time updates. Falls back to polling ~/.arca/mundana_state.json
if the bus is not running. Emits the same Qt signals either way.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger("gnosium.mundana")


class MundanaWatcher(QObject):
    """Hybrid bus subscriber / file poller for ambient state."""

    state_changed = pyqtSignal(dict)       # cosmetic+behaviour payload
    connected     = pyqtSignal()
    disconnected  = pyqtSignal(str)        # reason text

    def __init__(
        self,
        state_path: Path,
        *,
        poll_seconds: int = 30,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._path = Path(state_path)
        self._poll_ms = max(1, poll_seconds) * 1000
        self._last_mtime: Optional[float] = None
        self._is_connected = False
        self._bus_connected = False
        self._bridges: list = []
        self._bus_state: dict = {}

        # File polling timer (fallback)
        self._timer = QTimer(self)
        self._timer.setInterval(self._poll_ms)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        # Try bus subscription first
        if self._try_bus_connect():
            logger.info("Mundana: connected via State Bus")
        else:
            logger.info("Mundana: falling back to file polling")
            self._tick()
            self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        for bridge in self._bridges:
            try:
                bridge.disconnect()
            except Exception:
                pass

    def is_connected(self) -> bool:
        return self._is_connected

    # ── Bus subscription ──────────────────────────────────────────
    def _try_bus_connect(self) -> bool:
        """Attempt to subscribe to Mundana bus channels."""
        try:
            exo = Path.home() / "ArcaCognitorium" / "Exocognii"
            if str(exo) not in sys.path:
                sys.path.insert(0, str(exo))
            from MundanaStateBus.mundana_qt_bridge import MundanaQtBridge
            from MundanaStateBus.mundana_client import BusDaemonNotRunningError
        except ImportError:
            return False

        channels = ["mundana.horologica", "mundana.caelestis"]
        connected_count = 0
        for channel in channels:
            sig = pyqtSignal(dict)
            bridge = MundanaQtBridge(channel, self.state_changed)
            try:
                bridge.connect()
                connected_count += 1
                self._bridges.append(bridge)
            except BusDaemonNotRunningError:
                pass

        if connected_count > 0:
            self._bus_connected = True
            self._is_connected = True
            self.connected.emit()
            return True
        return False

    # ── File polling (fallback) ────────────────────────────────────
    def _tick(self) -> None:
        try:
            if not self._path.exists():
                self._mark_disconnected("state file missing")
                return
            mtime = self._path.stat().st_mtime
            if mtime == self._last_mtime:
                return  # no change
            self._last_mtime = mtime
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._mark_disconnected(f"read error: {exc}")
            return

        if not self._is_connected:
            self._is_connected = True
            self.connected.emit()
        self.state_changed.emit(data)

    def _mark_disconnected(self, reason: str) -> None:
        if self._is_connected:
            self._is_connected = False
            self.disconnected.emit(reason)
        elif self._last_mtime is None:
            # First tick and still no file — emit once
            self.disconnected.emit(reason)
            self._last_mtime = 0.0  # prevent repeat disconnect spam
