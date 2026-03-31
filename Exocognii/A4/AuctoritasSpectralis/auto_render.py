# Auctoritas Spectralis — auto_render.py
# v1.0.0
"""Live QSS generation and debounced application."""

from PyQt6.QtCore import QTimer

from .constants import MODUS_ARCANUS_DEFAULTS, FONT_STACK, FONT_STACK_MONO


class AutoRenderer:
    """Generates and applies QSS from a TokenDict on every change."""

    def __init__(self, app):
        self._app = app
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._apply)
        self._pending_tokens = None

    def schedule(self, tokens: dict) -> None:
        """Queue a re-render. Debounced at 150ms."""
        self._pending_tokens = tokens
        self._timer.start()

    def _apply(self) -> None:
        """Generate and apply QSS."""
        if self._pending_tokens is None:
            return
        try:
            qss = generate_qss(self._pending_tokens)
            self._app.setStyleSheet(qss)
        except Exception:
            # Revert to defaults on failure
            fallback = generate_qss(MODUS_ARCANUS_DEFAULTS)
            self._app.setStyleSheet(fallback)

    def apply_immediate(self, tokens: dict) -> None:
        """Apply without debounce — used on startup."""
        try:
            qss = generate_qss(tokens)
            self._app.setStyleSheet(qss)
        except Exception:
            fallback = generate_qss(MODUS_ARCANUS_DEFAULTS)
            self._app.setStyleSheet(fallback)


def generate_qss(tokens: dict) -> str:
    """Produce complete QSS string from token dict.

    Covers all ModusArcanus widget patterns with token values substituted.
    """
    t = tokens
    return f"""
    QMainWindow, QWidget {{
        background-color: {t['c_bg']};
        color: {t['c_text']};
        font-family: {FONT_STACK};
    }}
    QFrame {{
        background-color: transparent;
    }}
    QPushButton {{
        background: {t['c_panel']};
        color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']};
        font-family: Georgia, serif;
        font-size: 11px;
        padding: 6px 14px;
        letter-spacing: 1px;
    }}
    QPushButton:hover {{
        background: {t['c_gold_dark']};
        border-color: {t['c_gold']};
    }}
    QPushButton:pressed {{
        background: {t['c_subtle']};
    }}
    QPushButton:disabled {{
        color: {t['c_gold_dark']};
        border-color: {t['c_subtle']};
    }}
    QPushButton[accent="teal"] {{
        color: {t['c_teal']};
        border-color: {t['c_teal']};
    }}
    QPushButton[accent="crimson"] {{
        color: {t['c_crimson']};
        border-color: {t['c_crimson']};
    }}
    QLabel {{
        color: {t['c_text']};
        font-family: Georgia, serif;
        background: transparent;
    }}
    QLabel[role="title"] {{
        color: {t['c_gold']};
        font-weight: bold;
        font-size: 14px;
    }}
    QLabel[role="micro"] {{
        color: {t['c_gold_dim']};
        font-size: 9px;
        letter-spacing: 2px;
    }}
    QLabel[role="dim"] {{
        color: {t['c_gold_dim']};
        font-size: 10px;
    }}
    QLabel[role="emphasis"] {{
        color: {t['c_white']};
        font-weight: bold;
    }}
    QLineEdit {{
        background: {t['c_bg']};
        color: {t['c_text']};
        border: 1px solid {t['c_subtle']};
        padding: 6px;
        font-family: Georgia, serif;
        font-size: 11px;
    }}
    QLineEdit:focus {{
        border-color: {t['c_gold']};
        color: {t['c_white']};
    }}
    QSlider::groove:horizontal {{
        background: {t['c_subtle']};
        height: 4px;
    }}
    QSlider::handle:horizontal {{
        background: {t['c_gold']};
        width: 12px; height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}
    QSlider::sub-page:horizontal {{
        background: {t['c_gold_dim']};
    }}
    QComboBox {{
        background: {t['c_bg']};
        color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']};
        padding: 4px 8px;
        font-family: Georgia, serif;
    }}
    QComboBox QAbstractItemView {{
        background: {t['c_panel']};
        color: {t['c_text']};
        selection-background-color: {t['c_gold_dark']};
        selection-color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']};
    }}
    QScrollBar:vertical {{
        background: {t['c_panel']};
        width: 8px; border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {t['c_gold_dark']};
        border-radius: 4px; min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {t['c_panel']};
        height: 8px; border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {t['c_gold_dark']};
        border-radius: 4px;
    }}
    QToolTip {{
        background: {t['c_panel']};
        color: {t['c_gold']};
        border: 1px solid {t['c_gold_dark']};
        font-family: Georgia, serif;
        padding: 4px;
    }}
    QTableWidget {{
        background: {t['c_bg']};
        color: {t['c_text']};
        gridline-color: {t['c_subtle']};
        border: 1px solid {t['c_subtle']};
        font-family: Georgia, serif;
        font-size: 11px;
    }}
    QTableWidget::item {{
        padding: 4px;
    }}
    QTableWidget::item:selected {{
        background: {t['c_gold_dark']};
        color: {t['c_gold']};
    }}
    QHeaderView::section {{
        background: {t['c_panel']};
        color: {t['c_gold']};
        font-weight: bold;
        border: 1px solid {t['c_gold_dark']};
        padding: 4px;
        font-family: Georgia, serif;
        font-size: 10px;
    }}
    QSplitter::handle {{
        background: {t['c_gold_dark']};
        width: 2px;
    }}
    QDialog {{
        background: {t['c_panel']};
        border: 1px solid {t['c_gold']};
    }}
    QGroupBox {{
        background: {t['c_panel']};
        border: 1px solid {t['c_gold_dark']};
        margin-top: 12px;
        padding-top: 14px;
        font-family: Georgia, serif;
    }}
    QGroupBox::title {{
        color: {t['c_gold']};
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        font-size: 10px;
        letter-spacing: 2px;
    }}
    """
