#!/usr/bin/env python3
# PRAESIDIUM · widgets/mundana_ambient.py
# Mundana channel subscriber — ambient machinae data display.
# version: 1.0.0

from __future__ import annotations

import sys
import time
from pathlib import Path
from datetime import datetime, timezone

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame, QWidget,
)

from widget_base import ArcaneWidget
from theme import (
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT,
    C_STATUS_OK, C_STATUS_ERROR, C_STATUS_IDLE, C_SUBTLE,
    dim_label, micro_label,
)

# ── Channel definitions ─────────────────────────────────────────────
MACHINAE_CHANNELS = (
    ("mundana.horologica",    "HOROLOGICA",    "System time"),
    ("mundana.caelestis",     "CAELESTIS",     "Celestial engine"),
    ("mundana.circadiana",    "CIRCADIANA",     "Circadian phase"),
    ("mundana.meteorologica", "METEOROLOGICA",  "Weather state"),
    ("mundana.solaris",       "SOLARIS",        "Solar data"),
    ("mundana.tidalis",       "TIDALIS",        "Tidal state"),
)


class _ChannelRow(QFrame):
    """Single row displaying one Mundana channel's state."""

    def __init__(self, channel: str, label: str, desc: str, parent=None):
        super().__init__(parent)
        self.channel = channel
        self._last_update: float | None = None

        self.setStyleSheet(f"background: transparent; border: none;")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setFixedWidth(12)
        self._dot.setStyleSheet(
            f"color: {C_STATUS_IDLE}; font-size: 10px; background: transparent;"
        )
        row.addWidget(self._dot)

        self._name = QLabel(label)
        self._name.setFixedWidth(110)
        self._name.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; "
            f"font-size: 10px; font-weight: bold; letter-spacing: 1px; background: transparent;"
        )
        row.addWidget(self._name)

        self._summary = QLabel("—")
        self._summary.setStyleSheet(
            f"color: {C_TEXT}; font-family: Georgia, serif; "
            f"font-size: 10px; background: transparent;"
        )
        row.addWidget(self._summary, 1)

        self._age = QLabel("")
        self._age.setFixedWidth(40)
        self._age.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._age.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            f"font-size: 9px; background: transparent;"
        )
        row.addWidget(self._age)

    def on_data(self, payload: dict) -> None:
        self._last_update = time.time()
        self._dot.setStyleSheet(
            f"color: {C_STATUS_OK}; font-size: 10px; background: transparent;"
        )
        summary = payload.get("summary") or payload.get("phase") or payload.get("state") or "active"
        if isinstance(summary, dict):
            summary = str(summary.get("label", summary.get("name", "active")))
        self._summary.setText(str(summary)[:60])

    def refresh_age(self) -> None:
        if self._last_update is None:
            self._age.setText("")
            return
        age = int(time.time() - self._last_update)
        if age < 60:
            self._age.setText(f"{age}s")
        elif age < 3600:
            self._age.setText(f"{age // 60}m")
        else:
            self._age.setText(f"{age // 3600}h")

        # Stale after 30s — dim the dot
        if age > 30:
            self._dot.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-size: 10px; background: transparent;"
            )


class MundanaAmbientWidget(ArcaneWidget):
    """
    Subscribes to all 6 Machinae Mundana channels.
    Displays ambient data with status dots and age indicators.
    """
    # Per-channel signals (MundanaQtBridge emits dict payloads)
    _sig_horologica    = pyqtSignal(dict)
    _sig_caelestis     = pyqtSignal(dict)
    _sig_circadiana    = pyqtSignal(dict)
    _sig_meteorologica = pyqtSignal(dict)
    _sig_solaris       = pyqtSignal(dict)
    _sig_tidalis       = pyqtSignal(dict)

    _SIGNAL_MAP = {
        "mundana.horologica":    "_sig_horologica",
        "mundana.caelestis":     "_sig_caelestis",
        "mundana.circadiana":    "_sig_circadiana",
        "mundana.meteorologica": "_sig_meteorologica",
        "mundana.solaris":       "_sig_solaris",
        "mundana.tidalis":       "_sig_tidalis",
    }

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Mundana Ambient", parent)

        self._rows: dict[str, _ChannelRow] = {}
        self._bridges: list = []

        for channel, label, desc in MACHINAE_CHANNELS:
            row = _ChannelRow(channel, label, desc)
            self._body_layout.addWidget(row)
            self._rows[channel] = row

            # Connect per-channel signal to row handler
            sig = getattr(self, self._SIGNAL_MAP[channel])
            sig.connect(row.on_data)

        self._body_layout.addStretch()

        # Status label
        self._status_lbl = dim_label("Connecting...")
        self._body_layout.addWidget(self._status_lbl)

        # Age refresh timer
        self._age_timer = QTimer(self)
        self._age_timer.setInterval(5000)
        self._age_timer.timeout.connect(self._refresh_ages)
        self._age_timer.start()

        # Deferred bus connect
        QTimer.singleShot(500, self._connect_bus)

    def _connect_bus(self) -> None:
        try:
            exo = Path.home() / "ArcaCognitorium" / "Exocognii"
            if str(exo) not in sys.path:
                sys.path.insert(0, str(exo))
            from MundanaStateBus.mundana_qt_bridge import MundanaQtBridge
            from MundanaStateBus.mundana_client import BusDaemonNotRunningError
        except ImportError:
            self._status_lbl.setText("MundanaStateBus not found")
            self.set_status("error", "import failed")
            return

        connected = 0
        for channel in self._rows:
            sig = getattr(self, self._SIGNAL_MAP[channel])
            bridge = MundanaQtBridge(channel, sig)
            try:
                bridge.connect()
                connected += 1
            except BusDaemonNotRunningError:
                pass
            self._bridges.append(bridge)

        if connected > 0:
            self._status_lbl.setText(f"{connected}/{len(self._rows)} channels live")
            self.set_status("ok", f"{connected} channels")
        else:
            self._status_lbl.setText("Mundana offline")
            self.set_status("idle", "offline")

    def _refresh_ages(self) -> None:
        for row in self._rows.values():
            row.refresh_age()

    def cleanup(self) -> None:
        for bridge in self._bridges:
            try:
                bridge.disconnect()
            except Exception:
                pass
