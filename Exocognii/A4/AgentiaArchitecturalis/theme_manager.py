"""
Theme Manager — token registry and QSS builder.

Bureau I is the sole writer of theme.json. Bureau II reads only.
This is constitutional, not collegial.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from . import tokens


class ThemeManager:
    """Loads, validates, and applies token-based themes."""

    def __init__(self) -> None:
        self._active_tokens: dict[str, str] = dict(tokens.DEFAULTS)
        self._theme_name: str = "Nox Aurum"
        self._theme_path: Optional[Path] = None

    @property
    def theme_name(self) -> str:
        return self._theme_name

    @property
    def active_tokens(self) -> dict[str, str]:
        return dict(self._active_tokens)

    def load_theme(self, path: Path) -> tuple[bool, str]:
        """Load a theme.json file. Returns (success, message)."""
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            return False, f"Failed to load theme: {e}"

        missing = [t for t in tokens.TOKEN_NAMES if t not in raw.get("tokens", {})]
        if missing:
            return False, f"Missing tokens: {', '.join(missing)}"

        self._active_tokens = {k: raw["tokens"][k] for k in tokens.TOKEN_NAMES}
        self._theme_name = raw.get("name", path.stem)
        self._theme_path = path
        return True, f"Theme '{self._theme_name}' loaded."

    def reset_to_defaults(self) -> None:
        """Reset to ModusArcanus defaults (Nox Aurum)."""
        self._active_tokens = dict(tokens.DEFAULTS)
        self._theme_name = "Nox Aurum"
        self._theme_path = None

    def build_qss(self) -> str:
        """Generate a global QSS stylesheet from active tokens."""
        t = self._active_tokens
        return f"""
        /* ── Agentia Architecturalis · ModusArcanus QSS ── */
        QMainWindow, QWidget {{
            background-color: {t['C_BG']};
            color: {t['C_TEXT']};
            font-family: {tokens.FONT_SERIF};
            font-size: 13px;
        }}
        QLabel {{
            color: {t['C_TEXT']};
            background: transparent;
        }}
        QPushButton {{
            background-color: {t['C_PANEL']};
            color: {t['C_GOLD']};
            border: 1px solid {t['C_GOLD_DARK']};
            padding: 4px 10px;
            font-family: {tokens.FONT_SERIF};
            font-size: 9px;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background-color: {t['C_GOLD_DARK']};
            border-color: {t['C_GOLD']};
        }}
        QPushButton[cssClass="teal"] {{
            color: #3aacac;
            border-color: {t['C_TEAL']};
        }}
        QPushButton[cssClass="teal"]:hover {{
            background-color: #0d3030;
        }}
        QPushButton[cssClass="crimson"] {{
            color: #c04040;
            border-color: {t['C_CRIMSON']};
        }}
        QPushButton[cssClass="crimson"]:hover {{
            background-color: #2a0808;
        }}
        QFrame {{
            background-color: {t['C_PANEL']};
            border: 1px solid {t['C_GOLD_DARK']};
        }}
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {t['C_BG']};
            color: {t['C_TEXT']};
            border: 1px solid {t['C_GOLD_DARK']};
            padding: 3px 7px;
            font-family: {tokens.FONT_MONO};
            font-size: 9px;
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border-color: {t['C_GOLD']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['C_PANEL']};
            color: {t['C_TEXT']};
            border: 1px solid {t['C_GOLD_DARK']};
            selection-background-color: {t['C_GOLD_DARK']};
            selection-color: {t['C_GOLD']};
        }}
        QScrollBar:vertical {{
            background: {t['C_BG']};
            width: 8px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {t['C_SUBTLE']};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['C_GOLD_DIM']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {t['C_BG']};
            height: 8px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background: {t['C_SUBTLE']};
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t['C_GOLD_DIM']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QTableView {{
            background-color: {t['C_BG']};
            color: {t['C_TEXT']};
            border: 1px solid {t['C_GOLD_DARK']};
            gridline-color: {t['C_SUBTLE']};
            font-family: {tokens.FONT_MONO};
            font-size: 9px;
        }}
        QTableView::item:selected {{
            background-color: {t['C_GOLD_DARK']};
            color: {t['C_GOLD']};
        }}
        QHeaderView::section {{
            background-color: {t['C_PANEL']};
            color: {t['C_GOLD_DIM']};
            border: none;
            border-bottom: 1px solid {t['C_GOLD_DARK']};
            padding: 4px 8px;
            font-size: 8px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        QSlider::groove:horizontal {{
            background: {t['C_SUBTLE']};
            height: 4px;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {t['C_GOLD']};
            width: 12px;
            height: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }}
        QProgressBar {{
            background: {t['C_BG']};
            border: 1px solid {t['C_GOLD_DARK']};
            text-align: center;
            color: {t['C_GOLD_DIM']};
            font-size: 8px;
        }}
        QProgressBar::chunk {{
            background: {t['C_GOLD_DARK']};
        }}
        QGroupBox {{
            background-color: {t['C_PANEL']};
            border: 1px solid {t['C_GOLD_DARK']};
            margin-top: 14px;
            padding-top: 8px;
            font-size: 9px;
            color: {t['C_GOLD']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }}
        QTabWidget::pane {{
            background: {t['C_PANEL']};
            border: 1px solid {t['C_GOLD_DARK']};
        }}
        QTabBar::tab {{
            background: {t['C_BG']};
            color: {t['C_GOLD_DIM']};
            border: 1px solid {t['C_GOLD_DARK']};
            padding: 4px 10px;
            font-size: 9px;
        }}
        QTabBar::tab:selected {{
            background: {t['C_GOLD_DARK']};
            color: {t['C_GOLD']};
        }}
        QSplitter::handle {{
            background: {t['C_GOLD_DARK']};
        }}
        QToolTip {{
            background-color: {t['C_PANEL']};
            color: {t['C_TEXT']};
            border: 1px solid {t['C_GOLD_DARK']};
            padding: 4px;
            font-size: 9px;
        }}
        QTextEdit, QPlainTextEdit {{
            background-color: {t['C_BG']};
            color: {t['C_TEXT']};
            border: 1px solid {t['C_GOLD_DARK']};
            font-family: {tokens.FONT_MONO};
            font-size: 10px;
        }}
        """
