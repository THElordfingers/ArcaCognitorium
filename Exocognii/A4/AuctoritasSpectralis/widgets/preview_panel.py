# Auctoritas Spectralis — widgets/preview_panel.py
# v1.0.0
"""Specularium Vivum — self-rendering preview panel using live palette."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSlider, QComboBox, QLineEdit,
)
from PyQt6.QtCore import Qt


class PreviewPanel(QWidget):
    """Self-rendering preview with real ModusArcanus widget patterns.

    All widgets in this panel are rendered using the live QSS from
    auto_render, so the Wizard sees the theme on real widget anatomy.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ── Title ──
        title = QLabel('SPECULARIUM VIVUM')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        # ── Preview frame ──
        frame = QFrame()
        frame.setStyleSheet('')  # inherits from QSS
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)

        # Section header
        header = QLabel('\u2726  Titulus  \u2726')
        header.setProperty('role', 'title')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(header)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        frame_layout.addWidget(sep)

        # Body text
        body = QLabel(
            'Body text in the parchment tone renders here '
            'as a live preview. The apparatus reskins itself '
            'in real time as the Wizard adjusts the base pair.'
        )
        body.setWordWrap(True)
        frame_layout.addWidget(body)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        btn_manifest = QPushButton('\u2697 Manifest')
        btn_row.addWidget(btn_manifest)

        btn_seal = QPushButton('\U0001f732 Sigillare')
        btn_seal.setProperty('accent', 'teal')
        btn_row.addWidget(btn_seal)

        btn_discard = QPushButton('\u2715 Dissolvere')
        btn_discard.setProperty('accent', 'crimson')
        btn_row.addWidget(btn_discard)

        frame_layout.addLayout(btn_row)

        # Slider
        slider_row = QHBoxLayout()
        slider_lbl = QLabel('\u25c8 Slider')
        slider_lbl.setProperty('role', 'dim')
        slider_row.addWidget(slider_lbl)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(50)
        slider_row.addWidget(slider)
        frame_layout.addLayout(slider_row)

        # ComboBox
        combo = QComboBox()
        combo.addItems(['Selectio Prima', 'Selectio Altera', 'Selectio Tertia'])
        frame_layout.addWidget(combo)

        # Input
        input_field = QLineEdit()
        input_field.setPlaceholderText('Inscriptio...')
        frame_layout.addWidget(input_field)

        # Status line
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        frame_layout.addWidget(sep2)

        status = QLabel('Status: The apparatus awaits.')
        status.setProperty('role', 'dim')
        frame_layout.addWidget(status)

        layout.addWidget(frame, 1)
        layout.addStretch()
