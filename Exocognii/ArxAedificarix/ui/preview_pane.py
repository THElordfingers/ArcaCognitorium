#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            ui/preview_pane.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.response_parser import OutputFile
from ui.arcane_highlighter import ArcaneHighlighter

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_TEAL      = "#1a5a5a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"


class PreviewPane(QWidget):
    """
    Syntax-highlighted read-only display for a selected OutputFile.
    Copy button writes content to clipboard via xclip (X11).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_file: OutputFile | None = None
        self._highlighter: ArcaneHighlighter | None = None
        self._build_ui()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def load_file(self, f: OutputFile) -> None:
        """Display a file in the preview. Attaches appropriate highlighter."""
        self._current_file = f

        # Header
        self._filename_label.setText(f"  {f.filename}")
        self._desc_label.setText(f"  {f.description}" if f.description else "")

        # Content — set plain text first, then apply highlighter
        self._editor.setPlainText(f.content)

        # Swap highlighter
        if self._highlighter:
            self._highlighter.setDocument(None)
        self._highlighter = ArcaneHighlighter(f.language, self._editor.document())

        self._copy_btn.setEnabled(True)

    def clear(self) -> None:
        """Clear display. Called on conversation switch."""
        self._current_file = None
        self._filename_label.setText("  PREVIEW")
        self._desc_label.setText("")
        self._editor.clear()
        if self._highlighter:
            self._highlighter.setDocument(None)
            self._highlighter = None
        self._copy_btn.setEnabled(False)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header row
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK};")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 8, 0)

        self._filename_label = QLabel("  PREVIEW")
        self._filename_label.setStyleSheet(f"""
            color: {C_GOLD};
            font-family: Georgia, serif;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 6px 0px;
        """)
        header_layout.addWidget(self._filename_label)
        header_layout.addStretch()

        self._copy_btn = QPushButton("Copy")
        self._copy_btn.setEnabled(False)
        self._copy_btn.setFixedHeight(24)
        self._copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL};
                color: {C_GOLD};
                border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif;
                font-size: 10px;
                padding: 2px 10px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: {C_GOLD_DARK}; border-color: {C_GOLD}; }}
            QPushButton:pressed {{ background: {C_SUBTLE}; }}
            QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
        """)
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        header_layout.addWidget(self._copy_btn)
        layout.addWidget(header_widget)

        # Description label
        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet(f"""
            color: {C_GOLD_DIM};
            font-family: Georgia, serif;
            font-size: 10px;
            font-style: italic;
            padding: 3px 8px;
            background: {C_PANEL};
            border-bottom: 1px solid {C_SUBTLE};
        """)
        self._desc_label.setVisible(False)
        layout.addWidget(self._desc_label)

        # Editor (read-only)
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setFont(QFont("Monospace", 10))
        self._editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C_BG};
                color: {C_TEXT};
                border: none;
                font-family: Monospace, 'Courier New', monospace;
                font-size: 10px;
                padding: 8px;
            }}
            QScrollBar:vertical {{
                background: {C_PANEL}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar:horizontal {{
                background: {C_PANEL}; height: 8px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {C_GOLD_DARK}; border-radius: 4px;
            }}
        """)
        layout.addWidget(self._editor)

    def _copy_to_clipboard(self) -> None:
        if self._current_file is None:
            return
        content = self._current_file.content
        try:
            proc = subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=content.encode("utf-8"),
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            # xclip not available — fall back to Qt clipboard
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(content)
