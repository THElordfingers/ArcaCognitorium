"""
Armarium Componentium — Component Library feature page.

Full canvas with table, filters (category, theme_designator), search.
Seal/Load/Fork/Export operations.
"""
from __future__ import annotations

import json
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QLineEdit, QTableView, QHeaderView,
    QInputDialog, QMessageBox,
)

from ... import tokens
from .armarium_db import ArmariumDB
from ...nuntius_emit import emit_event


class ArmariumFeature(QWidget):
    """Armarium Componentium feature page."""

    load_to_canvas = pyqtSignal(str)   # design_json to load
    export_code = pyqtSignal(str)      # design_json to export

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = ArmariumDB()
        self._build_ui()
        self.refresh_table()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        header = QLabel("ARMARIUM COMPONENTIUM")
        header.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(header)

        # Filters
        filter_row = QHBoxLayout()
        self._cat_filter = QComboBox()
        self._cat_filter.addItem("All Categories")
        for cat in self._db.categories():
            self._cat_filter.addItem(cat)
        self._cat_filter.currentTextChanged.connect(lambda _: self.refresh_table())

        self._theme_filter = QComboBox()
        self._theme_filter.addItem("All Themes")
        self._theme_filter.addItem("Nox Aurum")
        self._theme_filter.addItem("default")
        self._theme_filter.currentTextChanged.connect(lambda _: self.refresh_table())

        self._search = QLineEdit()
        self._search.setPlaceholderText("Quaere...")
        self._search.textChanged.connect(lambda _: self.refresh_table())

        filter_row.addWidget(self._cat_filter)
        filter_row.addWidget(self._theme_filter)
        filter_row.addWidget(self._search)
        layout.addLayout(filter_row)

        # Table
        self._table = QTableView()
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["#", "Name", "Category", "Version", "Theme", "Actions"])
        self._table.setModel(self._model)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, 1)

        # Footer
        footer = QHBoxLayout()
        self._count_label = QLabel("0 componentes")
        self._count_label.setStyleSheet(
            f"font-size: 8.5px; color: {tokens.C_GOLD_DIM}; font-family: {tokens.FONT_MONO};"
        )
        footer.addWidget(self._count_label)
        footer.addStretch()
        layout.addLayout(footer)

    def refresh_table(self) -> None:
        cat = self._cat_filter.currentText()
        if cat == "All Categories":
            cat = ""
        theme = self._theme_filter.currentText()
        if theme == "All Themes":
            theme = ""
        search = self._search.text().strip()

        records = self._db.list_all(category=cat, theme=theme, search=search)
        self._model.setRowCount(0)

        for i, rec in enumerate(records):
            self._model.appendRow([
                QStandardItem(str(rec.id)),
                QStandardItem(rec.name),
                QStandardItem(rec.category),
                QStandardItem(f"v{rec.version}"),
                QStandardItem(rec.theme_designator),
                QStandardItem(""),  # Actions handled via button delegate (simplified)
            ])

        self._count_label.setText(
            f"{len(records)} componentes \u00b7 involucrum_id field reserved"
        )

    def seal_canvas(self, design_json: str, theme: str = "Nox Aurum", thumbnail: bytes | None = None) -> None:
        """Seal current canvas as a library component."""
        name, ok = QInputDialog.getText(self, "Sigilla", "Component name:")
        if not ok or not name.strip():
            return
        cat, ok = QInputDialog.getItem(
            self, "Categoria", "Category:",
            self._db.categories() + ["(new...)"], 0, False,
        )
        if not ok:
            return
        if cat == "(new...)":
            cat, ok = QInputDialog.getText(self, "Nova Categoria", "Category name:")
            if not ok or not cat.strip():
                return

        self._db.seal(name.strip(), cat.strip(), design_json, theme, thumbnail)
        self.refresh_table()

        emit_event("component_sealed", {
            "name": name.strip(),
            "category": cat.strip(),
            "theme_designator": theme,
        })

    def load_selected(self) -> None:
        idx = self._table.currentIndex()
        if not idx.isValid():
            return
        comp_id = int(self._model.item(idx.row(), 0).text())
        rec = self._db.load(comp_id)
        if rec:
            self.load_to_canvas.emit(rec.design_json)

    def fork_selected(self) -> None:
        idx = self._table.currentIndex()
        if not idx.isValid():
            return
        comp_id = int(self._model.item(idx.row(), 0).text())
        new_id = self._db.fork(comp_id)
        if new_id:
            self.refresh_table()

    def export_selected(self) -> None:
        idx = self._table.currentIndex()
        if not idx.isValid():
            return
        comp_id = int(self._model.item(idx.row(), 0).text())
        rec = self._db.load(comp_id)
        if rec:
            self._db.log_export(comp_id, "clipboard")
            self.export_code.emit(rec.design_json)
