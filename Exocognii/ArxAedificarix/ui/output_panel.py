#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            ui/output_panel.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.response_parser import OutputFile

# ModusArcanus
C_BG       = "#050507"
C_PANEL    = "#0a0a12"
C_GOLD     = "#d4af37"
C_GOLD_DIM = "#7a6a2a"
C_GOLD_DARK= "#3a2e10"
C_TEAL     = "#1a5a5a"
C_CRIMSON  = "#8b1a1a"
C_TEXT     = "#c8b88a"
C_SUBTLE   = "#3a3528"

_STATUS_COLOURS = {
    "pending":  C_GOLD_DIM,
    "ready":    C_GOLD,
    "exported": C_TEAL,
}

_STATUS_LABELS = {
    "pending":  "PEND.",
    "ready":    "READY",
    "exported": "EXPORTED",
}


class OutputPanel(QWidget):
    """
    Right-pane file list. Displays generated output files with state badges.
    State transitions: pending → ready (on parse) → exported (on zip write).

    Emits file_selected(OutputFile) on click for PreviewPane population.
    """

    file_selected = pyqtSignal(object)  # OutputFile

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # filename → (OutputFile, status)
        self._files: dict[str, tuple[OutputFile, str]] = {}
        self._build_ui()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def add_file(self, f: OutputFile) -> None:
        """
        Register a newly parsed file. Initial state: ready.
        If a file with the same filename already exists, it is replaced
        (handles re-delivery of a file in the same session).
        """
        self._files[f.filename] = (f, "ready")
        self._sync_list()

    def mark_exported(self, filename: str) -> None:
        """Transition a file's state to exported."""
        if filename in self._files:
            f, _ = self._files[filename]
            self._files[filename] = (f, "exported")
            self._sync_list()

    def mark_all_exported(self) -> None:
        """Mark all files exported. Called after ZipExporter completes."""
        self._files = {
            fn: (f, "exported") for fn, (f, _) in self._files.items()
        }
        self._sync_list()

    def clear(self) -> None:
        """Clear all files. Called on conversation switch."""
        self._files.clear()
        self._list.clear()

    def load_files(self, output_files: list) -> None:
        """
        Populate from SessionStore OutputFile rows on conversation restore.
        Accepts SessionStore OutputFile dataclasses (have .export_status).
        """
        self._files.clear()
        for f in output_files:
            status = "exported" if getattr(f, "export_status", "") == "exported" else "ready"
            # Wrap in response_parser.OutputFile shape if needed
            if not isinstance(f, OutputFile):
                wrapped = OutputFile(
                    filename=f.filename,
                    language=f.language,
                    content=f.content,
                    description=f.description,
                )
            else:
                wrapped = f
            self._files[wrapped.filename] = (wrapped, status)
        self._sync_list()

    def has_pending(self) -> bool:
        """Return True if any file is not yet exported."""
        return any(status != "exported" for _, status in self._files.values())

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("  OUTPUT FILES")
        header.setStyleSheet(f"""
            QLabel {{
                background: {C_PANEL};
                color: {C_GOLD};
                font-family: Georgia, serif;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 6px 8px;
                border-bottom: 1px solid {C_GOLD_DARK};
            }}
        """)
        layout.addWidget(header)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: {C_BG};
                color: {C_TEXT};
                font-family: Georgia, serif;
                font-size: 11px;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-bottom: 1px solid {C_SUBTLE};
            }}
            QListWidget::item:selected {{
                background: {C_GOLD_DARK};
                color: {C_GOLD};
            }}
            QListWidget::item:hover {{
                background: {C_PANEL};
            }}
            QScrollBar:vertical {{
                background: {C_PANEL}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self._list.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._list)

    def _sync_list(self) -> None:
        """Rebuild the list widget from self._files."""
        # Remember selection
        selected_fn = None
        current = self._list.currentItem()
        if current:
            selected_fn = current.data(Qt.ItemDataRole.UserRole)

        self._list.blockSignals(True)
        self._list.clear()

        for filename, (f, status) in self._files.items():
            badge   = _STATUS_LABELS.get(status, status.upper())
            colour  = _STATUS_COLOURS.get(status, C_TEXT)
            item = QListWidgetItem(f"⬡  {filename}    [{badge}]")
            item.setData(Qt.ItemDataRole.UserRole, filename)
            item.setForeground(QColor(colour))
            item.setFont(QFont("Georgia", 10))
            self._list.addItem(item)

        # Restore selection
        if selected_fn:
            for i in range(self._list.count()):
                if self._list.item(i).data(Qt.ItemDataRole.UserRole) == selected_fn:
                    self._list.setCurrentRow(i)
                    break

        self._list.blockSignals(False)

    def _on_selection(
        self, current: QListWidgetItem, _previous: QListWidgetItem
    ) -> None:
        if current:
            filename = current.data(Qt.ItemDataRole.UserRole)
            entry = self._files.get(filename)
            if entry:
                self.file_selected.emit(entry[0])
