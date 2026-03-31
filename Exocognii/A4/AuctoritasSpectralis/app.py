# Auctoritas Spectralis — app.py
# v1.0.0
"""QApplication setup and main window assembly for Codexium Chromaticus."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QSplitter, QMessageBox, QInputDialog,
    QStatusBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence

from .constants import (
    APP_TITLE, APP_SUBTITLE, BUREAU_LATIN, BUREAU_FULL,
    MODUS_ARCANUS_DEFAULTS, DEFAULT_BG, DEFAULT_FG,
)
from .compositio import Compositio
from .auto_render import AutoRenderer
from .ratificatio import generate_seal, can_ratify
from .designator_gen import suggest_designator
from .registry import ChromaticRegistry
from .promulgatio import export_all
from .workers import IoWorker

from .widgets.forge_panel import ForgePanel
from .widgets.contrast_grid import ContrastGrid
from .widgets.sequence_viewer import SequenceViewer
from .widgets.vision_overlay import VisionOverlay
from .widgets.preview_panel import PreviewPanel
from .widgets.registry_drawer import RegistryDrawer


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


class MainWindow(QMainWindow):
    """Codexium Chromaticus main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1200, 700)

        # ── Core systems ──
        self._app = QApplication.instance()
        self._renderer = AutoRenderer(self._app)
        self._compositio = Compositio(self)
        self._registry = ChromaticRegistry(
            get_storage_path() / 'chromatic_registry.db'
        )
        self._registry_ok = self._registry.connect()
        self._current_seal = None  # last ratified SealRecord
        self._undo_stack = []
        self._redo_stack = []

        self._build_ui()
        self._wire_signals()
        self._setup_shortcuts()

        # ── Initial render ──
        self._renderer.apply_immediate(MODUS_ARCANUS_DEFAULTS)
        QTimer.singleShot(100, self._initial_derive)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Top Bar ──
        topbar = QFrame()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet(
            'QFrame { border-bottom: 1px solid #3a2e10; }'
        )
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(16, 0, 16, 0)

        title_lbl = QLabel(APP_TITLE)
        title_lbl.setProperty('role', 'title')
        topbar_layout.addWidget(title_lbl)

        topbar_layout.addStretch()

        subtitle = QLabel(BUREAU_LATIN)
        subtitle.setProperty('role', 'dim')
        topbar_layout.addWidget(subtitle)

        # Vision sim toggle (in topbar)
        self._vision = VisionOverlay()
        topbar_layout.addWidget(self._vision)

        root_layout.addWidget(topbar)

        # ── Main content (3-pane splitter) ──
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(2)

        # Left: Compositio (ForgePanel)
        self._forge = ForgePanel()
        self._forge.setMinimumWidth(220)
        self._forge.setMaximumWidth(340)
        self._splitter.addWidget(self._forge)

        # Centre: Scrutinium
        centre = QWidget()
        centre_layout = QVBoxLayout(centre)
        centre_layout.setContentsMargins(8, 8, 8, 8)
        centre_layout.setSpacing(8)

        self._contrast_grid = ContrastGrid()
        centre_layout.addWidget(self._contrast_grid, 2)

        self._sequence = SequenceViewer()
        centre_layout.addWidget(self._sequence, 1)

        self._splitter.addWidget(centre)

        # Right: Specularium Vivum
        self._preview = PreviewPanel()
        self._preview.setMinimumWidth(220)
        self._splitter.addWidget(self._preview)

        self._splitter.setSizes([280, 500, 300])
        root_layout.addWidget(self._splitter, 1)

        # ── Bottom: Registry Drawer ──
        self._drawer = RegistryDrawer()
        root_layout.addWidget(self._drawer)

        # ── Status Bar ──
        self._status_frame = QFrame()
        self._status_frame.setFixedHeight(28)
        self._status_frame.setStyleSheet(
            'QFrame { border-top: 1px solid #3a2e10; }'
        )
        status_layout = QHBoxLayout(self._status_frame)
        status_layout.setContentsMargins(12, 0, 12, 0)

        self._status_msg = QLabel(
            f'\u2699 {BUREAU_FULL} awaits.'
        )
        self._status_msg.setProperty('role', 'dim')
        status_layout.addWidget(self._status_msg)

        status_layout.addStretch()

        self._stage_label = QLabel('Compositio \u00b7 Unsaved')
        self._stage_label.setProperty('role', 'dim')
        status_layout.addWidget(self._stage_label)

        root_layout.addWidget(self._status_frame)

    def _wire_signals(self):
        # Forge → Compositio
        self._forge.palette_changed.connect(self._on_palette_changed)

        # Compositio → UI
        self._compositio.tokens_derived.connect(self._on_tokens_derived)
        self._compositio.audit_complete.connect(self._on_audit_complete)
        self._compositio.palette_ready.connect(self._renderer.schedule)

        # Vision sim
        self._vision.mode_changed.connect(self._compositio.on_vision_mode_changed)

        # Registry drawer
        self._drawer.load_requested.connect(self._on_registry_load)
        self._drawer.export_requested.connect(self._on_registry_export)

    def _setup_shortcuts(self):
        # q — Exire
        QShortcut(QKeySequence('q'), self).activated.connect(self.close)

        # Ctrl+R — Ratificare
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(self._ratify)

        # Ctrl+E — Promulgare
        QShortcut(QKeySequence('Ctrl+E'), self).activated.connect(self._export)

        # Ctrl+S — Sigillare (save working state)
        QShortcut(QKeySequence('Ctrl+S'), self).activated.connect(self._save_state)

        # Ctrl+Z — Revocare (undo)
        QShortcut(QKeySequence('Ctrl+Z'), self).activated.connect(self._undo)

        # Ctrl+Shift+Z — Restituere (redo)
        QShortcut(QKeySequence('Ctrl+Shift+Z'), self).activated.connect(self._redo)

        # Ctrl+G — Registrum toggle
        QShortcut(QKeySequence('Ctrl+G'), self).activated.connect(
            self._drawer.toggle
        )

        # Ctrl+Shift+V — Visio cycle
        QShortcut(QKeySequence('Ctrl+Shift+V'), self).activated.connect(
            self._vision.cycle
        )

        # Ctrl+1/2/3 — Focus panels
        QShortcut(QKeySequence('Ctrl+1'), self).activated.connect(
            lambda: self._forge.setFocus()
        )
        QShortcut(QKeySequence('Ctrl+2'), self).activated.connect(
            lambda: self._contrast_grid.setFocus()
        )
        QShortcut(QKeySequence('Ctrl+3'), self).activated.connect(
            lambda: self._preview.setFocus()
        )

    # ── Pipeline callbacks ──

    def _initial_derive(self):
        self._forge.set_base_pair(DEFAULT_BG, DEFAULT_FG)
        self._refresh_registry()

    def _on_palette_changed(self, bg_hex: str, fg_hex: str):
        # Push to undo stack
        self._undo_stack.append((bg_hex, fg_hex))
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

        self._compositio.on_palette_changed(bg_hex, fg_hex)
        self._stage_label.setText('Compositio \u00b7 Unsaved')

    def _on_tokens_derived(self, tokens: dict, oklab: dict, clipped: list):
        self._forge.update_derived(tokens, clipped)
        self._sequence.update_data(oklab, tokens)
        if clipped:
            self._status_msg.setText(
                f'\u2334 Gamut clipping on: {", ".join(clipped)}'
            )

    def _on_audit_complete(self, matrix: list, audit: dict):
        self._contrast_grid.update_matrix(matrix, audit)

    # ── Actions ──

    def _ratify(self):
        if not self._registry_ok:
            QMessageBox.warning(
                self, 'Registry Unavailable',
                'The Chromatic Registry could not be opened.\n'
                'Ratification is not available.'
            )
            return

        audit = self._compositio.get_current_audit()
        passes, failing = can_ratify(audit)

        if not passes:
            pairs_text = '\n'.join(
                f"  {e['fg_token']} on {e['bg_token']}: "
                f"{e['wcag_ratio']:.1f}:1 (requires 4.5:1)"
                for e in failing
            )
            result = QMessageBox.warning(
                self,
                '\u2334  Ratificatio Denegata',
                f'The following token pairs fail WCAG AA:\n\n'
                f'{pairs_text}\n\n'
                f'Adjust the base pair or override.',
                QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ignore,
                QMessageBox.StandardButton.Cancel,
            )
            if result == QMessageBox.StandardButton.Cancel:
                return

        # Suggest designator
        tokens = self._compositio.get_current_tokens()
        suggested = suggest_designator(tokens)
        designator, ok = QInputDialog.getText(
            self, 'Ratificare',
            'Designator for this palette:',
            text=suggested,
        )
        if not ok or not designator.strip():
            return
        designator = designator.strip()

        # Generate seal
        seal = generate_seal(tokens, designator)
        self._current_seal = seal

        # Write to registry
        oklab = self._compositio.get_current_oklab()
        bg_ok = oklab.get('c_bg', {'l': 0, 'a': 0, 'b': 0})
        fg_ok = oklab.get('c_gold', {'l': 0, 'a': 0, 'b': 0})

        try:
            self._registry.insert_palette(
                designator=designator,
                seal_hash=seal['seal_hash'],
                tokens=tokens,
                oklab_bg=bg_ok,
                oklab_fg=fg_ok,
                wcag_min=audit.get('min_wcag_ratio', 0),
                apca_min=audit.get('min_apca_lc', 0),
                passes_aa=audit.get('passes_aa', False),
                passes_aaa=audit.get('passes_aaa', False),
                canonical_json=seal['canonical_json'],
                sealed_at=seal['sealed_at'],
                notes='' if passes else 'Override: AA compliance waived',
            )
        except Exception as e:
            QMessageBox.critical(
                self, '\u2715 Registry Error',
                f'Failed to write to registry:\n{e}'
            )
            return

        self._refresh_registry()
        self._status_msg.setText(
            f'\u2726  Palette ratified: {designator}'
        )
        self._stage_label.setText(f'Ratificatio \u00b7 {designator}')

    def _export(self):
        if self._current_seal is None:
            QMessageBox.information(
                self, 'No Seal',
                'No palette has been ratified in this session.\n'
                'Ratify first (Ctrl+R), then export.'
            )
            return

        tokens = self._compositio.get_current_tokens()
        oklab = self._compositio.get_current_oklab()
        base_pair = self._compositio.get_base_pair_dict()
        audit = self._compositio.get_current_audit()
        export_dir = get_exports_path()

        try:
            paths = export_all(
                tokens, oklab, base_pair,
                self._current_seal, audit, export_dir
            )
            # Log exports
            if self._registry_ok:
                palettes = self._registry.list_palettes()
                if palettes:
                    rid = palettes[0]['id']
                    for fmt, path in paths.items():
                        self._registry.log_export(rid, fmt, str(path))

            self._status_msg.setText(
                f'\u2726  Theme promulgated: {self._current_seal["designator"]}'
            )
        except Exception as e:
            QMessageBox.critical(
                self, '\u2715  Inscriptio Defecta',
                f'The seal could not be committed to disk.\n'
                f'Verify write permissions on:\n{export_dir}\n\n'
                f'Error: {e}'
            )

    def _save_state(self):
        self._status_msg.setText('\u2726  Working state preserved.')

    def _undo(self):
        if len(self._undo_stack) < 2:
            return
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        bg, fg = self._undo_stack[-1]
        self._forge.set_base_pair(bg, fg)

    def _redo(self):
        if not self._redo_stack:
            return
        state = self._redo_stack.pop()
        bg, fg = state
        self._forge.set_base_pair(bg, fg)

    def _on_registry_load(self, registry_id: int):
        row = self._registry.get_palette(registry_id)
        if row is None:
            return
        self._forge.set_base_pair(row['c_bg'], row['c_gold'])
        self._status_msg.setText(
            f'\u2726  Loaded: {row["designator"]}'
        )

    def _on_registry_export(self, registry_id: int):
        row = self._registry.get_palette(registry_id)
        if row is None:
            return
        tokens = self._registry.get_tokens_from_row(row)
        # Create a minimal seal record for export
        self._current_seal = {
            'seal_hash': row['seal_hash'],
            'sealed_at': row['created_at'],
            'designator': row['designator'],
            'canonical_json': '',
        }
        self._compositio.on_palette_changed(row['c_bg'], row['c_gold'])
        QTimer.singleShot(200, self._export)

    def _refresh_registry(self):
        if self._registry_ok:
            palettes = self._registry.list_palettes()
            self._drawer.populate(palettes)

    def closeEvent(self, event):
        self._registry.close()
        super().closeEvent(event)


def main() -> int:
    try:
        import colour  # noqa: F401
    except ImportError:
        print(
            "ERROR: colour-science not found.\n"
            "Install it: pip install colour-science",
            file=sys.stderr,
        )
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName('Codexium Chromaticus')

    window = MainWindow()
    window.show()
    return app.exec()
