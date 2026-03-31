# Auctoritas Spectralis — widgets/hex_input.py
# v1.0.0
"""Validated hex color input widget with inline swatch."""

import re

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QColorDialog,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QRegularExpressionValidator, QColor


_HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


class HexInput(QWidget):
    """Hex color input with validated QLineEdit and color picker button."""

    hex_changed = pyqtSignal(str)  # emits valid #RRGGBB

    def __init__(self, initial: str = '#000000', parent=None):
        super().__init__(parent)
        self._last_valid = initial.lower()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._edit = QLineEdit(initial)
        self._edit.setMaxLength(7)
        self._edit.setFixedWidth(90)
        validator = QRegularExpressionValidator(
            self._edit
        )
        from PyQt6.QtCore import QRegularExpression
        validator.setRegularExpression(QRegularExpression(r'^#[0-9a-fA-F]{0,6}$'))
        self._edit.setValidator(validator)
        self._edit.editingFinished.connect(self._on_edit_finished)
        layout.addWidget(self._edit)

        self._swatch = QPushButton('\u25c8')
        self._swatch.setFixedSize(28, 28)
        self._swatch.setToolTip("Pick color")
        self._swatch.clicked.connect(self._on_pick)
        self._update_swatch(initial)
        layout.addWidget(self._swatch)

    def _on_edit_finished(self):
        text = self._edit.text().strip().lower()
        if _HEX_RE.match(text):
            self._last_valid = text
            self._update_swatch(text)
            self.hex_changed.emit(text)
        else:
            # Revert to last valid value
            self._edit.setText(self._last_valid)

    def _on_pick(self):
        color = QColorDialog.getColor(
            QColor(self._last_valid),
            self,
            "Select Color"
        )
        if color.isValid():
            hex_val = color.name().lower()
            self._last_valid = hex_val
            self._edit.setText(hex_val)
            self._update_swatch(hex_val)
            self.hex_changed.emit(hex_val)

    def _update_swatch(self, hex_color: str):
        self._swatch.setStyleSheet(
            f"QPushButton {{ background: {hex_color}; color: #ffffff; "
            f"border: 1px solid #3a2e10; font-size: 14px; }}"
        )

    def set_hex(self, hex_color: str):
        """Programmatically set the hex value without emitting signal."""
        hex_color = hex_color.lower()
        if _HEX_RE.match(hex_color):
            self._last_valid = hex_color
            self._edit.setText(hex_color)
            self._update_swatch(hex_color)

    def get_hex(self) -> str:
        return self._last_valid
