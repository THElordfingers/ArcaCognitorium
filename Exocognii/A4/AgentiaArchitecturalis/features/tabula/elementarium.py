"""
Elementarium — categorised drag source panel (110px width).

Intra-Tabula panel. Part of Zone IV, not Zone II.
Elements are dragged from here onto the canvas grid.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
)

from ... import tokens
from .element_registry import CATEGORIES


class _ElementItem(QLabel):
    """A draggable element item in the palette."""

    def __init__(self, display_name: str, element_type: str, parent: QWidget | None = None) -> None:
        super().__init__(display_name, parent)
        self.element_type = element_type
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_TEXT}; "
            f"padding: 2px 8px 2px 16px; "
            f"font-family: {tokens.FONT_MONO};"
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.element_type)
            mime.setData("application/x-aa-element", self.element_type.encode("utf-8"))
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.CopyAction)

    def enterEvent(self, event) -> None:
        self.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD}; "
            f"padding: 2px 8px 2px 16px; "
            f"font-family: {tokens.FONT_MONO}; "
            f"background: rgba(212,175,55,0.04);"
        )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_TEXT}; "
            f"padding: 2px 8px 2px 16px; "
            f"font-family: {tokens.FONT_MONO};"
        )
        super().leaveEvent(event)


class _CategoryHeader(QLabel):
    """Collapsible category header."""

    def __init__(self, name: str, parent: QWidget | None = None) -> None:
        super().__init__(f"\u25be {name}", parent)
        self._expanded = True
        self._name = name
        self._items: list[_ElementItem] = []
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; "
            f"padding: 4px 8px 2px; letter-spacing: 0.5px;"
        )

    def register_item(self, item: _ElementItem) -> None:
        self._items.append(item)

    def mousePressEvent(self, event) -> None:
        self._expanded = not self._expanded
        prefix = "\u25be" if self._expanded else "\u25b8"
        self.setText(f"{prefix} {self._name}")
        for item in self._items:
            item.setVisible(self._expanded)
        super().mousePressEvent(event)


class Elementarium(QFrame):
    """Categorised element palette, 110px width."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(110)
        self.setObjectName("elementarium")
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        head = QLabel("Elementarium")
        head.setStyleSheet(
            f"font-size: 7px; letter-spacing: 2px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; padding: 0 8px 5px; "
            f"border-bottom: 1px solid {tokens.C_GOLD_DARK};"
        )
        outer.addWidget(head)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 3, 0, 0)
        layout.setSpacing(0)

        for cat_name, elements in CATEGORIES:
            header = _CategoryHeader(cat_name)
            layout.addWidget(header)
            for edef in elements:
                item = _ElementItem(edef.display_name, edef.element_type)
                header.register_item(item)
                layout.addWidget(item)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"Elementarium {{ background: {tokens.C_PANEL}; "
            f"border-right: 1px solid {tokens.C_GOLD_DARK}; "
            f"font-family: {tokens.FONT_MONO}; font-size: 8.5px; }}"
        )
