"""
ui/widgets.py — Dolium v2
Reusable atomic widgets: ArcaneField, GateBar.
These compose into the larger panels.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QProgressBar, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor

import style
from chambers import GateResult


# ── ArcaneField ───────────────────────────────────────────────────────────────

class ArcaneField(QWidget):
    """
    A labelled QTextEdit with character counter.
    Used for all idea text fields in WorkspacePanel.
    Emits text_changed(field_name, text) on every keystroke.
    """

    text_changed = pyqtSignal(str, str)  # (field_name, text)

    def __init__(
        self,
        field_name:  str,
        label:       str,
        placeholder: str = "",
        min_height:  int = 80,
        required:    bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self._field_name = field_name
        self._required   = required

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Header row: label + char counter
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        lbl_text = f"{label}  ◆" if required else label
        self._label = style.gold_label(lbl_text, size=10)
        self._counter = style.dim_label("", size=9)
        self._counter.setAlignment(Qt.AlignmentFlag.AlignRight)

        header.addWidget(self._label)
        header.addStretch()
        header.addWidget(self._counter)
        layout.addLayout(header)

        # Text surface
        self._edit = style.arcane_text_edit(placeholder)
        self._edit.setMinimumHeight(min_height)
        self._edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._edit)

    def _on_text_changed(self) -> None:
        text = self._edit.toPlainText()
        count = len(text.strip())
        self._counter.setText(f"{count}")
        self.text_changed.emit(self._field_name, text)

    def set_text(self, text: str) -> None:
        """Set text without emitting signals (for load operations)."""
        self._edit.blockSignals(True)
        self._edit.setPlainText(text)
        self._edit.blockSignals(False)
        count = len(text.strip())
        self._counter.setText(f"{count}")

    def get_text(self) -> str:
        return self._edit.toPlainText()

    def set_read_only(self, value: bool) -> None:
        self._edit.setReadOnly(value)

    def field_name(self) -> str:
        return self._field_name

    def append_text(self, text: str) -> None:
        """Append text to the field (used by /save command pattern)."""
        cursor = self._edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self._edit.setTextCursor(cursor)


# ── GateBar ───────────────────────────────────────────────────────────────────

class GateBar(QWidget):
    """
    Displays current gate status.
    Shows a progress bar, condition count, and the advance/return/cull buttons.
    """

    advance_requested = pyqtSignal()
    return_requested  = pyqtSignal()
    cull_requested    = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: GateResult | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        # Gate status line
        self._status_label = style.dim_label("", size=10)
        layout.addWidget(self._status_label)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setMaximum(100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(3)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {style.C_BORDER};
                border: none;
                border-radius: 1px;
            }}
            QProgressBar::chunk {{
                background-color: {style.C_GOLD_DIM};
                border-radius: 1px;
            }}
        """)
        layout.addWidget(self._progress)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(6)

        self._advance_btn = style.arcane_button("Advance ›")
        self._return_btn  = style.arcane_button("Return ‹", accent=style.C_DIM, small=True)
        self._cull_btn    = style.danger_button("Cull")
        self._cull_btn.setFixedWidth(50)

        self._advance_btn.clicked.connect(self.advance_requested)
        self._return_btn.clicked.connect(self.return_requested)
        self._cull_btn.clicked.connect(self.cull_requested)

        btn_row.addWidget(self._advance_btn)
        btn_row.addWidget(self._return_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._cull_btn)
        layout.addLayout(btn_row)

        self.setStyleSheet(f"""
            GateBar {{
                background-color: {style.C_PANEL};
                border-top: 1px solid {style.C_BORDER};
            }}
        """)

    def update_gate(self, result: GateResult, chamber: int) -> None:
        self._result = result
        self._advance_btn.setEnabled(result.passed)

        if result.passed:
            from models import CHAMBER_CODEX
            if chamber >= CHAMBER_CODEX:
                self._status_label.setText("◈  Ready for Declaration")
                self._advance_btn.setText("Declare ›")
            else:
                self._status_label.setText("◈  Gate clear — ready to advance")
                self._advance_btn.setText("Advance ›")
            self._progress.setValue(100)
            self._progress.setStyleSheet(self._progress.styleSheet().replace(
                style.C_GOLD_DIM, style.C_SUCCESS
            ))
        else:
            count = len(result.failures)
            noun  = "condition" if count == 1 else "conditions"
            self._status_label.setText(f"◇  {count} {noun} remaining")
            self._advance_btn.setText("Advance ›")
            # Rough progress: each failure reduces from 100
            pct = max(0, 100 - (count * 33))
            self._progress.setValue(pct)
            self._progress.setStyleSheet(self._progress.styleSheet().replace(
                style.C_SUCCESS, style.C_GOLD_DIM
            ))

    def get_failures(self) -> list[str]:
        if self._result:
            return self._result.failures
        return []
