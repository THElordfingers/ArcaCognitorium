#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/todo_board.py                                          ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/todo_board.py
# Tabbed TODO / Notice board. Multiple named lists, independent persistence.
# version: 2.0.0

import json
import uuid
from pathlib import Path

from PyQt6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QPushButton, QTabWidget,
    QInputDialog, QTabBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

DEFAULT_TAB = "General"


class _TodoList(QWidget):
    """Single list — items, input, scroll. Standalone QWidget, not ArcaneWidget."""

    changed = pyqtSignal()   # emit on any mutation so parent can save

    def __init__(self, items: list[dict], parent=None):
        super().__init__(parent)
        self._items = items
        self._build()

    def _build(self) -> None:
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)

        # Input row
        row = QHBoxLayout()
        row.setSpacing(4)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Add note…")
        self._input.setStyleSheet(
            f"QLineEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 3px 6px; }}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._input.returnPressed.connect(self._add)
        row.addWidget(self._input)
        btn = arcane_button("+ ADD")
        btn.setFixedHeight(24)
        btn.clicked.connect(self._add)
        row.addWidget(btn)
        vbox.addLayout(row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        vbox.addWidget(sep)

        # Scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {C_BG}; }}")
        self._inner = QWidget()
        self._inner.setStyleSheet(f"background: {C_BG};")
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(2)
        self._inner_layout.addStretch()
        self._scroll.setWidget(self._inner)
        vbox.addWidget(self._scroll)

        self._render()

    def _render(self) -> None:
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for rec in self._items:
            self._inner_layout.insertWidget(
                self._inner_layout.count() - 1,
                self._make_row(rec),
            )

    def _make_row(self, rec: dict) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C_BG};")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(6)

        done = rec.get("done", False)
        check = QPushButton("☑" if done else "☐")
        check.setFixedSize(20, 20)
        check.setStyleSheet(
            f"QPushButton {{ background: transparent; color: "
            f"{'#1a9a1a' if done else C_GOLD_DIM}; border: none; font-size: 12px; }}"
            f"QPushButton:hover {{ color: {C_TEAL}; }}"
        )
        item_id = rec["id"]
        check.clicked.connect(lambda _, i=item_id: self._toggle(i))
        row.addWidget(check)

        lbl = QLabel(rec["text"])
        lbl.setWordWrap(True)
        strike = "text-decoration: line-through;" if done else ""
        lbl.setStyleSheet(
            f"color: {C_GOLD_DIM if done else C_TEXT}; "
            f"font-family: Georgia, serif; font-size: 10px; {strike}"
        )
        row.addWidget(lbl, 1)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(16, 16)
        btn_del.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_GOLD_DARK}; border: none; font-size: 9px; }}"
            f"QPushButton:hover {{ color: {C_CRIMSON}; }}"
        )
        btn_del.clicked.connect(lambda _, i=item_id: self._delete(i))
        row.addWidget(btn_del)
        return container

    def _add(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._items.insert(0, {"id": str(uuid.uuid4()), "text": text, "done": False})
        self._input.clear()
        self._render()
        self.changed.emit()

    def _toggle(self, item_id: str) -> None:
        for r in self._items:
            if r["id"] == item_id:
                r["done"] = not r["done"]
                break
        self._render()
        self.changed.emit()

    def _delete(self, item_id: str) -> None:
        self._items = [r for r in self._items if r["id"] != item_id]
        self._render()
        self.changed.emit()

    def get_items(self) -> list[dict]:
        return self._items

    def pending_count(self) -> int:
        return sum(1 for r in self._items if not r.get("done"))


class TodoBoard(ArcaneWidget):
    """
    Tabbed persistent notice board.
    Each tab is a named list stored independently.
    Data: storage/widget_state/todo_tabs.json
    """

    def __init__(self, widget_id: str, storage_path: Path, parent=None):
        super().__init__(widget_id, "Todo · Notice Board", parent)
        self._path = Path(storage_path) / "widget_state" / "todo_tabs.json"
        self._data: dict[str, list] = {}   # tab_name → [items]
        self._load()
        self._build_body()
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Tab bar controls
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(4)
        btn_new_tab = arcane_button("+ TAB")
        btn_new_tab.setFixedHeight(22)
        btn_new_tab.clicked.connect(self._add_tab)
        ctrl_row.addWidget(btn_new_tab)

        btn_rename = arcane_button("✎ RENAME")
        btn_rename.setFixedHeight(22)
        btn_rename.clicked.connect(self._rename_tab)
        ctrl_row.addWidget(btn_rename)

        btn_del_tab = arcane_button("✕ TAB")
        btn_del_tab.setFixedHeight(22)
        btn_del_tab.clicked.connect(self._delete_tab)
        ctrl_row.addWidget(btn_del_tab)
        ctrl_row.addStretch()
        L.addLayout(ctrl_row)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {C_BG};
                border: 1px solid {C_GOLD_DARK};
                border-top: none;
            }}
            QTabBar::tab {{
                background: {C_PANEL};
                color: {C_GOLD_DIM};
                border: 1px solid {C_GOLD_DARK};
                border-bottom: none;
                padding: 4px 10px;
                font-family: Georgia, serif;
                font-size: 9px;
                letter-spacing: 1px;
            }}
            QTabBar::tab:selected {{
                background: {C_BG};
                color: {C_GOLD};
                border-bottom: 1px solid {C_BG};
            }}
            QTabBar::tab:hover {{
                color: {C_GOLD};
            }}
        """)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        L.addWidget(self._tabs, 1)

        # Populate tabs
        if not self._data:
            self._data[DEFAULT_TAB] = []
        for name, items in self._data.items():
            self._create_tab_widget(name, items)

    # ------------------------------------------------------------------
    # Tab management
    # ------------------------------------------------------------------

    def _create_tab_widget(self, name: str, items: list) -> _TodoList:
        todo = _TodoList(items)
        todo.changed.connect(self._on_changed)
        self._tabs.addTab(todo, name.upper())
        return todo

    def _add_tab(self) -> None:
        name, ok = QInputDialog.getText(self, "New Tab", "Tab name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self._data:
            return
        self._data[name] = []
        self._create_tab_widget(name, [])
        self._tabs.setCurrentIndex(self._tabs.count() - 1)
        self._save()

    def _rename_tab(self) -> None:
        idx = self._tabs.currentIndex()
        if idx < 0:
            return
        old_name = self._get_tab_name(idx)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "New name:", text=old_name)
        if not ok or not new_name.strip() or new_name == old_name:
            return
        new_name = new_name.strip()
        # Migrate data
        self._data[new_name] = self._data.pop(old_name)
        self._tabs.setTabText(idx, new_name.upper())
        self._save()

    def _delete_tab(self) -> None:
        if self._tabs.count() <= 1:
            return   # never delete the last tab
        idx = self._tabs.currentIndex()
        name = self._get_tab_name(idx)
        self._data.pop(name, None)
        self._tabs.removeTab(idx)
        self._save()

    def _get_tab_name(self, idx: int) -> str:
        """Recover original-case name from _data matching the tab label."""
        label = self._tabs.tabText(idx).upper()
        for name in self._data:
            if name.upper() == label:
                return name
        return self._tabs.tabText(idx)

    def _on_tab_changed(self, idx: int) -> None:
        self._update_status()

    def _on_changed(self) -> None:
        # Sync widget items back to _data
        for i in range(self._tabs.count()):
            name = self._get_tab_name(i)
            widget = self._tabs.widget(i)
            if isinstance(widget, _TodoList):
                self._data[name] = widget.get_items()
        self._save()
        self._update_status()

    def _update_status(self) -> None:
        total_pending = sum(
            w.pending_count()
            for i in range(self._tabs.count())
            if isinstance((w := self._tabs.widget(i)), _TodoList)
        )
        self.set_status(
            "ok" if total_pending == 0 else "warn",
            f"{total_pending} open"
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            # Migrate from old single-list format if it exists
            old = self._path.parent / "todo_board.json"
            if old.exists():
                try:
                    items = json.loads(old.read_text())
                    self._data = {DEFAULT_TAB: items}
                    return
                except Exception:
                    pass
            return
        try:
            self._data = json.loads(self._path.read_text())
        except Exception:
            self._data = {}

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._data, indent=2))
            tmp.replace(self._path)
        except Exception:
            pass
