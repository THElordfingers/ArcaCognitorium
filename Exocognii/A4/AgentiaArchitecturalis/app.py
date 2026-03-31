# Agentia Architecturalis — app.py
# v1.0.0
"""QApplication setup and main window assembly."""

import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QSplitter, QMessageBox, QInputDialog,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QClipboard

from .constants import (
    APP_TITLE, APP_SUBTITLE, BUREAU_LATIN, BUREAU_FULL,
    MODUS_ARCANUS_DEFAULTS,
)
from .canvas import DesignCanvas
from .palette import ElementPalette
from .inspector import PropertyInspector
from .preview import PreviewRenderer
from .library import ComponentLibrary
from .codegen import generate_code
from .theme_loader import (
    load_theme, get_active_tokens, get_active_designator,
    generate_qss, reset_to_defaults,
)


def get_app_root() -> Path:
    return Path(__file__).resolve().parent

def get_storage_path() -> Path:
    storage = get_app_root() / 'storage'
    storage.mkdir(exist_ok=True)
    return storage

def get_exports_path() -> Path:
    exports = get_app_root() / 'exports'
    exports.mkdir(exist_ok=True)
    return exports


class LibraryDrawer(QWidget):
    """Collapsible bottom drawer for the component library."""

    def __init__(self, library: ComponentLibrary, parent=None):
        super().__init__(parent)
        self._library = library
        self._expanded = False
        self.setMaximumHeight(32)

        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        self._anim_class = QPropertyAnimation
        self._ease = QEasingCurve

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 12, 0)
        title = QLabel('ARMARIUM COMPONENTIUM')
        title.setProperty('role', 'micro')
        hl.addWidget(title)
        hl.addStretch()
        self._toggle_btn = QPushButton('\u25b2')
        self._toggle_btn.setFixedSize(28, 24)
        self._toggle_btn.clicked.connect(self.toggle)
        hl.addWidget(self._toggle_btn)
        layout.addWidget(header)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ['#', 'Name', 'Category', 'Version', 'Theme', 'Actions']
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        # Callbacks set by MainWindow
        self.on_load = None
        self.on_fork = None
        self.on_export = None

    def toggle(self):
        target = 220 if not self._expanded else 32
        anim = self._anim_class(self, b"maximumHeight", self)
        anim.setDuration(220)
        anim.setEasingCurve(self._ease.Type.InOutQuad)
        anim.setStartValue(self.maximumHeight())
        anim.setEndValue(target)
        anim.start(self._anim_class.DeletionPolicy.DeleteWhenStopped)
        self._expanded = not self._expanded
        self._toggle_btn.setText('\u25bc' if self._expanded else '\u25b2')

    def refresh(self):
        if not self._library.enabled:
            return
        comps = self._library.list_components()
        self._table.setRowCount(len(comps))
        for row, c in enumerate(comps):
            self._table.setItem(row, 0, QTableWidgetItem(str(c.get('id', ''))))
            self._table.setItem(row, 1, QTableWidgetItem(c.get('name', '')))
            self._table.setItem(row, 2, QTableWidgetItem(c.get('category', '')))
            self._table.setItem(row, 3, QTableWidgetItem(f"v{c.get('version', 1)}"))
            self._table.setItem(row, 4, QTableWidgetItem(c.get('theme_designator', '—') or '—'))

            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(2, 0, 2, 0)
            al.setSpacing(4)
            cid = c['id']
            load_btn = QPushButton('Load')
            load_btn.setFixedHeight(22)
            load_btn.clicked.connect(lambda _, r=cid: self.on_load and self.on_load(r))
            al.addWidget(load_btn)
            fork_btn = QPushButton('Fork')
            fork_btn.setFixedHeight(22)
            fork_btn.clicked.connect(lambda _, r=cid: self.on_fork and self.on_fork(r))
            al.addWidget(fork_btn)
            exp_btn = QPushButton('Exp')
            exp_btn.setFixedHeight(22)
            exp_btn.clicked.connect(lambda _, r=cid: self.on_export and self.on_export(r))
            al.addWidget(exp_btn)
            self._table.setCellWidget(row, 5, actions)


class MainWindow(QMainWindow):
    """Agentia Architecturalis main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1300, 750)

        self._library = ComponentLibrary(get_storage_path() / 'component_library.db')
        self._library_ok = self._library.initialize()
        self._current_component_id: int | None = None

        self._build_ui()
        self._wire_signals()
        self._setup_shortcuts()

        # Apply initial QSS
        tokens = get_active_tokens()
        qss = generate_qss(tokens)
        QApplication.instance().setStyleSheet(qss)
        self._refresh_library()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TopBar
        topbar = QFrame()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet('QFrame { border-bottom: 1px solid #3a2e10; }')
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)
        title = QLabel(APP_TITLE)
        title.setProperty('role', 'title')
        tb_layout.addWidget(title)
        tb_layout.addStretch()
        sub = QLabel(BUREAU_LATIN)
        sub.setProperty('role', 'dim')
        tb_layout.addWidget(sub)
        root.addWidget(topbar)

        # Main content — 3-pane
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(2)

        # Left: Palette
        self._palette = ElementPalette()
        main_splitter.addWidget(self._palette)

        # Centre: Canvas
        self._canvas = DesignCanvas()
        main_splitter.addWidget(self._canvas)

        # Right: Inspector + Preview stacked
        right = QSplitter(Qt.Orientation.Vertical)
        self._inspector = PropertyInspector()
        right.addWidget(self._inspector)
        self._preview = PreviewRenderer()
        right.addWidget(self._preview)
        right.setSizes([350, 300])
        main_splitter.addWidget(right)

        main_splitter.setSizes([170, 600, 280])
        root.addWidget(main_splitter, 1)

        # Bottom: Library drawer
        self._drawer = LibraryDrawer(self._library)
        root.addWidget(self._drawer)

        # Status bar
        status = QFrame()
        status.setFixedHeight(28)
        status.setStyleSheet('QFrame { border-top: 1px solid #3a2e10; }')
        sl = QHBoxLayout(status)
        sl.setContentsMargins(12, 0, 12, 0)
        self._status_msg = QLabel(f'\u2699 {BUREAU_FULL} awaits alignment.')
        self._status_msg.setProperty('role', 'dim')
        sl.addWidget(self._status_msg)
        sl.addStretch()
        self._stage_label = QLabel('Compositio \u00b7 Unsaved \u00b7 0 elms')
        self._stage_label.setProperty('role', 'dim')
        sl.addWidget(self._stage_label)
        root.addWidget(status)

    def _wire_signals(self):
        self._canvas.element_selected.connect(self._on_element_selected)
        self._canvas.design_changed.connect(self._on_design_changed)
        self._canvas.element_dropped.connect(self._on_element_dropped)
        self._inspector.property_changed.connect(self._on_property_changed)
        self._drawer.on_load = self._load_component
        self._drawer.on_fork = self._fork_component
        self._drawer.on_export = self._export_component

    def _setup_shortcuts(self):
        QShortcut(QKeySequence('q'), self).activated.connect(self.close)
        QShortcut(QKeySequence('Ctrl+S'), self).activated.connect(self._save)
        QShortcut(QKeySequence('Ctrl+Shift+S'), self).activated.connect(self._save_as_new)
        QShortcut(QKeySequence('Ctrl+E'), self).activated.connect(self._export_clipboard)
        QShortcut(QKeySequence('Ctrl+Shift+E'), self).activated.connect(self._export_file)
        QShortcut(QKeySequence('Ctrl+Z'), self).activated.connect(self._canvas.undo)
        QShortcut(QKeySequence('Ctrl+Shift+Z'), self).activated.connect(self._canvas.redo)
        QShortcut(QKeySequence('Ctrl+N'), self).activated.connect(self._new_canvas)
        QShortcut(QKeySequence('Ctrl+L'), self).activated.connect(self._drawer.toggle)
        QShortcut(QKeySequence('Ctrl+T'), self).activated.connect(self._load_theme)
        QShortcut(QKeySequence('Ctrl+P'), self).activated.connect(
            lambda: self._preview.setVisible(not self._preview.isVisible()))
        QShortcut(QKeySequence('Delete'), self).activated.connect(self._canvas.remove_selected)
        QShortcut(QKeySequence('Ctrl+D'), self).activated.connect(self._canvas.duplicate_selected)
        QShortcut(QKeySequence('Ctrl+G'), self).activated.connect(self._canvas.group_selected)
        QShortcut(QKeySequence('Ctrl+Shift+G'), self).activated.connect(self._canvas.ungroup_selected)

    # ── Callbacks ──

    def _on_element_selected(self, element):
        self._inspector.set_element(element)

    def _on_design_changed(self):
        count = self._canvas.get_element_count()
        self._stage_label.setText(f'Compositio \u00b7 Unsaved \u00b7 {count} elms')
        tokens = get_active_tokens()
        tree = self._canvas.serialize_all()
        self._preview.schedule_rebuild(tree, tokens)

    def _on_element_dropped(self, element_type: str, x: float, y: float):
        self._canvas.add_element(element_type, x, y)

    def _on_property_changed(self, elem_id, prop, value):
        self._canvas.design_changed.emit()

    # ── Actions ──

    def _new_canvas(self):
        self._canvas.clear_canvas()
        self._current_component_id = None
        self._status_msg.setText('\u2726 New canvas.')

    def _save(self):
        if not self._library_ok:
            QMessageBox.warning(self, 'Library Unavailable',
                                'Component Library could not be opened.')
            return
        tree = self._canvas.serialize_all()
        if not tree:
            self._status_msg.setText('\u2334 Nothing to save.')
            return
        design_doc = {
            'schema_version': '1.0',
            'canvas_width': 2000, 'canvas_height': 2000,
            'root_elements': tree,
            'theme_designator': get_active_designator(),
            'metadata': {},
        }
        design_json = json.dumps(design_doc)

        if self._current_component_id:
            comp = self._library.load(self._current_component_id)
            if comp:
                self._library.save(
                    comp['name'], comp['category'], design_json,
                    comp.get('description', ''), comp.get('tags', ''),
                    self._preview.capture_thumbnail(),
                    get_active_designator(),
                    self._current_component_id
                )
                self._status_msg.setText(f'\U0001f732 Component updated: {comp["name"]}')
                self._refresh_library()
                return

        self._save_as_new()

    def _save_as_new(self):
        if not self._library_ok:
            QMessageBox.warning(self, 'Library Unavailable',
                                'Component Library could not be opened.')
            return
        tree = self._canvas.serialize_all()
        if not tree:
            return
        name, ok = QInputDialog.getText(self, 'Sigillare', 'Component name:')
        if not ok or not name.strip():
            return
        category, ok = QInputDialog.getItem(
            self, 'Category', 'Select category:',
            ['panel', 'dialog', 'toolbar', 'card', 'composite', 'fragment'],
            0, False
        )
        if not ok:
            return
        design_doc = {
            'schema_version': '1.0',
            'canvas_width': 2000, 'canvas_height': 2000,
            'root_elements': tree,
            'theme_designator': get_active_designator(),
            'metadata': {},
        }
        cid = self._library.save(
            name.strip(), category, json.dumps(design_doc),
            thumbnail=self._preview.capture_thumbnail(),
            theme_designator=get_active_designator(),
        )
        self._current_component_id = cid
        self._status_msg.setText(f'\U0001f732 Component sealed: {name.strip()} v1')
        self._refresh_library()

    def _export_clipboard(self):
        tree = self._canvas.serialize_all()
        if not tree:
            self._status_msg.setText('\u2334 Nothing to export.')
            return
        tokens = get_active_tokens()
        design = {'root_elements': tree}
        try:
            code = generate_code(design, tokens)
            clipboard = QApplication.clipboard()
            clipboard.setText(code)
            self._status_msg.setText('\u2726 Code exported to clipboard.')
        except SyntaxError as e:
            QMessageBox.critical(self, '\u2715 Codegen Error', str(e))
        except Exception as e:
            # Fallback to file
            self._export_file_direct(code if 'code' in dir() else '')

    def _export_file(self):
        tree = self._canvas.serialize_all()
        if not tree:
            return
        tokens = get_active_tokens()
        design = {'root_elements': tree}
        try:
            code = generate_code(design, tokens)
            self._export_file_direct(code)
        except SyntaxError as e:
            QMessageBox.critical(self, '\u2715 Codegen Error', str(e))

    def _export_file_direct(self, code: str):
        path = get_exports_path() / 'generated_panel.py'
        path.write_text(code, encoding='utf-8')
        self._status_msg.setText(f'\u2726 Code written to {path.name}')

    def _load_theme(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Theme', '', 'JSON Files (*.json)'
        )
        if not path:
            return
        try:
            tokens = load_theme(Path(path))
            qss = generate_qss(tokens)
            QApplication.instance().setStyleSheet(qss)
            self._canvas.set_tokens(tokens)
            self._canvas.design_changed.emit()
            self._status_msg.setText(
                f'\u2726 Theme loaded: {get_active_designator() or "custom"}'
            )
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            self._status_msg.setText(f'\u2334 Theme not loaded. Defaults active.')
            reset_to_defaults()

    def _load_component(self, cid: int):
        comp = self._library.load(cid)
        if not comp:
            return
        try:
            design = json.loads(comp['design_json'])
            self._canvas.deserialize_all(design.get('root_elements', []))
            self._current_component_id = cid
            self._status_msg.setText(f'\u2726 Loaded: {comp["name"]}')
        except (json.JSONDecodeError, KeyError) as e:
            QMessageBox.critical(self, '\u2715 Load Error',
                                 f'Corrupt design data:\n{e}')

    def _fork_component(self, cid: int):
        comp = self._library.load(cid)
        if not comp:
            return
        new_name = f"{comp['name']} (fork)"
        new_id = self._library.fork(cid, new_name)
        self._status_msg.setText(f'\u2726 Forked: {new_name}')
        self._refresh_library()

    def _export_component(self, cid: int):
        comp = self._library.load(cid)
        if not comp:
            return
        try:
            design = json.loads(comp['design_json'])
            tokens = get_active_tokens()
            code = generate_code(design, tokens, comp['name'].replace(' ', ''))
            clipboard = QApplication.clipboard()
            clipboard.setText(code)
            self._library.log_export(cid, 'clipboard')
            self._status_msg.setText(f'\u2726 Code exported: {comp["name"]}')
        except Exception as e:
            QMessageBox.critical(self, '\u2715 Export Error', str(e))

    def _refresh_library(self):
        self._drawer.refresh()

    def closeEvent(self, event):
        self._library.close()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName('Agentia Architecturalis')
    window = MainWindow()
    window.show()
    return app.exec()
