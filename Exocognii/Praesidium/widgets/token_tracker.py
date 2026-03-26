#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ████████  ██████  ██   ██ ███████ ███    ██      ████████ ██████   █████   ██████ ██   ██ ███████ ██████  ▍
🮈     ██    ██    ██ ██  ██  ██      ████   ██         ██    ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ ▍
🮈     ██    ██    ██ █████   █████   ██ ██  ██         ██    ██████  ███████ ██      █████   █████   ██████  ▍
🮈     ██    ██    ██ ██  ██  ██      ██  ██ ██         ██    ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ ▍
🮈     ██     ██████  ██   ██ ███████ ██   ████ ███████ ██    ██   ██ ██   ██  ██████ ██   ██ ███████ ██   ██ ▍
🮈                                                                                                            ▍
🮈                                                                                                            ▍
🮈                                               Python Script                                                ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
█🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
█🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
█      PRAESIDIUM · widgets/token_tracker.py   ▍
█▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/token_tracker.py
# Cross-app token ledger. Watches ~/.arca/token_log.jsonl via QFileSystemWatcher.
# Tracks all apps that write to the shared log — Tower, Dolium, Praesidium, etc.
# version: 2.0.0

import json
from datetime import date, datetime, timezone
from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame, QProgressBar, QScrollArea, QWidget,
)
from PyQt6.QtCore import pyqtSignal, QFileSystemWatcher, QTimer

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

LOG_PATH = Path.home() / ".arca" / "token_log.jsonl"

COST_PER_M_INPUT  = 3.00
COST_PER_M_OUTPUT = 15.00

SESSION_LIMIT = 10_000
DAILY_LIMIT   = 100_000
COST_LIMIT    = 1.00

# Colours per app
APP_COLOURS = {
    "tower":      "#7a4a9a",   # purple
    "dolium":     "#1a5a5a",   # teal
    "praesidium": "#d4af37",   # gold
    "unknown":    "#3a3528",
}


class TokenTracker(ArcaneWidget):
    """
    Watches ~/.arca/token_log.jsonl and displays cross-app token totals.
    Updates live whenever any app appends a record.
    record_usage() still available for direct signal feeding (Praesidium chat).
    """

    usage_recorded = pyqtSignal(str, int, int, str)   # model, input, output, session_id

    def __init__(self, widget_id: str, storage_path: Path, parent=None):
        super().__init__(widget_id, "Token Tracker", parent)
        self._today         = str(date.today())
        self._session_start = datetime.now(timezone.utc).isoformat()
        self._last_line     = 0    # lines already read

        # Totals by scope
        self._session_in  = 0
        self._session_out = 0
        self._daily_in    = 0
        self._daily_out   = 0
        self._by_app: dict[str, dict] = {}   # app → {in, out}

        self._build_body()
        self._setup_watcher()
        self._read_log(full=True)
        self._refresh()

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Session
        L.addWidget(micro_label("session"))
        self._bar_session = self._make_bar(C_TEAL)
        L.addWidget(self._bar_session)
        self._lbl_session = self._data_label("0 / 10k tokens")
        L.addWidget(self._lbl_session)

        L.addWidget(self._sep())

        # Daily
        L.addWidget(micro_label("today  (all apps)"))
        self._bar_daily = self._make_bar(C_TEAL)
        L.addWidget(self._bar_daily)
        self._lbl_daily = self._data_label("0 / 100k tokens")
        L.addWidget(self._lbl_daily)

        L.addWidget(self._sep())

        # Cost
        L.addWidget(micro_label("estimated cost  (today)"))
        self._bar_cost = self._make_bar("#8b5a2b")
        L.addWidget(self._bar_cost)
        self._lbl_cost = self._data_label("$0.0000")
        L.addWidget(self._lbl_cost)

        L.addWidget(self._sep())

        # Per-app breakdown
        L.addWidget(micro_label("by app"))
        self._app_area = QVBoxLayout()
        self._app_area.setSpacing(2)
        L.addLayout(self._app_area)

        L.addWidget(self._sep())

        # Buttons
        row = QHBoxLayout()
        row.setSpacing(4)
        btn_reset = arcane_button("↺ RESET SESSION")
        btn_reset.setFixedHeight(24)
        btn_reset.clicked.connect(self._reset_session)
        row.addWidget(btn_reset)
        row.addStretch()
        L.addLayout(row)

    def _make_bar(self, colour: str) -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_BG}; border: 1px solid {C_GOLD_DARK}; border-radius: 2px;
            }}
            QProgressBar::chunk {{ background: {colour}; border-radius: 2px; }}
        """)
        return bar

    def _data_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {C_TEXT}; font-family: Georgia, serif; font-size: 10px;"
        )
        return lbl

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    def _rebuild_app_rows(self) -> None:
        while self._app_area.count():
            item = self._app_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for app, totals in sorted(self._by_app.items()):
            total = totals["in"] + totals["out"]
            colour = APP_COLOURS.get(app, APP_COLOURS["unknown"])
            row = QHBoxLayout()

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {colour}; font-size: 9px; font-family: Georgia, serif;")
            row.addWidget(dot)

            name = QLabel(app.upper())
            name.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-size: 9px; font-family: Georgia, serif; letter-spacing: 1px;"
            )
            row.addWidget(name)
            row.addStretch()

            count = QLabel(f"{total:,}")
            count.setStyleSheet(
                f"color: {C_TEXT}; font-size: 9px; font-family: Georgia, serif;"
            )
            row.addWidget(count)

            container = QWidget()
            container.setStyleSheet(f"background: {C_BG};")
            container.setLayout(row)
            self._app_area.addWidget(container)

    # ------------------------------------------------------------------
    # File watcher
    # ------------------------------------------------------------------

    def _setup_watcher(self) -> None:
        self._watcher = QFileSystemWatcher()
        # Watch the directory — file may not exist yet
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._watcher.addPath(str(LOG_PATH.parent))
        if LOG_PATH.exists():
            self._watcher.addPath(str(LOG_PATH))
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._watcher.directoryChanged.connect(self._on_dir_changed)

    def _on_file_changed(self, _path: str) -> None:
        self._read_log(full=False)
        self._refresh()

    def _on_dir_changed(self, _path: str) -> None:
        # File may have just been created
        if LOG_PATH.exists() and str(LOG_PATH) not in self._watcher.files():
            self._watcher.addPath(str(LOG_PATH))
        self._read_log(full=False)
        self._refresh()

    # ------------------------------------------------------------------
    # Log reading
    # ------------------------------------------------------------------

    def _read_log(self, full: bool = False) -> None:
        if not LOG_PATH.exists():
            return

        today = str(date.today())
        if today != self._today:
            self._today     = today
            self._daily_in  = 0
            self._daily_out = 0
            self._by_app    = {}
            full = True

        try:
            lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
        except Exception:
            return

        start = 0 if full else self._last_line
        self._last_line = len(lines)

        for line in lines[start:]:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            app  = rec.get("app", "unknown")
            ts   = rec.get("ts", "")
            inp  = int(rec.get("input_tokens",  0))
            out  = int(rec.get("output_tokens", 0))

            # Daily
            if ts.startswith(today):
                self._daily_in  += inp
                self._daily_out += out

                # Per-app (today only)
                if app not in self._by_app:
                    self._by_app[app] = {"in": 0, "out": 0}
                self._by_app[app]["in"]  += inp
                self._by_app[app]["out"] += out

            # Session — records since this widget was initialised
            if ts >= self._session_start:
                self._session_in  += inp
                self._session_out += out

    # ------------------------------------------------------------------
    # Public API — direct feed from Praesidium chat (no log roundtrip)
    # ------------------------------------------------------------------

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        session_id: str = "default",
    ) -> None:
        """
        Direct feed — called by ChatWidget via signal.
        The log watcher will also pick this up from the file,
        so we don't double-count here — just re-read the log.
        """
        self.usage_recorded.emit(model, input_tokens, output_tokens, session_id)
        # Trigger a re-read after a short delay to let the file write complete
        QTimer.singleShot(200, lambda: (self._read_log(full=False), self._refresh()))

    # ------------------------------------------------------------------
    # Refresh display
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        session_total = self._session_in + self._session_out
        daily_total   = self._daily_in   + self._daily_out
        daily_cost    = (
            (self._daily_in  / 1_000_000) * COST_PER_M_INPUT +
            (self._daily_out / 1_000_000) * COST_PER_M_OUTPUT
        )

        self._bar_session.setValue(min(100, int(session_total / SESSION_LIMIT * 100)))
        self._bar_daily.setValue(  min(100, int(daily_total   / DAILY_LIMIT   * 100)))
        self._bar_cost.setValue(   min(100, int(daily_cost    / COST_LIMIT    * 100)))

        self._lbl_session.setText(f"{session_total:,} / {SESSION_LIMIT:,} tokens")
        self._lbl_daily.setText(  f"{daily_total:,} / {DAILY_LIMIT:,} tokens  (all apps)")
        self._lbl_cost.setText(   f"${daily_cost:.4f} / ${COST_LIMIT:.2f}")

        self._rebuild_app_rows()

        if daily_cost >= COST_LIMIT * 0.8:
            self.set_status("warn", "Approaching cost limit")
        elif daily_total > 0:
            self.set_status("ok", "")
        else:
            self.set_status("idle", "")

    def _reset_session(self) -> None:
        self._session_start = datetime.now(timezone.utc).isoformat()
        self._session_in    = 0
        self._session_out   = 0
        self._refresh()
        self.set_status("idle", "Session reset")
