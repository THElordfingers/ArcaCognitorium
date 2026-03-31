# Agentia Architecturalis — theme_loader.py
# v1.0.0
"""Load and validate theme.json from Bureau I."""

import json
from pathlib import Path

from .constants import MODUS_ARCANUS_DEFAULTS, TOKEN_NAMES, FONT_STACK

REQUIRED_TOKENS = TOKEN_NAMES

_active_tokens: dict = dict(MODUS_ARCANUS_DEFAULTS)
_active_designator: str | None = None


def load_theme(path: Path) -> dict:
    """Load and validate a theme.json file. Returns tokens dict."""
    if not path.exists():
        raise FileNotFoundError(f"Theme not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    errors = validate_theme(data)
    if errors:
        raise ValueError(f"Invalid theme: {'; '.join(errors)}")

    global _active_tokens, _active_designator
    _active_tokens = dict(data['tokens'])
    _active_designator = data.get('designator')
    return _active_tokens


def validate_theme(data: dict) -> list[str]:
    """Check theme.json against required structure. Returns error list."""
    errors = []
    if 'tokens' not in data:
        errors.append("Missing 'tokens' section")
        return errors
    tokens = data['tokens']
    for key in REQUIRED_TOKENS:
        if key not in tokens:
            errors.append(f"Missing key 'tokens.{key}'")
    return errors


def get_active_tokens() -> dict:
    """Return currently loaded tokens, or defaults if none loaded."""
    return dict(_active_tokens)


def get_active_designator() -> str | None:
    return _active_designator


def reset_to_defaults():
    """Reset to ModusArcanus defaults."""
    global _active_tokens, _active_designator
    _active_tokens = dict(MODUS_ARCANUS_DEFAULTS)
    _active_designator = None


def generate_qss(tokens: dict) -> str:
    """Generate complete QSS from token dict — matches Bureau I output."""
    t = tokens
    return f"""
    QMainWindow, QWidget {{
        background-color: {t['c_bg']};
        color: {t['c_text']};
        font-family: {FONT_STACK};
    }}
    QFrame {{ background-color: transparent; }}
    QPushButton {{
        background: {t['c_panel']}; color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']};
        font-family: Georgia, serif; font-size: 11px;
        padding: 6px 14px; letter-spacing: 1px;
    }}
    QPushButton:hover {{ background: {t['c_gold_dark']}; border-color: {t['c_gold']}; }}
    QPushButton:pressed {{ background: {t['c_subtle']}; }}
    QPushButton:disabled {{ color: {t['c_gold_dark']}; border-color: {t['c_subtle']}; }}
    QPushButton[accent="teal"] {{ color: {t['c_teal']}; border-color: {t['c_teal']}; }}
    QPushButton[accent="crimson"] {{ color: {t['c_crimson']}; border-color: {t['c_crimson']}; }}
    QLabel {{ color: {t['c_text']}; font-family: Georgia, serif; background: transparent; }}
    QLabel[role="title"] {{ color: {t['c_gold']}; font-weight: bold; font-size: 14px; }}
    QLabel[role="micro"] {{ color: {t['c_gold_dim']}; font-size: 9px; letter-spacing: 2px; }}
    QLabel[role="dim"] {{ color: {t['c_gold_dim']}; font-size: 10px; }}
    QLineEdit {{
        background: {t['c_bg']}; color: {t['c_text']};
        border: 1px solid {t['c_subtle']}; padding: 6px;
        font-family: Georgia, serif; font-size: 11px;
    }}
    QLineEdit:focus {{ border-color: {t['c_gold']}; color: {t['c_white']}; }}
    QSlider::groove:horizontal {{ background: {t['c_subtle']}; height: 4px; }}
    QSlider::handle:horizontal {{ background: {t['c_gold']}; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }}
    QSlider::sub-page:horizontal {{ background: {t['c_gold_dim']}; }}
    QComboBox {{ background: {t['c_bg']}; color: {t['c_gold']}; border: 1px solid {t['c_gold_dark']}; padding: 4px 8px; }}
    QComboBox QAbstractItemView {{ background: {t['c_panel']}; color: {t['c_text']}; selection-background-color: {t['c_gold_dark']}; }}
    QScrollBar:vertical {{ background: {t['c_panel']}; width: 8px; border: none; }}
    QScrollBar::handle:vertical {{ background: {t['c_gold_dark']}; border-radius: 4px; min-height: 20px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QToolTip {{ background: {t['c_panel']}; color: {t['c_gold']}; border: 1px solid {t['c_gold_dark']}; padding: 4px; }}
    QTableWidget {{ background: {t['c_bg']}; color: {t['c_text']}; gridline-color: {t['c_subtle']}; border: 1px solid {t['c_subtle']}; }}
    QHeaderView::section {{ background: {t['c_panel']}; color: {t['c_gold']}; font-weight: bold; border: 1px solid {t['c_gold_dark']}; padding: 4px; }}
    QSplitter::handle {{ background: {t['c_gold_dark']}; width: 2px; }}
    QGroupBox {{ background: {t['c_panel']}; border: 1px solid {t['c_gold_dark']}; margin-top: 12px; padding-top: 14px; }}
    QGroupBox::title {{ color: {t['c_gold']}; subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; font-size: 10px; letter-spacing: 2px; }}
    QProgressBar {{ background: {t['c_subtle']}; border: none; height: 8px; }}
    QProgressBar::chunk {{ background: {t['c_gold']}; }}
    """
