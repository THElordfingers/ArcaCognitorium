# Departamentum Documentalis · mandate_bench.py · v1.2
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QComboBox, QLineEdit, QHeaderView)
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.nuntius_emit import emit_event

class MandateBench(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build_ui(); self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("MANDATE BENCH"))
        hdr.addWidget(QLabel("TEXTUS MANDATUM ORDINATIO")); hdr.addStretch()
        br = QPushButton("REFRESH"); br.clicked.connect(self.refresh); hdr.addWidget(br)
        layout.addLayout(hdr)

        layout.addWidget(QLabel("Active Mandates:"))
        self._tbl = QTableWidget(0, 3)
        self._tbl.setHorizontalHeaderLabels(["Doc Type","Mandated Forma","Set At"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._tbl.horizontalHeader().setStretchLastSection(True)
        self._tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tbl)

        layout.addWidget(QLabel("SWAP Mandate:"))
        sr = QHBoxLayout()
        self._dt = QLineEdit(); self._dt.setPlaceholderText("doc_type")
        self._forma_cb = QComboBox(); self._load_formae()
        bs = QPushButton("SWAP"); bs.clicked.connect(self._swap)
        sr.addWidget(self._dt); sr.addWidget(self._forma_cb); sr.addWidget(bs)
        layout.addLayout(sr)

        layout.addWidget(QLabel("Mandate History (append-only):"))
        self._hist = QTableWidget(0, 3)
        self._hist.setHorizontalHeaderLabels(["Doc Type","Forma","Set At"])
        self._hist.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._hist.horizontalHeader().setStretchLastSection(True)
        self._hist.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._hist)

    def _load_formae(self):
        self._forma_cb.clear()
        for f in db.get_all_formae():
            self._forma_cb.addItem(f"{f['name']} [{f['doc_type']}]", f["forma_id"])

    def refresh(self):
        rows = db.get_mandate_bench(); self._tbl.setRowCount(0)
        for r in rows:
            row = self._tbl.rowCount(); self._tbl.insertRow(row)
            self._tbl.setItem(row, 0, QTableWidgetItem(r["doc_type"]))
            self._tbl.setItem(row, 1, QTableWidgetItem(r["forma_name"]))
            self._tbl.setItem(row, 2, QTableWidgetItem(r["set_at"]))
        hist = db.fetch_all(
            "SELECT mh.*, f.name AS forma_name FROM mandate_history mh "
            "JOIN formae f ON f.forma_id = mh.forma_id ORDER BY mh.set_at DESC LIMIT 100")
        self._hist.setRowCount(0)
        for r in hist:
            row = self._hist.rowCount(); self._hist.insertRow(row)
            self._hist.setItem(row, 0, QTableWidgetItem(r["doc_type"]))
            self._hist.setItem(row, 1, QTableWidgetItem(r["forma_name"]))
            self._hist.setItem(row, 2, QTableWidgetItem(r["set_at"]))

    def _swap(self):
        doc_type = self._dt.text().strip()
        forma_id = self._forma_cb.currentData()
        if not doc_type or not forma_id: return
        existing = db.fetch_one("SELECT * FROM mandate_bench WHERE doc_type = ?", (doc_type,))
        if existing:
            archives = db.fetch_all(
                "SELECT a.* FROM archive a JOIN formae f ON f.forma_id = a.forma_id "
                "WHERE f.doc_type = ? AND a.status = 'CURRENT'", (doc_type,))
            for arch in archives:
                db.execute(
                    "INSERT INTO propagatio_queue (queue_id,archive_id,target_forma_id) "
                    "VALUES (?,?,?)",
                    (str(uuid.uuid4()), arch["archive_id"], forma_id))
            db.execute(
                "UPDATE mandate_bench SET forma_id=?,set_at=datetime('now') WHERE doc_type=?",
                (forma_id, doc_type))
        else:
            db.execute(
                "INSERT INTO mandate_bench (doc_type,forma_id) VALUES (?,?)", (doc_type, forma_id))
        db.execute(
            "INSERT INTO mandate_history (history_id,doc_type,forma_id) VALUES (?,?,?)",
            (str(uuid.uuid4()), doc_type, forma_id))
        emit_event("mandate_swap", {
            "doc_type": doc_type, "new_forma_id": forma_id})
        self.refresh(); self._dt.clear()
