# Auctoritas Spectralis — widgets/vision_overlay.py
# v1.0.0
"""Vision simulation toggle controls for deuteranopia/protanopia/achromatopsia."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class VisionOverlay(QWidget):
    """Vision simulation mode selector."""

    mode_changed = pyqtSignal(str)  # '' = off, 'deuteranopia', 'protanopia', 'achromatopsia'

    MODES = [
        ('', 'OFF'),
        ('deuteranopia', 'Deuter'),
        ('protanopia', 'Protan'),
        ('achromatopsia', 'Achro'),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = ''

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = QLabel('Vision Sim:')
        lbl.setProperty('role', 'dim')
        layout.addWidget(lbl)

        self._buttons = {}
        for mode, label in self.MODES:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(mode == '')
            btn.setFixedHeight(24)
            btn.clicked.connect(lambda checked, m=mode: self._on_click(m))
            layout.addWidget(btn)
            self._buttons[mode] = btn

        layout.addStretch()

    def _on_click(self, mode: str):
        self._current = mode
        for m, btn in self._buttons.items():
            btn.setChecked(m == mode)
        self.mode_changed.emit(mode)

    def get_mode(self) -> str:
        return self._current

    def cycle(self):
        """Cycle to next vision mode (for Ctrl+V shortcut)."""
        modes = [m for m, _ in self.MODES]
        idx = modes.index(self._current) if self._current in modes else 0
        next_mode = modes[(idx + 1) % len(modes)]
        self._on_click(next_mode)
