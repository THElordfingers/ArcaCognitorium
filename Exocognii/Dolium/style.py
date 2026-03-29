"""
style.py — Dolium v2
Modus Arcanus palette constants, GLOBAL_STYLE, and widget factory functions.
All visual definitions live here. No inline stylesheets in UI files.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QPushButton, QLabel, QTextEdit, QFrame, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# ── Palette ───────────────────────────────────────────────────────────────────

C_BG         = "#050507"   # Void
C_PANEL      = "#0a0a12"   # Obsidian
C_PANEL_MID  = "#0f0f1a"   # Obsidian Mid
C_GOLD       = "#d4af37"   # Aurum
C_GOLD_DIM   = "#7a6a2a"   # Aurum Dimmus
C_GOLD_DARK  = "#3a2e10"   # Aurum Nox
C_CRIMSON    = "#8b1a1a"   # Sanguis
C_TEAL       = "#1a5a5a"   # Viridis
C_TEXT       = "#c8b88a"   # Parchment
C_SUBTLE     = "#3a3528"   # Umbra
C_WHITE      = "#e8e0cc"   # Vellum
C_DIM        = "#6a5f4a"   # Penumbra
C_SUCCESS    = "#2a6a2a"   # Viridis Minor
C_ERROR      = "#8b1a1a"   # Sanguis (same as crimson, semantic alias)
C_BORDER     = "#2a2518"   # Limen


# ── Fonts ─────────────────────────────────────────────────────────────────────

FONT_SERIF   = "Georgia, Constantia, 'Times New Roman', serif"
FONT_MONO    = "'Courier New', Courier, monospace"


# ── Global Stylesheet ─────────────────────────────────────────────────────────

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
    font-size: 11px;
}}

QSplitter::handle {{
    background-color: {C_BORDER};
    width: 1px;
    height: 1px;
}}

QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical   {{ height: 1px; }}

QScrollBar:vertical {{
    background: {C_PANEL};
    width: 7px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: {C_PANEL};
    height: 7px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK};
    border-radius: 3px;
    min-width: 20px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QTextEdit {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 2px;
    padding: 6px;
    font-family: Georgia, Constantia, serif;
    font-size: 12px;
    selection-background-color: {C_GOLD_DARK};
    selection-color: {C_WHITE};
}}

QLineEdit {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 2px;
    padding: 4px 6px;
    font-family: Georgia, Constantia, serif;
    font-size: 11px;
    selection-background-color: {C_GOLD_DARK};
}}
QLineEdit:focus {{
    border-color: {C_GOLD_DIM};
}}

QPushButton {{
    background-color: {C_PANEL};
    color: {C_GOLD_DIM};
    border: 1px solid {C_BORDER};
    border-radius: 2px;
    padding: 4px 10px;
    font-family: Georgia, Constantia, serif;
    font-size: 10px;
}}
QPushButton:hover {{
    background-color: {C_GOLD_DARK};
    color: {C_GOLD};
    border-color: {C_GOLD_DIM};
}}
QPushButton:pressed {{
    background-color: {C_SUBTLE};
}}
QPushButton:disabled {{
    color: {C_SUBTLE};
    border-color: {C_SUBTLE};
}}

QTreeWidget {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    border: none;
    font-family: Georgia, Constantia, serif;
    font-size: 11px;
    outline: 0;
}}
QTreeWidget::item {{
    padding: 3px 4px;
    border: none;
}}
QTreeWidget::item:selected {{
    background-color: {C_GOLD_DARK};
    color: {C_GOLD};
}}
QTreeWidget::item:hover {{
    background-color: {C_SUBTLE};
}}
QTreeWidget QHeaderView::section {{
    background-color: {C_PANEL};
    color: {C_DIM};
    border: none;
    border-bottom: 1px solid {C_BORDER};
    padding: 3px 4px;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QDialog {{
    background-color: {C_BG};
    color: {C_TEXT};
}}

QLabel {{
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}

QStatusBar {{
    background-color: {C_PANEL};
    color: {C_DIM};
    border-top: 1px solid {C_BORDER};
    font-size: 10px;
    font-family: Georgia, Constantia, serif;
}}

QToolTip {{
    background-color: {C_PANEL_MID};
    color: {C_TEXT};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, Constantia, serif;
    font-size: 10px;
    padding: 3px 6px;
}}

QMenu {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
}}
QMenu::item:selected {{
    background-color: {C_GOLD_DARK};
    color: {C_GOLD};
}}
"""


# ── Widget Factories ──────────────────────────────────────────────────────────

def arcane_button(text: str, accent: str = C_GOLD, small: bool = False) -> QPushButton:
    """A gold-accented button. Standard UI action element."""
    btn = QPushButton(text)
    size = "9px" if small else "10px"
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_PANEL};
            color: {accent};
            border: 1px solid {C_GOLD_DARK};
            border-radius: 2px;
            padding: {'3px 7px' if small else '4px 12px'};
            font-family: Georgia, Constantia, serif;
            font-size: {size};
        }}
        QPushButton:hover {{
            background-color: {C_GOLD_DARK};
            color: {C_GOLD};
            border-color: {accent};
        }}
        QPushButton:pressed {{
            background-color: {C_SUBTLE};
        }}
        QPushButton:disabled {{
            color: {C_SUBTLE};
            border-color: {C_SUBTLE};
        }}
    """)
    return btn


def danger_button(text: str) -> QPushButton:
    """A crimson-accented button for destructive actions."""
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_PANEL};
            color: {C_CRIMSON};
            border: 1px solid {C_CRIMSON};
            border-radius: 2px;
            padding: 4px 12px;
            font-family: Georgia, Constantia, serif;
            font-size: 10px;
        }}
        QPushButton:hover {{
            background-color: {C_CRIMSON};
            color: {C_WHITE};
        }}
    """)
    return btn


def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel:
    """A gold-coloured label. Used for section headers and field labels."""
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(f"""
        QLabel {{
            color: {C_GOLD};
            font-family: Georgia, Constantia, serif;
            font-size: {size}px;
            font-weight: {weight};
        }}
    """)
    return lbl


def dim_label(text: str, size: int = 10) -> QLabel:
    """A dimmed label. Used for secondary info, counters, hints."""
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        QLabel {{
            color: {C_DIM};
            font-family: Georgia, Constantia, serif;
            font-size: {size}px;
        }}
    """)
    return lbl


def arcane_text_edit(placeholder: str = "", read_only: bool = False) -> QTextEdit:
    """The standard living text surface. Used for all idea fields."""
    edit = QTextEdit()
    if placeholder:
        edit.setPlaceholderText(placeholder)
    edit.setReadOnly(read_only)
    edit.setStyleSheet(f"""
        QTextEdit {{
            background-color: {C_PANEL};
            color: {C_TEXT};
            border: 1px solid {C_BORDER};
            border-radius: 2px;
            padding: 7px;
            font-family: Georgia, Constantia, serif;
            font-size: 12px;
            selection-background-color: {C_GOLD_DARK};
            selection-color: {C_WHITE};
        }}
        QTextEdit:focus {{
            border-color: {C_GOLD_DIM};
        }}
    """)
    return edit


def whisper_text_edit() -> QTextEdit:
    """Read-only display for ambient whisper stream. Slightly dimmer text."""
    edit = QTextEdit()
    edit.setReadOnly(True)
    edit.setStyleSheet(f"""
        QTextEdit {{
            background-color: {C_BG};
            color: {C_DIM};
            border: none;
            border-bottom: 1px solid {C_BORDER};
            padding: 7px;
            font-family: Georgia, Constantia, serif;
            font-size: 11px;
            font-style: italic;
        }}
    """)
    return edit


def conversation_text_edit() -> QTextEdit:
    """Read-only display for the conversation stream."""
    edit = QTextEdit()
    edit.setReadOnly(True)
    edit.setStyleSheet(f"""
        QTextEdit {{
            background-color: {C_BG};
            color: {C_TEXT};
            border: none;
            padding: 7px;
            font-family: Georgia, Constantia, serif;
            font-size: 11px;
        }}
    """)
    return edit


def h_rule() -> QFrame:
    """A thin horizontal rule in the Umbra colour."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {C_BORDER}; background-color: {C_BORDER}; max-height: 1px;")
    return line


def panel_frame() -> QFrame:
    """A panel container with Obsidian background and subtle border."""
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {C_PANEL};
            border: 1px solid {C_BORDER};
            border-radius: 2px;
        }}
    """)
    return frame


# ── Chamber accent colours ────────────────────────────────────────────────────

CHAMBER_ACCENTS = {
    1: C_GOLD_DIM,
    2: C_TEAL,
    3: C_GOLD,
    4: C_WHITE,
}

def chamber_accent(chamber: int) -> str:
    return CHAMBER_ACCENTS.get(chamber, C_GOLD_DIM)
