# Departamentum Documentalis — app.py
# v1.0.0
"""QApplication setup and main window for Bureau III."""

import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QSplitter, QMessageBox, QFileDialog,
    QInputDialog, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence

from .constants import (
    APP_TITLE, APP_SUBTITLE, BUREAU_LATIN, BUREAU_FULL,
    MODUS_ARCANUS_DEFAULTS,
)
from .editor import BureauEditor
from .preview import PreviewPanel
from .bureau_parser import parse_bureau
from .bureau_writer import write_bureau
from .emitter_md import emit_to_file as emit_md
from .emitter_wiz import emit_wiz
from .templates import get_template, list_templates
from .library import DocumentLibrary
from .theme_loader import (
    get_active_tokens, generate_qss, load_theme,
    get_active_designator,
)


def get_app_root() -> Path:
    return Path(__file__).resolve().parent

def get_storage_path() -> Path:
    s = get_app_root() / 'storage'; s.mkdir(exist_ok=True); return s

def get_exports_path() -> Path:
    e = get_app_root() / 'exports'; e.mkdir(exist_ok=True); return e


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1100, 700)

        self._library = DocumentLibrary(get_storage_path() / 'document_library.db')
        self._library_ok = self._library.initialize()
        self._current_path: Path | None = None

        self._build_ui()
        self._wire_signals()
        self._setup_shortcuts()

        qss = generate_qss(get_active_tokens())
        QApplication.instance().setStyleSheet(qss)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TopBar ──
        topbar = QFrame()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet('QFrame { border-bottom: 1px solid #3a2e10; }')
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(16, 0, 16, 0)

        title = QLabel(APP_TITLE)
        title.setProperty('role', 'title')
        tb.addWidget(title)
        tb.addStretch()

        sub = QLabel(BUREAU_LATIN)
        sub.setProperty('role', 'dim')
        tb.addWidget(sub)
        root.addWidget(topbar)

        # ── Splitter: Editor | Preview ──
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(2)

        self._editor = BureauEditor()
        self._splitter.addWidget(self._editor)

        self._preview = PreviewPanel()
        self._splitter.addWidget(self._preview)

        self._splitter.setSizes([550, 450])
        root.addWidget(self._splitter, 1)

        # ── StatusBar ──
        status = QFrame()
        status.setFixedHeight(28)
        status.setStyleSheet('QFrame { border-top: 1px solid #3a2e10; }')
        sl = QHBoxLayout(status)
        sl.setContentsMargins(12, 0, 12, 0)

        self._status_msg = QLabel(
            f'\u2699 {BUREAU_FULL} awaits.'
        )
        self._status_msg.setProperty('role', 'dim')
        sl.addWidget(self._status_msg)
        sl.addStretch()

        self._stage_label = QLabel('Compositio \u00b7 New')
        self._stage_label.setProperty('role', 'dim')
        sl.addWidget(self._stage_label)
        root.addWidget(status)

    def _wire_signals(self):
        self._editor.content_changed.connect(self._on_content_changed)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence('q'), self).activated.connect(self.close)
        QShortcut(QKeySequence('Ctrl+N'), self).activated.connect(self._new_from_template)
        QShortcut(QKeySequence('Ctrl+O'), self).activated.connect(self._open_file)
        QShortcut(QKeySequence('Ctrl+S'), self).activated.connect(self._save)
        QShortcut(QKeySequence('Ctrl+Shift+S'), self).activated.connect(self._save_as)
        QShortcut(QKeySequence('Ctrl+E'), self).activated.connect(self._compile)
        QShortcut(QKeySequence('Ctrl+T'), self).activated.connect(self._load_theme)
        QShortcut(QKeySequence('Ctrl+P'), self).activated.connect(
            lambda: self._preview.setVisible(not self._preview.isVisible())
        )

    # ── Preview ──

    def _on_content_changed(self):
        text = self._editor.get_text()
        try:
            doc = parse_bureau(text)
            self._preview.schedule_rebuild(doc)
            self._stage_label.setText('Compositio \u00b7 Unsaved')
        except Exception:
            pass

    # ── File ops ──

    def _new_from_template(self):
        templates = list_templates()
        tmpl, ok = QInputDialog.getItem(
            self, 'Novum', 'Select template:', templates, editable=False
        )
        if not ok:
            return
        title, ok2 = QInputDialog.getText(self, 'Novum', 'Document title:')
        if not ok2 or not title.strip():
            return
        content = get_template(tmpl, title=title.strip())
        self._editor.set_text(content)
        self._current_path = None
        self._status_msg.setText(f'\u2726  New {tmpl}: {title.strip()}')
        self._stage_label.setText('Compositio \u00b7 New')

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Aperire', '', 'Bureau Files (*.bureau);;All Files (*)'
        )
        if not path:
            return
        p = Path(path)
        text = p.read_text(encoding='utf-8')
        self._editor.set_text(text)
        self._current_path = p
        self._status_msg.setText(f'\u2726  Opened: {p.name}')
        self._stage_label.setText(f'Compositio \u00b7 {p.name}')

    def _save(self):
        if self._current_path:
            self._current_path.write_text(
                self._editor.get_text(), encoding='utf-8'
            )
            self._status_msg.setText(f'\U0001f732  Saved: {self._current_path.name}')
            self._stage_label.setText(f'Sigillare \u00b7 {self._current_path.name}')
        else:
            self._save_as()

    def _save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Sigillare', '', 'Bureau Files (*.bureau)'
        )
        if not path:
            return
        p = Path(path)
        if not p.suffix:
            p = p.with_suffix('.bureau')
        p.write_text(self._editor.get_text(), encoding='utf-8')
        self._current_path = p
        self._status_msg.setText(f'\U0001f732  Saved: {p.name}')

    # ── Compile ──

    def _compile(self):
        text = self._editor.get_text()
        if not text.strip():
            self._status_msg.setText('\u2334  Nothing to compile.')
            return

        try:
            doc = parse_bureau(text, source_path=str(self._current_path or ''))
        except Exception as e:
            QMessageBox.critical(self, 'Parse Error', str(e))
            return

        outdir = get_exports_path()
        stem = doc.header.title.replace(' ', '_').replace('/', '_') or 'document'

        md_path = outdir / f'{stem}.md'
        wiz_path = outdir / f'{stem}.wiz'

        try:
            from .emitter_md import emit_to_file
            emit_to_file(doc, md_path)
            self._status_msg.setText(f'\u2726  {md_path.name}')
        except Exception as e:
            QMessageBox.warning(self, '.md Error', str(e))

        try:
            emit_wiz(doc, wiz_path)
            self._status_msg.setText(
                f'\u2726  Compiled: {stem}.wiz + {stem}.md'
            )
        except RuntimeError as e:
            self._status_msg.setText(f'\u2334  .wiz failed: {e}')
            QMessageBox.warning(self, '.wiz Error', str(e))

        # Companion JSON
        from datetime import datetime, timezone
        companion = {
            'source': str(self._current_path or ''),
            'outputs': {'wiz': str(wiz_path), 'md': str(md_path)},
            'template': doc.header.doc_type,
            'document_theme': doc.header.theme,
            'gui_theme_designator': get_active_designator(),
            'compiled_at': datetime.now(timezone.utc).isoformat(),
            'version': doc.header.version,
            'author': doc.header.author,
        }
        cj_path = outdir / f'{stem}.bureau.json'
        cj_path.write_text(
            json.dumps(companion, indent=2), encoding='utf-8'
        )

        # Record in library
        if self._library_ok:
            self._library.record(
                title=doc.header.title, doc_type=doc.header.doc_type,
                source_path=str(self._current_path or ''),
                wiz_path=str(wiz_path), md_path=str(md_path),
                bureau_json=json.dumps(companion),
                version=doc.header.version, author=doc.header.author,
                theme=doc.header.theme,
            )

        self._stage_label.setText(f'Promulgatio \u00b7 {stem}')

    # ── Theme ──

    def _load_theme(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Thema', '', 'JSON Files (*.json)'
        )
        if not path:
            return
        try:
            tokens = load_theme(Path(path))
            qss = generate_qss(tokens)
            QApplication.instance().setStyleSheet(qss)
            self._status_msg.setText(
                f'\u2726  GUI theme: {get_active_designator() or "custom"}'
            )
        except Exception as e:
            self._status_msg.setText('\u2334  Theme failed. Defaults active.')
            QMessageBox.warning(self, 'Theme Error', str(e))

    def closeEvent(self, event):
        self._library.close()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName('Departamentum Documentalis')
    window = MainWindow()
    window.show()
    return app.exec()
