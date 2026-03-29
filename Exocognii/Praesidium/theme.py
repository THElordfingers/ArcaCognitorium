"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈                  ████████ ██   ██ ███████ ███    ███ ███████ ▍
🮈                     ██    ██   ██ ██      ████  ████ ██      ▍
🮈                     ██    ███████ █████   ██ ████ ██ █████   ▍
🮈                     ██    ██   ██ ██      ██  ██  ██ ██      ▍
🮈                     ██    ██   ██ ███████ ██      ██ ███████ ▍
🮈                                                              ▍
🮈                                                              ▍
🮈           Python Script           ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮈      PRAESIDIUM · theme.py                                                       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                    theme.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · theme.py
# Colour constants, QSS factories, widget style helpers.
# version: 1.0.0
"""

from PyQt6.QtWidgets import QPushButton, QLabel

# ---------------------------------------------------------------------------
# Chromata Arcana
# ---------------------------------------------------------------------------
C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"
C_WHITE     = "#e8e0cc"

# Status dot colours
C_STATUS_OK    = "#1a9a1a"
C_STATUS_WARN  = "#d4af37"
C_STATUS_ERROR = "#8b1a1a"
C_STATUS_IDLE  = "#3a3528"

# ---------------------------------------------------------------------------
# Global stylesheet
# ---------------------------------------------------------------------------
GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QScrollBar:vertical {{
    background: {C_PANEL}; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {C_PANEL}; height: 8px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK}; border-radius: 4px;
}}
QToolTip {{
    background: {C_PANEL}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
QFrame {{
    background-color: {C_BG};
}}
"""

# ArcaneWidget QSS — applied per-instance
ARCANE_WIDGET_STYLE = f"""
ArcaneWidget {{
    background-color: {C_PANEL};
    border: 1px solid {C_GOLD_DARK};
}}
ArcaneWidget > QFrame#header_bar {{
    background-color: {C_PANEL};
    border-bottom: 1px solid {C_GOLD_DARK};
    min-height: 28px; max-height: 28px;
}}
QLabel#status_dot[status="ok"]    {{ color: {C_STATUS_OK};    font-size: 10px; }}
QLabel#status_dot[status="warn"]  {{ color: {C_STATUS_WARN};  font-size: 10px; }}
QLabel#status_dot[status="error"] {{ color: {C_STATUS_ERROR}; font-size: 10px; }}
QLabel#status_dot[status="idle"]  {{ color: {C_STATUS_IDLE};  font-size: 10px; }}
QLabel#stage_active   {{ color: {C_GOLD};     font-weight: bold;
                         border-bottom: 2px solid {C_GOLD}; }}
QLabel#stage_inactive {{ color: {C_GOLD_DIM}; }}
"""


# ---------------------------------------------------------------------------
# Widget factories
# ---------------------------------------------------------------------------

def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {C_PANEL};
            color: {accent};
            border: 1px solid {C_GOLD_DARK};
            font-family: Georgia, serif;
            font-size: 11px;
            padding: 6px 14px;
            letter-spacing: 1px;
        }}
        QPushButton:hover   {{ background: {C_GOLD_DARK}; border-color: {accent}; }}
        QPushButton:pressed {{ background: {C_SUBTLE}; }}
        QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
    """)
    return btn


def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(
        f"color: {C_GOLD}; font-family: Georgia, serif; "
        f"font-size: {size}px; font-weight: {weight};"
    )
    return lbl


def dim_label(text: str, size: int = 10) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: {size}px;"
    )
    return lbl


def micro_label(text: str) -> QLabel:
    """9px uppercase letter-spaced label — the engraved signature move."""
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
        "font-size: 9px; letter-spacing: 2px;"
    )
    return lbl

