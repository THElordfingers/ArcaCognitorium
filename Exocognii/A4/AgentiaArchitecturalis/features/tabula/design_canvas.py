"""
Design Canvas — QGraphicsView/Scene for element placement.

16px grid, pan/zoom, drag-drop from Elementarium, container nesting,
50-step undo/redo, serialize/deserialize, refresh_tokens.
"""
from __future__ import annotations

import copy
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QPen, QColor, QPainter, QWheelEvent, QMouseEvent,
    QDragEnterEvent, QDropEvent,
)
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
)

from ... import tokens
from ...models import ElementNode
from .canvas_element import CanvasElement, GRID_SIZE
from .element_registry import get_element_def

MAX_UNDO = 50


class DesignCanvas(QGraphicsView):
    """The central design surface."""

    element_selected = pyqtSignal(object)    # CanvasElement or None
    design_changed = pyqtSignal()            # for dirty state + Specularium
    element_count_changed = pyqtSignal(int)  # status bar updates

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._scene.setSceneRect(0, 0, 4000, 4000)
        self.setScene(self._scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._elements: list[CanvasElement] = []
        self._selected: CanvasElement | None = None
        self._var_counter: int = 0

        # Undo/redo
        self._undo_stack: list[list[dict]] = []
        self._redo_stack: list[list[dict]] = []

        # Pan state
        self._panning = False
        self._pan_start = QPointF()

        self._scene.selectionChanged.connect(self._on_selection_changed)
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(f"QGraphicsView {{ border: none; background: {tokens.C_BG}; }}")

    def drawBackground(self, painter: QPainter, rect) -> None:
        """Draw 16px grid."""
        super().drawBackground(painter, rect)
        pen = QPen(QColor(tokens.C_GOLD_DARK))
        pen.setWidthF(0.3)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)

        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += GRID_SIZE
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += GRID_SIZE

    # ── Drag & Drop ─────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("application/x-aa-element"):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat("application/x-aa-element"):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasFormat("application/x-aa-element"):
            super().dropEvent(event)
            return

        element_type = bytes(event.mimeData().data("application/x-aa-element")).decode("utf-8")
        # PyQt6: .position().toPoint()
        scene_pos = self.mapToScene(event.position().toPoint())

        self._push_undo()
        parent = self._container_at(scene_pos)
        self._var_counter += 1
        var_name = f"{element_type.lower().replace('(', '').replace(')', '')}_{self._var_counter}"

        # Snap to grid
        sx = round(scene_pos.x() / GRID_SIZE) * GRID_SIZE
        sy = round(scene_pos.y() / GRID_SIZE) * GRID_SIZE

        if parent:
            # Position relative to parent origin
            parent_pos = parent.graphics_item.scenePos()
            rx = round((scene_pos.x() - parent_pos.x()) / GRID_SIZE) * GRID_SIZE
            ry = round((scene_pos.y() - parent_pos.y()) / GRID_SIZE) * GRID_SIZE
            elem = CanvasElement(element_type, var_name, rx, ry, parent_element=parent)
            parent.add_child(elem)
        else:
            elem = CanvasElement(element_type, var_name, sx, sy)
            self._scene.addItem(elem.graphics_item)

        self._elements.append(elem)
        self.design_changed.emit()
        self.element_count_changed.emit(len(self._elements))
        event.acceptProposedAction()

    def _container_at(self, scene_pos: QPointF) -> CanvasElement | None:
        """Find the frontmost container at scene_pos."""
        items = self._scene.items(scene_pos)
        for item in items:
            elem = item.data(0)
            if isinstance(elem, CanvasElement) and elem.accepts_children():
                return elem
        return None

    # ── Selection ───────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        selected_items = self._scene.selectedItems()
        if selected_items:
            elem = selected_items[0].data(0)
            if isinstance(elem, CanvasElement):
                if self._selected and self._selected is not elem:
                    self._selected.set_selected_style(False)
                self._selected = elem
                elem.set_selected_style(True)
                self.element_selected.emit(elem)
                return
        if self._selected:
            self._selected.set_selected_style(False)
        self._selected = None
        self.element_selected.emit(None)

    def selected_element(self) -> CanvasElement | None:
        return self._selected

    # ── Pan & Zoom ──────────────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
            current = self.transform().m11()
            if 0.25 <= current * factor <= 4.0:
                self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            # Snap on release
            if self._selected:
                self._selected.snap_to_grid()
                self.design_changed.emit()
            super().mouseReleaseEvent(event)

    # ── Undo / Redo ─────────────────────────────────────────────

    def _push_undo(self) -> None:
        state = [e.serialize().to_dict() for e in self._root_elements()]
        self._undo_stack.append(state)
        if len(self._undo_stack) > MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> None:
        if not self._undo_stack:
            return
        current = [e.serialize().to_dict() for e in self._root_elements()]
        self._redo_stack.append(current)
        state = self._undo_stack.pop()
        self._restore_state(state)

    def redo(self) -> None:
        if not self._redo_stack:
            return
        current = [e.serialize().to_dict() for e in self._root_elements()]
        self._undo_stack.append(current)
        state = self._redo_stack.pop()
        self._restore_state(state)

    def _restore_state(self, state: list[dict]) -> None:
        self.clear_canvas(emit=False)
        nodes = [ElementNode.from_dict(d) for d in state]
        self.deserialize_all(nodes)
        self.design_changed.emit()

    # ── Element Operations ──────────────────────────────────────

    def delete_selected(self) -> None:
        if not self._selected:
            return
        self._push_undo()
        self._remove_element(self._selected)
        self._selected = None
        self.element_selected.emit(None)
        self.design_changed.emit()
        self.element_count_changed.emit(len(self._elements))

    def duplicate_selected(self) -> None:
        if not self._selected:
            return
        self._push_undo()
        node = self._selected.serialize()
        node.x += GRID_SIZE * 2
        node.y += GRID_SIZE * 2
        self._var_counter += 1
        node.var_name = f"{node.element_type.lower()}_{self._var_counter}"
        elem = CanvasElement.from_node(node, parent_element=self._selected.parent_element)
        if self._selected.parent_element:
            self._selected.parent_element.add_child(elem)
        else:
            self._scene.addItem(elem.graphics_item)
        self._elements.append(elem)
        self._collect_all_elements(elem)
        self.design_changed.emit()
        self.element_count_changed.emit(len(self._elements))

    def group_selected(self) -> None:
        """Wrap selected element in a new QFrame container."""
        if not self._selected:
            return
        self._push_undo()
        sel = self._selected
        # Create container slightly larger
        w = sel.properties.get("width", 200) + GRID_SIZE * 2
        h = sel.properties.get("height", 100) + GRID_SIZE * 2
        pos = sel.graphics_item.scenePos()

        self._var_counter += 1
        container = CanvasElement(
            "QFrame", f"group_{self._var_counter}",
            int(pos.x()) - GRID_SIZE, int(pos.y()) - GRID_SIZE,
            w, h,
        )

        # Remove old from scene/parent
        if sel.parent_element:
            sel.parent_element.remove_child(sel)
        else:
            self._scene.removeItem(sel.graphics_item)

        # Add container to scene
        self._scene.addItem(container.graphics_item)
        self._elements.append(container)

        # Reparent selected into container
        container.add_child(sel)
        sel.graphics_item.setPos(GRID_SIZE, GRID_SIZE)

        self.design_changed.emit()
        self.element_count_changed.emit(len(self._elements))

    def _remove_element(self, elem: CanvasElement) -> None:
        # Remove children first
        for child in list(elem.children):
            self._remove_element(child)
        if elem.parent_element:
            elem.parent_element.remove_child(elem)
        else:
            self._scene.removeItem(elem.graphics_item)
        if elem in self._elements:
            self._elements.remove(elem)

    def _collect_all_elements(self, elem: CanvasElement) -> None:
        """Add element and all children to the flat list."""
        for child in elem.children:
            if child not in self._elements:
                self._elements.append(child)
            self._collect_all_elements(child)

    # ── Serialization ───────────────────────────────────────────

    def _root_elements(self) -> list[CanvasElement]:
        """Return only root-level (non-parented) elements."""
        return [e for e in self._elements if e.parent_element is None]

    def serialize_all(self) -> list[ElementNode]:
        """Serialize the entire canvas tree. x/y parent-relative."""
        return [e.serialize() for e in self._root_elements()]

    def deserialize_all(self, nodes: list[ElementNode]) -> None:
        """Reconstruct canvas from serialized nodes."""
        for node in nodes:
            elem = CanvasElement.from_node(node)
            self._scene.addItem(elem.graphics_item)
            self._elements.append(elem)
            self._collect_all_elements(elem)
        self.element_count_changed.emit(len(self._elements))

    def clear_canvas(self, emit: bool = True) -> None:
        self._scene.clear()
        self._elements.clear()
        self._selected = None
        if emit:
            self.design_changed.emit()
            self.element_count_changed.emit(0)

    # ── Theme refresh ───────────────────────────────────────────

    def refresh_tokens(self, token_dict: dict[str, str]) -> None:
        """Repaint all elements with new tokens. No clearing."""
        for elem in self._elements:
            elem.refresh_tokens(token_dict)

    # ── Accessors ───────────────────────────────────────────────

    def element_count(self) -> int:
        return len(self._elements)

    def all_elements(self) -> list[CanvasElement]:
        return list(self._elements)
