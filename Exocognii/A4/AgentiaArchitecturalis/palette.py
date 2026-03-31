# Agentia Architecturalis — palette.py
# v1.0.0
"""Categorized element palette — the Elementarium."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtGui import QDrag

from .constants import PALETTE_CATEGORIES, ELEMENT_REGISTRY


class PaletteItem(QPushButton):
    """A single draggable element in the palette."""

    def __init__(self, element_type: str, display_name: str,
                 description: str, parent=None):
        super().__init__(display_name, parent)
        self._element_type = element_type
        self.setToolTip(description)
        self.setFixedHeight(26)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self._element_type)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.CopyAction)


class PaletteCategory(QWidget):
    """Collapsible category group in the palette."""

    def __init__(self, category_id: str, label: str,
                 elements: list[str], parent=None):
        super().__init__(parent)
        self._expanded = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._header = QPushButton(f'\u25b8 {label}')
        self._header.setFixedHeight(24)
        self._header.setStyleSheet(
            'QPushButton { text-align: left; padding-left: 8px; '
            'font-size: 10px; letter-spacing: 1px; }'
        )
        self._header.clicked.connect(self._toggle)
        layout.addWidget(self._header)

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(12, 0, 0, 4)
        self._container_layout.setSpacing(2)

        for et in elements:
            info = ELEMENT_REGISTRY.get(et, ('unknown', et, ''))
            item = PaletteItem(et, info[1], info[2])
            self._container_layout.addWidget(item)

        layout.addWidget(self._container)

    def _toggle(self):
        self._expanded = not self._expanded
        self._container.setVisible(self._expanded)
        arrow = '\u25be' if self._expanded else '\u25b8'
        text = self._header.text()
        self._header.setText(f'{arrow}{text[1:]}')


class ElementPalette(QScrollArea):
    """The Elementarium — full categorized element browser."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setMinimumWidth(150)
        self.setMaximumWidth(180)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        title = QLabel('ELEMENTARIUM')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        for cat in PALETTE_CATEGORIES:
            group = PaletteCategory(
                cat['id'], cat['label'], cat['elements']
            )
            layout.addWidget(group)

        layout.addStretch()
        self.setWidget(inner)
