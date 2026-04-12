"""
Tabula Designandi — Feature page with 3-panel split.

Elementarium (left, 110px) | Canvas (centre) | Inspector (right, 170px)
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter,
)

from .elementarium import Elementarium
from .design_canvas import DesignCanvas
from .session_manager import SessionManager
from ..inspector.inspector_feature import InspectorFeature


class TabulaFeature(QWidget):
    """Tabula Designandi feature page."""

    canvas_name_changed = pyqtSignal(str)
    dirty_changed = pyqtSignal(bool)
    element_count_changed = pyqtSignal(int)
    design_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = SessionManager()
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.elementarium = Elementarium()
        self.canvas = DesignCanvas()
        self.inspector = InspectorFeature()

        # QScrollArea in QSplitter must be wrapped in QWidget (constraint #13)
        canvas_wrapper = QWidget()
        cw_layout = QHBoxLayout(canvas_wrapper)
        cw_layout.setContentsMargins(0, 0, 0, 0)
        cw_layout.addWidget(self.canvas)

        layout.addWidget(self.elementarium)
        layout.addWidget(canvas_wrapper, 1)
        layout.addWidget(self.inspector)

    def _wire_signals(self) -> None:
        self.canvas.element_selected.connect(self._on_element_selected)
        self.canvas.design_changed.connect(self._on_design_changed)
        self.canvas.element_count_changed.connect(self.element_count_changed.emit)
        self.inspector.property_changed.connect(self._on_property_changed)

    def _on_element_selected(self, element) -> None:
        self.inspector.set_element(element)

    def _on_design_changed(self) -> None:
        self.session.mark_dirty()
        self.dirty_changed.emit(True)
        self.design_changed.emit()

    def _on_property_changed(self) -> None:
        self.session.mark_dirty()
        self.dirty_changed.emit(True)
        self.canvas.design_changed.emit()

    def new_canvas(self) -> None:
        if self.session.new_canvas(self):
            self.canvas.clear_canvas()
            self.canvas_name_changed.emit("")
            self.dirty_changed.emit(False)

    def open_canvas(self) -> None:
        if not self.session.check_dirty_guard(self):
            return
        doc = self.session.load(self)
        if doc:
            self.canvas.clear_canvas(emit=False)
            self.canvas.deserialize_all(doc.elements)
            self.canvas_name_changed.emit(doc.name)
            self.dirty_changed.emit(False)

    def save_canvas(self) -> bool:
        elements = self.canvas.serialize_all()
        if self.session.save(elements, self):
            self.canvas_name_changed.emit(self.session.current_name)
            self.dirty_changed.emit(False)
            return True
        return False

    def save_canvas_as(self) -> bool:
        elements = self.canvas.serialize_all()
        if self.session.save_as(elements, self):
            self.canvas_name_changed.emit(self.session.current_name)
            self.dirty_changed.emit(False)
            return True
        return False
