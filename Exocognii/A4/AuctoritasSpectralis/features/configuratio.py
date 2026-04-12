"""
AUCTORITAS SPECTRALIS — v1.0.0
features/configuratio.py — CONFIGURATIO modal

Not a feature. Accessed via ⚙ Config in Fascia.
Opens as a modal overlay on the canvas. Closed by Escape or ✕ Discede.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal

import AuctoritasSpectralis.config as cfg
from AuctoritasSpectralis.i18n import t
from AuctoritasSpectralis.engine.harmony import HARMONY_MODELS

C_VOID      = "#050507"
C_OBSIDIAN  = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_PARCHMENT = "#c8b88a"
C_TEAL      = "#1a5a5a"

CONTRAST_ALGOS = ["WCAG", "APCA", "DeltaE"]
SPECULARIUM_CONTEXTS = ["Instrumentum", "Documentum", "Insignia", "Token Strip"]


def _mono(text: str, size: int = 8, color: str = C_GOLD_DIM) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-family: 'Share Tech Mono', monospace; font-size: {size}px; "
        f"color: {color}; background: transparent; letter-spacing: 1px; "
        f"text-transform: uppercase;"
    )
    return lbl


class ConfiguratioModal(QWidget):
    """
    Semi-transparent overlay that covers the canvas.
    Sits as a child of the canvas widget, fills it entirely.
    """

    saved   = pyqtSignal(dict)   # emits updated config dict
    closed  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self._build()
        self.hide()

    def _build(self):
        # Dim overlay layer
        self._overlay = QWidget(self)
        self._overlay.setStyleSheet("background: rgba(5,5,7,0.88);")
        self._overlay.lower()

        # Modal card
        self._card = QFrame(self)
        self._card.setFixedWidth(380)
        self._card.setStyleSheet(
            f"background: {C_OBSIDIAN}; border: 1px solid {C_GOLD};"
        )

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(0)

        # Title
        title = QLabel("⚙  CONFIGURATIO")
        title.setStyleSheet(
            f"font-family: 'Cinzel', Georgia, serif; font-size: 12px; "
            f"color: {C_GOLD}; letter-spacing: 2px; text-transform: uppercase; "
            f"background: transparent; border-bottom: 1px solid {C_GOLD_DARK}; "
            f"padding-bottom: 8px; margin-bottom: 14px;"
        )
        card_layout.addWidget(title)

        # ── Settings rows ──

        self._widgets: dict[str, QWidget] = {}

        def add_row(label_text: str, widget: QWidget):
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 0, 0, 10)
            lbl = _mono(label_text)
            lbl.setFixedWidth(170)
            lbl.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(widget, stretch=1)
            card_layout.addLayout(row)

        # Default Harmony
        self._combo_harmony = QComboBox()
        for m in HARMONY_MODELS:
            self._combo_harmony.addItem(m)
        add_row("Default Harmony", self._combo_harmony)
        self._widgets["default_harmony"] = self._combo_harmony

        # Default Contrast Algo
        self._combo_contrast = QComboBox()
        for a in CONTRAST_ALGOS:
            self._combo_contrast.addItem(a)
        add_row("Default Contrast Algo", self._combo_contrast)
        self._widgets["default_contrast_algo"] = self._combo_contrast

        # Export Directory
        self._edit_export = QLineEdit()
        add_row("Export Directory", self._edit_export)
        self._widgets["export_directory"] = self._edit_export

        # Mundana State Bus
        self._edit_bus = QLineEdit()
        self._edit_bus.setPlaceholderText("Not connected (interim)")
        add_row("Mundana State Bus", self._edit_bus)
        self._widgets["mundana_bus_target"] = self._edit_bus

        # Signal File Path
        self._edit_signal = QLineEdit()
        add_row("Signal File Path", self._edit_signal)
        self._widgets["signal_file_path"] = self._edit_signal

        # Specularium Default
        self._combo_spec = QComboBox()
        for ctx in SPECULARIUM_CONTEXTS:
            self._combo_spec.addItem(ctx)
        add_row("Specularium Default", self._combo_spec)
        self._widgets["specularium_default_ctx"] = self._combo_spec

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK}; background: {C_GOLD_DARK};")
        sep.setFixedHeight(1)
        card_layout.addWidget(sep)
        card_layout.addSpacing(12)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        def _btn(text, color=C_GOLD_DIM, border=None):
            b = QPushButton(text)
            bc = border or C_GOLD_DARK
            b.setStyleSheet(
                f"QPushButton {{ font-family: 'Share Tech Mono', monospace; "
                f"font-size: 8px; letter-spacing: 1.5px; text-transform: uppercase; "
                f"color: {color}; border: 1px solid {bc}; "
                f"background: {C_VOID}; padding: 7px 12px; }}"
                f"QPushButton:hover {{ background: {C_GOLD_DARK}; color: {C_GOLD}; }}"
            )
            return b

        b_save  = _btn(t("cfg.save"),   color=C_TEAL, border=C_TEAL)
        b_reset = _btn(t("cfg.reset"))
        b_close = _btn(t("cfg.close"),  color=C_GOLD_DIM, border=C_GOLD_DARK)

        self._b_save  = b_save
        self._b_reset = b_reset
        self._b_close = b_close
        b_save.clicked.connect(self._on_save)
        b_reset.clicked.connect(self._on_reset)
        b_close.clicked.connect(self.close_modal)

        btn_row.addWidget(b_save)
        btn_row.addWidget(b_reset)
        btn_row.addStretch()
        btn_row.addWidget(b_close)
        card_layout.addLayout(btn_row)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())
        # Centre the card
        cx = (self.width()  - self._card.width())  // 2
        cy = (self.height() - self._card.sizeHint().height()) // 2
        self._card.move(cx, max(cy, 20))

    def open_modal(self) -> None:
        """Populate fields from current config and show."""
        current = cfg.load()

        harmony_idx = HARMONY_MODELS.index(current.get("default_harmony", "Complementary")) \
            if current.get("default_harmony") in HARMONY_MODELS else 0
        self._combo_harmony.setCurrentIndex(harmony_idx)

        contrast_idx = CONTRAST_ALGOS.index(current.get("default_contrast_algo", "WCAG")) \
            if current.get("default_contrast_algo") in CONTRAST_ALGOS else 0
        self._combo_contrast.setCurrentIndex(contrast_idx)

        self._edit_export.setText(current.get("export_directory", ""))
        self._edit_bus.setText(current.get("mundana_bus_target", ""))
        self._edit_signal.setText(current.get("signal_file_path", ""))

        spec_ctx = current.get("specularium_default_ctx", "Instrumentum")
        spec_idx = SPECULARIUM_CONTEXTS.index(spec_ctx) \
            if spec_ctx in SPECULARIUM_CONTEXTS else 0
        self._combo_spec.setCurrentIndex(spec_idx)

        self.show()
        self.raise_()

    def set_mode(self, mode: str) -> None:
        if hasattr(self, "_b_save"):
            self._b_save.setText(t("cfg.save",  mode))
            self._b_reset.setText(t("cfg.reset", mode))
            self._b_close.setText(t("cfg.close", mode))

    def close_modal(self) -> None:
        self.hide()
        self.closed.emit()

    def _on_save(self) -> None:
        updated = cfg.load()
        updated["default_harmony"]         = self._combo_harmony.currentText()
        updated["default_contrast_algo"]   = self._combo_contrast.currentText()
        updated["export_directory"]        = self._edit_export.text().strip()
        updated["mundana_bus_target"]      = self._edit_bus.text().strip()
        updated["signal_file_path"]        = self._edit_signal.text().strip()
        updated["specularium_default_ctx"] = self._combo_spec.currentText()
        cfg.save(updated)
        self.saved.emit(updated)
        self.close_modal()

    def _on_reset(self) -> None:
        cfg.save(dict(cfg.DEFAULTS))
        self.open_modal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_modal()
        else:
            super().keyPressEvent(event)
