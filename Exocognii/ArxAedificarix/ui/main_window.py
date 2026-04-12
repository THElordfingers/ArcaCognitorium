#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            ui/main_window.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import os
from pathlib import Path

from PyQt6.QtCore import QRunnable, QThreadPool, QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from bridge.builder_signal_bridge import BuilderSignalBridge
from core.attachment_manager import AttachmentError, AttachmentManager
from core.compression_engine import CompressionEngine, CompressionError
from core.config_loader import ConfigLoader
from core.context_engine import ContextEngine
from core.prompt_loader import PromptLoader
from core.response_parser import ResponseParser
from core.session_store import SessionStore
from core.zip_exporter import ExportError, ZipExporter
from ui.attachment_dialog import AttachmentDialog
from ui.chat_pane import ChatPane
from ui.output_panel import OutputPanel
from ui.preview_pane import PreviewPane
from ui.project_tree import ProjectTree
from ui.token_gauge import TokenGauge
from nuntius_emit import emit_event
from core.build_doc_watcher import BuildDocWatcher

logger = logging.getLogger("arx.main_window")

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"
C_WHITE     = "#e8e0cc"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QSplitter::handle {{
    background: {C_GOLD_DARK};
    width: 1px;
    height: 1px;
}}
QScrollBar:vertical {{
    background: {C_PANEL}; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QToolTip {{
    background: {C_PANEL}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
QInputDialog, QMessageBox {{
    background: {C_PANEL}; color: {C_TEXT};
    font-family: Georgia, serif;
}}
QInputDialog QLabel, QMessageBox QLabel {{
    color: {C_TEXT}; font-family: Georgia, serif;
}}
QInputDialog QLineEdit {{
    background: {C_BG}; color: {C_TEXT};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
"""


# ---------------------------------------------------------------------------
# Worker runnables
# ---------------------------------------------------------------------------

class _AttachWorker(QRunnable):
    """Runs AttachmentManager.attach_file() off the main thread."""

    def __init__(self, manager, path, scope, conv_id, proj_id, on_done, on_error):
        super().__init__()
        self._manager  = manager
        self._path     = path
        self._scope    = scope
        self._conv_id  = conv_id
        self._proj_id  = proj_id
        self._on_done  = on_done
        self._on_error = on_error

    @pyqtSlot()
    def run(self):
        try:
            att = self._manager.attach_file(
                self._path, self._scope,
                conversation_id=self._conv_id,
                project_id=self._proj_id,
            )
            self._on_done(att)
        except Exception as exc:
            self._on_error(str(exc))


class _CompressionWorker(QRunnable):
    """Runs CompressionEngine.trigger() off the main thread."""

    def __init__(self, engine, conv_id, on_done, on_error):
        super().__init__()
        self._engine  = engine
        self._conv_id = conv_id
        self._on_done  = on_done
        self._on_error = on_error

    @pyqtSlot()
    def run(self):
        try:
            record = self._engine.trigger(self._conv_id)
            self._on_done(record)
        except CompressionError as exc:
            self._on_error(str(exc))
        except Exception as exc:
            self._on_error(str(exc))


# ---------------------------------------------------------------------------
# MainWindow
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """
    Three-pane layout: ProjectTree (left, 240px) | ChatPane (centre, flex)
    | OutputPanel + PreviewPane (right, 320px).

    Footer: TokenGauge (left) + conversation title (centre) + Export button (right).

    Wires all signals. Owns the send pipeline, compression pipeline,
    and attachment pipeline.
    """

    def __init__(self, store: SessionStore, box, comp_box) -> None:
        """
        Parameters
        ----------
        store    : SessionStore — initialised before construction.
        box      : ClaudeBox — primary streaming box.
        comp_box : ClaudeBox — dedicated synchronous box for compression.
        """
        super().__init__()
        self._store    = store
        self._box      = box
        self._comp_box = comp_box
        self._conv_id: str | None = None
        self._pool = QThreadPool.globalInstance()

        self._init_core()
        self._init_build_doc_watcher()
        self._build_ui()
        self._wire_signals()
        self._restore_session()

        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowTitle("ARX AEDIFICARIX  ·  v1.0")
        self.resize(1400, 860)

    # -----------------------------------------------------------------------
    # Initialisation
    # -----------------------------------------------------------------------

    def _init_build_doc_watcher(self) -> None:
        dolium_exports = Path(os.environ.get(
            "ARX_BUILD_DOCS",
            str(Path.home() / "ArcaCognitorium" / "Exocognii" / "Dolium" / "storage" / "exports"),
        ))
        self._build_watcher = BuildDocWatcher(dolium_exports, parent=self)
        self._build_docs: list = []

    def _init_core(self) -> None:
        builder_prompt = PromptLoader.load(ConfigLoader.builder_prompt_path())

        self._context_engine = ContextEngine(self._store, builder_prompt)
        self._response_parser = ResponseParser()
        self._zip_exporter = ZipExporter(self._store)
        self._attachment_manager = AttachmentManager(self._store, self._box)
        self._compression_engine = CompressionEngine(self._store, self._comp_box)
        self._bridge = BuilderSignalBridge(self._box, parent=self)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ----- splitter -----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left — ProjectTree (240px fixed)
        self._project_tree = ProjectTree(self._store)
        self._project_tree.setFixedWidth(240)
        splitter.addWidget(self._project_tree)

        # Centre — ChatPane
        self._gauge = TokenGauge(total=ConfigLoader.model_context_limit())
        self._chat_pane = ChatPane(self._gauge)
        splitter.addWidget(self._chat_pane)

        # Right — OutputPanel + PreviewPane stacked vertically (320px fixed)
        right_widget = QWidget()
        right_widget.setFixedWidth(320)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(1)

        self._output_panel = OutputPanel()
        self._preview_pane = PreviewPane()
        right_splitter.addWidget(self._output_panel)
        right_splitter.addWidget(self._preview_pane)
        right_splitter.setSizes([240, 480])

        right_layout.addWidget(right_splitter)
        splitter.addWidget(right_widget)

        splitter.setSizes([240, 840, 320])
        root_layout.addWidget(splitter, stretch=1)

        # ----- footer -----
        footer = self._build_footer()
        root_layout.addWidget(footer)

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setFixedHeight(36)
        footer.setStyleSheet(
            f"background: {C_PANEL}; border-top: 1px solid {C_GOLD_DARK};"
        )
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 2, 8, 2)

        layout.addWidget(self._gauge)

        # Build doc picker
        self._build_doc_combo = QComboBox()
        self._build_doc_combo.setFixedWidth(200)
        self._build_doc_combo.setFixedHeight(24)
        self._build_doc_combo.addItem("— no build doc —")
        self._build_doc_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C_BG}; color: {C_TEAL};
                border: 1px solid {C_TEAL};
                font-family: Georgia, serif; font-size: 9px;
                padding: 2px 6px;
            }}
            QComboBox::drop-down {{ border: none; width: 16px; }}
            QComboBox QAbstractItemView {{
                background: {C_PANEL}; color: {C_TEXT};
                border: 1px solid {C_GOLD_DARK};
                selection-background-color: {C_TEAL};
            }}
        """)
        layout.addWidget(self._build_doc_combo)

        self._conv_title_label = QLabel("")
        self._conv_title_label.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 10px;"
        )
        layout.addWidget(self._conv_title_label, stretch=1)

        self._export_btn = QPushButton("⬡  Export Package")
        self._export_btn.setFixedHeight(26)
        self._export_btn.setEnabled(False)
        self._export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL}; color: {C_TEAL};
                border: 1px solid {C_TEAL};
                font-family: Georgia, serif; font-size: 10px;
                padding: 3px 14px; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: {C_TEAL}; color: {C_WHITE}; }}
            QPushButton:pressed {{ background: #154f4f; }}
            QPushButton:disabled {{
                color: {C_SUBTLE}; border-color: {C_SUBTLE};
            }}
        """)
        self._export_btn.clicked.connect(self._on_export)
        layout.addWidget(self._export_btn)

        return footer

    def _wire_signals(self) -> None:
        # ProjectTree → window
        self._project_tree.conversation_selected.connect(self._on_conversation_selected)
        self._project_tree.conversation_created.connect(self._on_conversation_selected)
        self._project_tree.conversation_deleted.connect(self._on_conversation_deleted)

        # BuildDocWatcher → footer combo
        self._build_watcher.docs_changed.connect(self._on_build_docs_changed)

        # ChatPane → window
        self._chat_pane.send_requested.connect(self._on_send_requested)
        self._chat_pane.attachment_add_requested.connect(self._on_attachment_add)

        # Bridge → ChatPane / OutputPanel / Gauge
        self._bridge.token_received.connect(self._chat_pane.append_token)
        self._bridge.response_complete.connect(self._on_response_complete)
        self._bridge.error_occurred.connect(self._on_error)
        self._bridge.token_usage_updated.connect(self._gauge.update_exact)
        self._bridge.phase_changed.connect(self._chat_pane.set_phase)
        self._bridge.compression_complete.connect(
            self._chat_pane.show_compression_notice
        )
        self._bridge.send_finished.connect(self._on_send_finished)

        # OutputPanel → PreviewPane
        self._output_panel.file_selected.connect(self._preview_pane.load_file)

    def _restore_session(self) -> None:
        """Restore last active conversation on launch, if any."""
        last_id = self._store.restore_last_active()
        if last_id:
            self._load_conversation(last_id)
            self._project_tree.select_conversation(last_id)

    # -----------------------------------------------------------------------
    # Conversation management
    # -----------------------------------------------------------------------

    def _on_conversation_selected(self, conv_id: str) -> None:
        if conv_id == self._conv_id:
            return
        self._load_conversation(conv_id)

    def _on_conversation_deleted(self, conv_id: str) -> None:
        if conv_id == self._conv_id:
            self._conv_id = None
            self._chat_pane.clear()
            self._output_panel.clear()
            self._preview_pane.clear()
            self._gauge.reset()
            self._conv_title_label.setText("")
            self._export_btn.setEnabled(False)

    def _load_conversation(self, conv_id: str) -> None:
        """Switch to a conversation — restore history and output files."""
        self._conv_id = conv_id

        conv = self._store.get_conversation(conv_id)
        title = conv.title if conv else conv_id
        emit_event("build_session_opened", {
            "session_id": conv_id,
            "build_doc": title,
        })
        self._conv_title_label.setText(f"  {title}  ·  {conv.last_active_at[:10] if conv else ''}")

        # Chat history
        messages = self._store.get_messages(conv_id)
        self._chat_pane.clear()
        self._chat_pane.load_history(messages)

        # Output files
        self._output_panel.clear()
        output_files = self._store.get_output_files(conv_id)
        if output_files:
            self._output_panel.load_files(output_files)

        # Preview
        self._preview_pane.clear()

        # Gauge — estimate from stored messages
        payload = self._context_engine.assemble_payload(conv_id)
        self._gauge.update_exact(payload.estimated_tokens, 0)

        # Export button
        self._export_btn.setEnabled(self._zip_exporter.can_export(conv_id))

        self._set_status(f"The forge is open — {title}")

    # -----------------------------------------------------------------------
    # Send pipeline
    # -----------------------------------------------------------------------

    def _on_send_requested(self, text: str, attachment_ids: list[str]) -> None:
        if self._conv_id is None:
            self._set_status("No conversation selected.")
            return

        if self._bridge.is_active():
            return

        # Save user message
        self._store.save_message(self._conv_id, "user", text)
        self._chat_pane.append_user_message(text)

        # Assemble payload
        payload = self._context_engine.assemble_payload(self._conv_id)

        # Check compression threshold
        if self._context_engine.threshold_exceeded(payload.estimated_tokens):
            self._run_compression_then_send(text)
        else:
            self._do_send(payload)

    def _do_send(self, payload) -> None:
        """Dispatch to bridge."""
        self._bridge.send(payload.system_block, payload.messages_array)

    def _run_compression_then_send(self, original_text: str) -> None:
        """Compress oldest turns, then reassemble payload and send."""
        conv_id = self._conv_id

        def on_done(record):
            preview = self._compression_engine.summary_preview(record)
            self._bridge.emit_compression_complete(preview)
            # Reassemble and send
            payload = self._context_engine.assemble_payload(conv_id)
            self._do_send(payload)

        def on_error(msg: str):
            logger.error("Compression failed: %s — sending without compression.", msg)
            payload = self._context_engine.assemble_payload(conv_id)
            self._do_send(payload)

        worker = _CompressionWorker(
            self._compression_engine, conv_id, on_done, on_error
        )
        self._pool.start(worker)

    def _on_send_finished(self) -> None:
        """Update export button after every response."""
        if self._conv_id:
            self._export_btn.setEnabled(self._zip_exporter.can_export(self._conv_id))

    # -----------------------------------------------------------------------
    # Response handling
    # -----------------------------------------------------------------------

    def _on_response_complete(self, full_text: str) -> None:
        if self._conv_id is None:
            return

        prose, files, phase = ResponseParser.parse(full_text)

        # Finalise streaming bubble
        self._chat_pane.finalise_stream(prose)

        # Phase indicator
        if phase:
            self._chat_pane.set_phase(phase)

        # Persist assistant message
        self._store.save_message(self._conv_id, "assistant", full_text)

        # Output files
        for f in files:
            self._store.save_output_file(
                self._conv_id, f.filename, f.language, f.content, f.description
            )
            self._output_panel.add_file(f)

    def _on_error(self, message: str) -> None:
        self._chat_pane.show_error(message)
        self._set_status(f"Error — {message[:60]}")

    # -----------------------------------------------------------------------
    # Attachment pipeline
    # -----------------------------------------------------------------------

    def _on_attachment_add(self) -> None:
        if self._conv_id is None:
            return

        conv = self._store.get_conversation(self._conv_id)
        proj_id = conv.project_id if conv else None

        conv_atts = self._store.get_attachments(conversation_id=self._conv_id)
        proj_atts = self._store.get_attachments(project_id=proj_id) if proj_id else []
        all_atts  = conv_atts + proj_atts

        if all_atts:
            # Show dialog to re-attach existing
            dlg = AttachmentDialog(all_atts, parent=self)
            # Also offer to add new file
            dlg_result = dlg.exec()
            selected = dlg.selected_ids() if dlg_result else []
            for att in all_atts:
                if att.id in selected:
                    self._chat_pane.add_attachment_chip(att)
        else:
            # No existing attachments — go straight to file picker
            self._pick_and_attach_file()

    def _pick_and_attach_file(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Attach File", str(Path.home()),
            "All Files (*)"
        )
        if not path_str:
            return

        path = Path(path_str)
        conv_id = self._conv_id
        conv = self._store.get_conversation(conv_id) if conv_id else None
        proj_id = conv.project_id if conv else None

        self._set_status(f"Attaching {path.name}…")

        def on_done(att):
            self._chat_pane.add_attachment_chip(att)
            if att.summary_cache is None:
                self._set_status(f"⚠ {path.name} attached — summarisation failed. Retry available.")
            else:
                self._set_status(f"{path.name} attached and summarised.")

        def on_error(msg: str):
            self._set_status(f"Error attaching {path.name}: {msg}")

        worker = _AttachWorker(
            self._attachment_manager, path,
            "conversation", conv_id, proj_id,
            on_done, on_error,
        )
        self._pool.start(worker)

    # -----------------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------------

    def _on_export(self) -> None:
        if self._conv_id is None:
            return

        conv = self._store.get_conversation(self._conv_id)
        default_name = f"{conv.title.replace(' ', '_')}_package.zip" if conv else "package.zip"

        dest_str, _ = QFileDialog.getSaveFileName(
            self, "Export Package",
            str(Path.home() / default_name),
            "Zip Archives (*.zip)"
        )
        if not dest_str:
            return

        dest = Path(dest_str)
        try:
            self._zip_exporter.assemble_package(self._conv_id, dest)
            self._output_panel.mark_all_exported()
            self._export_btn.setEnabled(False)
            self._set_status(f"Package exported — {dest.name}")
        except ExportError as exc:
            self._set_status(f"Export failed: {exc}")

    # -----------------------------------------------------------------------
    # Build doc pick list
    # -----------------------------------------------------------------------

    def _on_build_docs_changed(self, docs: list) -> None:
        self._build_docs = docs
        self._build_doc_combo.clear()
        self._build_doc_combo.addItem("— no build doc —")
        for doc in docs:
            self._build_doc_combo.addItem(doc.title, str(doc.path))
        if docs:
            self._set_status(f"{len(docs)} build doc(s) available from Dolium")

    def get_active_build_doc(self) -> str | None:
        """Return the path of the selected build doc, or None."""
        idx = self._build_doc_combo.currentIndex()
        if idx <= 0:
            return None
        return self._build_doc_combo.currentData()

    # -----------------------------------------------------------------------
    # Status bar
    # -----------------------------------------------------------------------

    def _set_status(self, message: str) -> None:
        bar = self.statusBar()
        bar.setStyleSheet(
            f"QStatusBar {{ background: {C_PANEL}; color: {C_GOLD_DIM}; "
            f"font-family: Georgia, serif; font-size: 10px; "
            f"border-top: 1px solid {C_GOLD_DARK}; }}"
        )
        bar.showMessage(f"  {message}", 8000)

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._conv_id:
            emit_event("build_session_closed", {
                "session_id": self._conv_id,
                "duration_minutes": None,
            })
        self._bridge.teardown()
        super().closeEvent(event)
