# Departamentum Documentalis — theme_loader.py
# v1.0.0
"""Bureau I theme.json consumer for GUI chrome styling."""

import json
from pathlib import Path
from .constants import MODUS_ARCANUS_DEFAULTS, TOKEN_NAMES, FONT_STACK

_active_tokens: dict = dict(MODUS_ARCANUS_DEFAULTS)
_active_designator: str | None = None


def load_theme(path: Path) -> dict:
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
    errors = []
    if 'tokens' not in data:
        errors.append("Missing 'tokens'")
        return errors
    for key in TOKEN_NAMES:
        if key not in data['tokens']:
            errors.append(f"Missing 'tokens.{key}'")
    return errors


def get_active_tokens() -> dict:
    return dict(_active_tokens)


def get_active_designator() -> str | None:
    return _active_designator


def generate_qss(tokens: dict) -> str:
    t = tokens
    return f"""
    QMainWindow, QWidget {{
        background-color: {t['c_bg']}; color: {t['c_text']};
        font-family: {FONT_STACK};
    }}
    QFrame {{ background-color: transparent; }}
    QPushButton {{
        background: {t['c_panel']}; color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']}; font-family: Georgia, serif;
        font-size: 11px; padding: 6px 14px; letter-spacing: 1px;
    }}
    QPushButton:hover {{ background: {t['c_gold_dark']}; border-color: {t['c_gold']}; }}
    QPushButton:pressed {{ background: {t['c_subtle']}; }}
    QLabel {{ color: {t['c_text']}; font-family: Georgia, serif; background: transparent; }}
    QLabel[role="title"] {{ color: {t['c_gold']}; font-weight: bold; font-size: 14px; }}
    QLabel[role="micro"] {{ color: {t['c_gold_dim']}; font-size: 9px; letter-spacing: 2px; }}
    QLabel[role="dim"] {{ color: {t['c_gold_dim']}; font-size: 10px; }}
    QPlainTextEdit {{
        background: {t['c_bg']}; color: {t['c_text']};
        border: 1px solid {t['c_subtle']}; padding: 6px;
        font-family: 'Courier New', monospace; font-size: 11px;
    }}
    QPlainTextEdit:focus {{ border-color: {t['c_gold']}; }}
    QTextEdit {{
        background: {t['c_panel']}; color: {t['c_text']};
        border: 1px solid {t['c_subtle']}; padding: 8px;
        font-family: Georgia, serif; font-size: 11px;
    }}
    QLineEdit {{
        background: {t['c_bg']}; color: {t['c_text']};
        border: 1px solid {t['c_subtle']}; padding: 6px;
        font-family: Georgia, serif; font-size: 11px;
    }}
    QLineEdit:focus {{ border-color: {t['c_gold']}; color: {t['c_white']}; }}
    QComboBox {{
        background: {t['c_bg']}; color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']}; padding: 4px 8px;
    }}
    QScrollBar:vertical {{
        background: {t['c_panel']}; width: 8px; border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {t['c_gold_dark']}; border-radius: 4px; min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QToolTip {{
        background: {t['c_panel']}; color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']}; padding: 4px;
    }}
    QSplitter::handle {{ background: {t['c_gold_dark']}; width: 2px; }}
    """
