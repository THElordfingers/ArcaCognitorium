# Departamentum Documentalis · document_archive.py · v1.1
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QHeaderView)
from PyQt6.QtCore import Qt
import DepartamentumDocumentalis.db as db

STATUS_OBJ = {
    "CURRENT": "badge_current", "VERSIO PRIOR": "badge_versio_prior",
    "ARCHIVED": "badge_archived", "ORPHANED": "badge_orphaned",
}

class DocumentArchive(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build_ui(); self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        hdr = QHBoxLayout(); hdr.addWidget(QLabel("DOCUMENT ARCHIVE")); hdr.addStretch()
        btn = QPushButton("REFRESH"); btn.clicked.connect(self.refresh); hdr.addWidget(btn)
        layout.addLayout(hdr)
        self._tbl = QTableWidget(0, 6)
        self._tbl.setHorizontalHeaderLabels(
            ["Archive ID","Doc Type","Status","Bureau","Chromaticum","Emitted"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._tbl.horizontalHeader().setStretchLastSection(True)
        self._tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tbl)

    def refresh(self):
        rows = db.get_archive(200); self._tbl.setRowCount(0)
        for r in rows:
            row = self._tbl.rowCount(); self._tbl.insertRow(row)
            self._tbl.setItem(row, 0, QTableWidgetItem(r["archive_id"][:8]+"…"))
            forma = db.get_forma(r["forma_id"])
            self._tbl.setItem(row, 1, QTableWidgetItem(
                forma["doc_type"] if forma else r["forma_id"][:8]))
            sl = QLabel(r["status"])
            sl.setObjectName(STATUS_OBJ.get(r["status"], "badge_draft"))
            sl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl.setCellWidget(row, 2, sl)
            self._tbl.setItem(row, 3, QTableWidgetItem(r["bureau_marker"] or ""))
            self._tbl.setItem(row, 4, QTableWidgetItem(r["chromaticum_name"] or ""))
            self._tbl.setItem(row, 5, QTableWidgetItem(r["emitted_at"] or ""))
