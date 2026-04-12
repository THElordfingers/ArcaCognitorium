#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                           ui/project_tree.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.session_store import SessionStore

logger = logging.getLogger("arx.project_tree")

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"

_ROLE_ID   = Qt.ItemDataRole.UserRole        # conversation_id or project_id
_ROLE_TYPE = Qt.ItemDataRole.UserRole + 1    # "conversation" | "project"


class ProjectTree(QWidget):
    """
    Left-pane project/conversation hierarchy.

    Projects are top-level nodes; conversations are children.
    Ungrouped conversations appear below a dashed separator at tree root.

    Drag-drop (InternalMove) reorders conversations and reassigns them
    between projects. Drop handler writes new project_id to SQLite.

    Signals
    -------
    conversation_selected(str) — emits conversation_id on click.
    conversation_created(str)  — emits new conversation_id.
    conversation_deleted(str)  — emits deleted conversation_id.
    """

    conversation_selected = pyqtSignal(str)
    conversation_created  = pyqtSignal(str)
    conversation_deleted  = pyqtSignal(str)

    def __init__(self, store: SessionStore, parent=None) -> None:
        super().__init__(parent)
        self._store = store
        self._loading = False  # suppress selection signals during reload
        self._build_ui()
        self.reload()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def reload(self) -> None:
        """Rebuild the tree from the database."""
        self._loading = True
        self._tree.blockSignals(True)
        self._tree.clear()

        projects = self._store.get_all_projects()
        for project in projects:
            p_item = QTreeWidgetItem([f"▸  {project.name}"])
            p_item.setData(0, _ROLE_ID, project.id)
            p_item.setData(0, _ROLE_TYPE, "project")
            p_item.setForeground(0, QColor(C_GOLD))
            p_item.setFont(0, QFont("Georgia", 10, QFont.Weight.Bold))
            p_item.setFlags(
                p_item.flags()
                | Qt.ItemFlag.ItemIsDropEnabled
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            convs = self._store.get_conversations_for_project(project.id)
            for conv in convs:
                c_item = self._make_conv_item(conv)
                p_item.addChild(c_item)
            self._tree.addTopLevelItem(p_item)
            p_item.setExpanded(True)

        # Separator
        sep = QTreeWidgetItem(["  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─"])
        sep.setFlags(Qt.ItemFlag.NoItemFlags)
        sep.setForeground(0, QColor(C_SUBTLE))
        sep.setFont(0, QFont("Georgia", 8))
        self._tree.addTopLevelItem(sep)

        ungrouped = self._store.get_ungrouped_conversations()
        for conv in ungrouped:
            c_item = self._make_conv_item(conv)
            self._tree.addTopLevelItem(c_item)

        self._tree.blockSignals(False)
        self._loading = False

    def select_conversation(self, conversation_id: str) -> None:
        """Programmatically select a conversation item by id."""
        self._loading = True
        self._tree.blockSignals(True)
        it = self._find_item(conversation_id)
        if it:
            self._tree.setCurrentItem(it)
        self._tree.blockSignals(False)
        self._loading = False

    # -----------------------------------------------------------------------
    # Private — UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet(f"background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK};")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(4, 4, 4, 4)
        tb_layout.setSpacing(4)

        for label, slot in [("+ Conv", self._new_conversation),
                             ("+ Proj", self._new_project),
                             ("Del",    self._delete_selected)]:
            btn = QPushButton(label)
            btn.setFixedHeight(22)
            colour = C_CRIMSON if label == "Del" else C_GOLD
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_PANEL}; color: {colour};
                    border: 1px solid {C_GOLD_DARK};
                    font-family: Georgia, serif; font-size: 10px;
                    padding: 2px 8px; letter-spacing: 1px;
                }}
                QPushButton:hover {{ background: {C_GOLD_DARK}; border-color: {colour}; }}
                QPushButton:pressed {{ background: {C_SUBTLE}; }}
            """)
            btn.clicked.connect(slot)
            tb_layout.addWidget(btn)
        tb_layout.addStretch()
        layout.addWidget(toolbar)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {C_BG}; color: {C_TEXT};
                font-family: Georgia, serif; font-size: 11px;
                border: none; outline: none;
            }}
            QTreeWidget::item {{
                padding: 4px 4px; border-bottom: 1px solid {C_SUBTLE};
            }}
            QTreeWidget::item:selected {{
                background: {C_GOLD_DARK}; color: {C_GOLD};
                border-left: 2px solid {C_GOLD};
            }}
            QTreeWidget::item:hover {{ background: {C_PANEL}; }}
            QScrollBar:vertical {{
                background: {C_PANEL}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self._tree.dropEvent = self._on_drop
        self._tree.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._tree)

    def _make_conv_item(self, conv) -> QTreeWidgetItem:
        item = QTreeWidgetItem([f"  ●  {conv.title}"])
        item.setData(0, _ROLE_ID, conv.id)
        item.setData(0, _ROLE_TYPE, "conversation")
        item.setForeground(0, QColor(C_TEXT))
        item.setFont(0, QFont("Georgia", 10))
        item.setFlags(
            item.flags()
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )
        return item

    # -----------------------------------------------------------------------
    # Private — event handlers
    # -----------------------------------------------------------------------

    def _on_selection(self, current: QTreeWidgetItem, _prev) -> None:
        if self._loading or current is None:
            return
        if current.data(0, _ROLE_TYPE) == "conversation":
            conv_id = current.data(0, _ROLE_ID)
            if conv_id:
                self.conversation_selected.emit(conv_id)

    def _on_drop(self, event) -> None:
        """Handle drag-drop. Update project_id in SQLite after Qt moves item."""
        dragged = self._tree.currentItem()
        if dragged is None or dragged.data(0, _ROLE_TYPE) != "conversation":
            QTreeWidget.dropEvent(self._tree, event)
            return

        conv_id = dragged.data(0, _ROLE_ID)
        # Let Qt handle the visual move first
        QTreeWidget.dropEvent(self._tree, event)

        new_parent = dragged.parent()
        if new_parent is None or new_parent.data(0, _ROLE_TYPE) != "project":
            # Dropped at root — ungrouped
            try:
                self._store.update_conversation_project(conv_id, None)
            except Exception as exc:
                logger.error("Drop handler: failed to ungroup conversation: %s", exc)
                self.reload()
        else:
            project_id = new_parent.data(0, _ROLE_ID)
            try:
                self._store.update_conversation_project(conv_id, project_id)
            except Exception as exc:
                logger.error("Drop handler: failed to reassign conversation: %s", exc)
                self.reload()

    def _new_conversation(self) -> None:
        title, ok = QInputDialog.getText(
            self, "New Conversation", "Title:", text="Untitled"
        )
        if not ok or not title.strip():
            return

        # Assign to currently selected project if one is selected
        project_id = None
        current = self._tree.currentItem()
        if current:
            if current.data(0, _ROLE_TYPE) == "project":
                project_id = current.data(0, _ROLE_ID)
            elif current.data(0, _ROLE_TYPE) == "conversation":
                parent = current.parent()
                if parent and parent.data(0, _ROLE_TYPE) == "project":
                    project_id = parent.data(0, _ROLE_ID)

        conv_id = self._store.create_conversation(title.strip(), project_id=project_id)
        self.reload()
        self.select_conversation(conv_id)
        self.conversation_created.emit(conv_id)

    def _new_project(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Project", "Project name:"
        )
        if not ok or not name.strip():
            return
        self._store.create_project(name.strip())
        self.reload()

    def _delete_selected(self) -> None:
        current = self._tree.currentItem()
        if current is None:
            return

        item_type = current.data(0, _ROLE_TYPE)
        item_id   = current.data(0, _ROLE_ID)

        if item_type == "conversation":
            reply = QMessageBox.question(
                self, "Delete Conversation",
                f"Delete this conversation and all its messages?\n\n"
                f"This cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._store.delete_conversation(item_id)
                self.reload()
                self.conversation_deleted.emit(item_id)

        elif item_type == "project":
            reply = QMessageBox.question(
                self, "Delete Project",
                f"Delete this project? Conversations inside will become ungrouped.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._store.delete_project(item_id)
                self.reload()

    def _find_item(self, conversation_id: str) -> QTreeWidgetItem | None:
        """Recursively search for an item by conversation_id."""
        def _search(item: QTreeWidgetItem) -> QTreeWidgetItem | None:
            if item.data(0, _ROLE_ID) == conversation_id:
                return item
            for i in range(item.childCount()):
                result = _search(item.child(i))
                if result:
                    return result
            return None

        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            result = _search(root.child(i))
            if result:
                return result
        return None
