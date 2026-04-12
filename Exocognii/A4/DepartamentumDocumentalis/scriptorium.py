# Departamentum Documentalis · scriptorium.py · v1.2
import uuid, json, re
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPlainTextEdit, QTextEdit, QLabel, QPushButton, QComboBox, QLineEdit)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThreadPool
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.scriptura_parser import parse
from DepartamentumDocumentalis.md_renderer import render as md_render
from DepartamentumDocumentalis.wiz_renderer import render as wiz_render, WizRenderError
from DepartamentumDocumentalis.pdf_renderer import render as pdf_render, PdfRenderError
from DepartamentumDocumentalis.chromaticum_bridge import get_theme_snapshot
from DepartamentumDocumentalis.nuntius_emit import emit_event
from DepartamentumDocumentalis.config import CFG
from DepartamentumDocumentalis.workers import Worker

class ScripturaHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._fmt = QTextCharFormat()
        self._fmt.setForeground(QColor("#d4af37"))
        self._fmt.setFontWeight(QFont.Weight.Bold)
        self._re = re.compile(r"\|[A-Z]+:[^|]*\||\|END\|")

    def highlightBlock(self, text):
        for m in self._re.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self._fmt)

class Scriptorium(QWidget):
    dirty_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dirty   = False
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._update_preview)
        self._forma_id = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16)
        tb = QHBoxLayout(); tb.addWidget(QLabel("SCRIPTORIUM")); tb.addStretch()
        self._forma_combo = QComboBox()
        self._forma_combo.currentIndexChanged.connect(self._on_forma_changed)
        self._title_input = QLineEdit(); self._title_input.setPlaceholderText("Document title")
        self._title_input.setMaximumWidth(200)
        tb.addWidget(QLabel("Forma:")); tb.addWidget(self._forma_combo)
        tb.addWidget(self._title_input); layout.addLayout(tb)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._editor = QPlainTextEdit()
        self._editor.setFont(QFont("Courier Prime", 11))
        self._editor.textChanged.connect(self._on_edit)
        ScripturaHighlighter(self._editor.document())
        self._preview = QTextEdit(); self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Georgia", 11))
        splitter.addWidget(self._editor); splitter.addWidget(self._preview)
        splitter.setSizes([500, 500]); layout.addWidget(splitter)

        self._err = QLabel("")
        self._err.setStyleSheet("color:#cc4444;font-family:'Courier Prime';font-size:9px;")
        layout.addWidget(self._err)

        er = QHBoxLayout(); er.addStretch()
        for lbl, tgt in [("EMIT .md","md"),("EMIT .wiz","wiz"),("EMIT .pdf","pdf")]:
            b = QPushButton(lbl); b.clicked.connect(lambda _, t=tgt: self._emit(t))
            er.addWidget(b)
        layout.addLayout(er)
        self._load_formae()

    def _load_formae(self):
        self._forma_combo.clear()
        for f in db.get_all_formae():
            self._forma_combo.addItem(f["name"], f["forma_id"])

    def _on_forma_changed(self, idx):
        fid = self._forma_combo.itemData(idx)
        if not fid: return
        self._forma_id = fid
        if not self._editor.toPlainText():
            parts = []
            for f in db.get_forma_fields(fid):
                if f["field_type"] == "FIXED":
                    parts.append(f"|FIXED:{f['name']}|{f['fixed_value'] or ''}|END|")
                else:
                    parts.append(f"|FIELD:{f['name']}|\n|END|")
            self._editor.setPlainText("\n".join(parts))

    def _on_edit(self):
        if not self._dirty: self._dirty = True; self.dirty_changed.emit(True)
        self._debounce.start(400)

    def _update_preview(self):
        result = parse(self._editor.toPlainText())
        self._err.setText(
            " · ".join(f"L{e.line}:{e.col} {e.message}" for e in result.errors)
            if result.errors else "")
        if result.ast:
            fields = db.get_forma_fields(self._forma_id) if self._forma_id else []
            fixed  = {f["name"]: f["fixed_value"] for f in fields
                      if f["field_type"] == "FIXED" and f["fixed_value"]}
            self._preview.setMarkdown(md_render(result.ast, fields, fixed))

    def _emit(self, target):
        if not self._forma_id: return
        fields = db.get_forma_fields(self._forma_id)
        fixed  = {f["name"]: f["fixed_value"] for f in fields
                  if f["field_type"] == "FIXED" and f["fixed_value"]}
        text   = self._editor.toPlainText()
        title  = self._title_input.text() or "Untitled"
        result = parse(text)
        if not result.ok: return
        out_dir = Path(CFG["output_dir"]); out_dir.mkdir(parents=True, exist_ok=True)
        aid = str(uuid.uuid4())
        ext = "docx" if target == "wiz" else target
        out_path = str(out_dir / f"{aid}.{ext}")

        def do_emit():
            if target == "md":
                md = md_render(result.ast, fields, fixed)
                Path(out_path).write_text(md, encoding="utf-8"); return out_path
            elif target == "wiz":
                return wiz_render(result.ast, fields, fixed, out_path)
            elif target == "pdf":
                return pdf_render(md_render(result.ast, fields, fixed), out_path)

        def on_done(path):
            forma = db.get_forma(self._forma_id)
            doc_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO documents (doc_id,forma_id,title,source_text) VALUES (?,?,?,?)",
                (doc_id, self._forma_id, title, text))
            chrom = forma["chromaticum_name"] or "ModusArcanus"
            db.execute(
                "INSERT INTO archive (archive_id,doc_id,forma_id,forma_version,status,"
                "bureau_marker,chromaticum_name,theme_snapshot,output_paths) "
                "VALUES (?,?,?,?,'CURRENT','III-DD',?,?,?)",
                (aid, doc_id, self._forma_id, forma["version"],
                 chrom, json.dumps(get_theme_snapshot(chrom)), json.dumps({target: path})))
            emit_event("document_composed", {
                "archive_id": aid, "target": target, "title": title,
                "forma_id": self._forma_id})
            self._dirty = False; self.dirty_changed.emit(False)

        w = Worker(do_emit); w.signals.finished.connect(on_done)
        QThreadPool.globalInstance().start(w)
