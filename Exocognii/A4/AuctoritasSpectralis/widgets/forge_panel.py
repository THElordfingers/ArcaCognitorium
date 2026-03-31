# Auctoritas Spectralis — widgets/forge_panel.py
# v1.0.0
"""Compositio panel: hex input + OKLAB sliders + derived token swatches."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame,
    QScrollArea, QGroupBox,
)
from PyQt6.QtCore import pyqtSignal, Qt

from .hex_input import HexInput
from ..constants import TOKEN_NAMES, TOKEN_LABELS


class OklabSliderGroup(QWidget):
    """Three OKLAB sliders (L, a, b) with value labels."""

    values_changed = pyqtSignal(float, float, float)  # L, a, b

    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._sliders = {}
        self._labels = {}
        for axis, (lo, hi, default) in [
            ('L', (0, 1000, 0)),      # Lightness [0.0, 1.0] * 1000
            ('a', (-400, 400, 0)),    # a axis [-0.4, 0.4] * 1000
            ('b', (-400, 400, 0)),    # b axis [-0.4, 0.4] * 1000
        ]:
            row = QHBoxLayout()
            row.setSpacing(6)

            lbl = QLabel(axis)
            lbl.setFixedWidth(14)
            lbl.setProperty('role', 'micro')
            row.addWidget(lbl)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(lo)
            slider.setMaximum(hi)
            slider.setValue(default)
            slider.valueChanged.connect(self._on_slider_changed)
            row.addWidget(slider, 1)

            val_lbl = QLabel('0.000')
            val_lbl.setFixedWidth(50)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            val_lbl.setProperty('role', 'dim')
            row.addWidget(val_lbl)

            self._sliders[axis] = slider
            self._labels[axis] = val_lbl
            layout.addLayout(row)

    def _on_slider_changed(self):
        if self._updating:
            return
        l = self._sliders['L'].value() / 1000.0
        a = self._sliders['a'].value() / 1000.0
        b = self._sliders['b'].value() / 1000.0
        self._labels['L'].setText(f'{l:.3f}')
        self._labels['a'].setText(f'{a:.3f}')
        self._labels['b'].setText(f'{b:.3f}')
        self.values_changed.emit(l, a, b)

    def set_oklab(self, l: float, a: float, b: float):
        """Set slider positions from OKLAB values without emitting."""
        self._updating = True
        self._sliders['L'].setValue(int(l * 1000))
        self._sliders['a'].setValue(int(a * 1000))
        self._sliders['b'].setValue(int(b * 1000))
        self._labels['L'].setText(f'{l:.3f}')
        self._labels['a'].setText(f'{a:.3f}')
        self._labels['b'].setText(f'{b:.3f}')
        self._updating = False


class SwatchStrip(QWidget):
    """Vertical list of derived token color swatches with hex labels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._rows = {}
        for name in TOKEN_NAMES:
            row = QHBoxLayout()
            row.setSpacing(6)

            swatch = QLabel()
            swatch.setFixedSize(22, 18)
            swatch.setStyleSheet('background: #000000; border: 1px solid #3a2e10;')
            row.addWidget(swatch)

            label = QLabel(TOKEN_LABELS.get(name, name))
            label.setFixedWidth(90)
            label.setProperty('role', 'dim')
            row.addWidget(label)

            hex_lbl = QLabel('#000000')
            hex_lbl.setFixedWidth(62)
            hex_lbl.setProperty('role', 'dim')
            row.addWidget(hex_lbl)

            # Clipping indicator
            clip_lbl = QLabel('')
            clip_lbl.setFixedWidth(14)
            row.addWidget(clip_lbl)

            row.addStretch()
            layout.addLayout(row)
            self._rows[name] = (swatch, label, hex_lbl, clip_lbl)

    def update_tokens(self, tokens: dict, clipped: list[str] = None):
        """Update all swatch colors and hex labels."""
        clipped = clipped or []
        for name, (swatch, label, hex_lbl, clip_lbl) in self._rows.items():
            hex_val = tokens.get(name, '#000000')
            swatch.setStyleSheet(
                f'background: {hex_val}; border: 1px solid #3a2e10;'
            )
            hex_lbl.setText(hex_val)
            clip_lbl.setText('\u2334' if name in clipped else '')


class ForgePanel(QWidget):
    """Complete Compositio panel — the left column of the main window."""

    palette_changed = pyqtSignal(str, str)  # bg_hex, fg_hex

    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # ── Title ──
        title = QLabel('COMPOSITIO')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        # ── FUNDUS (Background) ──
        bg_group = QGroupBox('FUNDUS')
        bg_layout = QVBoxLayout(bg_group)
        bg_layout.setSpacing(6)

        self._bg_hex = HexInput('#050507')
        self._bg_hex.hex_changed.connect(self._on_bg_hex_changed)
        bg_layout.addWidget(self._bg_hex)

        self._bg_sliders = OklabSliderGroup()
        self._bg_sliders.values_changed.connect(self._on_bg_slider_changed)
        bg_layout.addWidget(self._bg_sliders)

        layout.addWidget(bg_group)

        # ── SCRIPTURA (Foreground) ──
        fg_group = QGroupBox('SCRIPTURA')
        fg_layout = QVBoxLayout(fg_group)
        fg_layout.setSpacing(6)

        self._fg_hex = HexInput('#d4af37')
        self._fg_hex.hex_changed.connect(self._on_fg_hex_changed)
        fg_layout.addWidget(self._fg_hex)

        self._fg_sliders = OklabSliderGroup()
        self._fg_sliders.values_changed.connect(self._on_fg_slider_changed)
        fg_layout.addWidget(self._fg_sliders)

        layout.addWidget(fg_group)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # ── CHROMATA DERIVATA ──
        cd_label = QLabel('CHROMATA DERIVATA')
        cd_label.setProperty('role', 'micro')
        layout.addWidget(cd_label)

        self._swatch_strip = SwatchStrip()
        layout.addWidget(self._swatch_strip)

        layout.addStretch()

    def _on_bg_hex_changed(self, hex_val: str):
        if self._updating:
            return
        from ..derivatio import hex_to_oklab
        l, a, b = hex_to_oklab(hex_val)
        self._updating = True
        self._bg_sliders.set_oklab(l, a, b)
        self._updating = False
        self.palette_changed.emit(hex_val, self._fg_hex.get_hex())

    def _on_fg_hex_changed(self, hex_val: str):
        if self._updating:
            return
        from ..derivatio import hex_to_oklab
        l, a, b = hex_to_oklab(hex_val)
        self._updating = True
        self._fg_sliders.set_oklab(l, a, b)
        self._updating = False
        self.palette_changed.emit(self._bg_hex.get_hex(), hex_val)

    def _on_bg_slider_changed(self, l: float, a: float, b: float):
        if self._updating:
            return
        from ..derivatio import oklab_to_hex
        hex_val = oklab_to_hex(l, a, b)
        self._updating = True
        self._bg_hex.set_hex(hex_val)
        self._updating = False
        self.palette_changed.emit(hex_val, self._fg_hex.get_hex())

    def _on_fg_slider_changed(self, l: float, a: float, b: float):
        if self._updating:
            return
        from ..derivatio import oklab_to_hex
        hex_val = oklab_to_hex(l, a, b)
        self._updating = True
        self._fg_hex.set_hex(hex_val)
        self._updating = False
        self.palette_changed.emit(self._bg_hex.get_hex(), hex_val)

    def update_derived(self, tokens: dict, clipped: list[str] = None):
        """Update the swatch strip with derived tokens."""
        self._swatch_strip.update_tokens(tokens, clipped)

    def set_base_pair(self, bg_hex: str, fg_hex: str):
        """Load a base pair into the forge (e.g. from registry)."""
        self._updating = True
        from ..derivatio import hex_to_oklab

        self._bg_hex.set_hex(bg_hex)
        l, a, b = hex_to_oklab(bg_hex)
        self._bg_sliders.set_oklab(l, a, b)

        self._fg_hex.set_hex(fg_hex)
        l, a, b = hex_to_oklab(fg_hex)
        self._fg_sliders.set_oklab(l, a, b)

        self._updating = False
        self.palette_changed.emit(bg_hex, fg_hex)

    def get_base_pair(self) -> tuple[str, str]:
        return self._bg_hex.get_hex(), self._fg_hex.get_hex()
