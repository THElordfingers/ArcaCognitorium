"""
Specularium Feature Page — contains PreviewRenderer A in QScrollArea.

This is the in-app preview. Renderer B lives in the floating window.
Both subscribe to the same PreviewDataModel.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)

from ... import tokens
from .preview_data_model import PreviewDataModel
from .preview_renderer import PreviewRenderer


class SpeculariumFeature(QWidget):
    """Specularium Vivum feature page with Renderer A."""

    def __init__(self, data_model: PreviewDataModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._model = data_model
        self._build_ui()
        self._model.design_updated.connect(self._on_design_updated)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        header = QLabel("Specularium Vivum \u00b7 Renderer A (feature page)")
        header.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(header)

        # Preview frame (wrapped in QScrollArea via QWidget container — constraint #13)
        scroll_container = QWidget()
        sc_layout = QVBoxLayout(scroll_container)
        sc_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        preview_frame = QFrame()
        preview_frame.setStyleSheet(
            f"QFrame {{ border: 1px solid {tokens.C_GOLD_DARK}; "
            f"background: {tokens.C_PANEL}; padding: 12px; }}"
        )
        pf_layout = QVBoxLayout(preview_frame)

        self.renderer = PreviewRenderer()
        pf_layout.addWidget(self.renderer)

        scroll.setWidget(preview_frame)
        sc_layout.addWidget(scroll)
        layout.addWidget(scroll_container, 1)

        # Render log area
        self._log_area = QVBoxLayout()
        self._log_area.setSpacing(3)
        log_frame = QWidget()
        log_frame.setLayout(self._log_area)
        layout.addWidget(log_frame)

    def _on_design_updated(self) -> None:
        self.renderer.schedule_rebuild(
            self._model.current_elements,
            self._model.current_tokens,
        )
        # Update render log display after a brief delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(300, self._update_log_display)

    def _update_log_display(self) -> None:
        # Clear old
        while self._log_area.count():
            item = self._log_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for entry in self.renderer.render_log:
            lbl = QLabel(f"{entry.element_type} \u00b7 {entry.var_name} \u2014 {entry.message}")
            if entry.status == "clean":
                lbl.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8.5px; font-family: {tokens.FONT_MONO};")
            elif entry.status == "stub":
                lbl.setStyleSheet(f"color: #a06030; font-size: 8.5px; font-family: {tokens.FONT_MONO};")
            else:
                lbl.setStyleSheet(f"color: #c04040; font-size: 8.5px; font-family: {tokens.FONT_MONO};")
            self._log_area.addWidget(lbl)
