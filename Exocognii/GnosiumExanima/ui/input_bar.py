# GNOSIUM EXANIMA — ui/input_bar.py
# v1.0.0
"""Text input + send button."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QWidget

from ..constants import (
    C_BG, C_GOLD, C_GOLD_DARK, C_GOLD_DIM, C_PANEL, C_TEXT,
)


class InputBar(QWidget):
    """Text entry + Send. Emits submitted(str)."""

    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_BG};")
        self.setFixedHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        self._editor = QTextEdit()
        self._editor.setFont(QFont("Georgia", 10))
        self._editor.setPlaceholderText("Speak to the Chamber…")
        self._editor.setStyleSheet(
            f"QTextEdit {{ background: {C_PANEL}; color: {C_TEXT}; "
            f"border: 1px solid {C_GOLD_DARK}; padding: 6px; }}"
        )
        layout.addWidget(self._editor, 1)

        self._send = QPushButton("Send")
        self._send.setFont(QFont("Cinzel", 10))
        self._send.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send.setFixedWidth(96)
        self._send.setStyleSheet(
            f"QPushButton {{ background: {C_PANEL}; color: {C_GOLD}; "
            f"border: 1px solid {C_GOLD_DARK}; letter-spacing: 2px; padding: 6px; }}"
            f"QPushButton:hover {{ background: {C_GOLD_DARK}; }}"
            f"QPushButton:disabled {{ color: {C_GOLD_DIM}; }}"
        )
        self._send.clicked.connect(self._submit)
        layout.addWidget(self._send)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._submit)

    # ── API ──────────────────────────────────────────────────────
    def set_enabled(self, enabled: bool) -> None:
        self._editor.setEnabled(enabled)
        self._send.setEnabled(enabled)

    def set_focus(self) -> None:
        self._editor.setFocus()

    def _submit(self) -> None:
        text = self._editor.toPlainText().strip()
        if not text:
            return
        self._editor.clear()
        self.submitted.emit(text)
