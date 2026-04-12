# GNOSIUM EXANIMA — ui/session_dialog.py
# v1.0.0
"""Session picker dialog: list, switch, new, delete."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox,
    QPushButton, QVBoxLayout,
)

from ..constants import C_BG, C_GOLD, C_GOLD_DARK, C_GOLD_DIM, C_PANEL, C_TEXT
from ..session.manager import SessionManager
from ..session.store import SessionRow


class SessionDialog(QDialog):
    def __init__(
        self,
        manager: SessionManager,
        current_mode: str,
        parent=None,
    ):
        super().__init__(parent)
        self._manager = manager
        self._mode = current_mode
        self.selected_session_id: Optional[str] = None
        self.created_new_session: bool = False

        self.setWindowTitle(f"Sessions — {current_mode.upper()}")
        self.setMinimumSize(560, 420)
        self.setStyleSheet(f"background: {C_BG}; color: {C_TEXT};")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        self._list = QListWidget()
        self._list.setFont(QFont("Georgia", 10))
        self._list.setStyleSheet(
            f"QListWidget {{ background: {C_PANEL}; color: {C_TEXT}; "
            f"border: 1px solid {C_GOLD_DARK}; }}"
            f"QListWidget::item {{ padding: 6px; }}"
            f"QListWidget::item:selected {{ background: {C_GOLD_DARK}; color: {C_GOLD}; }}"
        )
        root.addWidget(self._list, 1)

        button_row = QHBoxLayout()
        self._btn_switch = self._button("Switch")
        self._btn_new = self._button("New")
        self._btn_delete = self._button("Delete")
        self._btn_cancel = self._button("Cancel")
        button_row.addWidget(self._btn_switch)
        button_row.addWidget(self._btn_new)
        button_row.addWidget(self._btn_delete)
        button_row.addStretch(1)
        button_row.addWidget(self._btn_cancel)
        root.addLayout(button_row)

        self._btn_switch.clicked.connect(self._on_switch)
        self._btn_new.clicked.connect(self._on_new)
        self._btn_delete.clicked.connect(self._on_delete)
        self._btn_cancel.clicked.connect(self.reject)

        self._populate()

    def _button(self, text: str):
        btn = QPushButton(text)
        btn.setFont(QFont("Cinzel", 9))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton {{ background: {C_PANEL}; color: {C_GOLD}; "
            f"border: 1px solid {C_GOLD_DARK}; padding: 6px 16px; letter-spacing: 2px; }}"
            f"QPushButton:hover {{ background: {C_GOLD_DARK}; }}"
            f"QPushButton:disabled {{ color: {C_GOLD_DIM}; }}"
        )
        return btn

    def _populate(self) -> None:
        self._list.clear()
        for row in self._manager.list_for_mode(self._mode):
            item = QListWidgetItem(self._format_row(row))
            item.setData(Qt.ItemDataRole.UserRole, row.id)
            if row.is_current:
                item.setForeground(Qt.GlobalColor.yellow)
            self._list.addItem(item)

    def _format_row(self, row: SessionRow) -> str:
        marker = "★ " if row.is_current else "  "
        title = row.title or "(untitled)"
        updated = row.updated_at.split("T")[0]
        return (
            f"{marker}{title}  —  {updated}  —  "
            f"{len(row.active_entities)} entities"
        )

    def _selected_id(self) -> Optional[str]:
        item = self._list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _on_switch(self) -> None:
        sid = self._selected_id()
        if not sid:
            return
        self.selected_session_id = sid
        self.accept()

    def _on_new(self) -> None:
        self.created_new_session = True
        self.accept()

    def _on_delete(self) -> None:
        sid = self._selected_id()
        if not sid:
            return
        confirm = QMessageBox.question(
            self,
            "Delete session",
            "Delete this session permanently? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._manager.delete(sid)
        self._populate()
