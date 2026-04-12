#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                       ui/attachment_dialog.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"


class AttachmentDialog(QDialog):
    """
    Lists all attachments for the current conversation and project.
    Wizard checks items to re-add them to the current turn injection list.
    Returns selected attachment ids via selected_ids().
    """

    def __init__(self, attachments: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Re-attach Files")
        self.setMinimumWidth(460)
        self.setMinimumHeight(320)
        self._selected_ids: list[str] = []
        self._build_ui(attachments)
        self._apply_style()

    # -----------------------------------------------------------------------
    # Public
    # -----------------------------------------------------------------------

    def selected_ids(self) -> list[str]:
        """Return list of attachment ids checked by the Wizard."""
        return list(self._selected_ids)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _build_ui(self, attachments: list) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        instr = QLabel("Select files to re-inject into the current turn:")
        instr.setStyleSheet(f"""
            color: {C_GOLD_DIM};
            font-family: Georgia, serif;
            font-size: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(instr)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: {C_BG};
                color: {C_TEXT};
                font-family: Georgia, serif;
                font-size: 11px;
                border: 1px solid {C_GOLD_DARK};
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
        """)

        if not attachments:
            empty = QListWidgetItem("  No attachments in this conversation or project.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            empty.setForeground(QColor(C_GOLD_DIM))
            self._list.addItem(empty)
        else:
            for att in attachments:
                scope_tag = f"[{att.scope}]"
                if att.summary_cache:
                    status_tag = "✓"
                    colour = C_TEXT
                else:
                    status_tag = "⚠ unsummarised"
                    colour = C_GOLD_DIM
                label = f"📎  {att.filename}  {scope_tag}  {status_tag}"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, att.id)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setForeground(QColor(colour))
                self._list.addItem(item)

        layout.addWidget(self._list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL};
                color: {C_GOLD};
                border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif;
                font-size: 11px;
                padding: 5px 18px;
                letter-spacing: 1px;
                min-width: 70px;
            }}
            QPushButton:hover {{ background: {C_GOLD_DARK}; border-color: {C_GOLD}; }}
            QPushButton:pressed {{ background: {C_SUBTLE}; }}
        """)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _apply_style(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background: {C_PANEL};
                color: {C_TEXT};
                font-family: Georgia, serif;
            }}
        """)

    def _on_accept(self) -> None:
        self._selected_ids = [
            self._list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
            and self._list.item(i).data(Qt.ItemDataRole.UserRole) is not None
        ]
        self.accept()
