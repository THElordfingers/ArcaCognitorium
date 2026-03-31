# Agentia Architecturalis — elements/base.py
# v1.0.0
"""Abstract base class for all canvas elements."""

import uuid
from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QWidget
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor, QFont

from ..constants import ELEMENT_DEFAULTS, MODUS_ARCANUS_DEFAULTS, FONT_STACK


class CanvasElement(ABC):
    """Base class for all elements placeable on the design canvas."""

    def __init__(self, element_type: str, category: str):
        self.id = str(uuid.uuid4())
        self.element_type = element_type
        self.category = category
        self.properties: dict = self._default_properties()
        self.children: list['CanvasElement'] = []
        self.graphics_item: QGraphicsRectItem | None = None
        self._label_item: QGraphicsTextItem | None = None

    @abstractmethod
    def _default_properties(self) -> dict:
        """Return default PropertySet for this element type."""
        ...

    @abstractmethod
    def configurable_properties(self) -> list[str]:
        """Return list of property names the inspector should show."""
        ...

    @abstractmethod
    def create_preview_widget(self, tokens: dict) -> QWidget:
        """Create the real PyQt6 widget for live preview."""
        ...

    @abstractmethod
    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        """Generate Python/PyQt6 code lines for this element."""
        ...

    def create_graphics_item(self, x: float, y: float,
                             w: float, h: float,
                             tokens: dict = None) -> QGraphicsRectItem:
        """Create the QGraphicsItem for canvas rendering."""
        tokens = tokens or MODUS_ARCANUS_DEFAULTS
        bg = tokens.get(self.properties.get('bg_token', 'c_panel'), '#0a0a12')
        border = tokens.get(self.properties.get('border_token', 'c_gold_dark'), '#3a2e10')

        rect = QGraphicsRectItem(0, 0, w, h)
        rect.setPos(x, y)
        rect.setBrush(QBrush(QColor(bg)))
        rect.setPen(QPen(QColor(border), 1))
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        rect.setData(0, self.id)  # store element id

        # Type label
        label = QGraphicsTextItem(self.element_type, rect)
        label.setDefaultTextColor(QColor(tokens.get('c_gold_dim', '#7a6a2a')))
        font = QFont('Georgia', 8)
        label.setFont(font)
        label.setPos(4, 2)

        # Variable name label
        var_label = QGraphicsTextItem(
            self.properties.get('variable_name', ''), rect
        )
        var_label.setDefaultTextColor(QColor(tokens.get('c_gold', '#d4af37')))
        var_label.setFont(QFont('Georgia', 7))
        var_label.setPos(4, 16)

        self.graphics_item = rect
        self._label_item = label
        return rect

    def serialize(self) -> dict:
        """Serialize to ElementNode dict."""
        return {
            'id': self.id,
            'element_type': self.element_type,
            'element_category': self.category,
            'properties': dict(self.properties),
            'children': [c.serialize() for c in self.children],
            'x': self.graphics_item.pos().x() if self.graphics_item else 0,
            'y': self.graphics_item.pos().y() if self.graphics_item else 0,
        }

    @classmethod
    def deserialize(cls, node: dict) -> 'CanvasElement':
        """Reconstruct from ElementNode dict. Subclasses override."""
        raise NotImplementedError("Use element_factory() instead")

    def accepts_children(self) -> bool:
        return self.category == 'container'

    def update_property(self, key: str, value):
        """Update a single property."""
        self.properties[key] = value

    def _base_defaults(self) -> dict:
        """Get category-level defaults."""
        return dict(ELEMENT_DEFAULTS.get(self.category, {}))
