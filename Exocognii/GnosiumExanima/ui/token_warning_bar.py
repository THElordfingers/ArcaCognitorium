# GNOSIUM EXANIMA — ui/token_warning_bar.py
# v1.0.0
"""Yellow warning bar shown when composite system prompt exceeds threshold."""

from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout

from ..constants import C_BG, C_GOLD_DARK, C_WARN, ENTITY_PANEL_WIDTH


class TokenWarningBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(ENTITY_PANEL_WIDTH)
        self.setStyleSheet(f"background: {C_BG}; border-top: 1px solid {C_GOLD_DARK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        self._label = QLabel("")
        self._label.setFont(QFont("Georgia", 8))
        self._label.setWordWrap(True)
        self._label.setStyleSheet(f"color: {C_WARN}; background: {C_BG};")
        layout.addWidget(self._label)

        self.setVisible(False)

    def show_warning(self, token_count: int, entity_count: int) -> None:
        self._label.setText(
            f"System prompt: ~{token_count} tokens "
            f"({entity_count} entities active)"
        )
        self.setVisible(True)

    def clear(self) -> None:
        self.setVisible(False)
