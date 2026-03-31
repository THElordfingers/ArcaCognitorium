# Agentia Architecturalis — preview.py
# v1.0.0
"""Render design tree as real PyQt6 widgets in a preview panel."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import QTimer, Qt, QBuffer, QByteArray
from PyQt6.QtGui import QPixmap

from .elements.factory import deserialize_element
from .constants import MODUS_ARCANUS_DEFAULTS


class PreviewRenderer(QScrollArea):
    """Builds and displays real PyQt6 widgets from the design tree."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._rebuild)
        self._pending_design = None
        self._active_tokens = dict(MODUS_ARCANUS_DEFAULTS)
        self._preview_widget = None

        # Initial empty state
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        lbl = QLabel('SPECULARIUM VIVUM')
        lbl.setProperty('role', 'micro')
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        layout.addStretch()
        self.setWidget(placeholder)

    def schedule_rebuild(self, design_tree: list[dict],
                         tokens: dict) -> None:
        self._pending_design = design_tree
        self._active_tokens = tokens
        self._timer.start()

    def force_rebuild(self, design_tree: list[dict], tokens: dict):
        self._pending_design = design_tree
        self._active_tokens = tokens
        self._rebuild()

    def _rebuild(self):
        if self._pending_design is None:
            return

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel('SPECULARIUM VIVUM')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        for node in self._pending_design:
            try:
                element = deserialize_element(node)
                widget = element.create_preview_widget(self._active_tokens)
                if widget:
                    widget.setEnabled(False)  # Non-interactive preview
                    layout.addWidget(widget)
            except Exception as e:
                err = QLabel(f'\u2334 Preview error: {e}')
                err.setStyleSheet('color: #8b1a1a;')
                layout.addWidget(err)

        layout.addStretch()
        self._preview_widget = container
        self.setWidget(container)

    def capture_thumbnail(self, size: int = 256) -> bytes | None:
        """Grab the preview as a PNG byte string."""
        if self._preview_widget is None:
            return None
        try:
            pixmap = self._preview_widget.grab()
            scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio)
            ba = QByteArray()
            buf = QBuffer(ba)
            buf.open(QBuffer.OpenModeFlag.WriteOnly)
            scaled.save(buf, 'PNG')
            return bytes(ba)
        except Exception:
            return None
