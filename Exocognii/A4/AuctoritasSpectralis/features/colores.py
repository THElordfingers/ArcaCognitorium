"""
AUCTORITAS SPECTRALIS — v1.0.0
features/colores.py — Feature I: COLORES

Generation model (Pairz-style):
  - Void + Aurum each have independent H/L/C min/max sliders
  - Each can be individually locked (frozen hex, not re-randomised)
  - Algorithm + Threshold is the contrast constraint for the lead pair
  - Generator runs up to 1000 attempts; best result wins
  - Remaining 8 tokens derived entirely from the lead pair
  - Derivation shaped by: Harmony model + 5 global tweaks

Control tabs:
  Void   — H min/max, L min/max, C min/max, lock + live swatch
  Aurum  — H min/max, L min/max, C min/max, lock + live swatch
  Forge  — Algo, Threshold, Harmony, 5 derivation tweaks

Token display names (canonical):
  c_bg → Void       c_gold → Aurum       c_panel → Obsidian
  c_subtle → Umbra  c_gold_dark → Aurum Nox  c_gold_dim → Aurum Dimmus
  c_text → Parchment  c_white → Vellum
  c_crimson → Sanguis  c_teal → Viridis
"""

from __future__ import annotations
import random
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QScrollArea, QFrame, QComboBox,
    QSlider, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal

from AuctoritasSpectralis.engine.harmony import HARMONY_MODELS
from AuctoritasSpectralis.engine.nomen import generate_nomina
from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER
from AuctoritasSpectralis.engine.colour import (
    is_valid_hex, hex_to_lch, lch_hex_roundtrip, LCH,
    relative_luminance,
)
import AuctoritasSpectralis.config as cfg
from AuctoritasSpectralis.i18n import t

# ── Palette constants ─────────────────────────────────────────────────────

C_VOID      = "#050507"
C_OBSIDIAN  = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_PARCHMENT = "#c8b88a"
C_VELLUM    = "#e8e0cc"

# ── Token display names ───────────────────────────────────────────────────

TOKEN_DISPLAY_LAT: dict[str, str] = {
    "c_bg":        "Void",
    "c_gold":      "Aurum",
    "c_panel":     "Obsidian",
    "c_subtle":    "Umbra",
    "c_gold_dark": "Aurum Nox",
    "c_gold_dim":  "Aurum Dimmus",
    "c_text":      "Parchment",
    "c_white":     "Vellum",
    "c_crimson":   "Sanguis",
    "c_teal":      "Viridis",
}

TOKEN_DISPLAY_EN: dict[str, str] = {
    "c_bg":        "Void",
    "c_gold":      "Gold",
    "c_panel":     "Panel",
    "c_subtle":    "Shadow",
    "c_gold_dark": "Dark Gold",
    "c_gold_dim":  "Dim Gold",
    "c_text":      "Text",
    "c_white":     "Light",
    "c_crimson":   "Crimson",
    "c_teal":      "Teal",
}

DEFAULT_PALETTE: dict[str, str] = {
    "c_bg":        "#050507",
    "c_gold":      "#d4af37",
    "c_panel":     "#0a0a12",
    "c_subtle":    "#080810",
    "c_gold_dark": "#3a2e10",
    "c_gold_dim":  "#7a6a2a",
    "c_text":      "#c8b88a",
    "c_white":     "#e8e0cc",
    "c_crimson":   "#8b1a1a",
    "c_teal":      "#1a5a5a",
}

CONTRAST_ALGOS = ["WCAG 2.1", "APCA", "Delta Phi", "L* Distance", "Michelson", "Weber"]

ALGO_INFO: dict[str, str] = {
    "WCAG 2.1":    "Luminance ratio. Range 1–21.\nAA ≥ 4.5  AAA ≥ 7.0",
    "APCA":        "Advanced Perceptual Contrast.\n|Lc| ≥ 45 minimum  ≥ 60 body  ≥ 75 fluent",
    "Delta Phi":   "φ-scale perceptual contrast.\n≥ 10 minimum  ≥ 18 good  ≥ 28 excellent",
    "L* Distance": "CIE L* difference. Equal steps = equal perception.\n≥ 20 min  ≥ 40 comfortable  ≥ 60 high",
    "Michelson":   "(max−min)/(max+min). Range 0–1.\n≥ 0.5 low  ≥ 0.7 medium  ≥ 0.9 high",
    "Weber":       "Difference / background lum.\n≥ 1.0 noticeable  ≥ 5.0 clear  ≥ 15.0 high",
}

ALGO_RANGES: dict[str, tuple[float, float, float]] = {
    "WCAG 2.1":    (1.0,   21.0,  4.5),
    "APCA":        (0.0,  108.0, 60.0),
    "Delta Phi":   (0.0,   50.0, 18.0),
    "L* Distance": (0.0,  100.0, 40.0),
    "Michelson":   (0.0,    1.0,  0.7),
    "Weber":       (0.0,   20.0,  5.0),
}


# ── Contrast scoring ──────────────────────────────────────────────────────

def _score(fg: str, bg: str, algo: str) -> float:
    try:
        l1, l2 = relative_luminance(fg), relative_luminance(bg)
        if algo == "WCAG 2.1":
            return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        elif algo == "APCA":
            from AuctoritasSpectralis.engine.contrast import apca_lc
            return abs(apca_lc(fg, bg))
        elif algo == "L* Distance":
            return abs(hex_to_lch(fg).L - hex_to_lch(bg).L) * 100
        elif algo == "Michelson":
            d = l1 + l2
            return abs(l1 - l2) / d if d > 0 else 0.0
        elif algo == "Weber":
            return abs(l1 - l2) / (min(l1, l2) + 1e-6)
        elif algo == "Delta Phi":
            phi = 1.618033988
            return abs(l1 ** (1 / phi) - l2 ** (1 / phi)) * 100
    except Exception:
        pass
    return 0.0


# ── Palette derivation ────────────────────────────────────────────────────

def derive_palette(
    bg_hex:          str,
    gold_hex:        str,
    harmony:         str,
    chroma_scale:    float,  # 0.5–2.0 — scales all derived token chroma
    bg_depth:        float,  # 0.0–1.0 — how much darker panel/umbra are vs void
    text_brightness: float,  # 0.0–1.0 — where parchment/vellum sit
    accent_hue_off:  float,  # 0–180   — how far accents deviate from harmony
    accent_intensity:float,  # 0.0–1.0 — chroma of sanguis/viridis
) -> dict[str, str]:
    """
    Derive all 8 non-lead-pair tokens from bg_hex and gold_hex.
    Returns a complete 10-token palette dict.
    """
    try:
        bg_lch   = hex_to_lch(bg_hex)
        gold_lch = hex_to_lch(gold_hex)
    except Exception:
        return dict(DEFAULT_PALETTE)

    # ── Harmony hue offsets ──────────────────────────────────────────────
    # Each harmony model defines 4 hue families:
    # [0] = bg family, [1] = gold family, [2] = accent A, [3] = accent B
    from AuctoritasSpectralis.engine.harmony import HARMONY_OFFSETS
    offsets = HARMONY_OFFSETS.get(harmony, HARMONY_OFFSETS["Complementary"])
    hues = [(bg_lch.H + o) % 360.0 for o in offsets]

    bg_h   = hues[0]
    gold_h = hues[1]
    acc_a  = (hues[2] + accent_hue_off) % 360.0
    acc_b  = (hues[3] + accent_hue_off) % 360.0

    # Base chroma — use bg chroma as reference, minimum floor
    base_c = max(bg_lch.C, 0.03)

    def tok(L: float, C: float, H: float) -> str:
        C_scaled = max(0.005, C * chroma_scale)
        try:
            return lch_hex_roundtrip(LCH(L=max(0.0, min(1.0, L)),
                                         C=C_scaled, H=H % 360.0))
        except Exception:
            return "#080808"

    # ── Background tones ─────────────────────────────────────────────────
    # bg_depth: 0.0 = panel very close to void, 1.0 = panel noticeably lighter
    bg_L      = bg_lch.L
    panel_L   = bg_L + 0.04 + bg_depth * 0.08   # Obsidian
    subtle_L  = bg_L + 0.02 + bg_depth * 0.04   # Umbra

    panel  = tok(panel_L,  base_c * 0.6, bg_h)
    subtle = tok(subtle_L, base_c * 0.4, bg_h)

    # ── Aurum family ─────────────────────────────────────────────────────
    gold_L  = gold_lch.L
    gold_C  = max(gold_lch.C, 0.08)

    # text_brightness: 0.0 = darker parchment/vellum, 1.0 = brighter
    parch_L = 0.50 + text_brightness * 0.20   # Parchment
    vell_L  = 0.75 + text_brightness * 0.15   # Vellum

    aurum_nox_L  = max(bg_L + 0.06, gold_L * 0.25)
    aurum_dim_L  = gold_L * 0.55

    aurum_nox  = tok(aurum_nox_L, gold_C * 0.55, gold_h)
    aurum_dim  = tok(aurum_dim_L, gold_C * 0.65, gold_h)
    parchment  = tok(parch_L,     gold_C * 0.30, gold_h)
    vellum     = tok(vell_L,      gold_C * 0.12, gold_h)

    # ── Accents ──────────────────────────────────────────────────────────
    acc_c = max(0.08, accent_intensity * 0.28)

    sanguis = tok(0.28, acc_c, acc_a)
    viridis = tok(0.30, acc_c, acc_b)

    return {
        "c_bg":        bg_hex,
        "c_gold":      gold_hex,
        "c_panel":     panel,
        "c_subtle":    subtle,
        "c_gold_dark": aurum_nox,
        "c_gold_dim":  aurum_dim,
        "c_text":      parchment,
        "c_white":     vellum,
        "c_crimson":   sanguis,
        "c_teal":      viridis,
    }


# ── Labelled slider ───────────────────────────────────────────────────────

class LabelledSlider(QWidget):
    value_changed = pyqtSignal(float)

    def __init__(self, label: str, mn: float, mx: float,
                 default: float, decimals: int = 2, parent=None):
        super().__init__(parent)
        self._mn       = mn
        self._mx       = mx
        self._decimals = decimals
        self._steps    = 1000
        self._build(label, default)

    def _build(self, label: str, default: float):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 0)
        layout.setSpacing(1)

        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        self._lbl = QLabel(label)
        self._lbl.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:8px;"
            f"color:{C_GOLD_DIM};background:transparent;"
        )
        self._val = QLabel(self._fmt(default))
        self._val.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:8px;"
            f"color:{C_GOLD};background:transparent;"
        )
        hdr.addWidget(self._lbl)
        hdr.addStretch()
        hdr.addWidget(self._val)
        layout.addLayout(hdr)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, self._steps)
        self._slider.setValue(self._to_int(default))
        self._slider.setStyleSheet(
            f"QSlider::groove:horizontal{{height:3px;background:{C_GOLD_DARK};border-radius:1px;}}"
            f"QSlider::handle:horizontal{{width:10px;height:10px;margin:-4px 0;"
            f"background:{C_GOLD};border-radius:5px;}}"
            f"QSlider::sub-page:horizontal{{background:{C_GOLD_DIM};border-radius:1px;}}"
        )
        self._slider.valueChanged.connect(self._on_change)
        layout.addWidget(self._slider)

    def _fmt(self, v: float) -> str:
        return f"{v:.{self._decimals}f}"

    def _to_int(self, v: float) -> int:
        span = self._mx - self._mn
        if span == 0:
            return 0
        return max(0, min(self._steps, int(((v - self._mn) / span) * self._steps)))

    def _to_float(self, i: int) -> float:
        return self._mn + (i / self._steps) * (self._mx - self._mn)

    def _on_change(self, i: int):
        v = self._to_float(i)
        self._val.setText(self._fmt(v))
        self.value_changed.emit(v)

    def value(self) -> float:
        return self._to_float(self._slider.value())

    def set_value(self, v: float):
        self._slider.blockSignals(True)
        self._slider.setValue(self._to_int(max(self._mn, min(self._mx, v))))
        self._val.setText(self._fmt(self.value()))
        self._slider.blockSignals(False)

    def update_range(self, mn: float, mx: float, default: float):
        self._mn = mn
        self._mx = mx
        self.set_value(default)

    def set_label(self, text: str):
        self._lbl.setText(text)


# ── Lead pair tab ─────────────────────────────────────────────────────────

class LeadPairTab(QWidget):
    """
    One tab for either Void or Aurum.
    Contains: live swatch, hex display, lock button, H/L/C min/max sliders.
    """
    locked_changed = pyqtSignal(bool)   # emitted when lock toggled
    hex_changed    = pyqtSignal(str)    # emitted when hex field edited

    def __init__(self, token_name: str, default_hex: str,
                 h_default: tuple[float, float],
                 l_default: tuple[float, float],
                 c_default: tuple[float, float],
                 parent=None):
        super().__init__(parent)
        self._locked      = False
        self._current_hex = default_hex
        self._token_name  = token_name
        self._build(default_hex, h_default, l_default, c_default)

    def _build(self, default_hex: str,
               h_default: tuple[float, float],
               l_default: tuple[float, float],
               c_default: tuple[float, float]):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border:none;background:transparent;")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # ── Swatch + hex + lock row ───────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._swatch = QLabel()
        self._swatch.setFixedSize(44, 44)
        self._swatch.setStyleSheet(
            f"background:{default_hex};border:1px solid {C_GOLD_DARK};"
        )
        top_row.addWidget(self._swatch)

        mid = QVBoxLayout()
        mid.setSpacing(4)

        self._hex_edit = QLineEdit(default_hex)
        self._hex_edit.setMaxLength(7)
        self._hex_edit.setFixedHeight(26)
        self._hex_edit.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:11px;"
            f"color:{C_GOLD};background:{C_VOID};"
            f"border:1px solid {C_GOLD_DARK};padding:2px 6px;"
        )
        self._hex_edit.textChanged.connect(self._on_hex_changed)
        mid.addWidget(self._hex_edit)

        # LCH readout
        self._lch_lbl = QLabel()
        self._lch_lbl.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:8px;"
            f"color:{C_GOLD_DARK};background:transparent;"
        )
        self._update_lch(default_hex)
        mid.addWidget(self._lch_lbl)
        top_row.addLayout(mid, stretch=1)

        # Lock button
        self._lock_btn = QPushButton("○")
        self._lock_btn.setFixedSize(32, 32)
        self._lock_btn.setToolTip("Lock this colour")
        self._lock_btn.setStyleSheet(
            f"QPushButton{{font-size:16px;color:{C_GOLD_DARK};"
            f"background:transparent;border:none;padding:0;}}"
            f"QPushButton:hover{{color:{C_GOLD};}}"
        )
        self._lock_btn.clicked.connect(self._toggle_lock)
        top_row.addWidget(self._lock_btn)
        layout.addLayout(top_row)

        # ── Divider ───────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{C_GOLD_DARK};background:{C_GOLD_DARK};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        locked_note = QLabel("Sliders set the randomisation envelope.\nLocked = hex frozen, envelope ignored.")
        locked_note.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:7px;"
            f"color:{C_GOLD_DARK};background:transparent;line-height:1.4;"
        )
        locked_note.setWordWrap(True)
        layout.addWidget(locked_note)

        # ── Sliders ───────────────────────────────────────────────────────
        self._h_min = LabelledSlider("H min", 0.0,   360.0, h_default[0], decimals=1)
        self._h_max = LabelledSlider("H max", 0.0,   360.0, h_default[1], decimals=1)
        self._l_min = LabelledSlider("L min", 0.0,   1.0,   l_default[0], decimals=3)
        self._l_max = LabelledSlider("L max", 0.0,   1.0,   l_default[1], decimals=3)
        self._c_min = LabelledSlider("C min", 0.0,   0.4,   c_default[0], decimals=3)
        self._c_max = LabelledSlider("C max", 0.0,   0.4,   c_default[1], decimals=3)

        for s in [self._h_min, self._h_max,
                  self._l_min, self._l_max,
                  self._c_min, self._c_max]:
            layout.addWidget(s)

        layout.addStretch()
        scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_hex_changed(self, text: str) -> None:
        t = text if text.startswith("#") else f"#{text}"
        if is_valid_hex(t):
            self._current_hex = t
            self._swatch.setStyleSheet(
                f"background:{t};border:1px solid {C_GOLD_DARK};"
            )
            self._update_lch(t)
            self.hex_changed.emit(t)

    def _toggle_lock(self) -> None:
        self._locked = not self._locked
        if self._locked:
            self._lock_btn.setText("⊗")
            self._lock_btn.setStyleSheet(
                f"QPushButton{{font-size:16px;color:{C_GOLD};"
                f"background:transparent;border:none;padding:0;}}"
                f"QPushButton:hover{{color:{C_GOLD_DIM};}}"
            )
            self._lock_btn.setToolTip("Unlock this colour")
        else:
            self._lock_btn.setText("○")
            self._lock_btn.setStyleSheet(
                f"QPushButton{{font-size:16px;color:{C_GOLD_DARK};"
                f"background:transparent;border:none;padding:0;}}"
                f"QPushButton:hover{{color:{C_GOLD};}}"
            )
            self._lock_btn.setToolTip("Lock this colour")
        self.locked_changed.emit(self._locked)

    def _update_lch(self, hex_val: str) -> None:
        try:
            lch = hex_to_lch(hex_val)
            self._lch_lbl.setText(
                f"L {lch.L:.3f}  C {lch.C:.3f}  H {lch.H:.1f}°"
            )
        except Exception:
            self._lch_lbl.setText("")

    # ── Public ────────────────────────────────────────────────────────────

    def is_locked(self) -> bool:
        return self._locked

    def current_hex(self) -> str:
        return self._current_hex

    def set_hex(self, hex_val: str) -> None:
        self._hex_edit.blockSignals(True)
        self._hex_edit.setText(hex_val)
        self._hex_edit.blockSignals(False)
        self._current_hex = hex_val
        self._swatch.setStyleSheet(
            f"background:{hex_val};border:1px solid {C_GOLD_DARK};"
        )
        self._update_lch(hex_val)

    def random_hex(self) -> str:
        """Generate a random hex within the current slider envelopes."""
        h = random.uniform(self._h_min.value(), self._h_max.value())
        l = random.uniform(self._l_min.value(), self._l_max.value())
        # Enforce minimum chroma floor — pure C=0 collapses to achromatic,
        # producing near-identical results regardless of H.
        c_raw = random.uniform(self._c_min.value(), self._c_max.value())
        c = max(c_raw, 0.012)
        try:
            return lch_hex_roundtrip(LCH(L=l, C=c, H=h))
        except Exception:
            return self._current_hex


# ── Forge tab ─────────────────────────────────────────────────────────────

class ForgeTab(QWidget):
    """Algorithm, threshold, harmony, derivation tweaks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border:none;background:transparent;")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # ── Algorithm ────────────────────────────────────────────────────
        self._section(layout, "Generation Constraint")

        self._algo_combo = QComboBox()
        for a in CONTRAST_ALGOS:
            self._algo_combo.addItem(a)
        saved_algo = cfg.get("default_contrast_algo", "WCAG 2.1")
        if saved_algo in CONTRAST_ALGOS:
            self._algo_combo.setCurrentText(saved_algo)
        self._algo_combo.setStyleSheet(self._combo_css())
        self._algo_combo.currentTextChanged.connect(self._on_algo_changed)
        layout.addWidget(self._algo_combo)

        self._thresh = LabelledSlider("Threshold", 1.0, 21.0, 4.5)
        layout.addWidget(self._thresh)

        self._algo_info = QLabel()
        self._algo_info.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:8px;"
            f"color:{C_GOLD_DIM};background:{C_VOID};"
            f"border:1px solid {C_GOLD_DARK};padding:7px;line-height:1.6;"
        )
        self._algo_info.setWordWrap(True)
        layout.addWidget(self._algo_info)
        self._on_algo_changed(self._algo_combo.currentText())

        layout.addSpacing(8)

        # ── Harmony ───────────────────────────────────────────────────────
        self._section(layout, "Harmony")
        self._harmony_combo = QComboBox()
        for m in HARMONY_MODELS:
            self._harmony_combo.addItem(m)
        saved_h = cfg.get("default_harmony", "Complementary")
        if saved_h in HARMONY_MODELS:
            self._harmony_combo.setCurrentText(saved_h)
        self._harmony_combo.setStyleSheet(self._combo_css())
        layout.addWidget(self._harmony_combo)

        layout.addSpacing(8)

        # ── Derivation tweaks ─────────────────────────────────────────────
        self._section(layout, "Palette Derivation")

        self._chroma_scale    = LabelledSlider("Chroma Scale",     0.3,  2.0, 1.0)
        self._bg_depth        = LabelledSlider("BG Depth",         0.0,  1.0, 0.5)
        self._text_brightness = LabelledSlider("Text Brightness",  0.0,  1.0, 0.5)
        self._accent_hue_off  = LabelledSlider("Accent Hue Offset",0.0, 180.0, 0.0, decimals=1)
        self._accent_intensity= LabelledSlider("Accent Intensity", 0.1,  1.0, 0.6)

        for s in [self._chroma_scale, self._bg_depth, self._text_brightness,
                  self._accent_hue_off, self._accent_intensity]:
            layout.addWidget(s)

        layout.addStretch()
        scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _section(self, layout: QVBoxLayout, title: str):
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:7px;"
            f"letter-spacing:2px;color:{C_GOLD};background:transparent;margin-top:2px;"
        )
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{C_GOLD_DARK};background:{C_GOLD_DARK};")
        sep.setFixedHeight(1)
        layout.addWidget(lbl)
        layout.addWidget(sep)

    def _combo_css(self) -> str:
        return (
            f"QComboBox{{font-family:'Share Tech Mono',monospace;font-size:9px;"
            f"color:{C_GOLD};background:{C_VOID};border:1px solid {C_GOLD_DARK};padding:4px 8px;}}"
            f"QComboBox::drop-down{{border:none;width:14px;}}"
            f"QComboBox QAbstractItemView{{background:{C_OBSIDIAN};color:{C_PARCHMENT};"
            f"border:1px solid {C_GOLD_DARK};selection-background-color:{C_GOLD_DARK};}}"
        )

    def _on_algo_changed(self, algo: str) -> None:
        self._algo_info.setText(ALGO_INFO.get(algo, ""))
        mn, mx, default = ALGO_RANGES.get(algo, (1.0, 21.0, 4.5))
        self._thresh.update_range(mn, mx, default)

    # ── Accessors ─────────────────────────────────────────────────────────

    def algo(self)             -> str:   return self._algo_combo.currentText()
    def threshold(self)        -> float: return self._thresh.value()
    def harmony(self)          -> str:   return self._harmony_combo.currentText()
    def chroma_scale(self)     -> float: return self._chroma_scale.value()
    def bg_depth(self)         -> float: return self._bg_depth.value()
    def text_brightness(self)  -> float: return self._text_brightness.value()
    def accent_hue_off(self)   -> float: return self._accent_hue_off.value()
    def accent_intensity(self) -> float: return self._accent_intensity.value()


# ── Control strip ─────────────────────────────────────────────────────────

class ControlStrip(QWidget):
    generate_pair_pressed    = pyqtSignal()
    generate_palette_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(270)
        self.setStyleSheet(
            f"background:{C_OBSIDIAN};border-right:1px solid {C_GOLD_DARK};"
        )
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabBar::tab{{font-family:'Share Tech Mono',monospace;font-size:9px;"
            f"letter-spacing:1px;text-transform:uppercase;padding:6px 10px;"
            f"color:{C_GOLD_DIM};border-bottom:2px solid transparent;"
            f"background:transparent;margin-bottom:-1px;}}"
            f"QTabBar::tab:selected{{color:{C_GOLD};border-bottom:2px solid {C_GOLD};"
            f"background:rgba(212,175,55,0.04);}}"
            f"QTabWidget::pane{{border:none;border-top:1px solid {C_GOLD_DARK};}}"
            f"QTabWidget{{background:{C_OBSIDIAN};}}"
        )

        # Void tab
        self._void_tab = LeadPairTab(
            token_name="Void",
            default_hex=C_VOID,
            h_default=(0.0, 360.0),
            l_default=(0.01, 0.15),
            c_default=(0.0, 0.06),
        )
        # Aurum tab
        self._aurum_tab = LeadPairTab(
            token_name="Aurum",
            default_hex=C_GOLD,
            h_default=(20.0, 80.0),
            l_default=(0.50, 0.85),
            c_default=(0.06, 0.25),
        )
        # Forge tab
        self._forge_tab = ForgeTab()

        self._tabs.addTab(self._void_tab,  "Void")
        self._tabs.addTab(self._aurum_tab, "Aurum")
        self._tabs.addTab(self._forge_tab, "Forge")
        root.addWidget(self._tabs, stretch=1)

        # Two generate buttons — fixed at bottom, always visible
        bottom = QWidget()
        bottom.setFixedHeight(56)
        bottom.setStyleSheet(
            f"background:{C_OBSIDIAN};border-top:1px solid {C_GOLD_DARK};"
        )
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(10, 10, 10, 10)
        bl.setSpacing(6)

        self._pair_btn = QPushButton(t("gen.lead_pair", "LAT"))
        self._pair_btn.setFixedHeight(34)
        self._pair_btn.setToolTip("Randomise Void + Aurum within their envelopes")
        self._pair_btn.setStyleSheet(
            f"QPushButton{{font-family:'Share Tech Mono',monospace;font-size:9px;"
            f"letter-spacing:2px;text-transform:uppercase;color:{C_GOLD_DIM};"
            f"background:{C_VOID};border:1px solid {C_GOLD_DARK};}}"
            f"QPushButton:hover{{background:{C_GOLD_DARK};color:{C_GOLD};}}"
            f"QPushButton:pressed{{background:{C_GOLD_DIM};color:{C_VOID};}}"
        )
        self._pair_btn.clicked.connect(self.generate_pair_pressed)

        self._gen_btn = QPushButton(t("gen.generate", "LAT"))
        self._gen_btn.setFixedHeight(34)
        self._gen_btn.setToolTip("Derive full palette from current Lead Pair")
        self._gen_btn.setStyleSheet(
            f"QPushButton{{font-family:'Share Tech Mono',monospace;font-size:11px;"
            f"letter-spacing:3px;text-transform:uppercase;color:{C_GOLD};"
            f"background:{C_VOID};border:1px solid {C_GOLD_DIM};}}"
            f"QPushButton:hover{{background:{C_GOLD_DARK};}}"
            f"QPushButton:pressed{{background:{C_GOLD_DIM};color:{C_VOID};}}"
        )
        self._gen_btn.clicked.connect(self.generate_palette_pressed)

        bl.addWidget(self._pair_btn, stretch=1)
        bl.addWidget(self._gen_btn, stretch=2)
        root.addWidget(bottom)

    def set_mode(self, mode: str) -> None:
        """Update all translatable labels in the control strip."""
        self._pair_btn.setText(t("gen.lead_pair", mode))
        self._gen_btn.setText(t("gen.generate",   mode))

    # ── Accessors ─────────────────────────────────────────────────────────

    def void_locked(self)  -> bool:  return self._void_tab.is_locked()
    def aurum_locked(self) -> bool:  return self._aurum_tab.is_locked()
    def void_hex(self)     -> str:   return self._void_tab.current_hex()
    def aurum_hex(self)    -> str:   return self._aurum_tab.current_hex()

    def set_void_hex(self, h: str) -> None:
        self._void_tab.set_hex(h)

    def set_aurum_hex(self, h: str) -> None:
        self._aurum_tab.set_hex(h)

    def algo(self)              -> str:   return self._forge_tab.algo()
    def threshold(self)         -> float: return self._forge_tab.threshold()
    def harmony(self)           -> str:   return self._forge_tab.harmony()
    def chroma_scale(self)      -> float: return self._forge_tab.chroma_scale()
    def bg_depth(self)          -> float: return self._forge_tab.bg_depth()
    def text_brightness(self)   -> float: return self._forge_tab.text_brightness()
    def accent_hue_off(self)    -> float: return self._forge_tab.accent_hue_off()
    def accent_intensity(self)  -> float: return self._forge_tab.accent_intensity()


# ── Swatch block ──────────────────────────────────────────────────────────

class SwatchBlock(QWidget):
    def __init__(self, token_key: str, parent=None):
        super().__init__(parent)
        self.key = token_key
        self.setMinimumHeight(62)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._swatch = QLabel()
        self._swatch.setFixedWidth(72)
        self._swatch.setMinimumHeight(62)
        self._swatch.setStyleSheet(
            "background:#000000;border-right:1px solid #3a2e10;"
        )
        layout.addWidget(self._swatch)

        info = QWidget()
        info.setStyleSheet(
            f"background:{C_OBSIDIAN};border-bottom:1px solid {C_GOLD_DARK};"
        )
        info_l = QVBoxLayout(info)
        info_l.setContentsMargins(14, 8, 14, 8)
        info_l.setSpacing(2)

        name_row = QHBoxLayout()
        self._role_lbl = QLabel(TOKEN_DISPLAY_LAT.get(self.key, self.key))
        self._role_lbl.setStyleSheet(
            f"font-family:'Cinzel',Georgia,serif;font-size:12px;font-weight:600;"
            f"color:{C_GOLD};background:transparent;letter-spacing:1px;"
        )
        self._hex_lbl = QLabel("#000000")
        self._hex_lbl.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:9px;"
            f"color:{C_GOLD_DIM};background:transparent;"
        )
        name_row.addWidget(self._role_lbl)
        name_row.addStretch()
        name_row.addWidget(self._hex_lbl)
        info_l.addLayout(name_row)

        self._nomen_lbl = QLabel("—")
        self._nomen_lbl.setStyleSheet(
            f"font-family:'IM Fell English',Georgia,serif;font-size:11px;"
            f"font-style:italic;color:{C_PARCHMENT};background:transparent;"
        )
        info_l.addWidget(self._nomen_lbl)

        self._lch_lbl = QLabel("")
        self._lch_lbl.setStyleSheet(
            f"font-family:'Share Tech Mono',monospace;font-size:8px;"
            f"color:{C_GOLD_DARK};background:transparent;"
        )
        info_l.addWidget(self._lch_lbl)

        layout.addWidget(info, stretch=1)

    def update(self, hex_color: str, nomen: str) -> None:
        self._swatch.setStyleSheet(
            f"background:{hex_color};border-right:1px solid {C_GOLD_DARK};"
        )
        self._hex_lbl.setText(hex_color)
        self._nomen_lbl.setText(nomen)
        try:
            lch = hex_to_lch(hex_color)
            self._lch_lbl.setText(
                f"L {lch.L:.3f}  C {lch.C:.3f}  H {lch.H:.1f}°"
            )
        except Exception:
            self._lch_lbl.setText("")

    def set_mode(self, mode: str) -> None:
        names = TOKEN_DISPLAY_LAT if mode == "LAT" else TOKEN_DISPLAY_EN
        self._role_lbl.setText(names.get(self.key, self.key))


# ── Palette output ────────────────────────────────────────────────────────

class PaletteOutput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_VOID};")
        self._blocks: dict[str, SwatchBlock] = {}
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border:none;background:transparent;")

        container = QWidget()
        container.setStyleSheet(f"background:{C_VOID};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for key in TOKEN_ORDER:
            block = SwatchBlock(key)
            self._blocks[key] = block
            layout.addWidget(block)

        layout.addStretch()
        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(scroll)

    def refresh(self, palette: dict[str, str], nomina: dict[str, str]) -> None:
        for key, block in self._blocks.items():
            block.update(palette.get(key, "#000000"), nomina.get(key, "—"))

    def set_mode(self, mode: str) -> None:
        for block in self._blocks.values():
            block.set_mode(mode)


# ── COLORES main widget ───────────────────────────────────────────────────

class ColoresFeature(QWidget):
    palette_changed  = pyqtSignal(dict)
    ratify_requested = pyqtSignal(dict)
    export_requested = pyqtSignal(dict)
    save_requested   = pyqtSignal(dict)
    load_requested   = pyqtSignal()
    new_requested    = pyqtSignal()
    status_message   = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette: dict[str, str] = dict(DEFAULT_PALETTE)
        self._dirty   = False
        self._build()
        self._push_default()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._controls = ControlStrip()
        self._controls.generate_pair_pressed.connect(self._on_generate_pair)
        self._controls.generate_palette_pressed.connect(self._on_generate)
        self._output   = PaletteOutput()

        root.addWidget(self._controls)
        root.addWidget(self._output, stretch=1)

    def _push_default(self) -> None:
        nomina = generate_nomina(self._palette)
        self._output.refresh(self._palette, nomina)
        self.status_message.emit("Colores", "Default palette")

    # ── Generation ────────────────────────────────────────────────────────

    def _on_generate_pair(self) -> None:
        """Randomise the Lead Pair only. Does not re-derive the palette."""
        c             = self._controls
        algo          = c.algo()
        threshold     = c.threshold()
        void_locked   = c.void_locked()
        aurum_locked  = c.aurum_locked()

        # Seed from current hex as fallback only — not used as attempt 1
        best_void  = c.void_hex()
        best_gold  = c.aurum_hex()
        best_score = -1.0
        attempts   = 0

        for attempt in range(1, 1001):
            attempts = attempt

            # Always randomise unlocked tokens — never use current hex as attempt
            if void_locked and aurum_locked:
                try_void = best_void
                try_gold = best_gold
            elif void_locked:
                try_void = best_void
                try_gold = c._aurum_tab.random_hex()
            elif aurum_locked:
                try_void = c._void_tab.random_hex()
                try_gold = best_gold
            else:
                try_void = c._void_tab.random_hex()
                try_gold = c._aurum_tab.random_hex()

            if not is_valid_hex(try_void) or not is_valid_hex(try_gold):
                continue

            score = _score(try_gold, try_void, algo)
            if score > best_score:
                best_score = score
                best_void  = try_void
                best_gold  = try_gold

            if score >= threshold or (void_locked and aurum_locked):
                break

        c.set_void_hex(best_void)
        c.set_aurum_hex(best_gold)

        met  = best_score >= threshold
        flag = "" if met else "⚑ Below threshold  "
        self.status_message.emit(
            "◌  Colores  ·  Lead Pair",
            f"{flag}{algo}: {best_score:.2f}  ·  {attempts} attempt{'s' if attempts != 1 else ''}",
        )

    def _on_generate(self) -> None:
        c         = self._controls
        algo      = c.algo()
        threshold = c.threshold()

        void_locked  = c.void_locked()
        aurum_locked = c.aurum_locked()

        best_void  = c.void_hex()
        best_gold  = c.aurum_hex()
        best_score = -1.0
        attempts   = 0

        for attempt in range(1, 1001):
            attempts = attempt

            if void_locked and aurum_locked:
                try_void = best_void
                try_gold = best_gold
            elif void_locked:
                try_void = best_void
                try_gold = c._aurum_tab.random_hex()
            elif aurum_locked:
                try_void = c._void_tab.random_hex()
                try_gold = best_gold
            else:
                try_void = c._void_tab.random_hex()
                try_gold = c._aurum_tab.random_hex()

            if not is_valid_hex(try_void) or not is_valid_hex(try_gold):
                continue

            score = _score(try_gold, try_void, algo)
            if score > best_score:
                best_score = score
                best_void  = try_void
                best_gold  = try_gold

            if score >= threshold or (void_locked and aurum_locked):
                break

        # Update hex fields and swatches to reflect winning pair
        c.set_void_hex(best_void)
        c.set_aurum_hex(best_gold)

        # Derive the full palette
        palette = derive_palette(
            bg_hex           = best_void,
            gold_hex         = best_gold,
            harmony          = c.harmony(),
            chroma_scale     = c.chroma_scale(),
            bg_depth         = c.bg_depth(),
            text_brightness  = c.text_brightness(),
            accent_hue_off   = c.accent_hue_off(),
            accent_intensity = c.accent_intensity(),
        )

        self._palette = palette
        self._dirty   = True
        nomina = generate_nomina(palette)
        self._output.refresh(palette, nomina)

        met_threshold = best_score >= threshold
        flag = "" if met_threshold else "⚑ Below threshold  "
        self.status_message.emit(
            "◌  Colores",
            f"{flag}{algo}: {best_score:.2f}  ·  {attempts} attempt{'s' if attempts != 1 else ''}",
        )
        self.palette_changed.emit(palette)

    # ── Public API ────────────────────────────────────────────────────────

    def load_palette(self, palette: dict[str, str]) -> None:
        self._palette = dict(palette)
        self._dirty   = False
        nomina = generate_nomina(palette)
        self._output.refresh(palette, nomina)
        self.status_message.emit("Colores", "Palette loaded")
        self.palette_changed.emit(palette)
        bg   = palette.get("c_bg",   C_VOID)
        gold = palette.get("c_gold", C_GOLD)
        self._controls.set_void_hex(bg)
        self._controls.set_aurum_hex(gold)

    def get_palette(self) -> dict[str, str]:
        return dict(self._palette)

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self._output.set_mode(mode)
        self._controls.set_mode(mode)

    def get_fascia_buttons(self, mode: str = "LAT") -> list[QWidget]:
        from AuctoritasSpectralis.shell import FasciaButton

        b_new  = FasciaButton(t("btn.novum",      mode), "normal")
        b_open = FasciaButton(t("btn.aperire",     mode), "normal")
        b_save = FasciaButton(t("btn.servare",     mode), "normal")
        sep    = self._sep()
        b_rat  = FasciaButton(t("btn.ratificare",  mode), "confirm")
        b_pro  = FasciaButton(t("btn.promulgare",  mode), "confirm")

        b_new.clicked.connect(self.new_requested)
        b_open.clicked.connect(self.load_requested)
        b_save.clicked.connect(lambda: self.save_requested.emit(self._palette))
        b_rat.clicked.connect(lambda: self.ratify_requested.emit(self._palette))
        b_pro.clicked.connect(lambda: self.export_requested.emit(self._palette))

        return [b_new, b_open, b_save, sep, b_rat, b_pro]

    @staticmethod
    def _sep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setFixedHeight(20)
        sep.setStyleSheet(f"background:{C_GOLD_DARK};border:none;")
        return sep

    # ── Inductio API ──────────────────────────────────────────────────────

    def hide_all_token_rows(self) -> None:
        for block in self._output._blocks.values():
            eff = QGraphicsOpacityEffect(block)
            eff.setOpacity(0.0)
            block.setGraphicsEffect(eff)

    def reveal_token_row(self, index: int) -> None:
        keys = list(TOKEN_ORDER)
        if index < len(keys):
            block = self._output._blocks.get(keys[index])
            if block:
                eff = block.graphicsEffect()
                if not isinstance(eff, QGraphicsOpacityEffect):
                    eff = QGraphicsOpacityEffect(block)
                    block.setGraphicsEffect(eff)
                eff.setOpacity(1.0)
