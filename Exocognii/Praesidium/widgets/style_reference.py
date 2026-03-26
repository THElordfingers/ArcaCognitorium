"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████ ████████ ██    ██ ██      ███████         ██████  ███████ ███████ ███████ ██████  ███████ ███    ██  ██████ ███████ ▍
🮈  ██         ██     ██  ██  ██      ██              ██   ██ ██      ██      ██      ██   ██ ██      ████   ██ ██      ██      ▍
🮈  ███████    ██      ████   ██      █████           ██████  █████   █████   █████   ██████  █████   ██ ██  ██ ██      █████   ▍
🮈       ██    ██       ██    ██      ██              ██   ██ ██      ██      ██      ██   ██ ██      ██  ██ ██ ██      ██      ▍
🮈  ███████    ██       ██    ███████ ███████ ███████ ██   ██ ███████ ██      ███████ ██   ██ ███████ ██   ████  ██████ ███████ ▍
🮈                                                                                                                              ▍
🮈                                                                                                                              ▍
🮈                                                        Python Script                                                         ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# PRAESIDIUM · widgets/style_reference.py
# Scrollable palette + typography quick-reference panel.
# version: 1.0.0
"""

from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from widget_base import ArcaneWidget
from theme import (
    C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK,
    C_TEXT, C_WHITE, C_SUBTLE, C_CRIMSON, C_TEAL,
    micro_label,
)

PALETTE = [
    ("Void",      C_BG,        "C_BG"),
    ("Obsidian",  C_PANEL,     "C_PANEL"),
    ("Aurum",     C_GOLD,      "C_GOLD"),
    ("Aurum Dim", C_GOLD_DIM,  "C_GOLD_DIM"),
    ("Aurum Nox", C_GOLD_DARK, "C_GOLD_DARK"),
    ("Parchment", C_TEXT,      "C_TEXT"),
    ("Vellum",    C_WHITE,     "C_WHITE"),
    ("Umbra",     C_SUBTLE,    "C_SUBTLE"),
    ("Sanguis",   C_CRIMSON,   "C_CRIMSON"),
    ("Viridis",   C_TEAL,      "C_TEAL"),
]

TYPE_SAMPLES = [
    ("Window Title",   "16px · bold · Aurum"),
    ("Section Header", "13px · bold · Aurum"),
    ("Body Text",      "11px · normal · Parchment"),
    ("Dim Label",      "10px · normal · Aurum Dim"),
    ("MICRO LABEL",    "9px · spaced · Aurum Dim"),
]


class StyleReference(ArcaneWidget):
    """Scrollable palette + typography quick-reference."""

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Style Reference", parent)
        self._build_body()
        self.set_status("idle", "")

    def _build_body(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {C_BG}; }}")

        inner = QWidget()
        inner.setStyleSheet(f"background: {C_BG};")
        vbox = QVBoxLayout(inner)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(8)

        # ── Palette ───────────────────────────────────────────────────
        vbox.addWidget(micro_label("chromata arcana"))
        for name, colour, var in PALETTE:
            row = QHBoxLayout()
            swatch = QLabel("  ")
            swatch.setFixedSize(18, 18)
            swatch.setStyleSheet(
                f"background: {colour}; border: 1px solid {C_GOLD_DARK};"
            )
            row.addWidget(swatch)
            lbl = QLabel(f"{name}  ·  {colour}")
            lbl.setStyleSheet(
                f"color: {C_TEXT}; font-family: Georgia, serif; font-size: 10px;"
            )
            row.addWidget(lbl)
            row.addStretch()
            vbox.addLayout(row)

        # ── Separator ─────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK};")
        vbox.addWidget(sep)

        # ── Typography ────────────────────────────────────────────────
        vbox.addWidget(micro_label("typography"))
        for label, spec in TYPE_SAMPLES:
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet(
                f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 10px; font-weight: bold;"
            )
            spec_lbl = QLabel(spec)
            spec_lbl.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 9px; letter-spacing: 1px;"
            )
            vbox.addWidget(name_lbl)
            vbox.addWidget(spec_lbl)

        vbox.addStretch()
        scroll.setWidget(inner)
        self._body_layout.addWidget(scroll)
