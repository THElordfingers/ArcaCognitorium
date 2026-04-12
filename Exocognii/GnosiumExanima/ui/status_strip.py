# GNOSIUM EXANIMA — ui/status_strip.py
# v1.0.0
"""Bottom status strip: Mundana state + service status + token count."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from ..constants import (
    C_BG, C_GOLD, C_GOLD_DARK, C_GOLD_DIM, C_PANEL, C_TEXT,
)


class StatusStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: {C_PANEL}; border-top: 1px solid {C_GOLD_DARK};"
        )
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(16)

        self._mundana = self._label("Mundana: disconnected")
        self._services = self._label("Services: unknown")
        self._tokens = self._label("Tokens: 0")

        layout.addWidget(self._mundana)
        layout.addWidget(self._sep())
        layout.addWidget(self._services)
        layout.addStretch(1)
        layout.addWidget(self._tokens)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Georgia", 9))
        lbl.setStyleSheet(f"color: {C_GOLD_DIM};")
        return lbl

    def _sep(self) -> QLabel:
        sep = QLabel("·")
        sep.setStyleSheet(f"color: {C_GOLD_DARK};")
        return sep

    # ── API ──────────────────────────────────────────────────────
    def set_mundana_state(self, text: str, connected: bool) -> None:
        colour = C_GOLD if connected else C_GOLD_DIM
        self._mundana.setText(f"Mundana: {text}")
        self._mundana.setStyleSheet(f"color: {colour};")

    def set_services_state(self, text: str) -> None:
        self._services.setText(f"Services: {text}")

    def set_token_count(self, count: int) -> None:
        self._tokens.setText(f"Tokens: {count}")
