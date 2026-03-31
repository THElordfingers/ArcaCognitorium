# Agentia Architecturalis — canvas.py
# v1.0.0
"""QGraphicsScene-based design canvas with element management."""

import json
import copy

from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QWidget, QVBoxLayout,
)
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QBrush, QPainter

from .elements.base import CanvasElement
from .elements.factory import create_element, deserialize_element
from .constants import MODUS_ARCANUS_DEFAULTS


class DesignCanvas(QGraphicsView):
    """Main design surface. Manages element placement and selection."""

    element_selected = pyqtSignal(object)   # CanvasElement or None
    design_changed = pyqtSignal()
    element_dropped = pyqtSignal(str, float, float)

    def __init__(self, parent=None):
        self._scene = QGraphicsScene()
        super().__init__(self._scene, parent)
        self._elements: list[CanvasElement] = []
        self._all_elements: dict[str, CanvasElement] = {}  # id -> element
        self._selected: CanvasElement | None = None
        self._grid_visible = True
        self._snap_to_grid = True
        self._grid_size = 16
        self._zoom = 1.0
        self._tokens = dict(MODUS_ARCANUS_DEFAULTS)
        self._undo_stack: list[list[dict]] = []
        self._redo_stack: list[list[dict]] = []
        self._counter: dict[str, int] = {}

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        self._scene.setSceneRect(0, 0, 2000, 2000)
        self._draw_grid()

    def set_tokens(self, tokens: dict):
        self._tokens = tokens

    def add_element(self, element_type: str, x: float, y: float,
                    parent: CanvasElement = None) -> CanvasElement:
        """Place an element on the canvas."""
        self._push_undo()
        element = create_element(element_type)

        # Auto-name with counter
        base = element_type.lower().replace(' ', '_')
        self._counter[base] = self._counter.get(base, 0) + 1
        element.properties['variable_name'] = f"{base}_{self._counter[base]}"

        pos = self._snap_position(QPointF(x, y))
        w = element.properties.get('width', 200) or 200
        h = element.properties.get('height', 100) or 100
        gi = element.create_graphics_item(pos.x(), pos.y(), w, h, self._tokens)
        self._scene.addItem(gi)

        if parent and parent.accepts_children():
            parent.children.append(element)
        else:
            self._elements.append(element)

        self._all_elements[element.id] = element
        self.design_changed.emit()
        return element

    def remove_selected(self):
        if not self._selected:
            return
        self._push_undo()
        self._remove_element(self._selected)
        self._selected = None
        self.element_selected.emit(None)
        self.design_changed.emit()

    def _remove_element(self, element: CanvasElement):
        if element.graphics_item:
            self._scene.removeItem(element.graphics_item)
        if element in self._elements:
            self._elements.remove(element)
        self._all_elements.pop(element.id, None)
        # Remove from any parent
        for e in self._all_elements.values():
            if element in e.children:
                e.children.remove(element)

    def duplicate_selected(self):
        if not self._selected:
            return
        self._push_undo()
        node = self._selected.serialize()
        node['x'] = node.get('x', 0) + 20
        node['y'] = node.get('y', 0) + 20
        new_elem = deserialize_element(node)
        import uuid
        new_elem.id = str(uuid.uuid4())
        w = new_elem.properties.get('width', 200) or 200
        h = new_elem.properties.get('height', 100) or 100
        gi = new_elem.create_graphics_item(node['x'], node['y'], w, h, self._tokens)
        self._scene.addItem(gi)
        self._elements.append(new_elem)
        self._all_elements[new_elem.id] = new_elem
        self.design_changed.emit()

    def group_selected(self):
        """Wrap selected elements in a QFrame container."""
        # Simplified: works with single selection for now
        if not self._selected:
            return
        self._push_undo()
        container = create_element('QFrame')
        container.properties['variable_name'] = 'group_frame'
        container.children.append(self._selected)
        if self._selected in self._elements:
            idx = self._elements.index(self._selected)
            self._elements[idx] = container
        self._all_elements[container.id] = container
        self.design_changed.emit()

    def ungroup_selected(self):
        if not self._selected or not self._selected.accepts_children():
            return
        self._push_undo()
        children = list(self._selected.children)
        if self._selected in self._elements:
            idx = self._elements.index(self._selected)
            self._elements.pop(idx)
            for child in children:
                self._elements.insert(idx, child)
                idx += 1
        self._selected.children.clear()
        self._remove_element(self._selected)
        self._selected = None
        self.element_selected.emit(None)
        self.design_changed.emit()

    def serialize_all(self) -> list[dict]:
        return [e.serialize() for e in self._elements]

    def deserialize_all(self, nodes: list[dict]):
        self.clear_canvas()
        for node in nodes:
            element = deserialize_element(node)
            self._place_deserialized(element, node.get('x', 0), node.get('y', 0))

    def _place_deserialized(self, element: CanvasElement, x: float, y: float):
        w = element.properties.get('width', 200) or 200
        h = element.properties.get('height', 100) or 100
        gi = element.create_graphics_item(x, y, w, h, self._tokens)
        self._scene.addItem(gi)
        self._elements.append(element)
        self._all_elements[element.id] = element
        for child in element.children:
            self._all_elements[child.id] = child

    def clear_canvas(self):
        for elem in list(self._all_elements.values()):
            if elem.graphics_item:
                self._scene.removeItem(elem.graphics_item)
        self._elements.clear()
        self._all_elements.clear()
        self._selected = None
        self._counter.clear()
        self._draw_grid()

    def get_element_count(self) -> int:
        return len(self._all_elements)

    def _push_undo(self):
        state = self.serialize_all()
        self._undo_stack.append(state)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self.serialize_all())
        state = self._undo_stack.pop()
        self.deserialize_all(state)
        self.design_changed.emit()

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self.serialize_all())
        state = self._redo_stack.pop()
        self.deserialize_all(state)
        self.design_changed.emit()

    def _snap_position(self, pos: QPointF) -> QPointF:
        if not self._snap_to_grid:
            return pos
        g = self._grid_size
        return QPointF(round(pos.x() / g) * g, round(pos.y() / g) * g)

    def _draw_grid(self):
        """Draw dotted grid on scene background."""
        # Grid is drawn via the scene background
        pass  # QSS handles background; grid drawn in paintEvent override if needed

    def toggle_grid(self):
        self._grid_visible = not self._grid_visible
        self.viewport().update()

    def toggle_snap(self):
        self._snap_to_grid = not self._snap_to_grid

    def set_zoom(self, factor: float):
        self._zoom = factor
        self.resetTransform()
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            elem_id = item.data(0)
            if elem_id and elem_id in self._all_elements:
                self._selected = self._all_elements[elem_id]
                self.element_selected.emit(self._selected)
                return
            # Check parent items
            while item:
                elem_id = item.data(0)
                if elem_id and elem_id in self._all_elements:
                    self._selected = self._all_elements[elem_id]
                    self.element_selected.emit(self._selected)
                    return
                item = item.parentItem()
        self._selected = None
        self.element_selected.emit(None)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        element_type = event.mimeData().text()
        pos = self.mapToScene(event.pos())
        self.element_dropped.emit(element_type, pos.x(), pos.y())
        event.acceptProposedAction()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.1 if delta > 0 else 0.9
            self._zoom *= factor
            self._zoom = max(0.25, min(4.0, self._zoom))
            self.set_zoom(self._zoom)
            event.accept()
        else:
            super().wheelEvent(event)
