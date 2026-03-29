"""
ui/pipeline_panel.py — Dolium v2
PipelinePanel: left panel showing chamber tree and idea list.
Emits idea_selected(str) when the user selects an idea.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import style
from models import Idea, CHAMBER_NAMES
from store import IdeaStore


class PipelinePanel(QWidget):

    idea_selected    = pyqtSignal(str)   # idea_id
    new_idea_clicked = pyqtSignal()

    def __init__(self, store: IdeaStore, parent=None):
        super().__init__(parent)
        self._store       = store
        self._current_id  = None

        self.setFixedWidth(260)
        self.setStyleSheet(f"background-color: {style.C_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-bottom: 1px solid {style.C_BORDER};
        """)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(10, 8, 10, 8)
        h_layout.setSpacing(6)

        title_lbl = style.gold_label("◆  PIPELINE", size=9, bold=True)
        title_lbl.setStyleSheet(f"""
            QLabel {{
                color: {style.C_GOLD_DIM};
                font-family: Georgia, Constantia, serif;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
        """)
        h_layout.addWidget(title_lbl)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("/ search...")
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {style.C_BG};
                color: {style.C_TEXT};
                border: 1px solid {style.C_BORDER};
                border-radius: 2px;
                padding: 3px 6px;
                font-family: Georgia, Constantia, serif;
                font-size: 10px;
            }}
            QLineEdit:focus {{
                border-color: {style.C_GOLD_DIM};
            }}
        """)
        self._search.textChanged.connect(self._on_search)
        h_layout.addWidget(self._search)
        layout.addWidget(header)

        # ── Tree ──────────────────────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(12)
        self._tree.setAnimated(False)
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                border: none;
                font-family: Georgia, Constantia, serif;
                font-size: 11px;
                outline: 0;
            }}
            QTreeWidget::item {{
                padding: 3px 4px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background-color: {style.C_GOLD_DARK};
                color: {style.C_GOLD};
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {style.C_SUBTLE};
            }}
        """)
        layout.addWidget(self._tree)

        # ── Footer buttons ────────────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-top: 1px solid {style.C_BORDER};
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(8, 6, 8, 6)

        new_btn = style.arcane_button("+ New Idea")
        new_btn.clicked.connect(self.new_idea_clicked)
        f_layout.addWidget(new_btn)
        f_layout.addStretch()
        layout.addWidget(footer)

        self.refresh()

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh(self, select_id: str | None = None) -> None:
        """Rebuild the tree from store. Optionally select an idea by id."""
        self._tree.blockSignals(True)
        self._tree.clear()

        query = self._search.text().strip().lower()

        for chamber_num in range(1, 5):
            ideas = self._store.by_chamber(chamber_num)
            if query:
                ideas = [i for i in ideas if query in i.title.lower()]

            # Chamber root item
            name = CHAMBER_NAMES[chamber_num]
            root = QTreeWidgetItem([name])
            root.setData(0, Qt.ItemDataRole.UserRole, None)
            root.setFont(0, self._chamber_font())
            root.setForeground(0, self._chamber_brush(chamber_num))
            self._tree.addTopLevelItem(root)

            if ideas:
                for idea in ideas:
                    child = QTreeWidgetItem([f"  {idea.title or '(untitled)'}"])
                    child.setData(0, Qt.ItemDataRole.UserRole, idea.id)
                    child.setFont(0, self._idea_font())
                    root.addChild(child)
                    if idea.id == (select_id or self._current_id):
                        self._tree.setCurrentItem(child)
            else:
                empty = QTreeWidgetItem(["   — empty —"])
                empty.setData(0, Qt.ItemDataRole.UserRole, None)
                empty.setForeground(0, self._dim_brush())
                empty.setFont(0, self._dim_font())
                root.addChild(empty)

            root.setExpanded(True)

        self._tree.blockSignals(False)

    def set_current_idea(self, idea_id: str) -> None:
        self._current_id = idea_id
        self.refresh(select_id=idea_id)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        idea_id = item.data(0, Qt.ItemDataRole.UserRole)
        if idea_id:
            self._current_id = idea_id
            self.idea_selected.emit(idea_id)

    def _on_search(self, text: str) -> None:
        self.refresh()

    # ── Font / brush helpers ──────────────────────────────────────────────────

    def _chamber_font(self) -> QFont:
        f = QFont("Georgia")
        f.setPointSize(9)
        f.setBold(False)
        return f

    def _idea_font(self) -> QFont:
        f = QFont("Georgia")
        f.setPointSize(10)
        return f

    def _dim_font(self) -> QFont:
        f = QFont("Georgia")
        f.setPointSize(9)
        f.setItalic(True)
        return f

    def _chamber_brush(self, chamber: int):
        from PyQt6.QtGui import QBrush, QColor
        return QBrush(QColor(style.chamber_accent(chamber)))

    def _dim_brush(self):
        from PyQt6.QtGui import QBrush, QColor
        return QBrush(QColor(style.C_DIM))
