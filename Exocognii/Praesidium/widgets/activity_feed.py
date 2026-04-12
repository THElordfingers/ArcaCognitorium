#!/usr/bin/env python3
# PRAESIDIUM · widgets/activity_feed.py
# Live activity feed — aggregates recent NUNTIUS emissions.
# version: 1.0.0

from __future__ import annotations

import httpx
from datetime import datetime

from PyQt6.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QWidget,
)

from widget_base import ArcaneWidget
from theme import (
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_SUBTLE,
    C_STATUS_OK, C_STATUS_ERROR, C_STATUS_IDLE, C_STATUS_WARN,
    C_TEAL, C_CRIMSON,
    dim_label,
)

NUNTIUS_LOG_URL = "http://127.0.0.1:8730/log?limit=20"
POLL_MS         = 10_000
HTTP_TIMEOUT    = 2.0

# Colour per source app for badge
APP_COLOURS = {
    "PRAESIDIUM":              C_GOLD,
    "GNOSIUM_EXANIMA":         C_TEAL,
    "ARX_AEDIFICARIX":         "#6a8a6a",
    "DOLIUM":                  "#8a6a8a",
    "ENTITEX_REFINED":         "#6a6a8a",
    "AUCTORITAS_SPECTRALIS":   C_CRIMSON,
    "AGENTIA_ARCHITECTURALIS": "#8a8a6a",
    "DEPARTAMENTUM_DOCUMENTALIS": "#6a8a8a",
    "LEXIFERIUM":              "#8a7a5a",
}


class _FeedWorker(QObject):
    """Polls NUNTIUS /log off the main thread."""
    feed_ready = pyqtSignal(list)  # list of record dicts

    @pyqtSlot()
    def fetch(self) -> None:
        try:
            resp = httpx.get(NUNTIUS_LOG_URL, timeout=HTTP_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                self.feed_ready.emit(records)
            else:
                self.feed_ready.emit([])
        except Exception:
            self.feed_ready.emit([])


class _EventRow(QFrame):
    """Single event display row."""

    def __init__(self, record: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: {C_BG}; border-bottom: 1px solid {C_GOLD_DARK}; padding: 2px;"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(6)

        # Timestamp
        ts_raw = record.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts_raw)
            ts_str = dt.strftime("%H:%M:%S")
        except (ValueError, TypeError):
            ts_str = ts_raw[:8] if ts_raw else "—"

        ts_lbl = QLabel(ts_str)
        ts_lbl.setFixedWidth(55)
        ts_lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            f"font-size: 9px; background: transparent;"
        )
        row.addWidget(ts_lbl)

        # Source app badge
        source = record.get("source_app", "?")
        short = source[:12]
        colour = APP_COLOURS.get(source, C_TEXT)
        src_lbl = QLabel(short)
        src_lbl.setFixedWidth(90)
        src_lbl.setStyleSheet(
            f"color: {colour}; font-family: Georgia, serif; "
            f"font-size: 9px; font-weight: bold; background: transparent;"
        )
        row.addWidget(src_lbl)

        # Hint
        hint = record.get("hint", record.get("consumer_name", "—"))
        hint_lbl = QLabel(str(hint))
        hint_lbl.setStyleSheet(
            f"color: {C_TEXT}; font-family: Georgia, serif; "
            f"font-size: 9px; background: transparent;"
        )
        row.addWidget(hint_lbl, 1)

        # Outcome dot
        outcome = record.get("outcome", "")
        dot_colour = C_STATUS_OK if outcome == "success" else (
            C_STATUS_ERROR if outcome == "error" else C_STATUS_IDLE
        )
        dot = QLabel("●")
        dot.setFixedWidth(12)
        dot.setStyleSheet(
            f"color: {dot_colour}; font-size: 8px; background: transparent;"
        )
        row.addWidget(dot)


class ActivityFeedWidget(ArcaneWidget):
    """
    Scrollable live feed of recent NUNTIUS emissions.
    Polls /log every 10s. Colour-coded by source app.
    """

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Activity Feed", parent)

        # Scroll area for event rows
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background: {C_BG}; border: none; }}"
        )
        self._body_layout.addWidget(self._scroll, 1)

        self._container = QWidget()
        self._container.setStyleSheet(f"background: {C_BG};")
        self._feed_layout = QVBoxLayout(self._container)
        self._feed_layout.setContentsMargins(0, 0, 0, 0)
        self._feed_layout.setSpacing(0)
        self._feed_layout.addStretch()
        self._scroll.setWidget(self._container)

        # Status
        self._status_lbl = dim_label("Waiting for NUNTIUS...")
        self._body_layout.addWidget(self._status_lbl)

        # Worker thread
        self._thread = QThread(self)
        self._worker = _FeedWorker()
        self._worker.moveToThread(self._thread)
        self._worker.feed_ready.connect(self._on_feed)
        self._thread.start()

        # Poll timer
        self._timer = QTimer(self)
        self._timer.setInterval(POLL_MS)
        self._timer.timeout.connect(lambda: QTimer.singleShot(0, self._worker.fetch))
        self._timer.start()

        # Initial fetch
        QTimer.singleShot(1000, self._worker.fetch)

        self._last_id: int | None = None

    @pyqtSlot(list)
    def _on_feed(self, records: list) -> None:
        if not records:
            self._status_lbl.setText("NUNTIUS offline or empty")
            self.set_status("idle", "no data")
            return

        # Clear and rebuild (simple approach for v1)
        # Remove existing rows
        while self._feed_layout.count() > 1:  # keep the stretch
            item = self._feed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add rows (newest last for natural scroll)
        for record in reversed(records):
            row = _EventRow(record)
            self._feed_layout.insertWidget(self._feed_layout.count() - 1, row)

        count = len(records)
        self._status_lbl.setText(f"{count} events")
        self.set_status("ok", f"{count} events")

        # Auto-scroll to bottom
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def cleanup(self) -> None:
        self._timer.stop()
        self._thread.quit()
        self._thread.wait(2000)
