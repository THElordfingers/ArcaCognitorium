"""
ui/dialogs.py — Dolium v2
All modal QDialog subclasses.
Each returns a result via .exec() and exposes result properties.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QSizePolicy, QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import style
from models import Idea, CHAMBER_NAMES
from chambers import GateResult


# ── Base ──────────────────────────────────────────────────────────────────────

class ArcaneDialog(QDialog):
    """Base class with Modus Arcanus styling."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {style.C_BG};
                color: {style.C_TEXT};
                font-family: Georgia, Constantia, serif;
            }}
            QLabel {{
                color: {style.C_TEXT};
                font-family: Georgia, Constantia, serif;
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 16, 18, 16)
        self._layout.setSpacing(12)

        # Dialog title
        h = style.gold_label(title.upper(), size=10, bold=True)
        h.setStyleSheet(f"""
            QLabel {{
                color: {style.C_GOLD_DIM};
                font-family: Georgia, Constantia, serif;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
        """)
        self._layout.addWidget(h)
        self._layout.addWidget(style.h_rule())

    def _button_row(self, confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                    danger: bool = False):
        row = QHBoxLayout()
        row.addStretch()

        cancel = style.arcane_button(cancel_text)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)

        if danger:
            confirm = style.danger_button(confirm_text)
        else:
            confirm = style.arcane_button(confirm_text)
        confirm.clicked.connect(self.accept)
        row.addWidget(confirm)

        return row


# ── NewIdeaDialog ─────────────────────────────────────────────────────────────

class NewIdeaDialog(ArcaneDialog):

    def __init__(self, parent=None):
        super().__init__("New Idea", parent)
        self.setMinimumWidth(380)

        self._layout.addWidget(style.dim_label("Name this idea to begin.", size=11))

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Title...")
        self._title_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {style.C_PANEL};
                color: {style.C_WHITE};
                border: 1px solid {style.C_BORDER};
                border-radius: 2px;
                padding: 6px 8px;
                font-family: Georgia, Constantia, serif;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {style.C_GOLD_DIM};
            }}
        """)
        self._title_input.returnPressed.connect(self.accept)
        self._layout.addWidget(self._title_input)

        self._layout.addLayout(self._button_row("Create", "Cancel"))
        self._title_input.setFocus()

    @property
    def title(self) -> str:
        return self._title_input.text().strip()


# ── AdvanceDialog ─────────────────────────────────────────────────────────────

class AdvanceDialog(ArcaneDialog):
    """Shows gate result. Green if passed, red checklist if not."""

    def __init__(self, idea: Idea, result: GateResult, parent=None):
        super().__init__("Advance Chamber", parent)
        self.setMinimumWidth(360)

        from_name = CHAMBER_NAMES.get(idea.chamber, f"Chamber {idea.chamber}")
        to_num    = idea.chamber + 1
        to_name   = CHAMBER_NAMES.get(to_num, f"Chamber {to_num}")

        self._layout.addWidget(style.dim_label(f"{from_name}  →  {to_name}", size=11))

        if result.passed:
            ok = style.gold_label("◈  Gate clear. Ready to advance.", size=11)
            ok.setStyleSheet(f"color: {style.C_SUCCESS}; font-family: Georgia, serif; font-size: 11px;")
            self._layout.addWidget(ok)
            self._layout.addLayout(self._button_row("Advance ›", "Cancel"))
        else:
            fail_lbl = style.dim_label("Conditions not met:", size=10)
            self._layout.addWidget(fail_lbl)

            for failure in result.failures:
                row = QHBoxLayout()
                x_lbl = QLabel("✕")
                x_lbl.setStyleSheet(f"color: {style.C_CRIMSON}; font-size: 12px;")
                x_lbl.setFixedWidth(18)
                row.addWidget(x_lbl)
                row.addWidget(style.dim_label(failure, size=10))
                row.addStretch()
                container = QWidget()
                container.setLayout(row)
                self._layout.addWidget(container)

            close = style.arcane_button("Return to Work")
            close.clicked.connect(self.reject)
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            btn_row.addWidget(close)
            self._layout.addLayout(btn_row)


# ── ReturnToDialog ────────────────────────────────────────────────────────────

class ReturnToDialog(ArcaneDialog):

    def __init__(self, idea: Idea, parent=None):
        super().__init__("Return to Chamber", parent)
        self.setMinimumWidth(320)
        self._selected_chamber = None

        self._layout.addWidget(style.dim_label(
            f"Return '{idea.title or '(untitled)'}' to an earlier chamber.", size=10
        ))

        self._combo = QComboBox()
        self._combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                border: 1px solid {style.C_BORDER};
                border-radius: 2px;
                padding: 4px 8px;
                font-family: Georgia, Constantia, serif;
                font-size: 11px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                selection-background-color: {style.C_GOLD_DARK};
            }}
        """)
        for n in range(1, idea.chamber):
            self._combo.addItem(CHAMBER_NAMES[n], n)
        self._layout.addWidget(self._combo)

        self._layout.addLayout(self._button_row("Return ‹", "Cancel"))

    @property
    def selected_chamber(self) -> int | None:
        return self._combo.currentData()


# ── CullDialog ────────────────────────────────────────────────────────────────

class CullDialog(ArcaneDialog):

    def __init__(self, idea: Idea, parent=None):
        super().__init__("Cull Idea", parent)
        self.setMinimumWidth(360)

        self._layout.addWidget(style.dim_label(
            f"Cull '{idea.title or '(untitled)'}' from the pipeline.\nThis can be undone from the Cull Register.",
            size=10
        ))

        self._reason_input = QTextEdit()
        self._reason_input.setPlaceholderText("Why is this being culled?")
        self._reason_input.setFixedHeight(80)
        self._reason_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                border: 1px solid {style.C_BORDER};
                border-radius: 2px;
                padding: 6px;
                font-family: Georgia, Constantia, serif;
                font-size: 11px;
            }}
        """)
        self._layout.addWidget(self._reason_input)
        self._layout.addLayout(self._button_row("Cull", "Cancel", danger=True))

    @property
    def reason(self) -> str:
        return self._reason_input.toPlainText().strip()


# ── DeclarationDialog ─────────────────────────────────────────────────────────

class DeclarationDialog(ArcaneDialog):

    def __init__(self, idea: Idea, result: GateResult, parent=None):
        super().__init__("Declaration", parent)
        self.setMinimumWidth(400)

        if result.passed:
            self._layout.addWidget(style.gold_label(
                f"'{idea.title or '(untitled)'}' is ready to be declared.",
                size=11
            ))
            self._layout.addWidget(style.dim_label(
                "Declaration marks this idea complete. Export options will follow.",
                size=10
            ))
            self._layout.addLayout(self._button_row("Declare ◈", "Cancel"))
        else:
            self._layout.addWidget(style.dim_label("Declaration gate not met:", size=10))
            for f in result.failures:
                row_w = QWidget()
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                x = QLabel("✕")
                x.setStyleSheet(f"color: {style.C_CRIMSON}; font-size: 12px;")
                x.setFixedWidth(18)
                row_l.addWidget(x)
                row_l.addWidget(style.dim_label(f, size=10))
                row_l.addStretch()
                self._layout.addWidget(row_w)
            close = style.arcane_button("Return to Work")
            close.clicked.connect(self.reject)
            r = QHBoxLayout()
            r.addStretch()
            r.addWidget(close)
            self._layout.addLayout(r)


# ── ExportDialog ──────────────────────────────────────────────────────────────

class ExportDialog(ArcaneDialog):

    def __init__(self, idea: Idea, export_results: dict, parent=None):
        super().__init__("Export", parent)
        self.setMinimumWidth(360)

        self._layout.addWidget(style.gold_label(
            f"'{idea.title or '(untitled)'}' exported.", size=11
        ))

        for fmt, path in export_results.items():
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 2, 0, 2)

            if path:
                tick = QLabel("✓")
                tick.setStyleSheet(f"color: {style.C_SUCCESS}; font-size: 12px;")
                tick.setFixedWidth(18)
                row_l.addWidget(tick)
                row_l.addWidget(style.dim_label(f".{fmt}  —  {path.name}", size=10))
            else:
                dash = QLabel("—")
                dash.setStyleSheet(f"color: {style.C_DIM}; font-size: 12px;")
                dash.setFixedWidth(18)
                row_l.addWidget(dash)
                row_l.addWidget(style.dim_label(f".{fmt}  skipped", size=10))
            row_l.addStretch()
            self._layout.addWidget(row_w)

        close = style.arcane_button("Close")
        close.clicked.connect(self.accept)
        r = QHBoxLayout()
        r.addStretch()
        r.addWidget(close)
        self._layout.addLayout(r)


# ── CullRegisterDialog ────────────────────────────────────────────────────────

class CullRegisterDialog(ArcaneDialog):
    """Lists culled ideas with option to resurrect."""

    resurrect_requested = None  # set dynamically after construction if needed

    def __init__(self, culled_ideas: list[Idea], parent=None):
        super().__init__("Cull Register", parent)
        self.setMinimumWidth(420)
        self.setMinimumHeight(300)
        self._selected_id = None

        if not culled_ideas:
            self._layout.addWidget(style.dim_label("No ideas in the cull register.", size=11))
        else:
            self._layout.addWidget(style.dim_label(
                "Culled ideas. Select one to resurrect.", size=10
            ))
            self._list = QListWidget()
            self._list.setStyleSheet(f"""
                QListWidget {{
                    background-color: {style.C_PANEL};
                    color: {style.C_TEXT};
                    border: 1px solid {style.C_BORDER};
                    font-family: Georgia, Constantia, serif;
                    font-size: 11px;
                }}
                QListWidget::item:selected {{
                    background-color: {style.C_GOLD_DARK};
                    color: {style.C_GOLD};
                }}
            """)
            for idea in culled_ideas:
                item = QListWidgetItem(
                    f"{idea.title or '(untitled)'}  ·  {CHAMBER_NAMES.get(idea.chamber, '')}"
                )
                item.setData(Qt.ItemDataRole.UserRole, idea.id)
                self._list.addItem(item)
            self._layout.addWidget(self._list)

            res_btn = style.arcane_button("Resurrect")
            res_btn.clicked.connect(self._on_resurrect)
            close = style.arcane_button("Close")
            close.clicked.connect(self.accept)
            r = QHBoxLayout()
            r.addStretch()
            r.addWidget(close)
            r.addWidget(res_btn)
            self._layout.addLayout(r)

    def _on_resurrect(self) -> None:
        items = self._list.selectedItems()
        if items:
            self._selected_id = items[0].data(Qt.ItemDataRole.UserRole)
            self.accept()

    @property
    def selected_id(self) -> str | None:
        return self._selected_id
