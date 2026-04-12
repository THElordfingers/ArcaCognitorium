"""
AUCTORITAS SPECTRALIS — v1.0.0
features/bibliotheca.py — Feature IV: BIBLIOTHECA

Registry browser. Palette card list with swatch strips and compliance badges.
Detail panel: mini Specularium preview, full token list with Nomina, actions.
Actions: Onerare (load), Ramificare (fork), Comparare (compare).
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QSplitter,
)
from PyQt6.QtCore import Qt, pyqtSignal

from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER
from AuctoritasSpectralis.engine.nomen import generate_nomina
import AuctoritasSpectralis.registry.db as db
from AuctoritasSpectralis.i18n import t

C_VOID      = "#050507"
C_OBSIDIAN  = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_PARCHMENT = "#c8b88a"
C_PASS      = "#1a5a5a"
C_FAIL      = "#6b1212"
C_PASS_T    = "#a0d0c0"
C_FAIL_T    = "#e08080"


def _mono(text: str, size: int = 9, color: str = C_GOLD_DIM) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-family: 'Share Tech Mono', monospace; font-size: {size}px; "
        f"color: {color}; background: transparent; letter-spacing: 0.5px;"
    )
    return lbl


# ── Palette card ──────────────────────────────────────────────────────────

class PaletteCard(QWidget):
    selected = pyqtSignal(dict)  # emits the record dict

    def __init__(self, record: dict, parent=None):
        super().__init__(parent)
        self._record  = record
        self._active  = False
        self._build()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)
        self._refresh_style()

        # Designator
        self._des_lbl = QLabel(self._record.get("designator", "—"))
        self._des_lbl.setStyleSheet(
            f"font-family: 'IM Fell English', Georgia, serif; font-size: 13px; "
            f"color: {C_GOLD}; background: transparent; font-style: italic;"
        )
        layout.addWidget(self._des_lbl)

        # Metadata
        meta = QLabel(
            f"{self._record.get('sealed_at', '—')[:10]}  ·  "
            f"{'AA ✓' if self._record.get('aa_pass') else 'AA ✗'}  "
            f"{'AAA ✓' if self._record.get('aaa_pass') else 'AAA ✗'}"
        )
        meta.setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 7px; "
            f"color: {C_GOLD_DIM}; background: transparent; letter-spacing: 1px;"
        )
        layout.addWidget(meta)

        # Swatch strip
        strip = QHBoxLayout()
        strip.setContentsMargins(0, 3, 0, 0)
        strip.setSpacing(2)
        tokens = self._record.get("tokens", {})
        for key in TOKEN_ORDER:
            hex_val = tokens.get(key, "#000000")
            sw = QLabel()
            sw.setFixedSize(16, 11)
            sw.setStyleSheet(
                f"background: {hex_val}; "
                f"border: 1px solid rgba(58,46,16,0.5);"
            )
            strip.addWidget(sw)
        strip.addStretch()

        strip_w = QWidget()
        strip_w.setLayout(strip)
        layout.addWidget(strip_w)

    def _refresh_style(self):
        if self._active:
            self.setStyleSheet(
                f"background: {C_OBSIDIAN}; border: 1px solid {C_GOLD};"
            )
        else:
            self.setStyleSheet(
                f"background: {C_OBSIDIAN}; border: 1px solid {C_GOLD_DARK};"
            )

    def set_active(self, active: bool) -> None:
        self._active = active
        self._refresh_style()

    def mousePressEvent(self, event):
        self.selected.emit(self._record)
        super().mousePressEvent(event)


# ── Detail panel ─────────────────────────────────────────────────────────

class DetailPanel(QWidget):
    load_requested    = pyqtSignal(dict)  # palette tokens
    fork_requested    = pyqtSignal(dict)
    compare_requested = pyqtSignal(dict, dict)  # (selected, current)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._record: dict = {}
        self._current_palette: dict[str, str] = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self._title = QLabel("—")
        self._title.setStyleSheet(
            f"font-family: 'Cinzel', Georgia, serif; font-size: 15px; "
            f"color: {C_GOLD}; letter-spacing: 2px; background: transparent;"
        )
        self._title.setWordWrap(True)
        layout.addWidget(self._title)

        self._meta = _mono("", size=8)
        layout.addWidget(self._meta)

        # Mini swatch strip
        self._swatch_row = QHBoxLayout()
        self._swatch_row.setSpacing(3)
        self._swatches: list[QLabel] = []
        for _ in TOKEN_ORDER:
            sw = QLabel()
            sw.setFixedSize(22, 18)
            sw.setStyleSheet(f"background: #000; border: 1px solid {C_GOLD_DARK};")
            self._swatches.append(sw)
            self._swatch_row.addWidget(sw)
        self._swatch_row.addStretch()
        swatch_w = QWidget()
        swatch_w.setLayout(self._swatch_row)
        layout.addWidget(swatch_w)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK}; background: {C_GOLD_DARK};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Token list
        self._tok_container = QWidget()
        self._tok_layout = QVBoxLayout(self._tok_container)
        self._tok_layout.setContentsMargins(0, 0, 0, 0)
        self._tok_layout.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setWidget(self._tok_container)
        layout.addWidget(scroll, stretch=1)

        # Actions
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        def _btn(text, variant="normal"):
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ font-family: 'Share Tech Mono', monospace; "
                f"font-size: 8px; letter-spacing: 1.5px; text-transform: uppercase; "
                f"color: {'#1a5a5a' if variant == 'confirm' else C_GOLD_DIM}; "
                f"border: 1px solid {'#1a5a5a' if variant == 'confirm' else C_GOLD_DARK}; "
                f"background: {C_VOID}; padding: 5px 10px; }}"
                f"QPushButton:hover {{ background: {C_GOLD_DARK}; color: {C_GOLD}; }}"
            )
            return b

        self._btn_load    = _btn("Onerare",    "confirm")
        self._btn_fork    = _btn("Ramificare")
        self._btn_compare = _btn("Comparare")

        self._btn_load.clicked.connect(
            lambda: self.load_requested.emit(self._record.get("tokens", {}))
        )
        self._btn_fork.clicked.connect(
            lambda: self.fork_requested.emit(self._record.get("tokens", {}))
        )
        self._btn_compare.clicked.connect(
            lambda: self.compare_requested.emit(
                self._record.get("tokens", {}), self._current_palette
            )
        )

        btn_row.addWidget(self._btn_load)
        btn_row.addWidget(self._btn_fork)
        btn_row.addWidget(self._btn_compare)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def load_record(self, record: dict, current_palette: dict[str, str]) -> None:
        self._record          = record
        self._current_palette = current_palette
        tokens = record.get("tokens", {})
        nomina = record.get("nomina", generate_nomina(tokens))

        self._title.setText(record.get("designator", "—"))
        self._meta.setText(
            f"Sealed: {record.get('sealed_at', '?')[:19]}  "
            f"·  WCAG: {record.get('wcag_min', '?')}  "
            f"·  APCA: {record.get('apca_min', '?')}  "
            f"·  Seal: {record.get('seal', '?')[:8]}…"
        )

        for i, key in enumerate(TOKEN_ORDER):
            hex_val = tokens.get(key, "#000000")
            self._swatches[i].setStyleSheet(
                f"background: {hex_val}; border: 1px solid {C_GOLD_DARK};"
            )

        # Clear and rebuild token rows
        for i in reversed(range(self._tok_layout.count())):
            w = self._tok_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for key in TOKEN_ORDER:
            hex_val = tokens.get(key, "#000000")
            nomen   = nomina.get(key, "—")
            row_w   = QWidget()
            row_l   = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 1, 0, 1)
            row_l.setSpacing(8)

            sw = QLabel()
            sw.setFixedSize(18, 14)
            sw.setStyleSheet(f"background: {hex_val}; border: 1px solid {C_GOLD_DARK};")
            row_l.addWidget(sw)

            key_lbl = _mono(key, size=8)
            key_lbl.setFixedWidth(96)
            row_l.addWidget(key_lbl)

            hex_lbl = _mono(hex_val, size=8, color=C_GOLD_DIM)
            hex_lbl.setFixedWidth(72)
            row_l.addWidget(hex_lbl)

            nomen_lbl = QLabel(nomen)
            nomen_lbl.setStyleSheet(
                f"font-family: 'IM Fell English', Georgia, serif; font-size: 11px; "
                f"font-style: italic; color: {C_PARCHMENT}; background: transparent;"
            )
            row_l.addWidget(nomen_lbl, stretch=1)
            self._tok_layout.addWidget(row_w)

        self._tok_layout.addStretch()


# ── BIBLIOTHECA main widget ───────────────────────────────────────────────

class BibliothecaFeature(QWidget):
    load_requested    = pyqtSignal(dict)
    fork_requested    = pyqtSignal(dict)
    compare_requested = pyqtSignal(dict, dict)
    status_message    = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records:  list[dict] = []
        self._selected: dict = {}
        self._current_palette: dict[str, str] = {}
        self._active_card: PaletteCard | None = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {C_GOLD_DARK}; width: 1px; }}"
        )

        # Card list
        card_panel = QWidget()
        card_panel.setFixedWidth(280)
        card_layout = QVBoxLayout(card_panel)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(6)

        micro = _mono("CHROMATIC REGISTRY", size=8, color=C_GOLD_DIM)
        micro.setStyleSheet(micro.styleSheet() + " letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px;")
        card_layout.addWidget(micro)

        self._card_scroll = QScrollArea()
        self._card_scroll.setWidgetResizable(True)
        self._card_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._card_scroll.setStyleSheet("border: none; background: transparent;")

        self._card_container = QWidget()
        self._cards_layout   = QVBoxLayout(self._card_container)
        self._cards_layout.setContentsMargins(0, 0, 4, 0)
        self._cards_layout.setSpacing(3)
        self._cards_layout.addStretch()

        self._card_scroll.setWidget(self._card_container)
        card_layout.addWidget(self._card_scroll, stretch=1)
        splitter.addWidget(card_panel)

        # Detail panel
        self._detail = DetailPanel()
        self._detail.load_requested.connect(self.load_requested)
        self._detail.fork_requested.connect(self.fork_requested)
        self._detail.compare_requested.connect(self.compare_requested)
        splitter.addWidget(self._detail)

        splitter.setSizes([280, 600])
        layout.addWidget(splitter, stretch=1)

    def refresh(self, current_palette: dict[str, str] | None = None) -> None:
        if current_palette:
            self._current_palette = current_palette

        # Remove old cards
        for i in reversed(range(self._cards_layout.count())):
            w = self._cards_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self._records = db.fetch_all()
        # Clear stale reference before rebuilding — old widgets are being deleted
        self._active_card = None

        for record in self._records:
            card = PaletteCard(record)
            card.selected.connect(self._on_card_selected)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

        count = len(self._records)
        self.status_message.emit(
            "Bibliotheca",
            f"Bibliotheca · {count} palette{'s' if count != 1 else ''}",
        )

        # Auto-select first
        if self._records:
            first_card = self._cards_layout.itemAt(0).widget()
            if isinstance(first_card, PaletteCard):
                first_card.set_active(True)
                self._active_card = first_card
                self._detail.load_record(self._records[0], self._current_palette)

    def _on_card_selected(self, record: dict) -> None:
        # Deactivate previous — guard against Qt having already deleted the widget
        if self._active_card:
            try:
                self._active_card.set_active(False)
            except RuntimeError:
                pass
        self._active_card = None

        # Find and activate clicked card
        for i in range(self._cards_layout.count()):
            w = self._cards_layout.itemAt(i).widget()
            if isinstance(w, PaletteCard) and w._record == record:
                w.set_active(True)
                self._active_card = w
                break

        self._selected = record
        self._detail.load_record(record, self._current_palette)
        self.status_message.emit(
            f"✦ {record.get('designator', '—')} selected.",
            f"Bibliotheca · {len(self._records)} palettes",
        )

    def set_current_palette(self, palette: dict[str, str]) -> None:
        self._current_palette = palette
        self._detail._current_palette = palette

    def get_fascia_buttons(self, mode: str = "LAT") -> list[QWidget]:
        from AuctoritasSpectralis.shell import FasciaButton

        self._fb_load    = FasciaButton(t("btn.onerare",    mode), "confirm")
        self._fb_fork    = FasciaButton(t("btn.ramificare", mode), "normal")
        self._fb_compare = FasciaButton(t("btn.comparare",  mode), "normal")

        self._fb_load.clicked.connect(
            lambda: self.load_requested.emit(self._selected.get("tokens", {}))
            if self._selected else None
        )
        self._fb_fork.clicked.connect(
            lambda: self.fork_requested.emit(self._selected.get("tokens", {}))
            if self._selected else None
        )
        self._fb_compare.clicked.connect(
            lambda: self.compare_requested.emit(
                self._selected.get("tokens", {}), self._current_palette
            ) if self._selected else None
        )

        return [self._fb_load, self._fb_fork, self._fb_compare]

    def set_mode(self, mode: str) -> None:
        for attr, key in [("_fb_load", "btn.onerare"), ("_fb_fork", "btn.ramificare"), ("_fb_compare", "btn.comparare")]:
            btn = getattr(self, attr, None)
            if btn:
                btn.setText(t(key, mode))
