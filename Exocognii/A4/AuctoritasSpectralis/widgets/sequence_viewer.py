# Auctoritas Spectralis — widgets/sequence_viewer.py
# v1.0.0
"""Luminance ladder and OKLAB projection for the Sequentia Luminis."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

from ..constants import TOKEN_NAMES, TOKEN_LABELS


class LuminanceLadder(QWidget):
    """Bar chart showing OKLAB lightness of all 10 tokens, sorted."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setMinimumWidth(200)
        self._entries = []  # list of (name, L, hex)
        self._min_delta = 0.0

    def set_data(self, oklab_tokens: dict, tokens: dict):
        """Set token data for rendering."""
        self._entries = []
        for name in TOKEN_NAMES:
            ok = oklab_tokens.get(name, {})
            l_val = ok.get('l', 0.0)
            hex_val = tokens.get(name, '#000000')
            self._entries.append((name, l_val, hex_val))

        # Sort by lightness
        self._entries.sort(key=lambda x: x[1])

        # Compute minimum delta between adjacent tokens
        if len(self._entries) > 1:
            deltas = [
                self._entries[i+1][1] - self._entries[i][1]
                for i in range(len(self._entries) - 1)
            ]
            self._min_delta = min(deltas) if deltas else 0.0
        else:
            self._min_delta = 0.0

        self.update()

    def paintEvent(self, event):
        if not self._entries:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        n = len(self._entries)
        bar_w = max(4, (w - 20) // n - 2)
        x_start = 10

        for i, (name, l_val, hex_val) in enumerate(self._entries):
            bar_h = max(4, int(l_val * (h - 20)))
            x = x_start + i * (bar_w + 2)
            y = h - 10 - bar_h

            painter.setBrush(QColor(hex_val))
            painter.setPen(QColor('#3a2e10'))
            painter.drawRect(x, y, bar_w, bar_h)

        painter.end()


class SequenceViewer(QWidget):
    """Sequentia Luminis — luminance ladder with min-delta readout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel('SEQUENTIA LUMINIS')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        self._ladder = LuminanceLadder()
        layout.addWidget(self._ladder)

        self._delta_label = QLabel('Min \u0394L: —')
        self._delta_label.setProperty('role', 'dim')
        layout.addWidget(self._delta_label)

    def update_data(self, oklab_tokens: dict, tokens: dict):
        self._ladder.set_data(oklab_tokens, tokens)
        self._delta_label.setText(
            f'Min \u0394L: {self._ladder._min_delta:.3f}'
        )
