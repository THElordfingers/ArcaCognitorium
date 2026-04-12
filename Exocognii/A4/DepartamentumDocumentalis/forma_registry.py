# Departamentum Documentalis · forma_registry.py · v1.1
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt
import DepartamentumDocumentalis.db as db

class FormaRegistry(QWidget):
    forma_selected      = pyqtSignal(str)
    new_forma_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_formae = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("FORMA REGISTRY")); hdr.addStretch()
        btn = QPushButton("NEW FORMA"); btn.clicked.connect(self.new_forma_requested)
        hdr.addWidget(btn); layout.addLayout(hdr)
        frow = QHBoxLayout()
        self._search = QLineEdit(); self._search.setPlaceholderText("filter...")
        self._search.textChanged.connect(self._apply_filter)
        self._status_cb = QComboBox()
        self._status_cb.addItems(["ALL", "MANDATED", "DRAFT", "ARCHIVED"])
        self._status_cb.currentTextChanged.connect(self._apply_filter)
        frow.addWidget(self._search); frow.addWidget(self._status_cb)
        layout.addLayout(frow)
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(
            lambda item: self.forma_selected.emit(item.data(Qt.ItemDataRole.UserRole)))
        layout.addWidget(self._list)

    def refresh(self):
        self._all_formae = db.get_all_formae()
        self._apply_filter()

    def _apply_filter(self):
        self._list.clear()
        q      = self._search.text().lower()
        status = self._status_cb.currentText()
        mandated = {r["forma_id"] for r in db.get_mandate_bench()}
        for f in self._all_formae:
            fs = "MANDATED" if f["forma_id"] in mandated else f["status"]
            if status != "ALL" and fs != status: continue
            if q and q not in f["name"].lower() and q not in f["doc_type"].lower(): continue
            item = QListWidgetItem(f"{f['name']}  [{f['doc_type']}]")
            item.setData(Qt.ItemDataRole.UserRole, f["forma_id"])
            self._list.addItem(item)
