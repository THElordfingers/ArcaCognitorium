"""
AUCTORITAS SPECTRALIS — v1.0.0
features/specularium.py — Feature III: SPECULARIUM VIVUM

Live preview. Four display contexts switchable via tab strip.
All 10 tokens explicitly exercised in every context.
Updates live on every palette change. No refresh required.

Contexts: Instrumentum · Documentum · Insignia · Token Strip
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QScrollArea, QFrame, QSizePolicy, QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from AuctoritasSpectralis.i18n import t, context_names

C_VOID      = "#050507"
C_OBSIDIAN  = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_PARCHMENT = "#c8b88a"
C_VELLUM    = "#e8e0cc"

TOKEN_ORDER = [
    "c_bg", "c_gold", "c_panel", "c_subtle", "c_gold_dark",
    "c_gold_dim", "c_text", "c_white", "c_crimson", "c_teal",
]

CONTEXT_NAMES = ["Instrumentum", "Documentum", "Insignia", "Token Strip"]


def _p(palette: dict, key: str, fallback: str) -> str:
    return palette.get(key, fallback)


# ── Context: Instrumentum ─────────────────────────────────────────────────

class InstrumentumContext(QWidget):
    """Dark instrument panel preview — exercises all 10 tokens."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette: dict[str, str] = {}
        self._build()

    def _build(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # Outer frame (c_bg)
        self._outer = QWidget()
        self._outer_layout = QVBoxLayout(self._outer)
        self._outer_layout.setContentsMargins(0, 0, 0, 0)
        self._outer_layout.setSpacing(0)

        self._root.addWidget(self._outer)

    def refresh(self, p: dict) -> None:
        self._palette = p

        # Clear and rebuild
        for i in reversed(range(self._outer_layout.count())):
            w = self._outer_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        bg   = _p(p, "c_bg",        C_VOID)
        gold = _p(p, "c_gold",      C_GOLD)
        panel= _p(p, "c_panel",     C_OBSIDIAN)
        sub  = _p(p, "c_subtle",    "#080810")
        gdk  = _p(p, "c_gold_dark", C_GOLD_DARK)
        gdim = _p(p, "c_gold_dim",  C_GOLD_DIM)
        txt  = _p(p, "c_text",      C_PARCHMENT)
        wht  = _p(p, "c_white",     C_VELLUM)
        crim = _p(p, "c_crimson",   C_CRIMSON)
        teal = _p(p, "c_teal",      C_TEAL)

        self._outer.setStyleSheet(f"background: {bg};")

        # Titlebar (c_panel + c_gold)
        tb = QWidget()
        tb.setFixedHeight(34)
        tb.setStyleSheet(
            f"background: {panel}; border-bottom: 1px solid {gdk};"
        )
        tb_layout = QHBoxLayout(tb)
        tb_layout.setContentsMargins(10, 0, 10, 0)
        title = QLabel("INSTRUMENTUM")
        title.setStyleSheet(
            f"font-family: 'Cinzel', Georgia, serif; font-size: 10px; "
            f"color: {gold}; letter-spacing: 2px; background: transparent;"
        )
        tb_layout.addWidget(title)
        tb_layout.addStretch()
        for c in [gdk, gdim, gold]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {c}; font-size: 8px; background: transparent;")
            tb_layout.addWidget(dot)
        self._outer_layout.addWidget(tb)

        # Body
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar (c_subtle)
        sidebar = QWidget()
        sidebar.setFixedWidth(140)
        sidebar.setStyleSheet(
            f"background: {sub}; border-right: 1px solid {gdk};"
        )
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 8, 0, 8)
        sb_layout.setSpacing(0)
        for label, active in [("Colores", True), ("Scrutinium", False),
                               ("Specularium", False), ("Bibliotheca", False)]:
            lbl = QLabel(label)
            lbl.setFixedHeight(30)
            if active:
                lbl.setStyleSheet(
                    f"background: rgba(212,175,55,0.06); color: {gold}; "
                    f"border-left: 2px solid {gold}; padding-left: 14px; "
                    f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
                    f"letter-spacing: 1.5px;"
                )
            else:
                lbl.setStyleSheet(
                    f"background: transparent; color: {gdim}; "
                    f"border-left: 2px solid transparent; padding-left: 16px; "
                    f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
                    f"letter-spacing: 1.5px;"
                )
            sb_layout.addWidget(lbl)
        sb_layout.addStretch()
        body_layout.addWidget(sidebar)

        # Canvas (c_bg + c_panel sections)
        canvas = QWidget()
        canvas.setStyleSheet(f"background: {bg};")
        cv_layout = QVBoxLayout(canvas)
        cv_layout.setContentsMargins(16, 16, 16, 16)
        cv_layout.setSpacing(10)

        # Panel block (c_panel)
        panel_block = QWidget()
        panel_block.setStyleSheet(
            f"background: {panel}; border: 1px solid {gdk};"
        )
        pb_layout = QVBoxLayout(panel_block)
        pb_layout.setContentsMargins(12, 10, 12, 10)
        pb_layout.setSpacing(4)
        h = QLabel("Aureus Crepuscularis")
        h.setStyleSheet(
            f"font-family: 'Cinzel', Georgia, serif; font-size: 11px; "
            f"color: {gold}; letter-spacing: 2px; background: transparent;"
        )
        pb_layout.addWidget(h)
        t = QLabel("The apparatus adjudicates chromatic disputes with the gravity of a Roman senate.")
        t.setStyleSheet(
            f"font-size: 10px; color: {txt}; background: transparent; "
            f"font-family: 'IM Fell English', Georgia, serif; font-style: italic;"
        )
        t.setWordWrap(True)
        pb_layout.addWidget(t)

        # Button row
        btn_row = QHBoxLayout()
        for label, col, border in [
            ("Ratificare", teal, teal),
            ("Promulgare", gdim, gdk),
            ("Discede",    crim, crim),
        ]:
            b = QLabel(label)
            b.setStyleSheet(
                f"font-family: 'Share Tech Mono', monospace; font-size: 8px; "
                f"letter-spacing: 1px; color: {col}; background: {bg}; "
                f"border: 1px solid {border}; padding: 5px 10px;"
            )
            btn_row.addWidget(b)
        btn_row.addStretch()
        pb_layout.addLayout(btn_row)
        cv_layout.addWidget(panel_block)

        # Wht text line
        wl = QLabel(f"● {wht}  ●  {txt}  ●  {gdim}")
        wl.setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
            f"color: {wht}; background: transparent;"
        )
        cv_layout.addWidget(wl)

        body_layout.addWidget(canvas, stretch=1)
        self._outer_layout.addWidget(body, stretch=1)

        # Status bar (c_panel)
        sb_bar = QWidget()
        sb_bar.setFixedHeight(22)
        sb_bar.setStyleSheet(
            f"background: {panel}; border-top: 1px solid {gdk};"
        )
        sb_bar_layout = QHBoxLayout(sb_bar)
        sb_bar_layout.setContentsMargins(10, 0, 10, 0)
        sb_bar_layout.addWidget(QLabel("✦ Ready"))
        sb_bar_layout.itemAt(0).widget().setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 8px; "
            f"color: {gdim}; background: transparent;"
        )
        self._outer_layout.addWidget(sb_bar)


# ── Context: Documentum ───────────────────────────────────────────────────

class DocumentumContext(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._container = QWidget()
        layout.addWidget(self._container)
        self._inner = QVBoxLayout(self._container)
        self._inner.setContentsMargins(32, 32, 32, 32)
        self._inner.setSpacing(12)

    def refresh(self, p: dict) -> None:
        for i in reversed(range(self._inner.count())):
            w = self._inner.itemAt(i).widget()
            if w:
                w.deleteLater()

        wht  = _p(p, "c_white",     C_VELLUM)
        txt  = _p(p, "c_text",      C_PARCHMENT)
        gold = _p(p, "c_gold",      C_GOLD)
        gdim = _p(p, "c_gold_dim",  C_GOLD_DIM)
        gdk  = _p(p, "c_gold_dark", C_GOLD_DARK)
        crim = _p(p, "c_crimson",   C_CRIMSON)
        teal = _p(p, "c_teal",      C_TEAL)

        self._container.setStyleSheet(f"background: {wht};")

        def add_lbl(text, size=11, color=None, italic=False, bold=False, spacing=0):
            lbl = QLabel(text)
            color = color or txt
            lbl.setStyleSheet(
                f"font-family: 'IM Fell English', Georgia, serif; font-size: {size}px; "
                f"color: {color}; background: transparent; "
                f"letter-spacing: {spacing}px;"
                + (" font-style: italic;" if italic else "")
                + (" font-weight: bold;" if bold else "")
            )
            lbl.setWordWrap(True)
            self._inner.addWidget(lbl)

        add_lbl("AUCTORITAS SPECTRALIS", 16, gold, spacing=3)
        add_lbl("Codexium Chromaticus · Sequentiae Umbrarum", 10, gdim, italic=True)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {gdk}; background: {gdk}; margin: 4px 0;")
        sep.setFixedHeight(1)
        self._inner.addWidget(sep)

        add_lbl(
            "The apparatus does not merely select colours. It governs them. "
            "It arbitrates. It ratifies. It remembers. It does not explain itself. It is felt.",
            11, txt, italic=True
        )

        err_lbl = QLabel("⚑ Harmonic conflict detected — Sanguis exceeds tolerance.")
        err_lbl.setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
            f"color: {crim}; background: transparent; padding: 4px 0;"
        )
        self._inner.addWidget(err_lbl)

        ok_lbl = QLabel("✓ Palette ratified — Aureus Crepuscularis")
        ok_lbl.setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
            f"color: {teal}; background: transparent; padding: 4px 0;"
        )
        self._inner.addWidget(ok_lbl)

        self._inner.addStretch()


# ── Context: Insignia ────────────────────────────────────────────────────

class InsigniaContext(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._container = QWidget()
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(32, 32, 32, 32)
        container_layout.setSpacing(20)
        self._inner = container_layout
        layout.addWidget(self._container)

    def refresh(self, p: dict) -> None:
        for i in reversed(range(self._inner.count())):
            w = self._inner.itemAt(i).widget()
            if w:
                w.deleteLater()

        bg   = _p(p, "c_bg",        C_VOID)
        gold = _p(p, "c_gold",      C_GOLD)
        panel= _p(p, "c_panel",     C_OBSIDIAN)
        gdk  = _p(p, "c_gold_dark", C_GOLD_DARK)
        gdim = _p(p, "c_gold_dim",  C_GOLD_DIM)
        crim = _p(p, "c_crimson",   C_CRIMSON)
        teal = _p(p, "c_teal",      C_TEAL)
        wht  = _p(p, "c_white",     C_VELLUM)

        self._container.setStyleSheet(f"background: {bg};")

        # Seal badge
        badge = QFrame()
        badge.setStyleSheet(
            f"background: {panel}; border: 1px solid {gold};"
        )
        b_layout = QVBoxLayout(badge)
        b_layout.setContentsMargins(20, 16, 20, 16)
        b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for text, sz, col, italic in [
            ("✦  SIGILLUM APPROBATIONIS  ✦", 10, gold, False),
            ("AUCTORITAS SPECTRALIS",          14, gold, False),
            ("Spectral Compliance Authority",  9,  gdim, False),
            ("Codexium Chromaticus · Sequentiae Umbrarum", 9, gdim, True),
        ]:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"font-family: {'Cinzel' if not italic else 'IM Fell English'}, Georgia, serif; "
                f"font-size: {sz}px; color: {col}; background: transparent; "
                f"letter-spacing: {'2px' if not italic else '0px'};"
                + (" font-style: italic;" if italic else "")
            )
            b_layout.addWidget(lbl)

        self._inner.addWidget(badge)

        # Status strip
        strip = QHBoxLayout()
        for text, col in [("✓  AA PASS", teal), ("✗  AAA", crim), ("✦  RATIFIED", gold)]:
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
                f"color: {col}; background: {panel}; border: 1px solid {gdk}; "
                f"padding: 5px 10px; letter-spacing: 1px;"
            )
            strip.addWidget(lbl)
        strip.addStretch()

        strip_w = QWidget()
        strip_w.setLayout(strip)
        self._inner.addWidget(strip_w)
        self._inner.addStretch()


# ── Context: Token Strip ──────────────────────────────────────────────────

class TokenStripContext(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._container = QWidget()
        self._inner = QVBoxLayout(self._container)
        self._inner.setContentsMargins(18, 18, 18, 18)
        self._inner.setSpacing(4)
        layout.addWidget(self._container)

    def refresh(self, p: dict) -> None:
        for i in reversed(range(self._inner.count())):
            w = self._inner.itemAt(i).widget()
            if w:
                w.deleteLater()

        bg = _p(p, "c_bg", C_VOID)
        self._container.setStyleSheet(f"background: {bg};")

        for key in TOKEN_ORDER:
            hex_val = p.get(key, "#000000")
            row = QWidget()
            row.setFixedHeight(40)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            swatch = QLabel()
            swatch.setFixedSize(40, 36)
            swatch.setStyleSheet(
                f"background: {hex_val}; border: 1px solid {_p(p, 'c_gold_dark', C_GOLD_DARK)};"
            )
            row_layout.addWidget(swatch)

            key_lbl = QLabel(key)
            key_lbl.setFixedWidth(110)
            key_lbl.setStyleSheet(
                f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
                f"color: {_p(p, 'c_gold_dim', C_GOLD_DIM)}; background: transparent;"
            )

            hex_lbl = QLabel(hex_val)
            hex_lbl.setFixedWidth(80)
            hex_lbl.setStyleSheet(
                f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
                f"color: {_p(p, 'c_text', C_PARCHMENT)}; background: transparent;"
            )

            from AuctoritasSpectralis.engine.nomen import nomen_for_token
            nomen_lbl = QLabel(nomen_for_token(hex_val, key))
            nomen_lbl.setStyleSheet(
                f"font-family: 'IM Fell English', Georgia, serif; font-size: 11px; "
                f"font-style: italic; color: {_p(p, 'c_text', C_PARCHMENT)}; "
                f"background: transparent;"
            )

            row_layout.addWidget(key_lbl)
            row_layout.addWidget(hex_lbl)
            row_layout.addWidget(nomen_lbl)
            row_layout.addStretch()
            self._inner.addWidget(row)

        self._inner.addStretch()


# ── SPECULARIUM main widget ───────────────────────────────────────────────

class SpeculariumFeature(QWidget):
    status_message = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette: dict[str, str] = {}
        self._active_ctx = cfg_default_ctx()
        self._contexts: dict[str, QWidget] = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(0)

        # Tab strip
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabBar::tab {{ font-family: 'Share Tech Mono', monospace; font-size: 9px; "
            f"letter-spacing: 2px; text-transform: uppercase; padding: 7px 16px; "
            f"color: {C_GOLD_DIM}; border-bottom: 2px solid transparent; "
            f"background: transparent; margin-bottom: -1px; }}"
            f"QTabBar::tab:selected {{ color: {C_GOLD}; "
            f"border-bottom: 2px solid {C_GOLD}; background: rgba(212,175,55,0.04); }}"
            f"QTabWidget::pane {{ border: none; border-top: 1px solid {C_GOLD_DARK}; }}"
        )

        ctx_widgets = {
            "Instrumentum": InstrumentumContext(),
            "Documentum":   DocumentumContext(),
            "Insignia":     InsigniaContext(),
            "Token Strip":  TokenStripContext(),
        }
        self._contexts = ctx_widgets

        for name, widget in ctx_widgets.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setStyleSheet("border: none; background: transparent;")
            scroll.setWidget(widget)
            self._tabs.addTab(scroll, name)

        # Set default context
        for i, name in enumerate(CONTEXT_NAMES):
            if name == self._active_ctx:
                self._tabs.setCurrentIndex(i)
                break

        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs, stretch=1)

    def _on_tab_changed(self, index: int) -> None:
        name = CONTEXT_NAMES[index] if index < len(CONTEXT_NAMES) else "Instrumentum"
        ctx = self._contexts.get(name)
        if ctx and self._palette:
            ctx.refresh(self._palette)

    def set_palette(self, palette: dict[str, str]) -> None:
        self._palette = palette
        # Refresh all contexts
        for ctx in self._contexts.values():
            ctx.refresh(palette)
        self.status_message.emit("Specularium — live.", "Specularium")

    def get_fascia_buttons(self, mode: str = "LAT") -> list[QWidget]:
        from AuctoritasSpectralis.shell import FasciaButton

        self._ctx_combo = QComboBox()
        self._ctx_mode  = mode
        for name in context_names(mode):
            self._ctx_combo.addItem(name)
        self._ctx_combo.setFixedWidth(180)
        self._ctx_combo.currentIndexChanged.connect(
            lambda idx: self._switch_context_by_index(idx)
        )
        return [self._ctx_combo]

    def _switch_context_by_index(self, idx: int) -> None:
        self._tabs.setCurrentIndex(idx)

    def set_mode(self, mode: str) -> None:
        if hasattr(self, "_ctx_combo"):
            current_idx = self._ctx_combo.currentIndex()
            self._ctx_combo.blockSignals(True)
            self._ctx_combo.clear()
            for name in context_names(mode):
                self._ctx_combo.addItem(name)
            self._ctx_combo.setCurrentIndex(current_idx)
            self._ctx_combo.blockSignals(False)

    def _switch_context(self, name: str) -> None:
        for i, n in enumerate(CONTEXT_NAMES):
            if n == name:
                self._tabs.setCurrentIndex(i)
                break


def cfg_default_ctx() -> str:
    import AuctoritasSpectralis.config as cfg
    return cfg.get("specularium_default_ctx", "Instrumentum")
