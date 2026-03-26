#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈   ██████   ██████ ██    ██ ██      ██    ██ ███████  ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██ ██       ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██ ███████  ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██      ██  ▍
🮈   ██████   ██████  ██████  ███████  ██████  ███████  ▍
🮈                                                      ▍
🮈                                                      ▍
🮈                    Python Script                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# ╔══════════════════════════════════════════════════════════════════════════════════
# ║ ⛨    ArcaCognitorium / tools / oculus_prime.py
# ║ ⛨    The Oculus Prime — System Control Panel     v1.0
# ║ ⛨
# ║ ⛨    PyQt6 dockable debug monitor for the Arca Cognitorium.
# ║ ⛨    Run from the project root:
# ║ ⛨        python tools/oculus_prime.py
# ║ ⛨
# ║ ⛨    Safe to run alongside a live Tower session. Read-only. No Tower imports.
# ║ ⛨    Layout (dock positions, visibility) persists via QSettings.
# ╚══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

from PyQt6.QtCore import (
    Qt, QTimer, QSettings, QSize, pyqtSignal, QThread, QObject
)
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QPalette, QTextCharFormat,
    QTextCursor, QIcon, QAction
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSplitter, QFrame, QScrollArea, QGroupBox, QProgressBar,
    QComboBox, QLineEdit, QPushButton, QSizePolicy, QToolBar, QStatusBar,
    QTabWidget, QPlainTextEdit, QGridLayout, QCheckBox
)


# ════════════════════════════════════════════════════════════════════════════════
#  PATHS
# ════════════════════════════════════════════════════════════════════════════════

ROOT = Path(".")

PATHS = {
    "assessor_diag":     ROOT / "storage/logs/assessor_diag.log",
    "archivist_diag":    ROOT / "storage/logs/archivist_diag.log",
    "emergence_diag":    ROOT / "storage/logs/emergence_diag.log",
    "interruption_diag": ROOT / "storage/logs/interruption_diag.log",
    "entity_memory_diag":ROOT / "storage/logs/entity_memory_diag.log",
    "immutable":         ROOT / "storage/logs/immutable.jsonl",
    "reflections":       ROOT / "storage/logs/reflections.jsonl",
    "council_emerged":   ROOT / "storage/council/emerged.json",
    "vectors":           ROOT / "storage/vectors/vectors.pkl",
    "conversations_dir": ROOT / "storage/conversations",
    "grimoire":          ROOT / "storage/grimoire.json",
    "config":            ROOT / "config.yaml",
}


# ════════════════════════════════════════════════════════════════════════════════
#  PALETTE  — Arca Cognitorium canonical colours
# ════════════════════════════════════════════════════════════════════════════════

C = {
    "void":        "#0D0B0E",
    "umbra":       "#161218",
    "surface":     "#1E1A24",
    "border":      "#2A2535",
    "border_hi":   "#3D3550",
    "text_dim":    "#5A5068",
    "text_mid":    "#8A7FA0",
    "text_main":   "#D4C8A8",
    "aureate":     "#C9A84C",
    "aureate_dim": "#7A6030",
    "green":       "#4CAF80",
    "green_dim":   "#2A5A40",
    "red":         "#C05050",
    "red_dim":     "#602828",
    "yellow":      "#C8A84C",
    "cyan":        "#5AB0C0",
    "blue":        "#6A8FAF",
    # Entity jewels
    "luminarious":    "#C9A84C",
    "archivist":      "#6A8FAF",
    "contrarian":     "#A05C5C",
    "minimalist":     "#7A9E7E",
    "speculator":     "#8B6BAE",
    "pessimist":      "#8A7060",
    "toolsmith":      "#5E8A8A",
    "systems_thinker":"#7E7E9E",
    "socratic":       "#AF8C5A",
    "assessor":       "#5A7A6A",
}

ENTITY_SIGILS = {
    "luminarious":    "⬡",
    "archivist":      "◈",
    "contrarian":     "◇",
    "minimalist":     "◻",
    "speculator":     "◎",
    "pessimist":      "▲",
    "toolsmith":      "⬟",
    "systems_thinker":"⬠",
    "socratic":       "◉",
    "assessor":       "⛨",
}

ENTITY_DISPLAY = {
    "luminarious":    "LUMINARIOUS",
    "archivist":      "THE ARCHIVIST",
    "contrarian":     "THE CONTRARIAN",
    "minimalist":     "THE MINIMALIST",
    "speculator":     "THE SPECULATOR",
    "pessimist":      "THE PESSIMIST",
    "toolsmith":      "THE TOOLSMITH",
    "systems_thinker":"SYSTEMS THINKER",
    "socratic":       "THE SOCRATIC",
    "assessor":       "THE ASSESSOR",
}

ALL_ENTITIES = [
    "luminarious", "archivist", "contrarian", "minimalist",
    "speculator", "pessimist", "toolsmith", "systems_thinker", "socratic",
]

INTERRUPTION_PRESENCE = {
    "archivist":       0.70,
    "contrarian":      0.65,
    "speculator":      0.45,
    "pessimist":       0.55,
    "toolsmith":       0.40,
    "systems_thinker": 0.50,
    "socratic":        0.35,
    "minimalist":      0.50,
}

ENTITY_DOMAINS = {
    "archivist":      ["retrieve","history","past","remember","archive","search","chronicle"],
    "contrarian":     ["assume","wrong","challenge","disagree","but","however","alternative"],
    "minimalist":     ["simple","brief","short","essential","distill","core","just","only"],
    "speculator":     ["imagine","what if","possible","explore","future","potential","could"],
    "pessimist":      ["risk","problem","fail","wrong","danger","concern","downside","issue"],
    "toolsmith":      ["abstract","pattern","reuse","tool","build","function","class","system"],
    "systems_thinker":["system","constraint","dependency","flow","architecture","whole","map"],
    "socratic":       ["why","question","purpose","understand","meaning","what is","how does"],
}

SILENCE_RULES = {
    "contrarian": ["speculator", "minimalist"],
    "socratic":   [],
}

POST_SPEAK_MULTIPLIERS = {
    "socratic":   {"contrarian": 2.0},
    "contrarian": {"socratic":   1.5},
    "archivist":  {"toolsmith":  1.3},
}

EMERGENCE_THRESHOLD = 1.0
MAX_SIGNAL = 3.0
DOMAIN_THRESHOLD = 0.65


# ════════════════════════════════════════════════════════════════════════════════
#  DATA READERS  — pure filesystem, no Tower imports
# ════════════════════════════════════════════════════════════════════════════════

def _read_jsonl(path: Path, max_lines: int = 500) -> List[dict]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except OSError:
        return []
    out = []
    for line in lines[-max_lines:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"_raw": line})
    return out


def _read_plain_log(path: Path, max_lines: int = 500) -> List[str]:
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except OSError:
        return []


def _read_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _file_size_str(path: Path) -> str:
    if not path.exists():
        return "—"
    b = path.stat().st_size
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b/1024:.1f} KB"
    return f"{b/1024/1024:.2f} MB"


def _file_mtime_str(path: Path) -> str:
    if not path.exists():
        return "—"
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%H:%M:%S")


def _count_conversations() -> int:
    d = PATHS["conversations_dir"]
    if not d.exists():
        return 0
    try:
        return sum(1 for f in d.iterdir() if f.suffix == ".json")
    except OSError:
        return 0


def _grimoire_entries() -> List[dict]:
    data = _read_json(PATHS["grimoire"])
    if not data:
        return []
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def _chronicle_vector_estimate() -> int:
    vpath = PATHS["vectors"]
    if not vpath.exists():
        return 0
    return max(0, int(vpath.stat().st_size / 1024 / 1.5))


def _get_emerged_set() -> set:
    data = _read_json(PATHS["council_emerged"])
    if not data:
        return set()
    return set(data.get("emerged", []))


def _derive_signals() -> Dict[str, float]:
    """Re-derive entity signal strengths from reflections.jsonl."""
    signals = {eid: 0.0 for eid in ENTITY_DOMAINS}
    for record in _read_jsonl(PATHS["reflections"]):
        topics = {t.lower() for t in record.get("dominant_topics", [])}
        code_present = record.get("code_present", False)
        question_count = record.get("question_count", 0)
        for eid in ENTITY_DOMAINS:
            domain = set(ENTITY_DOMAINS[eid])
            matches = len(topics & domain)
            if matches > 0:
                signals[eid] = min(MAX_SIGNAL, signals[eid] + 0.15 * matches)
            else:
                signals[eid] = max(0.0, signals[eid] - 0.02)
            if eid in ("toolsmith", "systems_thinker") and code_present:
                signals[eid] = min(MAX_SIGNAL, signals[eid] + 0.05)
            if eid == "socratic" and question_count >= 3:
                signals[eid] = min(MAX_SIGNAL, signals[eid] + 0.08)
    return signals


def _latest_routing_signal() -> Optional[dict]:
    records = _read_jsonl(PATHS["reflections"])
    for r in reversed(records):
        if "dominant_topics" in r:
            return r
    return None


def _latest_analytics() -> List[dict]:
    return [r for r in _read_jsonl(PATHS["reflections"]) if r.get("type") == "self_analytics"]


def _latest_interruption_from_log() -> Optional[str]:
    """Read last interruption result line from interruption_diag.log."""
    lines = _read_plain_log(PATHS["interruption_diag"])
    for line in reversed(lines):
        if line.strip():
            return line.strip()
    return None


def _read_config_yaml() -> dict:
    """Minimal YAML reader — only extracts scalar key: value pairs."""
    path = PATHS["config"]
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        val = val.strip().strip('"').strip("'")
        result[key.strip()] = val
    return result


# ════════════════════════════════════════════════════════════════════════════════
#  STYLE HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _apply_app_palette(app: QApplication) -> None:
    palette = QPalette()
    bg = QColor(C["void"])
    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, QColor(C["text_main"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(C["umbra"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(C["surface"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(C["text_main"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(C["surface"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(C["text_main"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(C["aureate_dim"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(C["aureate"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(C["surface"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(C["text_main"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(C["cyan"]))
    app.setPalette(palette)


GLOBAL_QSS = f"""
QMainWindow {{
    background: {C['void']};
}}
QDockWidget {{
    background: {C['void']};
    color: {C['text_dim']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    titlebar-close-icon: none;
}}
QDockWidget::title {{
    background: {C['umbra']};
    color: {C['aureate']};
    padding: 4px 8px;
    border-bottom: 1px solid {C['border']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QWidget {{
    background: {C['void']};
    color: {C['text_main']};
    font-family: monospace;
    font-size: 12px;
}}
QTableWidget {{
    background: {C['void']};
    gridline-color: {C['border']};
    border: none;
    selection-background-color: {C['border_hi']};
    selection-color: {C['text_main']};
    alternate-background-color: {C['umbra']};
}}
QTableWidget::item {{
    padding: 2px 6px;
    border: none;
}}
QHeaderView::section {{
    background: {C['umbra']};
    color: {C['text_dim']};
    border: none;
    border-bottom: 1px solid {C['border']};
    padding: 4px 6px;
    font-size: 10px;
    letter-spacing: 1px;
}}
QScrollBar:vertical {{
    background: {C['void']};
    width: 6px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C['border_hi']};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {C['void']};
    height: 6px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C['border_hi']};
    border-radius: 3px;
    min-width: 20px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QPlainTextEdit, QTextEdit {{
    background: {C['void']};
    color: {C['text_main']};
    border: none;
    selection-background-color: {C['border_hi']};
}}
QLabel {{
    background: transparent;
    color: {C['text_main']};
}}
QProgressBar {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 2px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    border-radius: 2px;
    background: {C['aureate']};
}}
QComboBox {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text_main']};
    padding: 2px 6px;
    border-radius: 2px;
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text_main']};
    selection-background-color: {C['border_hi']};
}}
QLineEdit {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text_main']};
    padding: 2px 6px;
    border-radius: 2px;
}}
QLineEdit:focus {{
    border: 1px solid {C['aureate_dim']};
}}
QPushButton {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text_dim']};
    padding: 3px 10px;
    border-radius: 2px;
    font-size: 10px;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    border: 1px solid {C['border_hi']};
    color: {C['text_main']};
}}
QToolBar {{
    background: {C['umbra']};
    border-bottom: 1px solid {C['border']};
    spacing: 4px;
    padding: 2px 4px;
}}
QStatusBar {{
    background: {C['umbra']};
    color: {C['text_dim']};
    border-top: 1px solid {C['border']};
    font-size: 10px;
}}
QTabWidget::pane {{
    border: 1px solid {C['border']};
    background: {C['void']};
}}
QTabBar::tab {{
    background: {C['umbra']};
    color: {C['text_dim']};
    padding: 4px 10px;
    border-bottom: 1px solid {C['border']};
    font-size: 10px;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {C['surface']};
    color: {C['aureate']};
    border-bottom: 2px solid {C['aureate_dim']};
}}
QGroupBox {{
    color: {C['text_dim']};
    border: 1px solid {C['border']};
    border-radius: 3px;
    margin-top: 8px;
    font-size: 10px;
    letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: {C['text_dim']};
}}
QSplitter::handle {{
    background: {C['border']};
    width: 1px;
    height: 1px;
}}
"""

def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C['text_dim']}; font-size: 10px; letter-spacing: 2px; "
        f"background: {C['umbra']}; padding: 3px 8px; "
        f"border-bottom: 1px solid {C['border']};"
    )
    return lbl


def _value_label(text: str = "", color: str = C["text_main"]) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


def _dim_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {C['text_dim']}; background: transparent; font-size: 11px;")
    return lbl


def _make_table(headers: List[str], stretch_col: int = -1) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.horizontalHeader().setHighlightSections(False)
    if stretch_col >= 0:
        t.horizontalHeader().setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
    return t


def _cell(text: str, color: str = C["text_main"], align=Qt.AlignmentFlag.AlignLeft) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    item.setForeground(QColor(color))
    item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
    return item


# ════════════════════════════════════════════════════════════════════════════════
#  BASE DOCK PANEL
# ════════════════════════════════════════════════════════════════════════════════

class BaseDock(QDockWidget):
    """All panels inherit from this. Provides a styled content area and refresh slot."""

    DOCK_TITLE = "PANEL"

    def __init__(self, parent=None):
        super().__init__(self.DOCK_TITLE, parent)
        self.setObjectName(self.__class__.__name__)
        self.setAllowedAreas(
            Qt.DockWidgetArea.AllDockWidgetAreas
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        container = QWidget()
        container.setObjectName("dock_container")
        container.setStyleSheet(f"#dock_container {{ background: {C['void']}; }}")
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setWidget(container)
        self._build()

    def _build(self):
        """Override to populate self._layout."""
        pass

    def refresh(self):
        """Override to pull fresh data."""
        pass


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 1 — COUNCIL
# ════════════════════════════════════════════════════════════════════════════════

class CouncilDock(BaseDock):
    DOCK_TITLE = "⬡  COUNCIL"

    def _build(self):
        self._layout.addWidget(_section_label("ENTITY  ·  EMERGED  ·  SIGNAL  ·  PRESENCE"))

        self._table = _make_table(
            ["", "ENTITY", "EMERGED", "SIGNAL", "/ MAX", "PRES.", "DOMAINS"],
            stretch_col=6,
        )
        self._table.setColumnWidth(0, 28)
        self._table.setColumnWidth(1, 150)
        self._table.setColumnWidth(2, 70)
        self._table.setColumnWidth(3, 120)
        self._table.setColumnWidth(4, 48)
        self._table.setColumnWidth(5, 52)
        self._layout.addWidget(self._table)

        # Signal bars are QProgressBars embedded in cells via setCellWidget
        self._bars: Dict[str, QProgressBar] = {}
        self._populate()

    def _populate(self):
        emerged = _get_emerged_set()
        signals = _derive_signals()

        self._table.setRowCount(len(ALL_ENTITIES))
        for row, eid in enumerate(ALL_ENTITIES):
            color = C.get(eid, C["text_main"])
            sigil = ENTITY_SIGILS.get(eid, "·")
            display = ENTITY_DISPLAY.get(eid, eid.upper())
            is_emerged = eid in emerged or eid == "luminarious"
            signal = signals.get(eid, 0.0)
            pres = INTERRUPTION_PRESENCE.get(eid, 0.0)
            domains = ", ".join(ENTITY_DOMAINS.get(eid, [])[:4])

            self._table.setItem(row, 0, _cell(sigil, color, Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(row, 1, _cell(display, color))

            emerged_text = "● EMERGED" if is_emerged else "○  dormant"
            emerged_color = C["green"] if is_emerged else C["text_dim"]
            self._table.setItem(row, 2, _cell(emerged_text, emerged_color))

            # Signal bar
            bar = QProgressBar()
            bar.setRange(0, int(MAX_SIGNAL * 100))
            bar.setValue(int(signal * 100))
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setStyleSheet(self._bar_style(signal))
            wrapper = QWidget()
            wl = QHBoxLayout(wrapper)
            wl.setContentsMargins(4, 4, 4, 4)
            wl.addWidget(bar)
            self._table.setCellWidget(row, 3, wrapper)
            self._bars[eid] = bar

            self._table.setItem(row, 4, _cell(f"{signal:.2f}", color, Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(row, 5, _cell(f"{pres:.2f}" if pres else "—", C["text_dim"], Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(row, 6, _cell(domains, C["text_dim"]))

            self._table.setRowHeight(row, 24)

    def _bar_style(self, value: float) -> str:
        ratio = value / MAX_SIGNAL if MAX_SIGNAL > 0 else 0
        if ratio >= EMERGENCE_THRESHOLD / MAX_SIGNAL:
            chunk_color = C["green"]
        elif ratio >= 0.35:
            chunk_color = C["yellow"]
        else:
            chunk_color = C["border_hi"]
        return (
            f"QProgressBar {{ background: {C['surface']}; border: 1px solid {C['border']}; "
            f"border-radius: 2px; height: 8px; }}"
            f"QProgressBar::chunk {{ background: {chunk_color}; border-radius: 2px; }}"
        )

    def refresh(self):
        emerged = _get_emerged_set()
        signals = _derive_signals()
        for row, eid in enumerate(ALL_ENTITIES):
            is_emerged = eid in emerged or eid == "luminarious"
            signal = signals.get(eid, 0.0)
            color = C.get(eid, C["text_main"])

            emerged_text = "● EMERGED" if is_emerged else "○  dormant"
            emerged_color = C["green"] if is_emerged else C["text_dim"]
            if item := self._table.item(row, 2):
                item.setText(emerged_text)
                item.setForeground(QColor(emerged_color))

            if bar := self._bars.get(eid):
                bar.setValue(int(signal * 100))
                bar.setStyleSheet(self._bar_style(signal))

            if item := self._table.item(row, 4):
                item.setText(f"{signal:.2f}")
                item.setForeground(QColor(color))


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 2 — EMERGENCE ENGINE
# ════════════════════════════════════════════════════════════════════════════════

class EmergenceDock(BaseDock):
    DOCK_TITLE = "◎  EMERGENCE ENGINE"

    def _build(self):
        self._layout.addWidget(_section_label("SIGNAL STRENGTHS  ·  THRESHOLD  ·  DOMAIN KEYWORDS"))

        # Stats row
        stats = QWidget()
        sl = QHBoxLayout(stats)
        sl.setContentsMargins(8, 6, 8, 6)
        sl.setSpacing(24)

        self._lbl_threshold = _value_label(f"Threshold: {EMERGENCE_THRESHOLD:.1f}", C["aureate"])
        self._lbl_max       = _value_label(f"Max signal: {MAX_SIGNAL:.1f}", C["text_dim"])
        self._lbl_emerged_n = _value_label("Emerged: —", C["green"])
        self._lbl_records   = _value_label("Reflection records: —", C["text_dim"])

        for w in [self._lbl_threshold, self._lbl_max, self._lbl_emerged_n, self._lbl_records]:
            sl.addWidget(w)
        sl.addStretch()
        stats.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        self._layout.addWidget(stats)

        # Main table
        self._table = _make_table(
            ["ENTITY", "SIGNAL", "BAR", "EMERGED?", "THRESHOLD MET", "KEYWORDS"],
            stretch_col=5,
        )
        self._table.setColumnWidth(0, 150)
        self._table.setColumnWidth(1, 60)
        self._table.setColumnWidth(2, 140)
        self._table.setColumnWidth(3, 80)
        self._table.setColumnWidth(4, 110)
        self._bars: Dict[str, QProgressBar] = {}

        emerged_entities = [e for e in ALL_ENTITIES if e != "luminarious"]
        self._table.setRowCount(len(emerged_entities))
        for row, eid in enumerate(emerged_entities):
            self._table.setItem(row, 0, _cell(ENTITY_DISPLAY.get(eid, eid.upper()), C.get(eid, C["text_main"])))
            self._table.setItem(row, 1, _cell("—", C["text_dim"], Qt.AlignmentFlag.AlignCenter))

            bar = QProgressBar()
            bar.setRange(0, int(MAX_SIGNAL * 100))
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            wrapper = QWidget()
            wl = QHBoxLayout(wrapper)
            wl.setContentsMargins(4, 6, 4, 6)
            wl.addWidget(bar)
            self._table.setCellWidget(row, 2, wrapper)
            self._bars[eid] = bar

            self._table.setItem(row, 3, _cell("—", C["text_dim"], Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(row, 4, _cell("—", C["text_dim"], Qt.AlignmentFlag.AlignCenter))
            kws = ", ".join(ENTITY_DOMAINS.get(eid, []))
            self._table.setItem(row, 5, _cell(kws, C["text_dim"]))
            self._table.setRowHeight(row, 24)

        self._layout.addWidget(self._table)

        # Diag log
        self._layout.addWidget(_section_label("EMERGENCE DIAGNOSTIC LOG"))
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(120)
        self._log.setFont(QFont("monospace", 10))
        self._layout.addWidget(self._log)

        self._entity_rows = {eid: i for i, eid in enumerate([e for e in ALL_ENTITIES if e != "luminarious"])}
        self.refresh()

    def _bar_style(self, value: float) -> str:
        ratio = value / MAX_SIGNAL if MAX_SIGNAL > 0 else 0
        if ratio >= EMERGENCE_THRESHOLD / MAX_SIGNAL:
            chunk = C["green"]
        elif ratio >= 0.35:
            chunk = C["yellow"]
        else:
            chunk = C["border_hi"]
        return (
            f"QProgressBar {{ background: {C['surface']}; border: 1px solid {C['border']}; "
            f"border-radius: 2px; }}"
            f"QProgressBar::chunk {{ background: {chunk}; border-radius: 2px; }}"
        )

    def refresh(self):
        signals = _derive_signals()
        emerged = _get_emerged_set()
        records = _read_jsonl(PATHS["reflections"])
        n_records = len(records)

        self._lbl_emerged_n.setText(f"Emerged: {len(emerged)}")
        self._lbl_records.setText(f"Reflection records: {n_records}")

        for eid, row in self._entity_rows.items():
            signal = signals.get(eid, 0.0)
            is_emerged = eid in emerged
            met = signal >= EMERGENCE_THRESHOLD

            self._table.item(row, 1).setText(f"{signal:.3f}")
            self._table.item(row, 1).setForeground(QColor(C.get(eid, C["text_main"])))
            if bar := self._bars.get(eid):
                bar.setValue(int(signal * 100))
                bar.setStyleSheet(self._bar_style(signal))

            emerged_text = "YES" if is_emerged else "no"
            emerged_color = C["green"] if is_emerged else C["text_dim"]
            self._table.item(row, 3).setText(emerged_text)
            self._table.item(row, 3).setForeground(QColor(emerged_color))

            met_text = f"✓ {signal:.3f}" if met else f"✗ {signal:.3f}"
            met_color = C["green"] if met else C["text_dim"]
            self._table.item(row, 4).setText(met_text)
            self._table.item(row, 4).setForeground(QColor(met_color))

        # Diag log
        diag_lines = _read_plain_log(PATHS["emergence_diag"])
        self._log.setPlainText("\n".join(diag_lines[-60:]))
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 3 — INTERRUPTION ENGINE
# ════════════════════════════════════════════════════════════════════════════════

class InterruptionDock(BaseDock):
    DOCK_TITLE = "◈  INTERRUPTION ENGINE"

    def _build(self):
        self._layout.addWidget(_section_label("GATES  ·  DOMAIN THRESHOLD  ·  PRESENCE WEIGHTS"))

        # Config row
        cfg_row = QWidget()
        cl = QHBoxLayout(cfg_row)
        cl.setContentsMargins(8, 6, 8, 6)
        cl.setSpacing(24)
        self._lbl_domain_thresh = _value_label(f"Domain threshold: {DOMAIN_THRESHOLD:.2f}", C["aureate"])
        self._lbl_gate3 = _value_label("Gate 3 (signal): 0.3 min", C["text_dim"])
        self._lbl_last_result = _value_label("Last result: —", C["text_dim"])
        for w in [self._lbl_domain_thresh, self._lbl_gate3, self._lbl_last_result]:
            cl.addWidget(w)
        cl.addStretch()
        cfg_row.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        self._layout.addWidget(cfg_row)

        # Relationship graph
        self._layout.addWidget(_section_label("DYNAMICS — SILENCE RULES  ·  POST-SPEAK MULTIPLIERS"))
        self._rel_table = _make_table(["FROM", "TO", "RULE", "EFFECT"], stretch_col=3)
        self._rel_table.setColumnWidth(0, 130)
        self._rel_table.setColumnWidth(1, 130)
        self._rel_table.setColumnWidth(2, 110)
        self._rel_table.setMaximumHeight(220)

        rels = []
        for entity, silenced in SILENCE_RULES.items():
            for target in silenced:
                rels.append((entity, target, "SILENCE", f"After {entity} speaks, {target} silenced same turn"))
        for entity, targets in POST_SPEAK_MULTIPLIERS.items():
            for target, mult in targets.items():
                rels.append((entity, target, f"MULT ×{mult}", f"After {entity} speaks, {target} presence ×{mult} next turn"))
        rels.append(("pessimist", "speculator", "ALTERNATION", "Weighted to alternate; boost if partner spoke last"))

        self._rel_table.setRowCount(len(rels))
        for row, (frm, to, rule, effect) in enumerate(rels):
            self._rel_table.setItem(row, 0, _cell(frm.upper(), C.get(frm, C["text_mid"])))
            self._rel_table.setItem(row, 1, _cell(to.upper(), C.get(to, C["text_mid"])))
            self._rel_table.setItem(row, 2, _cell(rule, C["cyan"]))
            self._rel_table.setItem(row, 3, _cell(effect, C["text_dim"]))
            self._rel_table.setRowHeight(row, 22)
        self._layout.addWidget(self._rel_table)

        # Presence weights table
        self._layout.addWidget(_section_label("PRESENCE WEIGHTS  ·  INTERRUPTION DOMAINS"))
        self._pres_table = _make_table(["ENTITY", "WEIGHT", "DOMAIN KEYWORDS"], stretch_col=2)
        self._pres_table.setColumnWidth(0, 150)
        self._pres_table.setColumnWidth(1, 60)
        entities = [e for e in ALL_ENTITIES if e != "luminarious"]
        self._pres_table.setRowCount(len(entities))
        for row, eid in enumerate(entities):
            pres = INTERRUPTION_PRESENCE.get(eid, 0.0)
            kws = ", ".join(ENTITY_DOMAINS.get(eid, []))
            self._pres_table.setItem(row, 0, _cell(ENTITY_DISPLAY.get(eid, eid.upper()), C.get(eid, C["text_main"])))
            self._pres_table.setItem(row, 1, _cell(f"{pres:.2f}", C["aureate"], Qt.AlignmentFlag.AlignCenter))
            self._pres_table.setItem(row, 2, _cell(kws, C["text_dim"]))
            self._pres_table.setRowHeight(row, 22)
        self._layout.addWidget(self._pres_table)

        # Diag log
        self._layout.addWidget(_section_label("INTERRUPTION DIAGNOSTIC LOG"))
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(120)
        self._log.setFont(QFont("monospace", 10))
        self._layout.addWidget(self._log)

        self.refresh()

    def refresh(self):
        last = _latest_interruption_from_log()
        if last:
            self._lbl_last_result.setText(f"Last: {last[:80]}")
            self._lbl_last_result.setStyleSheet(f"color: {C['cyan']}; background: transparent;")

        lines = _read_plain_log(PATHS["interruption_diag"])
        self._log.setPlainText("\n".join(lines[-60:]))
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 4 — REFLECTION ENGINE
# ════════════════════════════════════════════════════════════════════════════════

class ReflectionDock(BaseDock):
    DOCK_TITLE = "◉  REFLECTION ENGINE"

    def _build(self):
        self._layout.addWidget(_section_label("ROUTING SIGNALS  ·  ANALYTICS"))

        # Live signal row
        sig_box = QGroupBox("LATEST ROUTING SIGNAL")
        sig_box.setMaximumHeight(130)
        sg = QGridLayout(sig_box)
        sg.setSpacing(6)
        sg.setContentsMargins(8, 12, 8, 8)

        self._lbl_topics     = _value_label("—", C["cyan"])
        self._lbl_turn_count = _value_label("—", C["text_main"])
        self._lbl_avg_len    = _value_label("—", C["text_main"])
        self._lbl_code       = _value_label("—", C["text_main"])
        self._lbl_questions  = _value_label("—", C["text_main"])
        self._lbl_sig_ts     = _value_label("—", C["text_dim"])

        for col, (label, val) in enumerate([
            ("Topics", self._lbl_topics),
            ("Turn count", self._lbl_turn_count),
            ("Avg msg len", self._lbl_avg_len),
            ("Code present", self._lbl_code),
            ("Question count", self._lbl_questions),
            ("Timestamp", self._lbl_sig_ts),
        ]):
            sg.addWidget(_dim_label(label), 0, col)
            sg.addWidget(val, 1, col)

        self._layout.addWidget(sig_box)

        # Analytics records table
        self._layout.addWidget(_section_label("SELF-ANALYTICS RECORDS"))
        self._analytics_table = _make_table(["TIMESTAMP", "MODEL", "SUGGESTIONS (PREVIEW)"], stretch_col=2)
        self._analytics_table.setColumnWidth(0, 140)
        self._analytics_table.setColumnWidth(1, 100)
        self._layout.addWidget(self._analytics_table)

        # Full text of selected analytics record
        self._layout.addWidget(_section_label("SELECTED RECORD — FULL TEXT"))
        self._detail = QPlainTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setMaximumHeight(140)
        self._detail.setFont(QFont("monospace", 10))
        self._layout.addWidget(self._detail)

        self._analytics_table.itemSelectionChanged.connect(self._on_selection)
        self._analytics_data: List[dict] = []
        self.refresh()

    def _on_selection(self):
        rows = self._analytics_table.selectedItems()
        if not rows:
            return
        row = self._analytics_table.currentRow()
        if row < len(self._analytics_data):
            rec = self._analytics_data[-(len(self._analytics_data) - row)]
            self._detail.setPlainText(rec.get("suggestions", ""))

    def refresh(self):
        sig = _latest_routing_signal()
        if sig:
            topics = ", ".join(sig.get("dominant_topics", [])) or "—"
            self._lbl_topics.setText(topics)
            self._lbl_turn_count.setText(str(sig.get("turn_count", "—")))
            avg = sig.get("message_length_avg", 0)
            self._lbl_avg_len.setText(f"{avg:.1f} words")
            code = sig.get("code_present", False)
            self._lbl_code.setText("YES" if code else "no")
            self._lbl_code.setStyleSheet(f"color: {C['green'] if code else C['text_dim']}; background: transparent;")
            self._lbl_questions.setText(str(sig.get("question_count", 0)))
            ts = sig.get("timestamp", "")[:19]
            self._lbl_sig_ts.setText(ts)

        analytics = _latest_analytics()
        self._analytics_data = analytics
        self._analytics_table.setRowCount(len(analytics))
        for row, rec in enumerate(analytics):
            ts = rec.get("ts", "")[:19]
            model = (rec.get("model") or "—").split("-")[1] if "-" in (rec.get("model") or "") else rec.get("model", "—")
            preview = (rec.get("suggestions") or "").split("\n")[0][:80]
            self._analytics_table.setItem(row, 0, _cell(ts, C["text_dim"]))
            self._analytics_table.setItem(row, 1, _cell(model, C["aureate"]))
            self._analytics_table.setItem(row, 2, _cell(preview, C["text_main"]))
            self._analytics_table.setRowHeight(row, 22)

        self._analytics_table.scrollToBottom()


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 5 — BACKGROUND ASSESSOR
# ════════════════════════════════════════════════════════════════════════════════

class AssessorDock(BaseDock):
    DOCK_TITLE = "⛨  BACKGROUND ASSESSOR"

    def _build(self):
        self._layout.addWidget(_section_label("ASSESSOR  ·  GRIMOIRE WRITER  ·  BACKGROUND CYCLE"))

        stats = QWidget()
        sl = QHBoxLayout(stats)
        sl.setContentsMargins(8, 6, 8, 6)
        sl.setSpacing(24)
        self._lbl_interval = _value_label("Interval: —", C["aureate"])
        self._lbl_grimoire  = _value_label("Grimoire entries: —", C["text_main"])
        self._lbl_last_fire = _value_label("Last fire: —", C["text_dim"])
        for w in [self._lbl_interval, self._lbl_grimoire, self._lbl_last_fire]:
            sl.addWidget(w)
        sl.addStretch()
        stats.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        self._layout.addWidget(stats)

        # Grimoire entries
        self._layout.addWidget(_section_label("GRIMOIRE ENTRIES"))
        self._grimoire_table = _make_table(["TIMESTAMP", "CONTENT PREVIEW"], stretch_col=1)
        self._grimoire_table.setColumnWidth(0, 140)
        self._grimoire_table.setMaximumHeight(180)
        self._layout.addWidget(self._grimoire_table)

        # Diag log
        self._layout.addWidget(_section_label("ASSESSOR DIAGNOSTIC LOG"))
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("monospace", 10))
        self._layout.addWidget(self._log)

        self._last_log_len = 0
        self.refresh()

    def refresh(self):
        cfg = _read_config_yaml()
        interval = cfg.get("assessor_interval_turns", "—")
        self._lbl_interval.setText(f"Fires every {interval} turns")

        entries = _grimoire_entries()
        self._lbl_grimoire.setText(f"Grimoire entries: {len(entries)}")
        self._grimoire_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            ts = str(entry.get("ts", entry.get("timestamp", "—")))[:19]
            content = str(entry.get("content", entry.get("text", "—")))[:100].replace("\n", " ")
            self._grimoire_table.setItem(row, 0, _cell(ts, C["text_dim"]))
            self._grimoire_table.setItem(row, 1, _cell(content, C["text_main"]))
            self._grimoire_table.setRowHeight(row, 22)

        lines = _read_plain_log(PATHS["assessor_diag"])
        if lines:
            self._lbl_last_fire.setText(f"Last entry: {lines[-1][:60]}")
        if len(lines) != self._last_log_len:
            self._last_log_len = len(lines)
            html = self._colorize_log(lines[-200:])
            self._log.setPlainText("\n".join(lines[-200:]))
            self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def _colorize_log(self, lines: List[str]) -> str:
        result = []
        for line in lines:
            if "ERROR" in line or "FAIL" in line:
                result.append(f'<span style="color:{C["red"]}">{line}</span>')
            elif "fired" in line.lower() or "writing" in line.lower():
                result.append(f'<span style="color:{C["green"]}">{line}</span>')
            else:
                result.append(f'<span style="color:{C["text_dim"]}">{line}</span>')
        return "<br>".join(result)


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 6 — BACKGROUND ARCHIVIST
# ════════════════════════════════════════════════════════════════════════════════

class ArchivistDock(BaseDock):
    DOCK_TITLE = "◈  BACKGROUND ARCHIVIST"

    def _build(self):
        self._layout.addWidget(_section_label("ARCHIVIST  ·  CHRONICLE WRITER  ·  BACKGROUND CYCLE"))

        stats = QWidget()
        sl = QHBoxLayout(stats)
        sl.setContentsMargins(8, 6, 8, 6)
        sl.setSpacing(24)
        self._lbl_interval = _value_label("Interval: —", C["aureate"])
        self._lbl_vectors   = _value_label("Vectors: —", C["text_main"])
        self._lbl_last_fire = _value_label("Last entry: —", C["text_dim"])
        for w in [self._lbl_interval, self._lbl_vectors, self._lbl_last_fire]:
            sl.addWidget(w)
        sl.addStretch()
        stats.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        self._layout.addWidget(stats)

        self._layout.addWidget(_section_label("ARCHIVIST DIAGNOSTIC LOG"))
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("monospace", 10))
        self._layout.addWidget(self._log)

        self._last_log_len = 0
        self.refresh()

    def refresh(self):
        cfg = _read_config_yaml()
        interval = cfg.get("archivist_interval_turns", "—")
        self._lbl_interval.setText(f"Fires every {interval} turns")
        self._lbl_vectors.setText(f"Chronicle vectors (est.): {_chronicle_vector_estimate()}")

        lines = _read_plain_log(PATHS["archivist_diag"])
        if lines:
            self._lbl_last_fire.setText(f"Last entry: {lines[-1][:60]}")
        if len(lines) != self._last_log_len:
            self._last_log_len = len(lines)
            self._log.setPlainText("\n".join(lines[-200:]))
            self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 7 — IMMUTABLE LOG
# ════════════════════════════════════════════════════════════════════════════════

class ImmutableLogDock(BaseDock):
    DOCK_TITLE = "▲  IMMUTABLE LOG"

    def _build(self):
        # Filter bar
        filter_row = QWidget()
        filter_row.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        fl = QHBoxLayout(filter_row)
        fl.setContentsMargins(8, 4, 8, 4)
        fl.setSpacing(8)

        fl.addWidget(_dim_label("Role:"))
        self._role_combo = QComboBox()
        self._role_combo.addItems(["all", "user", "assistant"])
        self._role_combo.setFixedWidth(90)
        fl.addWidget(self._role_combo)

        fl.addWidget(_dim_label("Search:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("filter content...")
        self._search.setFixedWidth(180)
        fl.addWidget(self._search)

        self._btn_refresh = QPushButton("REFRESH")
        self._btn_refresh.setFixedWidth(80)
        self._btn_refresh.clicked.connect(self.refresh)
        fl.addWidget(self._btn_refresh)

        self._lbl_count = _dim_label("0 records")
        fl.addWidget(self._lbl_count)
        fl.addStretch()

        self._layout.addWidget(filter_row)

        # Table
        self._table = _make_table(
            ["TIMESTAMP", "ROLE", "CONV ID", "MODEL", "TOKENS", "CONTENT"],
            stretch_col=5,
        )
        self._table.setColumnWidth(0, 140)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(2, 90)
        self._table.setColumnWidth(3, 110)
        self._table.setColumnWidth(4, 60)

        self._layout.addWidget(self._table)

        self._role_combo.currentIndexChanged.connect(self._apply_filter)
        self._search.textChanged.connect(self._apply_filter)
        self._all_records: List[dict] = []
        self._last_count = 0
        self.refresh()

    def _apply_filter(self):
        role_filter = self._role_combo.currentText()
        search = self._search.text().lower()
        filtered = [
            r for r in self._all_records
            if (role_filter == "all" or r.get("role") == role_filter)
            and (not search or search in (r.get("content") or "").lower()
                 or search in (r.get("conversation_id") or "").lower())
        ]
        self._render_records(filtered)

    def _render_records(self, records: List[dict]):
        self._table.setRowCount(len(records))
        for row, rec in enumerate(records):
            if "_raw" in rec:
                self._table.setItem(row, 5, _cell(rec["_raw"][:80], C["text_dim"]))
                self._table.setRowHeight(row, 22)
                continue

            ts = (rec.get("ts") or "")[:19]
            role = rec.get("role", "?")
            conv = (rec.get("conversation_id") or "")[:8]
            model_raw = rec.get("model") or ""
            model_parts = model_raw.split("-")
            model_short = model_parts[1] if len(model_parts) > 1 else model_raw[:12]
            content = (rec.get("content") or "").replace("\n", " ")[:100]
            usage = rec.get("usage") or {}
            tokens = str(usage.get("output_tokens") or usage.get("input_tokens") or "—")

            role_color = C["cyan"] if role == "user" else C["aureate"]
            self._table.setItem(row, 0, _cell(ts, C["text_dim"]))
            self._table.setItem(row, 1, _cell(role, role_color))
            self._table.setItem(row, 2, _cell(conv, C["text_dim"]))
            self._table.setItem(row, 3, _cell(model_short, C["text_mid"]))
            self._table.setItem(row, 4, _cell(tokens, C["text_dim"], Qt.AlignmentFlag.AlignRight))
            self._table.setItem(row, 5, _cell(content, C["text_main"]))
            self._table.setRowHeight(row, 22)

        self._lbl_count.setText(f"{len(records)} records")
        self._table.scrollToBottom()

    def refresh(self):
        records = _read_jsonl(PATHS["immutable"], max_lines=500)
        if len(records) != self._last_count:
            self._last_count = len(records)
            self._all_records = records
            self._apply_filter()


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 8 — CHRONICLE / MEMORY
# ════════════════════════════════════════════════════════════════════════════════

class MemoryDock(BaseDock):
    DOCK_TITLE = "◻  CHRONICLE & MEMORY"

    def _build(self):
        self._layout.addWidget(_section_label("MEMORY LAYERS  ·  DISTILLATION  ·  VECTORS"))

        # Summary stats grid
        stats = QGroupBox("CURRENT STATE")
        stats.setMaximumHeight(140)
        sg = QGridLayout(stats)
        sg.setSpacing(8)
        sg.setContentsMargins(10, 16, 10, 10)

        labels = [
            ("Grimoire entries", "grimoire"),
            ("Chronicle vectors (est.)", "vectors"),
            ("Conversations stored", "convs"),
            ("Reflection records", "reflections"),
            ("Immutable log entries", "immutable"),
            ("Vectors file size", "vec_size"),
        ]
        self._stat_values: Dict[str, QLabel] = {}
        for col, (lbl_text, key) in enumerate(labels):
            sg.addWidget(_dim_label(lbl_text), 0, col)
            v = _value_label("—", C["aureate"])
            sg.addWidget(v, 1, col)
            self._stat_values[key] = v

        self._layout.addWidget(stats)

        # Config values
        self._layout.addWidget(_section_label("MEMORY CONFIGURATION"))
        self._cfg_table = _make_table(["PARAMETER", "VALUE", "NOTES"], stretch_col=2)
        self._cfg_table.setColumnWidth(0, 220)
        self._cfg_table.setColumnWidth(1, 80)
        self._cfg_table.setMaximumHeight(220)

        cfg_rows = [
            ("short_term_max_messages",    "Max messages in short-term context"),
            ("retrieve_top_k",             "Chronicle retrieval top-K"),
            ("min_relevance_score",        "Min relevance for Chronicle hit"),
            ("assessor_interval_turns",    "Background Assessor fires every N turns"),
            ("archivist_interval_turns",   "Background Archivist fires every N turns"),
            ("distillation_threshold",     "Token threshold before distillation"),
            ("distillation_min_messages",  "Min thread length before distillation"),
            ("distillation_compress_model","Model used for distillation compression"),
            ("chronicle_auto_extract",     "Distillation feeds Chronicle"),
        ]
        self._cfg_table.setRowCount(len(cfg_rows))
        for row, (key, note) in enumerate(cfg_rows):
            self._cfg_table.setItem(row, 0, _cell(key, C["text_mid"]))
            self._cfg_table.setItem(row, 1, _cell("—", C["aureate"], Qt.AlignmentFlag.AlignCenter))
            self._cfg_table.setItem(row, 2, _cell(note, C["text_dim"]))
            self._cfg_table.setRowHeight(row, 22)
        self._cfg_rows = cfg_rows
        self._layout.addWidget(self._cfg_table)
        self.refresh()

    def refresh(self):
        grimoire_count = len(_grimoire_entries())
        vectors = _chronicle_vector_estimate()
        convs = _count_conversations()
        reflections = len(_read_jsonl(PATHS["reflections"]))
        immutable = len(_read_jsonl(PATHS["immutable"]))
        vec_size = _file_size_str(PATHS["vectors"])

        self._stat_values["grimoire"].setText(str(grimoire_count))
        self._stat_values["vectors"].setText(str(vectors))
        self._stat_values["convs"].setText(str(convs))
        self._stat_values["reflections"].setText(str(reflections))
        self._stat_values["immutable"].setText(str(immutable))
        self._stat_values["vec_size"].setText(vec_size)

        cfg = _read_config_yaml()
        for row, (key, _) in enumerate(self._cfg_rows):
            val = cfg.get(key, "—")
            if item := self._cfg_table.item(row, 1):
                item.setText(str(val))


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 9 — STORAGE STATE
# ════════════════════════════════════════════════════════════════════════════════

class StorageDock(BaseDock):
    DOCK_TITLE = "⬟  STORAGE STATE"

    def _build(self):
        self._layout.addWidget(_section_label("FILE SIZES  ·  MODIFICATION TIMES  ·  COUNTS"))

        self._table = _make_table(
            ["FILE / PATH", "EXISTS", "SIZE", "MODIFIED", "NOTES"],
            stretch_col=0,
        )
        self._table.setColumnWidth(1, 55)
        self._table.setColumnWidth(2, 90)
        self._table.setColumnWidth(3, 90)
        self._table.setColumnWidth(4, 220)

        self._file_rows = [
            ("immutable",         "Immutable message log"),
            ("reflections",       "Reflections + routing signals"),
            ("council_emerged",   "Emerged entity persistence"),
            ("vectors",           "Chronicle vector store"),
            ("grimoire",          "Grimoire JSON store"),
            ("assessor_diag",     "Assessor diagnostic log"),
            ("archivist_diag",    "Archivist diagnostic log"),
            ("emergence_diag",    "Emergence diagnostic log"),
            ("interruption_diag", "Interruption diagnostic log"),
            ("entity_memory_diag","Entity memory diagnostic log"),
            ("config",            "Application configuration"),
        ]

        self._table.setRowCount(len(self._file_rows) + 2)  # +2 for directory rows
        self._layout.addWidget(self._table)

        # Directory counts
        self._dir_rows_start = len(self._file_rows)

        self.refresh()

    def refresh(self):
        for row, (key, note) in enumerate(self._file_rows):
            path = PATHS.get(key)
            if path is None:
                continue
            exists = path.exists()
            size = _file_size_str(path) if exists else "—"
            mtime = _file_mtime_str(path) if exists else "—"
            exists_str = "✓" if exists else "✗"
            exists_color = C["green"] if exists else C["text_dim"]

            self._table.setItem(row, 0, _cell(str(path), C["text_dim"]))
            self._table.setItem(row, 1, _cell(exists_str, exists_color, Qt.AlignmentFlag.AlignCenter))
            self._table.setItem(row, 2, _cell(size, C["aureate"], Qt.AlignmentFlag.AlignRight))
            self._table.setItem(row, 3, _cell(mtime, C["text_dim"]))
            self._table.setItem(row, 4, _cell(note, C["text_dim"]))
            self._table.setRowHeight(row, 22)

        # Directories
        conv_count = _count_conversations()
        r = self._dir_rows_start
        self._table.setItem(r, 0, _cell(str(PATHS["conversations_dir"]), C["text_dim"]))
        self._table.setItem(r, 1, _cell("✓" if PATHS["conversations_dir"].exists() else "✗",
                                         C["green"] if PATHS["conversations_dir"].exists() else C["text_dim"],
                                         Qt.AlignmentFlag.AlignCenter))
        self._table.setItem(r, 2, _cell(f"{conv_count} files", C["aureate"], Qt.AlignmentFlag.AlignRight))
        self._table.setItem(r, 3, _cell("—", C["text_dim"]))
        self._table.setItem(r, 4, _cell("Stored conversations directory", C["text_dim"]))
        self._table.setRowHeight(r, 22)

        # Entity memory directory
        em_dir = ROOT / "storage/entities"
        entity_count = sum(1 for _ in em_dir.rglob("memory.json")) if em_dir.exists() else 0
        r2 = self._dir_rows_start + 1
        self._table.setItem(r2, 0, _cell(str(em_dir), C["text_dim"]))
        self._table.setItem(r2, 1, _cell("✓" if em_dir.exists() else "✗",
                                          C["green"] if em_dir.exists() else C["text_dim"],
                                          Qt.AlignmentFlag.AlignCenter))
        self._table.setItem(r2, 2, _cell(f"{entity_count} memory files", C["aureate"], Qt.AlignmentFlag.AlignRight))
        self._table.setItem(r2, 3, _cell("—", C["text_dim"]))
        self._table.setItem(r2, 4, _cell("Entity private memory files", C["text_dim"]))
        self._table.setRowHeight(r2, 22)


# ════════════════════════════════════════════════════════════════════════════════
#  PANEL 10 — RAW LOG VIEWER
# ════════════════════════════════════════════════════════════════════════════════

class RawLogDock(BaseDock):
    DOCK_TITLE = "⬠  RAW LOG VIEWER"

    LOG_SOURCES = {
        "assessor_diag":     ("plain", PATHS["assessor_diag"]),
        "archivist_diag":    ("plain", PATHS["archivist_diag"]),
        "emergence_diag":    ("plain", PATHS["emergence_diag"]),
        "interruption_diag": ("plain", PATHS["interruption_diag"]),
        "entity_memory_diag":("plain", PATHS["entity_memory_diag"]),
        "immutable.jsonl":   ("jsonl",  PATHS["immutable"]),
        "reflections.jsonl": ("jsonl",  PATHS["reflections"]),
    }

    def _build(self):
        ctrl = QWidget()
        ctrl.setStyleSheet(f"background: {C['umbra']}; border-bottom: 1px solid {C['border']};")
        cl = QHBoxLayout(ctrl)
        cl.setContentsMargins(8, 4, 8, 4)
        cl.setSpacing(8)

        cl.addWidget(_dim_label("Source:"))
        self._source_combo = QComboBox()
        for key in self.LOG_SOURCES:
            self._source_combo.addItem(key)
        self._source_combo.setFixedWidth(200)
        cl.addWidget(self._source_combo)

        cl.addWidget(_dim_label("Search:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("filter lines...")
        self._search.setFixedWidth(180)
        cl.addWidget(self._search)

        self._tail_check = QCheckBox("Tail")
        self._tail_check.setChecked(True)
        self._tail_check.setStyleSheet(f"color: {C['text_dim']};")
        cl.addWidget(self._tail_check)

        self._btn_load = QPushButton("LOAD")
        self._btn_load.setFixedWidth(70)
        self._btn_load.clicked.connect(self._load_source)
        cl.addWidget(self._btn_load)

        self._lbl_lines = _dim_label("—")
        cl.addWidget(self._lbl_lines)
        cl.addStretch()

        self._layout.addWidget(ctrl)

        self._viewer = QPlainTextEdit()
        self._viewer.setReadOnly(True)
        self._viewer.setFont(QFont("monospace", 10))
        self._viewer.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._layout.addWidget(self._viewer)

        self._source_combo.currentIndexChanged.connect(self._load_source)
        self._search.returnPressed.connect(self._load_source)
        self._last_source_len: Dict[str, int] = {}
        self._load_source()

    def _load_source(self):
        key = self._source_combo.currentText()
        if key not in self.LOG_SOURCES:
            return
        fmt, path = self.LOG_SOURCES[key]
        search = self._search.text().lower()

        if fmt == "plain":
            lines = _read_plain_log(path, max_lines=2000)
        else:
            records = _read_jsonl(path, max_lines=1000)
            lines = [json.dumps(r, ensure_ascii=False) for r in records]

        if search:
            lines = [l for l in lines if search in l.lower()]

        self._lbl_lines.setText(f"{len(lines)} lines")
        self._viewer.setPlainText("\n".join(lines))

        if self._tail_check.isChecked():
            self._viewer.verticalScrollBar().setValue(
                self._viewer.verticalScrollBar().maximum()
            )

    def refresh(self):
        key = self._source_combo.currentText()
        if key not in self.LOG_SOURCES:
            return
        fmt, path = self.LOG_SOURCES[key]

        if fmt == "plain":
            current_len = len(_read_plain_log(path))
        else:
            current_len = len(_read_jsonl(path))

        if current_len != self._last_source_len.get(key, -1):
            self._last_source_len[key] = current_len
            self._load_source()


# ════════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ════════════════════════════════════════════════════════════════════════════════

class OculusPrimeWindow(QMainWindow):
    SETTINGS_ORG  = "ArcaCognitorium"
    SETTINGS_APP  = "OculusPrime"
    REFRESH_MS    = 2000

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⛨  OCULUS PRIME  ·  Arca Cognitorium Control Panel")
        self.setMinimumSize(QSize(1200, 700))

        self._panels: List[BaseDock] = []
        self._build_docks()
        self._build_toolbar()
        self._build_statusbar()
        self._restore_layout()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.REFRESH_MS)

        self._tick_count = 0

    # ── Construction ──────────────────────────────────────────────────────────

    def _build_docks(self):
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks |
            QMainWindow.DockOption.AnimatedDocks
        )

        self._dock_council      = CouncilDock(self)
        self._dock_emergence    = EmergenceDock(self)
        self._dock_interruption = InterruptionDock(self)
        self._dock_reflection   = ReflectionDock(self)
        self._dock_assessor     = AssessorDock(self)
        self._dock_archivist    = ArchivistDock(self)
        self._dock_immutable    = ImmutableLogDock(self)
        self._dock_memory       = MemoryDock(self)
        self._dock_storage      = StorageDock(self)
        self._dock_rawlog       = RawLogDock(self)

        self._panels = [
            self._dock_council,
            self._dock_emergence,
            self._dock_interruption,
            self._dock_reflection,
            self._dock_assessor,
            self._dock_archivist,
            self._dock_immutable,
            self._dock_memory,
            self._dock_storage,
            self._dock_rawlog,
        ]

        # Default layout: left column, right column, bottom row
        L = Qt.DockWidgetArea.LeftDockWidgetArea
        R = Qt.DockWidgetArea.RightDockWidgetArea
        B = Qt.DockWidgetArea.BottomDockWidgetArea

        self.addDockWidget(L, self._dock_council)
        self.addDockWidget(L, self._dock_emergence)
        self.tabifyDockWidget(self._dock_council, self._dock_emergence)

        self.addDockWidget(L, self._dock_interruption)
        self.addDockWidget(L, self._dock_reflection)
        self.tabifyDockWidget(self._dock_interruption, self._dock_reflection)

        self.addDockWidget(R, self._dock_assessor)
        self.addDockWidget(R, self._dock_archivist)
        self.tabifyDockWidget(self._dock_assessor, self._dock_archivist)

        self.addDockWidget(R, self._dock_memory)
        self.addDockWidget(R, self._dock_storage)
        self.tabifyDockWidget(self._dock_memory, self._dock_storage)

        self.addDockWidget(B, self._dock_immutable)
        self.addDockWidget(B, self._dock_rawlog)
        self.tabifyDockWidget(self._dock_immutable, self._dock_rawlog)

        # Raise first tab in each group
        self._dock_council.raise_()
        self._dock_interruption.raise_()
        self._dock_assessor.raise_()
        self._dock_memory.raise_()
        self._dock_immutable.raise_()

        # Central placeholder
        central = QWidget()
        central.setStyleSheet(f"background: {C['void']};")
        central.setMaximumWidth(1)
        self.setCentralWidget(central)

    def _build_toolbar(self):
        tb = QToolBar("Controls")
        tb.setMovable(False)
        tb.setFloatable(False)

        title = QLabel("  ⛨  OCULUS PRIME  ")
        title.setStyleSheet(
            f"color: {C['aureate']}; font-size: 13px; font-weight: bold; "
            f"letter-spacing: 3px; background: transparent;"
        )
        tb.addWidget(title)

        sep = QLabel("  ·  ")
        sep.setStyleSheet(f"color: {C['text_dim']}; background: transparent;")
        tb.addWidget(sep)

        refresh_btn = QPushButton("⟳  REFRESH NOW")
        refresh_btn.clicked.connect(self._refresh_all)
        tb.addWidget(refresh_btn)

        tb.addSeparator()

        self._interval_combo = QComboBox()
        self._interval_combo.addItems(["1s", "2s", "5s", "10s", "30s"])
        self._interval_combo.setCurrentIndex(1)
        self._interval_combo.setFixedWidth(70)
        self._interval_combo.currentIndexChanged.connect(self._change_interval)
        interval_label = _dim_label("  Interval: ")
        tb.addWidget(interval_label)
        tb.addWidget(self._interval_combo)

        tb.addSeparator()

        # Panel visibility toggles
        for dock in self._panels:
            action = dock.toggleViewAction()
            action.setText(dock.DOCK_TITLE.split("  ", 1)[-1])
            tb.addAction(action)

        tb.addSeparator()

        reset_btn = QPushButton("RESET LAYOUT")
        reset_btn.clicked.connect(self._reset_layout)
        tb.addWidget(reset_btn)

        self.addToolBar(tb)

    def _build_statusbar(self):
        self._statusbar = QStatusBar()
        self._statusbar.setStyleSheet(
            f"background: {C['umbra']}; color: {C['text_dim']}; font-size: 10px;"
        )
        self.setStatusBar(self._statusbar)
        self._lbl_tick    = QLabel("tick: 0")
        self._lbl_ts      = QLabel("")
        self._lbl_root    = QLabel(f"root: {ROOT.absolute()}")
        self._lbl_emerged = QLabel("emerged: —")

        for lbl in [self._lbl_tick, self._lbl_ts, self._lbl_root, self._lbl_emerged]:
            lbl.setStyleSheet(f"color: {C['text_dim']}; padding: 0 8px;")
            self._statusbar.addPermanentWidget(lbl)

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _tick(self):
        self._tick_count += 1
        self._refresh_all()
        ts = datetime.now().strftime("%H:%M:%S")
        self._lbl_tick.setText(f"tick: {self._tick_count}")
        self._lbl_ts.setText(ts)
        emerged = _get_emerged_set()
        self._lbl_emerged.setText(f"emerged: {len(emerged)}  [{', '.join(sorted(emerged)[:4])}{'…' if len(emerged) > 4 else ''}]")

    def _refresh_all(self):
        for panel in self._panels:
            if not panel.isHidden():
                panel.refresh()

    def _change_interval(self):
        text = self._interval_combo.currentText()
        ms = int(text.rstrip("s")) * 1000
        self._timer.setInterval(ms)

    # ── Layout persistence ────────────────────────────────────────────────────

    def _restore_layout(self):
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        geometry = settings.value("geometry")
        state    = settings.value("windowState")
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)

    def _save_layout(self):
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.setValue("geometry",    self.saveGeometry())
        settings.setValue("windowState", self.saveState())

    def _reset_layout(self):
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.remove("geometry")
        settings.remove("windowState")
        self._statusbar.showMessage("Layout reset — restart to apply default positions.", 4000)

    def closeEvent(self, event):
        self._save_layout()
        super().closeEvent(event)


# ════════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

def main():
    # Locate project root
    if Path("config.yaml").exists():
        pass
    elif Path("../config.yaml").exists():
        os.chdir("..")
    else:
        print("ERROR: Run from the ArcaCognitorium project root.", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Oculus Prime")
    app.setOrganizationName("ArcaCognitorium")
    app.setStyle("Fusion")
    _apply_app_palette(app)
    app.setStyleSheet(GLOBAL_QSS)

    window = OculusPrimeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
