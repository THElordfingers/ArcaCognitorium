"""
Thema — Theme Management Workspace.

Full workspace (not dropdown). Token registry table with swatches.
Load theme.json, Apply & Repaint, Reset to defaults.
Bureau II never writes theme.json — read-only dependency.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView,
)

from ... import tokens
from ...theme_manager import ThemeManager


class _SwatchWidget(QFrame):
    """A colour swatch box."""

    def __init__(self, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(120, 12)
        self.set_color(color)

    def set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"background: {color}; border: 1px solid rgba(255,255,255,0.05);"
        )


class ThemaFeature(QWidget):
    """Thema feature page."""

    theme_applied = pyqtSignal(dict)   # new token dict
    theme_reset = pyqtSignal()

    def __init__(self, theme_manager: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tm = theme_manager
        self._swatches: dict[str, _SwatchWidget] = {}
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        self._header = QLabel()
        self._header.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(self._header)

        # File path row
        path_row = QHBoxLayout()
        self._path_input = QLineEdit("~/.arca/themes/nox_aurum.json")
        self._path_input.setMaximumWidth(340)
        load_btn = QPushButton("Onus Novum")
        load_btn.clicked.connect(self._browse_theme)
        path_row.addWidget(self._path_input)
        path_row.addWidget(load_btn)
        path_row.addStretch()
        layout.addLayout(path_row)

        # Token registry label
        reg_label = QLabel("REGISTRUM TOKENORUM")
        reg_label.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO}; margin-top: 8px;"
        )
        layout.addWidget(reg_label)

        # Token table
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Token", "Value", "Swatch"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table, 1)

        # Footer note
        note = QLabel("Bureau I writes. Bureau II reads. This is constitutional, not collegial.")
        note.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; font-style: italic; "
            f"font-family: {tokens.FONT_MONO}; border-top: 1px solid {tokens.C_GOLD_DARK}; "
            f"padding-top: 6px; margin-top: 4px;"
        )
        layout.addWidget(note)

    def _refresh_table(self) -> None:
        self._header.setText(
            f"Thema \u00b7 Activum: {self._tm.theme_name} \u00b7 Auctor: Bureau I"
        )
        tok = self._tm.active_tokens
        self._table.setRowCount(len(tokens.TOKEN_NAMES))
        self._swatches.clear()

        for i, name in enumerate(tokens.TOKEN_NAMES):
            val = tok.get(name, "#000000")

            token_item = QTableWidgetItem(name)
            token_item.setForeground(QColor(tokens.C_GOLD))
            self._table.setItem(i, 0, token_item)

            value_item = QTableWidgetItem(val)
            value_item.setForeground(QColor(tokens.C_GOLD_DIM))
            self._table.setItem(i, 1, value_item)

            swatch = _SwatchWidget(val)
            self._swatches[name] = swatch
            self._table.setCellWidget(i, 2, swatch)

    def load_theme(self) -> None:
        """Load theme from the path input."""
        path = Path(self._path_input.text().strip()).expanduser()
        success, msg = self._tm.load_theme(path)
        if success:
            self._refresh_table()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Theme Error", msg)

    def apply_and_repaint(self) -> None:
        """Apply current theme and emit signal."""
        self.theme_applied.emit(self._tm.active_tokens)

    def reset_theme(self) -> None:
        """Reset to ModusArcanus defaults."""
        self._tm.reset_to_defaults()
        self._refresh_table()
        self.theme_reset.emit()

    def _browse_theme(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Onus theme.json", "", "JSON (*.json)"
        )
        if path:
            self._path_input.setText(path)
            success, msg = self._tm.load_theme(Path(path))
            if success:
                self._refresh_table()
