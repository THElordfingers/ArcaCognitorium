#!/usr/bin/env python3
"""
vigilarum_patch.py — Vigilarum Omnia v2
Applies targeted fixes:
  1. info.py     — f-string backslash syntax error (line 208)
  2. control.py  — removes Columns panel
  3. display.py  — visible grip lines, larger grip zone
  4. runtime     — clears ghost/orphan widget entries from display_N.json

Run from ~/ArcaCognitorium/Exocognii/Vigilarum/
  python3 vigilarum_patch.py
"""
import os, json, pathlib, re, sys

BASE = pathlib.Path(__file__).parent
print(f"\nVigilarum patch — target: {BASE}\n")

# =============================================================================
# 1. Fix info.py — f-string backslash on line ~208
# =============================================================================

info_path = BASE / "info.py"
if info_path.exists():
    src = info_path.read_text(encoding="utf-8")
    old = (
        "f\"{'Currently ACTIVE \\u2014 inauspicious period.' if active else 'Currently inactive.'}\")"
    )
    new = (
        "('Currently ACTIVE \u2014 inauspicious period.' if active else 'Currently inactive.'))"
    )
    if old in src:
        src = src.replace(old, new)
        info_path.write_text(src, encoding="utf-8")
        print("  [1] info.py — f-string backslash fixed")
    else:
        # Try a regex approach for the specific line
        pattern = r"f\"(\{'Currently ACTIVE \\u2014 inauspicious period\.' if active else 'Currently inactive\.'\})\"(\))"
        replacement = r"('Currently ACTIVE \u2014 inauspicious period.' if active else 'Currently inactive.')\2"
        new_src, count = re.subn(pattern, replacement, src)
        if count:
            info_path.write_text(new_src, encoding="utf-8")
            print("  [1] info.py — f-string backslash fixed (regex)")
        else:
            # Just rewrite the full _live_context rahu_kalam block safely
            old_block = '''            return (f"Today\'s Rahu Kalam window: {s} \\u2014 {e}. "
                    f"{'Currently ACTIVE \\u2014 inauspicious period.' if active else 'Currently inactive.'}")'''
            new_block = '''            active_str = 'Currently ACTIVE \u2014 inauspicious period.' if active else 'Currently inactive.'
            return f"Today\'s Rahu Kalam window: {s} \u2014 {e}. " + active_str'''
            if old_block in src:
                src = src.replace(old_block, new_block)
                info_path.write_text(src, encoding="utf-8")
                print("  [1] info.py — f-string backslash fixed (block replacement)")
            else:
                print("  [1] info.py — WARNING: could not locate target line. Fix manually:")
                print("      Find the 'Currently ACTIVE' f-string and extract the conditional to a variable.")
else:
    print("  [1] info.py not found — skipping")

# =============================================================================
# 2. Rewrite control.py — remove Columns panel entirely
# =============================================================================

CONTROL = r'''# control.py — Vigilarum Omnia v2
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
'''

control_path = BASE / "control.py"
control_path.write_text(CONTROL, encoding="utf-8")
print("  [2] control.py — Columns panel removed")

# =============================================================================
# 3. Patch display.py — make grip visible and larger
# =============================================================================

display_path = BASE / "display.py"
if display_path.exists():
    src = display_path.read_text(encoding="utf-8")

    old_grip = '''    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Handle bar
        p.fillRect(0, 0, self.width(), HANDLE_H, QColor(C_PANEL))
        pen = QPen(QColor(C_BORDER)); pen.setWidth(1); p.setPen(pen)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Widget name in handle
        p.setFont(QFont(FONT_BODY, FONT_SMALL - 1))
        p.setPen(QColor(C_GOLD_DIM))
        p.drawText(6, 0, self.width() - 20, HANDLE_H,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self.display_name)

        # Resize grip (bottom-right triangle)
        gx = self.width() - GRIP_SIZE
        gy = self.height() - GRIP_SIZE
        p.setPen(QPen(QColor(C_GOLD_DIM), 1))
        for i in range(1, 4):
            offset = i * 3
            p.drawLine(gx + offset, self.height() - 1,
                       self.width() - 1, gy + offset)
        p.end()'''

    new_grip = '''    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Handle bar
        p.fillRect(0, 0, self.width(), HANDLE_H, QColor(C_PANEL))
        pen = QPen(QColor(C_BORDER)); pen.setWidth(1); p.setPen(pen)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Widget name in handle
        p.setFont(QFont(FONT_BODY, FONT_SMALL - 1))
        p.setPen(QColor(C_GOLD_DIM))
        p.drawText(6, 0, self.width() - 20, HANDLE_H,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self.display_name)

        # Resize grip — bright gold, clearly visible
        gx = self.width() - GRIP_SIZE
        gy = self.height() - GRIP_SIZE
        # Fill grip zone background
        p.fillRect(gx, gy, GRIP_SIZE, GRIP_SIZE, QColor("#1A1A2E"))
        # Draw grip lines
        grip_pen = QPen(QColor(C_GOLD)); grip_pen.setWidth(2); p.setPen(grip_pen)
        for i in range(2, 5):
            offset = i * 4
            p.drawLine(self.width() - offset, self.height() - 2,
                       self.width() - 2,      self.height() - offset)
        p.end()'''

    if old_grip in src:
        src = src.replace(old_grip, new_grip)
        display_path.write_text(src, encoding="utf-8")
        print("  [3] display.py — grip lines made visible")
    else:
        print("  [3] display.py — WARNING: grip paint block not found. May already be patched.")
else:
    print("  [3] display.py not found")

# =============================================================================
# 4. Clear ghost/orphan widgets from all display_N.json files
#    Ghost entries exist from old grid layout sessions.
#    We cross-reference against the current WIDGET_REGISTRY ids.
# =============================================================================

# Import WIDGET_BY_ID without running the full app
import importlib.util, sys as _sys
spec = importlib.util.spec_from_file_location("data", BASE / "data.py")
try:
    data_mod = importlib.util.load_from_spec = None
    # Just read the valid IDs directly from the registry pattern in data.py
    data_src = (BASE / "data.py").read_text(encoding="utf-8")
    import re as _re
    valid_ids = set(_re.findall(r'"((?:planet|node|panchang|time|lunar|aspects|season|summary|moon|zodiac|nakshatra|tithi|eclipse|planet_strip)[_a-z]+)"', data_src))
except Exception as e:
    valid_ids = set()
    print(f"  [4] Could not parse valid IDs: {e}")

displays_dir = pathlib.Path.home() / ".vigilarum" / "displays"
if displays_dir.exists() and valid_ids:
    cleaned = 0
    for f in displays_dir.glob("display_*.json"):
        try:
            cfg = json.loads(f.read_text(encoding="utf-8"))
            original_widgets = cfg.get("widgets", [])
            clean_widgets = [w for w in original_widgets if w in valid_ids]
            # Also clean layout entries
            layout = cfg.get("layout", {})
            clean_layout = {k: v for k, v in layout.items() if k in valid_ids}
            if clean_widgets != original_widgets or clean_layout != layout:
                cfg["widgets"] = clean_widgets
                cfg["layout"]  = clean_layout
                f.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
                removed = set(original_widgets) - set(clean_widgets)
                print(f"  [4] {f.name} — removed orphans: {removed}")
                cleaned += 1
        except Exception as e:
            print(f"  [4] {f.name} — error: {e}")
    if cleaned == 0:
        print("  [4] No orphan widgets found in display files")
else:
    if not displays_dir.exists():
        print("  [4] ~/.vigilarum/displays/ not found — nothing to clean")
    else:
        print("  [4] Could not validate IDs — skipping orphan cleanup")

print("\nPatch complete. Restart control.py and display.py.\n")
