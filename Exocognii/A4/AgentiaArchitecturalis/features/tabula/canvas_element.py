"""
CanvasElement — QGraphicsRectItem wrapper for design elements.

Each element on the canvas is a CanvasElement with:
- A QGraphicsRectItem representing its bounds
- A type label and var_name label
- Serialization to/from ElementNode
- Child management via setParentItem()
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
)

from ...models import ElementNode
from ... import tokens
from .element_registry import get_element_def


GRID_SIZE = 16


class CanvasElement:
    """A design element on the canvas, backed by a QGraphicsRectItem."""

    def __init__(
        self,
        element_type: str,
        var_name: str,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
        properties: dict | None = None,
        parent_element: CanvasElement | None = None,
    ) -> None:
        edef = get_element_def(element_type)
        self.element_type = element_type
        self.var_name = var_name
        self.category = edef.category if edef else ""
        self._accepts_children = edef.accepts_children if edef else False
        self.properties: dict = dict(properties or {})

        w = width or (edef.default_width if edef else 200)
        h = height or (edef.default_height if edef else 100)

        # Ensure width/height in properties
        self.properties.setdefault("width", w)
        self.properties.setdefault("height", h)
        self.properties.setdefault("var_name", var_name)

        # Create graphics item
        self.graphics_item = QGraphicsRectItem(0, 0, w, h)
        self.graphics_item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.graphics_item.setData(0, self)  # back-reference

        # Set parent if provided
        if parent_element:
            self.graphics_item.setParentItem(parent_element.graphics_item)
            self.graphics_item.setPos(x, y)
        else:
            self.graphics_item.setPos(x, y)

        # Style
        self._apply_default_style()
        self._build_labels()

        # Children tracking
        self.children: list[CanvasElement] = []
        self.parent_element: CanvasElement | None = parent_element

    def _apply_default_style(self) -> None:
        pen = QPen(QColor(tokens.C_GOLD_DARK))
        pen.setWidth(1)
        self.graphics_item.setPen(pen)
        self.graphics_item.setBrush(QBrush(QColor(tokens.C_PANEL)))

    def _build_labels(self) -> None:
        mono = QFont("Courier New", 7)

        # Type label
        self._type_label = QGraphicsTextItem(self.graphics_item)
        self._type_label.setFont(mono)
        self._type_label.setDefaultTextColor(QColor(tokens.C_GOLD_DIM))
        self._type_label.setPlainText(self.element_type)
        self._type_label.setPos(3, 2)

        # Name label
        self._name_label = QGraphicsTextItem(self.graphics_item)
        name_font = QFont("Courier New", 8)
        name_font.setBold(True)
        self._name_label.setFont(name_font)
        self._name_label.setDefaultTextColor(QColor(tokens.C_GOLD))
        self._name_label.setPlainText(self.var_name)
        self._name_label.setPos(3, 14)

    def accepts_children(self) -> bool:
        return self._accepts_children

    def add_child(self, child: CanvasElement) -> None:
        child.graphics_item.setParentItem(self.graphics_item)
        child.parent_element = self
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child: CanvasElement) -> None:
        child.graphics_item.setParentItem(None)
        child.parent_element = None
        if child in self.children:
            self.children.remove(child)

    def set_selected_style(self, selected: bool) -> None:
        if selected:
            pen = QPen(QColor(tokens.C_GOLD))
            pen.setWidth(2)
        else:
            pen = QPen(QColor(tokens.C_GOLD_DARK))
            pen.setWidth(1)
        self.graphics_item.setPen(pen)

    def resize(self, width: int, height: int) -> None:
        self.properties["width"] = width
        self.properties["height"] = height
        self.graphics_item.setRect(0, 0, width, height)

    def update_var_name(self, name: str) -> None:
        self.var_name = name
        self.properties["var_name"] = name
        self._name_label.setPlainText(name)

    def refresh_tokens(self, token_dict: dict[str, str]) -> None:
        """Repaint element with updated tokens — no clearing required."""
        bg = self.properties.get("bg_token", "C_PANEL")
        border = self.properties.get("border_token", "C_GOLD_DARK")
        bg_color = token_dict.get(bg, tokens.C_PANEL)
        border_color = token_dict.get(border, tokens.C_GOLD_DARK)
        self.graphics_item.setBrush(QBrush(QColor(bg_color)))
        pen = self.graphics_item.pen()
        pen.setColor(QColor(border_color))
        self.graphics_item.setPen(pen)

    def snap_to_grid(self) -> None:
        pos = self.graphics_item.pos()
        sx = round(pos.x() / GRID_SIZE) * GRID_SIZE
        sy = round(pos.y() / GRID_SIZE) * GRID_SIZE
        self.graphics_item.setPos(sx, sy)

    def serialize(self) -> ElementNode:
        """Serialize to ElementNode. x/y are parent-relative."""
        pos = self.graphics_item.pos()
        return ElementNode(
            element_type=self.element_type,
            var_name=self.var_name,
            category=self.category,
            properties=dict(self.properties),
            children=[c.serialize() for c in self.children],
            x=int(pos.x()),
            y=int(pos.y()),
        )

    @classmethod
    def from_node(
        cls,
        node: ElementNode,
        parent_element: CanvasElement | None = None,
    ) -> CanvasElement:
        """Deserialize from ElementNode. Reconstructs parent hierarchy."""
        elem = cls(
            element_type=node.element_type,
            var_name=node.var_name,
            x=node.x,
            y=node.y,
            width=node.properties.get("width"),
            height=node.properties.get("height"),
            properties=node.properties,
            parent_element=parent_element,
        )
        for child_node in node.children:
            child = cls.from_node(child_node, parent_element=elem)
            elem.children.append(child)
        return elem
