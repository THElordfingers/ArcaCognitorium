# control.py — Vigilarum Omnia v2
import sys, datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QStatusBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from data import (
    WIDGET_REGISTRY, WIDGET_CATEGORIES, MAX_DISPLAYS,
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_TEXT, C_TEXT_DIM,
    C_TEAL, C_RED, C_GREEN, FONT_BODY, FONT_SIZE, FONT_SMALL, FONT_TITLE,
)
from engine import calculate_all
from state import write_state, toggle_widget, widget_assignments

SS = f"""
QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};font-family:Georgia;font-size:11pt;}}
QScrollArea{{border:none;background:{C_BG};}}
QScrollBar:vertical{{background:{C_BG};width:8px;border:none;}}
QScrollBar::handle:vertical{{background:{C_GOLD_DIM};border-radius:4px;min-height:20px;}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}
QFrame#div{{background:{C_GOLD_DIM};}}
QStatusBar{{background:{C_PANEL};color:{C_TEXT_DIM};font-size:9pt;border-top:1px solid {C_GOLD_DIM};}}
"""

def _lbl(text, size=FONT_SIZE, color=C_TEXT, bold=False):
    l = QLabel(text)
    l.setFont(QFont(FONT_BODY, size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color};background:transparent;")
    return l

def _make_btn(text, active=False):
    bg = C_GOLD if active else C_GOLD_DIM
    fg = C_BG  if active else C_TEXT
    b = QPushButton(text); b.setFont(QFont(FONT_BODY, FONT_SMALL))
    b.setFixedSize(28, 22)
    b.setStyleSheet(f"""
        QPushButton{{background:{bg};color:{fg};border:1px solid {C_GOLD_DIM};border-radius:3px;}}
        QPushButton:hover{{background:{C_GOLD};color:{C_BG};}}
    """)
    return b

def _set_btn_active(btn, active):
    bg = C_GOLD if active else C_GOLD_DIM; fg = C_BG if active else C_TEXT
    btn.setStyleSheet(f"""
        QPushButton{{background:{bg};color:{fg};border:1px solid {C_GOLD_DIM};border-radius:3px;}}
        QPushButton:hover{{background:{C_GOLD};color:{C_BG};}}
    """)


class EngineWorker(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)
    def run(self):
        try: self.finished.emit(calculate_all())
        except Exception as e: self.error.emit(str(e))


class WidgetRow(QWidget):
    def __init__(self, wid, name, ctype, assignments, parent=None):
        super().__init__(parent)
        self.wid = wid; self._btns = {}
        row = QHBoxLayout(self); row.setContentsMargins(6,3,6,3); row.setSpacing(4)
        badge_color = C_TEAL if ctype == "visual" else C_GOLD_DIM
        badge_text  = "Vis" if ctype == "visual" else "Txt"
        badge = _lbl(badge_text, FONT_SMALL-1, badge_color); badge.setFixedWidth(24)
        row.addWidget(badge)
        name_lbl = _lbl(name, FONT_SIZE); name_lbl.setMinimumWidth(200)
        row.addWidget(name_lbl); row.addStretch()
        assigned = assignments.get(wid, [])
        for d in range(1, MAX_DISPLAYS+1):
            btn = _make_btn(str(d), active=(d in assigned))
            btn.clicked.connect(lambda checked, did=d: self._toggle(did))
            self._btns[d] = btn; row.addWidget(btn)

    def _toggle(self, did):
        now_on = toggle_widget(did, self.wid)
        _set_btn_active(self._btns[did], now_on)


class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vigilarum Omnia \u2014 Control")
        self.setMinimumSize(740, 660)
        self._last_state = None; self._engine_running = False
        self._build_ui(); self.setStyleSheet(SS)
        self._start_engine()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        root.addWidget(self._build_header())
        div = QFrame(); div.setObjectName("div"); div.setFixedHeight(1); root.addWidget(div)
        root.addWidget(self._build_list(), stretch=1)
        self._statusbar = QStatusBar(); self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Initialising engine\u2026")

    def _build_header(self):
        hdr = QWidget(); hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"background:{C_PANEL};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(16,0,16,0)
        hl.addWidget(_lbl("VIGILARUM OMNIA", FONT_TITLE, C_GOLD, bold=True))
        hl.addStretch()
        self._engine_lbl = _lbl("\u25cf Calculating\u2026", FONT_SMALL, C_GOLD_DIM)
        hl.addWidget(self._engine_lbl)
        self._sky_lbl = _lbl("", FONT_SMALL, C_TEXT_DIM)
        self._sky_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hl.addWidget(self._sky_lbl)
        return hdr

    def _build_list(self):
        container = QWidget(); vl = QVBoxLayout(container)
        vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        # column header
        hdr = QWidget(); hdr.setFixedHeight(26); hdr.setStyleSheet(f"background:{C_PANEL};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(6,0,6,0); hl.setSpacing(4)
        hl.addWidget(_lbl("Type", FONT_SMALL, C_GOLD_DIM, bold=True))
        hl.addWidget(_lbl("Widget", FONT_SMALL, C_GOLD_DIM, bold=True))
        hl.addStretch()
        for d in range(1, MAX_DISPLAYS+1):
            l = _lbl(str(d), FONT_SMALL, C_GOLD_DIM, bold=True)
            l.setFixedWidth(28); l.setAlignment(Qt.AlignmentFlag.AlignCenter); hl.addWidget(l)
        vl.addWidget(hdr)
        hdiv = QFrame(); hdiv.setObjectName("div"); hdiv.setFixedHeight(1); vl.addWidget(hdiv)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget(); cl = QVBoxLayout(content)
        cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
        assignments = widget_assignments()
        row_idx = 0
        by_cat = {}
        for wid, name, ctype, cat in WIDGET_REGISTRY:
            by_cat.setdefault(cat, []).append((wid, name, ctype))
        for cat in WIDGET_CATEGORIES:
            items = by_cat.get(cat, [])
            if not items: continue
            cat_hdr = QWidget(); cat_hdr.setFixedHeight(24)
            cat_hdr.setStyleSheet("background:#14142A;")
            ch = QHBoxLayout(cat_hdr); ch.setContentsMargins(8,0,8,0)
            ch.addWidget(_lbl(cat.upper(), FONT_SMALL, C_GOLD_DIM, bold=True))
            cl.addWidget(cat_hdr)
            for wid, name, ctype in items:
                row = WidgetRow(wid, name, ctype, assignments)
                bg = C_BG if row_idx % 2 == 0 else C_PANEL
                row.setStyleSheet(f"background:{bg};")
                cl.addWidget(row); row_idx += 1
        cl.addStretch(); scroll.setWidget(content); vl.addWidget(scroll)
        return container

    def _start_engine(self):
        self._run_engine()
        self._etimer = QTimer(self); self._etimer.setInterval(60_000)
        self._etimer.timeout.connect(self._run_engine); self._etimer.start()
        self._ctimer = QTimer(self); self._ctimer.setInterval(1_000)
        self._ctimer.timeout.connect(self._clock_tick); self._ctimer.start()

    def _run_engine(self):
        if self._engine_running: return
        self._engine_running = True
        self._worker = EngineWorker()
        self._worker.finished.connect(self._done)
        self._worker.error.connect(self._err)
        self._worker.start()

    def _done(self, state):
        self._engine_running = False; self._last_state = state
        write_state(state)
        self._engine_lbl.setText("\u25cf Live")
        self._engine_lbl.setStyleSheet(f"color:{C_GREEN};background:transparent;")
        self._sky_lbl.setText(state.get("sky_summary", ""))
        self._statusbar.showMessage(
            f"Engine updated \u00b7 {state.get('time_local','')} \u00b7 "
            f"{state.get('aspects_count',0)} aspects \u00b7 "
            f"{state.get('season','')} \u00b7 {state.get('moon_phase_name','')}")

    def _err(self, msg):
        self._engine_running = False
        self._engine_lbl.setText("\u25cf Error")
        self._engine_lbl.setStyleSheet(f"color:{C_RED};background:transparent;")
        self._statusbar.showMessage(f"Engine error: {msg}")

    def _clock_tick(self):
        if self._last_state is None: return
        now = datetime.datetime.now()
        self._last_state["time_local"]     = now.strftime("%H:%M:%S")
        self._last_state["time_timestamp"] = now.isoformat()
        write_state(self._last_state)


def main():
    app = QApplication(sys.argv)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,     QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(C_TEXT))
    pal.setColor(QPalette.ColorRole.Base,       QColor(C_PANEL))
    pal.setColor(QPalette.ColorRole.Text,       QColor(C_TEXT))
    app.setPalette(pal)
    w = ControlPanel(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
