# Departamentum Documentalis · forma_editor.py · v1.1
import uuid, json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QCheckBox, QTextEdit)
from PyQt6.QtCore import pyqtSignal
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.chromaticum_bridge import get_chromatica_list

class FormaEditor(QWidget):
    dirty_changed = pyqtSignal(bool)
    saved         = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._forma_id = None
        self._dirty = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(QLabel("FORMA EDITOR"))

        meta = QHBoxLayout()
        self._name     = QLineEdit(); self._name.setPlaceholderText("Forma name")
        self._doc_type = QLineEdit(); self._doc_type.setPlaceholderText("doc_type key")
        for w in (self._name, self._doc_type): w.textChanged.connect(self._mark_dirty)
        meta.addWidget(QLabel("Name:")); meta.addWidget(self._name)
        meta.addWidget(QLabel("Type:")); meta.addWidget(self._doc_type)
        layout.addLayout(meta)

        self._desc = QTextEdit(); self._desc.setMaximumHeight(60)
        self._desc.setPlaceholderText("Description")
        self._desc.textChanged.connect(self._mark_dirty)
        layout.addWidget(self._desc)

        crow = QHBoxLayout(); crow.addWidget(QLabel("Chromaticum:"))
        self._chrom = QComboBox(); self._chrom.currentTextChanged.connect(self._mark_dirty)
        btn_r = QPushButton("↻"); btn_r.setFixedWidth(28); btn_r.clicked.connect(self._load_chrom)
        crow.addWidget(self._chrom); crow.addWidget(btn_r); layout.addLayout(crow)

        trow = QHBoxLayout(); trow.addWidget(QLabel("Targets:"))
        self._t_md  = QCheckBox(".md");  self._t_md.setChecked(True)
        self._t_wiz = QCheckBox(".wiz")
        self._t_pdf = QCheckBox(".pdf")
        for cb in (self._t_md, self._t_wiz, self._t_pdf):
            cb.stateChanged.connect(self._mark_dirty); trow.addWidget(cb)
        layout.addLayout(trow)

        layout.addWidget(QLabel("Fields:"))
        self._tbl = QTableWidget(0, 5)
        self._tbl.setHorizontalHeaderLabels(["Name","Label","Type","Required","Fixed Value"])
        self._tbl.horizontalHeader().setStretchLastSection(True)
        self._tbl.cellChanged.connect(self._mark_dirty)
        layout.addWidget(self._tbl)

        brow = QHBoxLayout()
        ba = QPushButton("ADD FIELD");    ba.clicked.connect(lambda: self._add_row())
        br = QPushButton("REMOVE FIELD"); br.clicked.connect(self._rm_row)
        brow.addWidget(ba); brow.addWidget(br); brow.addStretch(); layout.addLayout(brow)

        sr = QHBoxLayout(); sr.addStretch()
        bs = QPushButton("SAVE FORMA"); bs.clicked.connect(self._save)
        sr.addWidget(bs); layout.addLayout(sr)

    def load_forma(self, forma_id: str):
        self._forma_id = forma_id
        f = db.get_forma(forma_id)
        if not f: return
        self._name.setText(f["name"])
        self._doc_type.setText(f["doc_type"])
        self._desc.setPlainText(f["description"] or "")
        self._load_chrom()
        idx = self._chrom.findText(f["chromaticum_name"] or "")
        if idx >= 0: self._chrom.setCurrentIndex(idx)
        targets = json.loads(f["output_targets"] or '["md"]')
        self._t_md.setChecked("md" in targets)
        self._t_wiz.setChecked("wiz" in targets)
        self._t_pdf.setChecked("pdf" in targets)
        self._load_fields(forma_id)
        self._dirty = False; self.dirty_changed.emit(False)

    def _load_chrom(self):
        curr = self._chrom.currentText()
        self._chrom.clear(); self._chrom.addItems([""] + get_chromatica_list())
        idx = self._chrom.findText(curr)
        if idx >= 0: self._chrom.setCurrentIndex(idx)

    def _load_fields(self, forma_id):
        self._tbl.setRowCount(0)
        for f in db.get_forma_fields(forma_id):
            self._add_row(f["name"], f["label"], f["field_type"],
                          bool(f["required"]), f["fixed_value"] or "")

    def _add_row(self, name="", label="", ftype="PERMISSIVE", req=False, fixed=""):
        r = self._tbl.rowCount(); self._tbl.insertRow(r)
        self._tbl.setItem(r, 0, QTableWidgetItem(name))
        self._tbl.setItem(r, 1, QTableWidgetItem(label))
        tc = QComboBox(); tc.addItems(["PERMISSIVE","FIXED"]); tc.setCurrentText(ftype)
        tc.currentTextChanged.connect(self._mark_dirty); self._tbl.setCellWidget(r, 2, tc)
        rc = QCheckBox(); rc.setChecked(req)
        rc.stateChanged.connect(self._mark_dirty); self._tbl.setCellWidget(r, 3, rc)
        self._tbl.setItem(r, 4, QTableWidgetItem(fixed))

    def _rm_row(self):
        r = self._tbl.currentRow()
        if r >= 0: self._tbl.removeRow(r); self._mark_dirty()

    def _mark_dirty(self, *_):
        if not self._dirty: self._dirty = True; self.dirty_changed.emit(True)

    def _save(self):
        targets = []
        if self._t_md.isChecked():  targets.append("md")
        if self._t_wiz.isChecked(): targets.append("wiz")
        if self._t_pdf.isChecked(): targets.append("pdf")
        if not self._forma_id:
            self._forma_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO formae (forma_id,name,doc_type,description,output_targets,"
                "chromaticum_name,status,version) VALUES (?,?,?,?,?,?,'DRAFT',1)",
                (self._forma_id, self._name.text(), self._doc_type.text(),
                 self._desc.toPlainText(), json.dumps(targets),
                 self._chrom.currentText() or None))
        else:
            db.execute(
                "UPDATE formae SET name=?,doc_type=?,description=?,output_targets=?,"
                "chromaticum_name=?,version=version+1,updated_at=datetime('now') WHERE forma_id=?",
                (self._name.text(), self._doc_type.text(), self._desc.toPlainText(),
                 json.dumps(targets), self._chrom.currentText() or None, self._forma_id))
        db.execute("DELETE FROM forma_fields WHERE forma_id=?", (self._forma_id,))
        for row in range(self._tbl.rowCount()):
            ni = self._tbl.item(row, 0); li = self._tbl.item(row, 1)
            tc = self._tbl.cellWidget(row, 2); rc = self._tbl.cellWidget(row, 3)
            fi = self._tbl.item(row, 4)
            if not ni or not ni.text(): continue
            db.execute(
                "INSERT INTO forma_fields (field_id,forma_id,name,label,field_type,"
                "required,fixed_value,position) VALUES (?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), self._forma_id, ni.text(),
                 li.text() if li else "",
                 tc.currentText() if tc else "PERMISSIVE",
                 1 if (rc and rc.isChecked()) else 0,
                 fi.text() if fi else "", row))
        self._dirty = False; self.dirty_changed.emit(False)
        self.saved.emit(self._forma_id)
