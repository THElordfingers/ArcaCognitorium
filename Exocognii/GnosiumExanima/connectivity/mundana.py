# GNOSIUM EXANIMA — connectivity/mundana.py
# v1.0.0
"""
Mundana state watcher — reads ~/.arca/mundana_state.json on a timer.

The machinae/mundana_state_bus.py module writes an atomic JSON file
with cosmetic + behaviour tracks. GNOSIUM polls that file, emits a Qt
signal when the content changes, and surfaces the summary in the
status strip. If the file never appears (daemon not running), the
watcher reports disconnected but never blocks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class MundanaWatcher(QObject):
    """Polls the mundana state file and emits updates on change."""

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

        self._timer = QTimer(self)
        self._timer.setInterval(self._poll_ms)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        self._tick()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def is_connected(self) -> bool:
        return self._is_connected

    # ── Polling ──────────────────────────────────────────────────
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
