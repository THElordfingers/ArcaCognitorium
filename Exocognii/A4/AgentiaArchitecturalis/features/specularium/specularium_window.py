"""
Specularium Window — floating QMainWindow with Renderer B.

150ms defer + setParent(None) + raise_() for X11 safety.
Hide on close (not destroy). Ctrl+P toggle.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel,
)

from ... import tokens
from .preview_data_model import PreviewDataModel
from .preview_renderer import PreviewRenderer


class SpeculariumWindow(QMainWindow):
    """Floating preview window with Renderer B."""

    def __init__(self, data_model: PreviewDataModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._model = data_model
        self._initialized = False
        self.setWindowTitle("\u2726 Specularium \u2014 Renderer B")
        self.setMinimumSize(400, 300)
        self.resize(600, 500)

    def _lazy_init(self) -> None:
        """Build UI on first show."""
        if self._initialized:
            return
        self._initialized = True

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QLabel("Specularium Vivum \u00b7 Renderer B (floating window)")
        header.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(header)

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
        layout.addWidget(scroll, 1)

        self._model.design_updated.connect(self._on_design_updated)

        # Apply theme
        from PyQt6.QtWidgets import QApplication
        qapp = QApplication.instance()
        if qapp:
            self.setStyleSheet(qapp.styleSheet())

    def _on_design_updated(self) -> None:
        if self.isVisible():
            self.renderer.schedule_rebuild(
                self._model.current_elements,
                self._model.current_tokens,
            )

    def toggle(self) -> None:
        """Toggle window visibility. 150ms defer + setParent(None) + raise_()."""
        if self.isVisible():
            self.hide()
        else:
            self._lazy_init()
            # X11 safety: 150ms defer + setParent(None) + raise_()
            self.setParent(None)
            QTimer.singleShot(150, self._show_deferred)

    def _show_deferred(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        # Trigger rebuild with current data
        self.renderer.schedule_rebuild(
            self._model.current_elements,
            self._model.current_tokens,
        )

    def closeEvent(self, event) -> None:
        """Hide on close, don't destroy."""
        event.ignore()
        self.hide()
