#!/usr/bin/env python3
"""
# PRAESIDIUM · widgets/services_widget.py
# Unified launcher and health monitor for background Exocognii services.
# version: 1.0.0
#
# Four services: NUNTIUS, Exvacua Loricum, Perpetuum Aedificare, Mundana State Bus.
# Health polled every 5s via off-thread QThread workers. Launch only — no stop.
# Emits nuntius_status_changed so PraesidiumApp can drive the exo status slot.
"""

from __future__ import annotations

import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

import httpx
from PyQt6.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QVBoxLayout, QScrollArea, QWidget,
)

from widget_base import ArcaneWidget
from theme import (
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT,
    C_STATUS_OK, C_STATUS_WARN, C_STATUS_ERROR, C_STATUS_IDLE,
)


# ---------------------------------------------------------------------------
# Service registry — module-level constant, not user-configurable in v1
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _ServiceDef:
    service_id:    str   # stable internal id
    name:          str   # display name
    script:        str   # path relative to arca_repo_path
    health_type:   str   # 'http' | 'socket'
    health_target: str   # URL for http, socket path for socket


SERVICES: tuple[_ServiceDef, ...] = (
    _ServiceDef(
        service_id    = "nuntius",
        name          = "NUNTIUS",
        script        = "Exocognii/Nuntius/launch_niuntius.sh",
        health_type   = "http",
        health_target = "http://127.0.0.1:8730/status",
    ),
    _ServiceDef(
        service_id    = "exvacua",
        name          = "EXVACUA LORICUM",
        script        = "Exocognii/ExvacuaLoricum/Exvacua.sh",
        health_type   = "http",
        health_target = "http://127.0.0.1:8731/status",
    ),
    _ServiceDef(
        service_id    = "perpetuum",
        name          = "PERPETUUM AEDIFICARE",
        script        = "Exocognii/PerpetuumAedificare/Perpetuum.sh",
        health_type   = "http",
        health_target = "http://127.0.0.1:8732/status",
    ),
    _ServiceDef(
        service_id    = "mundana",
        name          = "MUNDANA STATE BUS",
        script        = "Exocognii/MundanaStateBus/launch_mundana.sh",
        health_type   = "socket",
        health_target = "/tmp/mundana.sock",
    ),
)

NUNTIUS_LOG_URL = "http://127.0.0.1:8730/log?limit=10"
POLL_MS         = 5000
HTTP_TIMEOUT    = 1.5


# ---------------------------------------------------------------------------
# Health worker — one per service, moved onto its own QThread
# ---------------------------------------------------------------------------

class _HealthWorker(QObject):
    """Performs a single synchronous health check and emits the result."""
    result = pyqtSignal(str, str)  # service_id, 'running'|'offline'|'unknown'

    def __init__(self, sdef: _ServiceDef) -> None:
        super().__init__()
        self._sdef = sdef

    @pyqtSlot()
    def check(self) -> None:
        sd = self._sdef
        if sd.health_type == "http":
            try:
                r = httpx.get(sd.health_target, timeout=HTTP_TIMEOUT)
                self.result.emit(sd.service_id, "running" if r.status_code == 200 else "offline")
                return
            except Exception:
                self.result.emit(sd.service_id, "offline")
                return

        if sd.health_type == "socket":
            try:
                p = Path(sd.health_target)
                if p.exists() and stat.S_ISSOCK(os.stat(p).st_mode):
                    self.result.emit(sd.service_id, "running")
                else:
                    self.result.emit(sd.service_id, "offline")
            except Exception:
                self.result.emit(sd.service_id, "offline")
            return

        self.result.emit(sd.service_id, "unknown")


# ---------------------------------------------------------------------------
# Launch stdout reader — reads first ~20 lines then exits
# ---------------------------------------------------------------------------

class _LaunchReader(QThread):
    line_read = pyqtSignal(str, str)  # service_id, line
    finished_reading = pyqtSignal(str)  # service_id

    def __init__(self, service_id: str, proc: subprocess.Popen) -> None:
        super().__init__()
        self._service_id = service_id
        self._proc = proc

    def run(self) -> None:
        count = 0
        try:
            if self._proc.stdout is not None:
                for line in iter(self._proc.stdout.readline, ""):
                    if not line:
                        break
                    self.line_read.emit(self._service_id, line.rstrip("\n"))
                    count += 1
                    if count >= 20:
                        break
        except Exception:
            pass
        self.finished_reading.emit(self._service_id)


# ---------------------------------------------------------------------------
# NUNTIUS live-log worker
# ---------------------------------------------------------------------------

class _NuntiusLogWorker(QObject):
    log_ready = pyqtSignal(list)  # list[str] formatted lines

    @pyqtSlot()
    def fetch(self) -> None:
        try:
            r = httpx.get(NUNTIUS_LOG_URL, timeout=HTTP_TIMEOUT)
            if r.status_code != 200:
                self.log_ready.emit([])
                return
            data = r.json()
            # Accept either a list of records or an object with 'records'.
            records = data if isinstance(data, list) else data.get("records", [])
            lines: list[str] = []
            for rec in records[-10:]:
                if not isinstance(rec, dict):
                    continue
                ts   = str(rec.get("timestamp", ""))[:19]
                app  = str(rec.get("source_app", ""))
                hint = str(rec.get("hint", ""))
                cons = str(rec.get("consumer_name", rec.get("consumer", "")))
                out  = str(rec.get("outcome", ""))
                lines.append(f"{ts}  {app}  {hint}  {cons}  {out}".strip())
            self.log_ready.emit(lines)
        except Exception:
            self.log_ready.emit([])


# ---------------------------------------------------------------------------
# Service row — internal QFrame, one per service
# ---------------------------------------------------------------------------

class _ServiceRow(QFrame):
    launch_requested = pyqtSignal(str)  # service_id
    log_toggled      = pyqtSignal(str)  # service_id

    def __init__(self, sdef: _ServiceDef, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sdef = sdef
        self._status: str = "unknown"
        self.setObjectName("service_row")
        self.setStyleSheet(
            f"QFrame#service_row {{ background: transparent; border: none; }}"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 2, 0, 2)
        outer.setSpacing(2)

        # Top row: dot · name · status · launch button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(
            f"color: {C_STATUS_IDLE}; font-size: 11px; background: transparent;"
        )
        top.addWidget(self._dot)

        self._name_lbl = QLabel(sdef.name)
        self._name_lbl.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 10px; "
            "font-weight: bold; letter-spacing: 1px; background: transparent;"
        )
        top.addWidget(self._name_lbl)

        top.addStretch()

        self._status_lbl = QLabel("[UNKNOWN]")
        self._status_lbl.setStyleSheet(
            f"color: {C_STATUS_IDLE}; font-family: Georgia, serif; "
            "font-size: 9px; background: transparent;"
        )
        top.addWidget(self._status_lbl)

        self._launch_btn = QPushButton("▶ LAUNCH")
        self._launch_btn.setFixedHeight(22)
        self._launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._launch_btn.setStyleSheet(
            f"QPushButton {{ background: {C_PANEL}; color: {C_GOLD}; "
            f"border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif; "
            f"font-size: 9px; padding: 2px 8px; letter-spacing: 1px; }}"
            f"QPushButton:hover   {{ background: {C_GOLD_DARK}; }}"
            f"QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_GOLD_DARK}; }}"
        )
        self._launch_btn.clicked.connect(
            lambda: self.launch_requested.emit(self._sdef.service_id)
        )
        top.addWidget(self._launch_btn)

        outer.addLayout(top)

        # Log toggle row
        log_row = QHBoxLayout()
        log_row.setContentsMargins(12, 0, 0, 0)
        log_row.setSpacing(4)

        log_label_text = "▼ LIVE LOG" if sdef.service_id == "nuntius" else "▼ LAUNCH LOG"
        self._log_btn = QPushButton(log_label_text)
        self._log_btn.setFixedHeight(18)
        self._log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._log_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_GOLD_DIM}; "
            f"border: none; font-family: Georgia, serif; font-size: 9px; "
            "letter-spacing: 1px; text-align: left; }}"
            f"QPushButton:hover {{ color: {C_GOLD}; }}"
        )
        self._log_btn.clicked.connect(self._toggle_log)
        log_row.addWidget(self._log_btn)
        log_row.addStretch()
        outer.addLayout(log_row)

        # Log panel — hidden by default
        self._log_panel = QTextEdit()
        self._log_panel.setReadOnly(True)
        self._log_panel.setFixedHeight(80)
        self._log_panel.setStyleSheet(
            f"QTextEdit {{ background: {C_BG}; color: {C_GOLD_DIM}; "
            f"border: 1px solid {C_GOLD_DARK}; "
            "font-family: 'DejaVu Sans Mono', monospace; font-size: 9px; }}"
        )
        self._log_panel.hide()
        outer.addWidget(self._log_panel)

    # ------------------------------------------------------------------

    def service_id(self) -> str:
        return self._sdef.service_id

    def is_log_visible(self) -> bool:
        return self._log_panel.isVisible()

    def set_status(self, status: str) -> None:
        """status: 'running'|'offline'|'starting'|'unknown'"""
        self._status = status
        colour_map = {
            "running":  C_STATUS_OK,
            "offline":  C_STATUS_ERROR,
            "starting": C_STATUS_WARN,
            "unknown":  C_STATUS_IDLE,
        }
        text_map = {
            "running":  "[RUNNING]",
            "offline":  "[OFFLINE]",
            "starting": "[STARTING]",
            "unknown":  "[UNKNOWN]",
        }
        colour = colour_map.get(status, C_STATUS_IDLE)
        self._dot.setStyleSheet(
            f"color: {colour}; font-size: 11px; background: transparent;"
        )
        self._status_lbl.setText(text_map.get(status, "[UNKNOWN]"))
        self._status_lbl.setStyleSheet(
            f"color: {colour}; font-family: Georgia, serif; "
            "font-size: 9px; background: transparent;"
        )

    def status(self) -> str:
        return self._status

    def set_launch_enabled(self, enabled: bool) -> None:
        self._launch_btn.setEnabled(enabled)

    def clear_log(self) -> None:
        self._log_panel.clear()

    def append_log_line(self, line: str) -> None:
        self._log_panel.append(line)

    def set_log_lines(self, lines: list[str]) -> None:
        self._log_panel.clear()
        self._log_panel.append("\n".join(lines))

    def _toggle_log(self) -> None:
        visible = self._log_panel.isVisible()
        self._log_panel.setVisible(not visible)
        arrow = "▲" if not visible else "▼"
        kind = "LIVE LOG" if self._sdef.service_id == "nuntius" else "LAUNCH LOG"
        self._log_btn.setText(f"{arrow} {kind}")
        self.log_toggled.emit(self._sdef.service_id)


# ---------------------------------------------------------------------------
# ServicesWidget
# ---------------------------------------------------------------------------

class ServicesWidget(ArcaneWidget):
    nuntius_status_changed = pyqtSignal(str, str)  # status, summary

    def __init__(self, widget_id: str, configuus, parent: QWidget | None = None) -> None:
        super().__init__(widget_id=widget_id, title="Services", parent=parent)
        self._cfg = configuus
        self._repo_root: Path = configuus.arca_repo_path

        self._rows: dict[str, _ServiceRow] = {}
        self._last_nuntius_status: str = ""

        # Health plumbing — one QThread + worker per service
        self._workers: dict[str, _HealthWorker] = {}
        self._threads: dict[str, QThread] = {}

        self._build_body()

        # NUNTIUS live-log plumbing
        self._nlog_thread = QThread(self)
        self._nlog_worker = _NuntiusLogWorker()
        self._nlog_worker.moveToThread(self._nlog_thread)
        self._nlog_worker.log_ready.connect(self._on_nuntius_log_ready)
        self._nlog_thread.start()

        # Launch readers (kept alive until finished)
        self._launch_readers: dict[str, _LaunchReader] = {}

        # Health workers setup
        for sdef in SERVICES:
            worker = _HealthWorker(sdef)
            thread = QThread(self)
            worker.moveToThread(thread)
            worker.result.connect(self._on_health_result)
            thread.start()
            self._workers[sdef.service_id] = worker
            self._threads[sdef.service_id] = thread

        # Poll timer
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(POLL_MS)
        self._poll_timer.timeout.connect(self._poll_all)
        self._poll_timer.start()

        # Kick off first poll shortly after construction
        QTimer.singleShot(200, self._poll_all)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {C_BG}; border: none; }}")

        inner = QFrame()
        inner.setStyleSheet(f"QFrame {{ background: {C_BG}; }}")
        v = QVBoxLayout(inner)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(6)

        for sdef in SERVICES:
            row = _ServiceRow(sdef, parent=inner)
            row.launch_requested.connect(self._on_launch_requested)
            v.addWidget(row)
            self._rows[sdef.service_id] = row

        v.addStretch()
        scroll.setWidget(inner)
        self._body_layout.addWidget(scroll)

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def _poll_all(self) -> None:
        for sdef in SERVICES:
            worker = self._workers.get(sdef.service_id)
            if worker is None:
                continue
            # Invoke the check on the worker's own thread
            QTimer.singleShot(0, worker.check)

        # NUNTIUS live log — only if panel is open and NUNTIUS is running
        row = self._rows.get("nuntius")
        if row is not None and row.is_log_visible() and row.status() == "running":
            QTimer.singleShot(0, self._nlog_worker.fetch)

    @pyqtSlot(str, str)
    def _on_health_result(self, service_id: str, status: str) -> None:
        row = self._rows.get(service_id)
        if row is None:
            return
        # Never downgrade a STARTING row until a real status arrives.
        if row.status() == "starting" and status not in ("running",):
            return
        row.set_status(status)
        self._update_aggregate_dot()
        if service_id == "nuntius":
            self._emit_nuntius_status(status)

    def _update_aggregate_dot(self) -> None:
        statuses = [r.status() for r in self._rows.values()]
        if any(s == "offline" for s in statuses):
            self.set_status("error", "one or more services offline")
        elif any(s == "starting" for s in statuses):
            self.set_status("warn", "starting")
        elif statuses and all(s == "running" for s in statuses):
            self.set_status("ok", "all running")
        else:
            self.set_status("idle", "")

    def _emit_nuntius_status(self, status: str) -> None:
        if status == self._last_nuntius_status:
            return
        self._last_nuntius_status = status
        summary_map = {
            "running":  "online",
            "offline":  "offline",
            "starting": "starting",
            "unknown":  "unknown",
        }
        self.nuntius_status_changed.emit(status, summary_map.get(status, "unknown"))

    # ------------------------------------------------------------------
    # NUNTIUS live log
    # ------------------------------------------------------------------

    @pyqtSlot(list)
    def _on_nuntius_log_ready(self, lines: list) -> None:
        row = self._rows.get("nuntius")
        if row is None or not row.is_log_visible():
            return
        if not lines:
            row.set_log_lines(["(no recent emissions)"])
            return
        row.set_log_lines([str(x) for x in lines])

    # ------------------------------------------------------------------
    # Launch
    # ------------------------------------------------------------------

    @pyqtSlot(str)
    def _on_launch_requested(self, service_id: str) -> None:
        sdef = next((s for s in SERVICES if s.service_id == service_id), None)
        if sdef is None:
            return
        row = self._rows.get(service_id)
        if row is None:
            return

        script_path = self._repo_root / sdef.script
        if not script_path.exists():
            row.clear_log()
            row.append_log_line(f"[error] launcher not found: {script_path}")
            return

        row.set_status("starting")
        row.set_launch_enabled(False)
        row.clear_log()
        row.append_log_line(f"[launch] {script_path}")
        self._update_aggregate_dot()
        if service_id == "nuntius":
            self._emit_nuntius_status("starting")

        try:
            proc = subprocess.Popen(
                ["/bin/bash", str(script_path)],
                cwd=str(self._repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except Exception as e:
            row.append_log_line(f"[error] {e}")
            row.set_launch_enabled(True)
            row.set_status("offline")
            self._update_aggregate_dot()
            return

        reader = _LaunchReader(service_id, proc)
        reader.line_read.connect(self._on_launch_line)
        reader.finished_reading.connect(self._on_launch_reader_done)
        self._launch_readers[service_id] = reader
        reader.start()

        # Re-enable launch button after 3s regardless of outcome
        QTimer.singleShot(3000, lambda: row.set_launch_enabled(True))

    @pyqtSlot(str, str)
    def _on_launch_line(self, service_id: str, line: str) -> None:
        row = self._rows.get(service_id)
        if row is None:
            return
        row.append_log_line(line)

    @pyqtSlot(str)
    def _on_launch_reader_done(self, service_id: str) -> None:
        reader = self._launch_readers.pop(service_id, None)
        if reader is not None:
            reader.quit()
            reader.wait(500)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self._poll_timer.stop()
        except Exception:
            pass
        for thread in self._threads.values():
            try:
                thread.quit()
                thread.wait(500)
            except Exception:
                pass
        try:
            self._nlog_thread.quit()
            self._nlog_thread.wait(500)
        except Exception:
            pass
        for reader in list(self._launch_readers.values()):
            try:
                reader.quit()
                reader.wait(500)
            except Exception:
                pass
        super().closeEvent(event)
