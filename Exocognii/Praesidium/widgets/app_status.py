#!/usr/bin/env python3
# PRAESIDIUM · widgets/app_status.py
# App liveness LED panel — shows which Exocognii apps are running.
# version: 1.0.0

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame,
)

from widget_base import ArcaneWidget
from theme import (
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT,
    C_STATUS_OK, C_STATUS_ERROR, C_STATUS_IDLE,
)

POLL_MS = 10_000  # 10s between checks


@dataclass(frozen=True)
class _AppDef:
    app_id:   str   # stable key
    name:     str   # display name
    pattern:  str   # pgrep -f pattern


APPS: tuple[_AppDef, ...] = (
    _AppDef("praesidium",  "PRAESIDIUM",   "Praesidium"),
    _AppDef("gnosium",     "GNOSIUM",      "GnosiumExanima"),
    _AppDef("arx",         "ARX",          "ArxAedificarix"),
    _AppDef("dolium",      "DOLIUM",       "Dolium"),
    _AppDef("entitex",     "ENTITEX",      "EntitexRefined"),
    _AppDef("vigilarum",   "VIGILARUM",    "Vigilarum"),
    _AppDef("lexiferium",  "LEXIFERIUM",   "Lexiferium"),
    _AppDef("bureau_i",    "BUREAU I",     "AuctoritasSpectralis"),
    _AppDef("bureau_ii",   "BUREAU II",    "AgentiaArchitecturalis"),
    _AppDef("bureau_iii",  "BUREAU III",   "DepartamentumDocumentalis"),
)


class _CheckWorker(QObject):
    """Runs pgrep checks off the main thread."""
    results_ready = pyqtSignal(dict)  # {app_id: bool}

    @pyqtSlot()
    def check(self) -> None:
        statuses: dict[str, bool] = {}
        for app in APPS:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", app.pattern],
                    capture_output=True, timeout=2,
                )
                statuses[app.app_id] = result.returncode == 0
            except Exception:
                statuses[app.app_id] = False
        self.results_ready.emit(statuses)


class _AppRow(QFrame):
    """Single row: dot + app name."""

    def __init__(self, app: _AppDef, parent=None):
        super().__init__(parent)
        self.app_id = app.app_id
        self.setStyleSheet("background: transparent; border: none;")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 1, 0, 1)
        row.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setFixedWidth(12)
        self._dot.setStyleSheet(
            f"color: {C_STATUS_IDLE}; font-size: 10px; background: transparent;"
        )
        row.addWidget(self._dot)

        self._name = QLabel(app.name)
        self._name.setStyleSheet(
            f"color: {C_TEXT}; font-family: Georgia, serif; "
            f"font-size: 10px; background: transparent;"
        )
        row.addWidget(self._name, 1)

    def set_alive(self, alive: bool) -> None:
        colour = C_STATUS_OK if alive else C_STATUS_ERROR
        self._dot.setStyleSheet(
            f"color: {colour}; font-size: 10px; background: transparent;"
        )


class AppStatusWidget(ArcaneWidget):
    """
    Shows on/off LED for each Exocognii app.
    Polls process table every 10s via off-thread worker.
    """

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "App Status", parent)

        self._rows: dict[str, _AppRow] = {}

        for app in APPS:
            row = _AppRow(app)
            self._body_layout.addWidget(row)
            self._rows[app.app_id] = row

        self._body_layout.addStretch()

        # Worker thread
        self._thread = QThread(self)
        self._worker = _CheckWorker()
        self._worker.moveToThread(self._thread)
        self._worker.results_ready.connect(self._on_results)
        self._thread.start()

        # Poll timer
        self._timer = QTimer(self)
        self._timer.setInterval(POLL_MS)
        self._timer.timeout.connect(lambda: QTimer.singleShot(0, self._worker.check))
        self._timer.start()

        # Initial check
        QTimer.singleShot(500, self._worker.check)

    @pyqtSlot(dict)
    def _on_results(self, statuses: dict[str, bool]) -> None:
        alive_count = 0
        for app_id, alive in statuses.items():
            row = self._rows.get(app_id)
            if row:
                row.set_alive(alive)
                if alive:
                    alive_count += 1

        total = len(APPS)
        if alive_count == 0:
            self.set_status("idle", "no apps")
        elif alive_count < total:
            self.set_status("warn", f"{alive_count}/{total}")
        else:
            self.set_status("ok", f"{alive_count}/{total}")

    def cleanup(self) -> None:
        self._timer.stop()
        self._thread.quit()
        self._thread.wait(2000)
