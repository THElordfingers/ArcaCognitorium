# Departamentum Documentalis · propagatio_engine.py · v1.1
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QProgressBar, QHeaderView)
from PyQt6.QtCore import QThreadPool
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.propagatio_worker import PropagatioBatchWorker

class PropagatiEngine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build_ui(); self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        hdr = QHBoxLayout(); hdr.addWidget(QLabel("PROPAGATIO ENGINE")); hdr.addStretch()
        br = QPushButton("REFRESH"); br.clicked.connect(self.refresh)
        self._btn_run = QPushButton("RUN BATCH MIGRATION")
        self._btn_run.clicked.connect(self._run_batch)
        hdr.addWidget(br); hdr.addWidget(self._btn_run); layout.addLayout(hdr)
        self._prog = QProgressBar(); self._prog.setVisible(False); layout.addWidget(self._prog)
        self._status = QLabel("")
        self._status.setStyleSheet("color:#555566;font-size:9px;"); layout.addWidget(self._status)
        self._tbl = QTableWidget(0, 5)
        self._tbl.setHorizontalHeaderLabels(
            ["Queue ID","Archive ID","Target Forma","Status","Queued"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._tbl.horizontalHeader().setStretchLastSection(True)
        self._tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tbl)

    def refresh(self):
        rows = db.fetch_all("SELECT * FROM propagatio_queue ORDER BY queued_at DESC LIMIT 200")
        self._tbl.setRowCount(0)
        for r in rows:
            row = self._tbl.rowCount(); self._tbl.insertRow(row)
            self._tbl.setItem(row, 0, QTableWidgetItem(r["queue_id"][:8]+"…"))
            self._tbl.setItem(row, 1, QTableWidgetItem(r["archive_id"][:8]+"…"))
            forma = db.get_forma(r["target_forma_id"])
            self._tbl.setItem(row, 2, QTableWidgetItem(
                forma["name"] if forma else r["target_forma_id"][:8]))
            self._tbl.setItem(row, 3, QTableWidgetItem(r["status"]))
            self._tbl.setItem(row, 4, QTableWidgetItem(r["queued_at"]))

    def _run_batch(self):
        self._btn_run.setEnabled(False); self._prog.setVisible(True); self._prog.setValue(0)
        w = PropagatioBatchWorker()
        w.signals.progress.connect(lambda c, t: self._prog.setValue(int(c/t*100) if t else 0))
        w.signals.finished.connect(self._on_done)
        QThreadPool.globalInstance().start(w)

    def _on_done(self, ok, fail):
        self._btn_run.setEnabled(True); self._prog.setVisible(False)
        self._status.setText(f"Complete — {ok} succeeded · {fail} failed"); self.refresh()
