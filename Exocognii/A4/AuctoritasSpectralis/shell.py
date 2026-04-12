"""
AUCTORITAS SPECTRALIS — v1.0.0
shell.py — A4 Common Shell

Four canonical zones:
  Zone I   — Titulum   (TITULUM_W px, full left height)
  Zone II  — Feature Codex (TITULUM_W px, below Titulum, scrollable)
  Zone III — Fascia    (FASCIA_H px, top-right, feature-keyed stacked strips)
  Zone IV  — Canvas    (QStackedWidget, full remainder)
  Status bar — full width, STATUS_H px

Patterns borrowed from Agentia Architecturalis:
  - _CodexItem with enterEvent/leaveEvent for reliable hover
  - Fascia as QStackedWidget of per-feature strips
  - LAT/EN as two distinct toggle buttons, not a single cycler
  - Consistent 14px horizontal margins throughout
  - Typography: FONT_DISPLAY for headings, FONT_MONO for labels
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QFrame, QPushButton, QSizePolicy, QStackedWidget, QScrollArea,
    QApplication, QSplitter,
)

from AuctoritasSpectralis import tokens as tok
import AuctoritasSpectralis.config as cfg


# ── Tiny helpers ─────────────────────────────────────────────────────────

def _hsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{tok.C_GOLD_DARK};color:{tok.C_GOLD_DARK};max-height:1px;")
    return f


def _vsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setFixedWidth(1)
    f.setFixedHeight(22)
    f.setStyleSheet(f"background:{tok.C_GOLD_DARK};border:none;")
    return f


def _mono_label(text: str, size: int = 8, color: str = None,
                spacing: float = 1.0, upper: bool = False) -> QLabel:
    color = color or tok.C_GOLD_DIM
    lbl = QLabel(text.upper() if upper else text)
    lbl.setStyleSheet(
        f"font-family:{tok.FONT_MONO};font-size:{size}px;"
        f"color:{color};background:transparent;letter-spacing:{spacing}px;"
    )
    return lbl


# ── Feature names ─────────────────────────────────────────────────────────

FEATURE_NAMES_LAT = ["Colores", "Observatory", "Specularium", "Bibliotheca", "Registrum"]
FEATURE_NAMES_EN  = ["Colours", "Observatory", "Preview",     "Library",     "Registry"]
FEATURE_KEYS      = ["colores", "observatory", "specularium", "bibliotheca", "registrum"]


# ── Fascia button ─────────────────────────────────────────────────────────

class FasciaButton(QPushButton):
    """Styled fascia toolbar button. Variant: normal | primary | confirm | danger | config."""

    STYLES = {
        "normal":  (tok.C_GOLD_DIM,  tok.C_GOLD_DARK, False),
        "primary": (tok.C_GOLD,      tok.C_GOLD_DIM,  False),
        "confirm": (tok.C_TEAL,      tok.C_TEAL,      False),
        "danger":  (tok.C_CRIMSON,   tok.C_CRIMSON,   False),
        "config":  (tok.C_GOLD_DIM,  tok.C_GOLD_DARK, True),   # dashed border
    }

    def __init__(self, text: str, variant: str = "normal", parent=None):
        super().__init__(text, parent)
        self._variant = variant
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(28)
        self._apply()

    def _apply(self):
        color, border, dashed = self.STYLES.get(self._variant, self.STYLES["normal"])
        border_style = "dashed" if dashed else "solid"
        self.setStyleSheet(
            f"QPushButton{{"
            f"  font-family:{tok.FONT_MONO};font-size:9px;letter-spacing:1.5px;"
            f"  padding:5px 10px;color:{color};"
            f"  background:{tok.C_BG};border:1px {border_style} {border};}}"
            f"QPushButton:hover{{"
            f"  background:{tok.C_GOLD_DARK};color:{tok.C_GOLD};border-color:{tok.C_GOLD_DIM};}}"
            f"QPushButton:pressed{{"
            f"  background:{tok.C_GOLD_DIM};color:{tok.C_BG};}}"
            f"QPushButton:disabled{{"
            f"  color:{tok.C_GOLD_DARK};border-color:#1a1408;}}"
        )

    def set_warn(self, warn: bool):
        if warn:
            self.setStyleSheet(
                f"QPushButton{{font-family:{tok.FONT_MONO};font-size:9px;"
                f"letter-spacing:1.5px;padding:5px 10px;"
                f"color:{tok.C_TEXT};background:{tok.C_BG};"
                f"border:1px solid {tok.C_GOLD_DIM};}}"
                f"QPushButton:hover{{background:{tok.C_GOLD_DARK};color:{tok.C_GOLD};}}"
            )
        else:
            self._apply()


# ── Titulum (Zone I) ──────────────────────────────────────────────────────

class Titulum(QFrame):
    """Zone I — bureau identity panel. Fixed width. Never changes."""

    lang_changed = pyqtSignal(str)  # "LAT" or "EN"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titulum")
        self.setFixedWidth(tok.TITULUM_W)
        self.setStyleSheet(
            f"#titulum{{background:{tok.C_PANEL};"
            f"border-right:1px solid {tok.C_GOLD_DARK};"
            f"border-bottom:1px solid {tok.C_GOLD_DARK};}}"
        )
        self._lang = cfg.get("lat_en_mode", "LAT")
        self._theme_name = "—"
        self._seal_trunc = ""
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 12)
        layout.setSpacing(3)

        # Overline
        overline = _mono_label("Triumviratus · Bureau I", 7, tok.C_GOLD_DIM, 2.5)
        layout.addWidget(overline)

        layout.addSpacing(4)

        # Primary title
        title = QLabel("AUCTORITAS\nSPECTRALIS")
        title.setStyleSheet(
            f"font-family:{tok.FONT_DISPLAY};"
            f"font-size:13px;font-weight:900;"
            f"color:{tok.C_GOLD};letter-spacing:1.5px;line-height:1.3;"
            f"background:transparent;"
        )
        layout.addWidget(title)

        layout.addSpacing(2)

        # English name
        en = _mono_label("Spectral Compliance Authority", 8, tok.C_GOLD_DIM, 0.5)
        en.setWordWrap(True)
        layout.addWidget(en)

        layout.addSpacing(3)

        # Motto
        motto = QLabel("Codexium Chromaticus\n· Sequentiae Umbrarum")
        motto.setStyleSheet(
            f"font-family:{tok.FONT_SERIF};"
            f"font-size:9px;font-style:italic;"
            f"color:{tok.C_GOLD_DIM};background:transparent;"
        )
        layout.addWidget(motto)

        layout.addSpacing(6)
        layout.addWidget(_hsep())
        layout.addSpacing(6)

        # Description
        desc = QLabel(
            "The apparatus adjudicates chromatic "
            "disputes with the gravity of a Roman "
            "senate and the flexibility of a sealed "
            "vault. It does not negotiate. It ratifies."
        )
        desc.setStyleSheet(
            f"font-family:{tok.FONT_SERIF};"
            f"font-size:9px;font-style:italic;"
            f"color:{tok.C_TEXT};background:transparent;opacity:0.6;"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(8)
        layout.addWidget(_hsep())
        layout.addSpacing(5)

        # Active theme state
        self._theme_lbl = _mono_label("Theme: —", 8, tok.C_GOLD_DIM, 0.3)
        self._seal_lbl  = _mono_label("", 7, tok.C_GOLD_DARK, 0.3)
        layout.addWidget(self._theme_lbl)
        layout.addWidget(self._seal_lbl)

        layout.addStretch()
        layout.addWidget(_hsep())
        layout.addSpacing(6)

        # LAT / EN — two distinct buttons, AA pattern
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(0, 0, 0, 0)
        lang_row.setSpacing(0)

        self._btn_lat = QPushButton("LAT")
        self._btn_en  = QPushButton("EN")

        for btn in (self._btn_lat, self._btn_en):
            btn.setFixedHeight(22)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_lat.clicked.connect(lambda: self._set_lang("LAT"))
        self._btn_en.clicked.connect(lambda:  self._set_lang("EN"))

        lang_row.addWidget(self._btn_lat)
        lang_row.addWidget(self._btn_en)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        self._refresh_lang_buttons()

        layout.addSpacing(4)

        # Zone label
        zone = _mono_label("ZONE I · TITULUM", 7, f"rgba(122,106,42,0.4)", 2.0)
        zone.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(zone)

    # ── Lang ─────────────────────────────────────────────────────────────

    def _set_lang(self, lang: str):
        self._lang = lang
        cfg.set_key("lat_en_mode", lang)
        self._refresh_lang_buttons()
        self.lang_changed.emit(lang)

    def _refresh_lang_buttons(self):
        active = (
            f"background:{tok.C_GOLD_DARK};color:{tok.C_GOLD};"
            f"border:1px solid {tok.C_GOLD_DARK};"
            f"font-family:{tok.FONT_MONO};font-size:8px;"
            f"letter-spacing:1px;padding:2px 8px;"
        )
        inactive = (
            f"background:transparent;color:{tok.C_GOLD_DIM};"
            f"border:1px solid {tok.C_GOLD_DARK};"
            f"font-family:{tok.FONT_MONO};font-size:8px;"
            f"letter-spacing:1px;padding:2px 8px;"
        )
        self._btn_lat.setStyleSheet(active if self._lang == "LAT" else inactive)
        self._btn_en.setStyleSheet( active if self._lang == "EN"  else inactive)

    def update_theme_state(self, designator: str, seal_trunc: str):
        self._theme_lbl.setText(f"Theme: {designator}")
        self._seal_lbl.setText(seal_trunc)

    @property
    def lang(self) -> str:
        return self._lang


# ── _CodexItem ────────────────────────────────────────────────────────────

class _CodexItem(QLabel):
    """Clickable feature codex item. Hover via enterEvent/leaveEvent (AA pattern)."""

    clicked = pyqtSignal()

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False
        self._refresh_style()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        self._refresh_style()

    def _refresh_style(self):
        if self._active:
            self.setStyleSheet(
                f"padding:8px 14px;"
                f"font-family:{tok.FONT_MONO};font-size:9px;letter-spacing:1.5px;"
                f"text-transform:uppercase;"
                f"color:{tok.C_GOLD};"
                f"border-left:2px solid {tok.C_GOLD};"
                f"background:rgba(212,175,55,0.06);"
            )
        else:
            self.setStyleSheet(
                f"padding:8px 14px;"
                f"font-family:{tok.FONT_MONO};font-size:9px;letter-spacing:1.5px;"
                f"text-transform:uppercase;"
                f"color:{tok.C_GOLD_DIM};"
                f"border-left:2px solid transparent;"
                f"background:transparent;"
            )

    def enterEvent(self, event):
        if not self._active:
            self.setStyleSheet(
                f"padding:8px 14px;"
                f"font-family:{tok.FONT_MONO};font-size:9px;letter-spacing:1.5px;"
                f"text-transform:uppercase;"
                f"color:{tok.C_TEXT};"
                f"border-left:2px solid {tok.C_GOLD_DARK};"
                f"background:rgba(212,175,55,0.03);"
            )
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._refresh_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ── Feature Codex (Zone II) ───────────────────────────────────────────────

class FeatureCodex(QFrame):
    """Zone II — left rail feature navigation."""

    feature_selected = pyqtSignal(int)   # 0-indexed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("featureCodex")
        self.setFixedWidth(tok.TITULUM_W)
        self.setStyleSheet(
            f"#featureCodex{{background:{tok.C_PANEL};"
            f"border-right:1px solid {tok.C_GOLD_DARK};}}"
        )
        self._items: list[_CodexItem] = []
        self._active = 0
        self._mode = cfg.get("lat_en_mode", "LAT")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(0)

        # Header
        head = _mono_label("Feature Codex", 7, tok.C_GOLD_DIM, 2.5)
        head.setContentsMargins(14, 0, 14, 6)
        head.setStyleSheet(
            head.styleSheet() +
            f"border-bottom:1px solid {tok.C_GOLD_DARK};"
            f"padding-left:14px;padding-bottom:6px;"
        )
        layout.addWidget(head)

        names = FEATURE_NAMES_LAT if self._mode == "LAT" else FEATURE_NAMES_EN
        for i, name in enumerate(names):
            item = _CodexItem(f"◈  {name}" if i == 0 else name)
            item.clicked.connect(lambda idx=i: self._select(idx))
            self._items.append(item)
            layout.addWidget(item)

        layout.addStretch()

        # Zone label
        zone = _mono_label("ZONE II · FEATURE CODEX", 7, "rgba(122,106,42,0.4)", 1.5)
        zone.setAlignment(Qt.AlignmentFlag.AlignRight)
        zone.setContentsMargins(0, 0, 10, 0)
        zone.setStyleSheet(
            zone.styleSheet() +
            f"border-top:1px solid #1a1408;padding:5px 10px 5px 0;"
        )
        layout.addWidget(zone)

    def _select(self, index: int):
        self._active = index
        names = FEATURE_NAMES_LAT if self._mode == "LAT" else FEATURE_NAMES_EN
        for i, item in enumerate(self._items):
            item.active = (i == index)
            item.setText(f"◈  {names[i]}" if i == index else names[i])
        self.feature_selected.emit(index)

    def set_mode(self, mode: str):
        self._mode = mode
        names = FEATURE_NAMES_LAT if mode == "LAT" else FEATURE_NAMES_EN
        for i, item in enumerate(self._items):
            item.setText(f"◈  {names[i]}" if i == self._active else names[i])

    def select(self, index: int):
        self._select(index)

    @property
    def active(self) -> int:
        return self._active


# ── Fascia strip ──────────────────────────────────────────────────────────

class _FasciaStrip(QWidget):
    """One feature's toolbar content. Held in the Fascia stack."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 0, 12, 0)
        self._layout.setSpacing(5)

    def add(self, widget: QWidget) -> QWidget:
        self._layout.addWidget(widget)
        return widget

    def add_sep(self):
        self._layout.addWidget(_vsep())

    def add_stretch(self):
        self._layout.addStretch()

    def add_zone_label(self):
        lbl = _mono_label("FASCIA", 7, "rgba(122,106,42,0.4)", 2.0)
        lbl.setContentsMargins(0, 0, 6, 0)
        self._layout.addWidget(lbl)


# ── Fascia (Zone III) ─────────────────────────────────────────────────────

class Fascia(QFrame):
    """Zone III — feature-keyed action toolbar. 52px fixed height."""

    config_requested = pyqtSignal()
    help_requested   = pyqtSignal()
    lat_en_toggled   = pyqtSignal(str)   # kept for compat — now driven by Titulum

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fascia")
        self.setFixedHeight(tok.FASCIA_H)
        self.setStyleSheet(
            f"#fascia{{background:{tok.C_PANEL};"
            f"border-bottom:1px solid {tok.C_GOLD_DARK};}}"
        )
        self._stack   = QStackedWidget(self)
        self._strips: dict[str, _FasciaStrip] = {}

        # Root layout — stack fills the fascia
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._stack)

        self._build_all()

    def _build_all(self):
        for key in FEATURE_KEYS:
            strip = _FasciaStrip()
            strip.add_zone_label()
            strip.add_stretch()
            # Config + Help always rightmost
            b_cfg  = FasciaButton("⚙ Config", "config")
            b_help = FasciaButton("? Help",   "normal")
            b_cfg.clicked.connect(self.config_requested)
            b_help.clicked.connect(self.help_requested)
            strip.add(b_cfg)
            strip.add(b_help)
            self._strips[key] = strip
            self._stack.addWidget(strip)

    def set_feature_buttons(self, key: str, buttons: list[QWidget]):
        """
        Replace the feature-specific buttons in a strip.
        Called by app.py when a feature registers its Fascia buttons.
        Buttons are inserted before the stretch/Config/Help.
        """
        strip = self._strips.get(key)
        if strip is None:
            return
        layout = strip._layout
        # Remove everything except zone label (index 0) — rebuild
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().setParent(None)

        for btn in buttons:
            layout.addWidget(btn)

        layout.addStretch()

        b_cfg  = FasciaButton("⚙ Config", "config")
        b_help = FasciaButton("? Help",   "normal")
        b_cfg.clicked.connect(self.config_requested)
        b_help.clicked.connect(self.help_requested)
        layout.addWidget(b_cfg)
        layout.addWidget(b_help)

    def switch_to(self, key: str):
        strip = self._strips.get(key)
        if strip:
            self._stack.setCurrentWidget(strip)


# ── Status bar ────────────────────────────────────────────────────────────

class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(tok.STATUS_H)
        self.setStyleSheet(
            f"background:{tok.C_PANEL};border-top:1px solid {tok.C_GOLD_DARK};"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)

        self._left  = _mono_label("", 8, tok.C_GOLD_DIM, 0.5)
        self._right = _mono_label("", 8, tok.C_GOLD_DIM, 0.5)
        layout.addWidget(self._left)
        layout.addStretch()
        layout.addWidget(self._right)

    def set_status(self, left: str, right: str = ""):
        self._left.setText(left)
        self._right.setText(right)


# ── Main shell ────────────────────────────────────────────────────────────

class AuctoritasShell(QMainWindow):
    """A4 Common Shell. Four zones + status bar."""

    feature_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AUCTORITAS SPECTRALIS")
        self.setMinimumSize(QSize(1100, 680))
        self.resize(1280, 800)
        self.setStyleSheet(f"background:{tok.C_BG};")

        self._build_shell()
        self._connect_signals()

        esc = QShortcut(QKeySequence("Escape"), self)
        esc.activated.connect(self._on_escape)

    def _build_shell(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Splitter: left column | right column
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"QSplitter::handle{{background:{tok.C_GOLD_DARK};}}")

        # Left: Titulum + FeatureCodex
        left_col = QWidget()
        left_col.setFixedWidth(tok.TITULUM_W)
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.titulum = Titulum()
        self.codex   = FeatureCodex()
        left_layout.addWidget(self.titulum)
        left_layout.addWidget(self.codex, stretch=1)
        splitter.addWidget(left_col)

        # Right: Fascia + Canvas
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.fascia = Fascia()
        self.canvas = QStackedWidget()
        self.canvas.setStyleSheet(f"background:{tok.C_BG};")

        right_layout.addWidget(self.fascia)
        right_layout.addWidget(self.canvas, stretch=1)
        splitter.addWidget(right_col)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([tok.TITULUM_W, 1060])

        self.status_bar = StatusBar()

        root.addWidget(splitter, stretch=1)
        root.addWidget(self.status_bar)

    def _connect_signals(self):
        self.codex.feature_selected.connect(self._on_feature_selected)
        self.titulum.lang_changed.connect(self._on_lang_changed)
        self.fascia.config_requested.connect(self._on_config_requested)
        self.fascia.help_requested.connect(self._on_help_requested)

    def _on_feature_selected(self, index: int):
        self.canvas.setCurrentIndex(index)
        key = FEATURE_KEYS[index] if index < len(FEATURE_KEYS) else FEATURE_KEYS[0]
        self.fascia.switch_to(key)
        self.feature_changed.emit(index)

    def _on_lang_changed(self, mode: str):
        # Codex menu items update immediately
        self.codex.set_mode(mode)
        # Full propagation to features handled by app.py via titulum.lang_changed

    def _on_config_requested(self):
        pass   # handled by app.py

    def _on_help_requested(self):
        self._show_help()

    def _on_escape(self):
        pass   # handled by app.py

    def _show_help(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Auxilium")
        dlg.setMinimumSize(520, 500)
        dlg.setStyleSheet(f"QDialog{{background:{tok.C_PANEL};}}")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("AUXILIUM")
        title.setStyleSheet(
            f"font-family:{tok.FONT_DISPLAY};font-size:14px;font-weight:900;"
            f"color:{tok.C_GOLD};letter-spacing:3px;background:transparent;"
        )
        layout.addWidget(title)
        layout.addWidget(_hsep())

        help_text = (
            f"<span style='font-family:\"Share Tech Mono\",monospace;font-size:9px;"
            f"color:{tok.C_GOLD};letter-spacing:2px;'>GENERATION</span><br><br>"
            f"<b style='color:{tok.C_GOLD};'>Void tab</b> — H, L, C min/max sliders define the randomisation "
            f"envelope for the background. Lock ⊗ to freeze the current hex.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Aurum tab</b> — Same controls for the foreground seed colour.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Forge tab</b> — Algorithm and threshold constrain the "
            f"generation loop. Harmony shapes the hue relationships. "
            f"The five derivation tweaks shape all 8 non-lead tokens.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>LEAD PAIR</b> — Randomise Void + Aurum within their envelopes "
            f"until the contrast threshold is met. Updates hex fields only.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>GENERATE</b> — Derive the full 10-token palette from the current "
            f"Lead Pair using Forge settings.<br><br>"
            f"<span style='font-family:\"Share Tech Mono\",monospace;font-size:9px;"
            f"color:{tok.C_GOLD};letter-spacing:2px;'>FEATURES</span><br><br>"
            f"<b style='color:{tok.C_GOLD};'>Observatory</b> — Contrast audit. All six metrics for any FG/BG pair. "
            f"Contrast matrix shows all combinations.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Specularium</b> — Live preview across four contexts.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Bibliotheca</b> — Browser for ratified palettes. "
            f"Onerare loads, Ramificare forks, Comparare audits.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Registrum</b> — Permanent ledger. Read only. Nothing deleted.<br><br>"
            f"<span style='font-family:\"Share Tech Mono\",monospace;font-size:9px;"
            f"color:{tok.C_GOLD};letter-spacing:2px;'>RATIFICATION</span><br><br>"
            f"<b style='color:{tok.C_GOLD};'>Ratificare</b> — SHA-256 seal, Latin designator, writes theme.json, "
            f"signals downstream consumers, enters Registry. Permanent.<br><br>"
            f"<b style='color:{tok.C_GOLD};'>Promulgare</b> — Export all formats without sealing.<br><br>"
            f"<span style='font-family:\"Share Tech Mono\",monospace;font-size:9px;"
            f"color:{tok.C_GOLD};letter-spacing:2px;'>FILES</span><br><br>"
            f"theme.json → ~/.arca/theme.json<br>"
            f"Registry   → ~/.arca/chromatic_registry.db<br>"
            f"Signal     → ~/.arca/signals/theme_updated<br>"
            f"Config     → ~/.arca/spectralis.json"
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border:1px solid {tok.C_GOLD_DARK};background:{tok.C_BG};")
        body = QLabel(help_text)
        body.setStyleSheet(
            f"font-family:{tok.FONT_SERIF};font-size:11px;"
            f"color:{tok.C_TEXT};background:transparent;padding:14px;line-height:1.6;"
        )
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        scroll.setWidget(body)
        layout.addWidget(scroll, stretch=1)

        close = FasciaButton("Discede", "normal")
        close.setFixedHeight(28)
        close.clicked.connect(dlg.accept)
        layout.addWidget(close)
        dlg.exec()

    # ── Public API ────────────────────────────────────────────────────────

    def add_feature(self, widget: QWidget) -> int:
        return self.canvas.addWidget(widget)

    def set_feature_buttons(self, buttons: list[QWidget]) -> None:
        """Set fascia buttons for the currently active feature."""
        idx = self.canvas.currentIndex()
        key = FEATURE_KEYS[idx] if idx < len(FEATURE_KEYS) else FEATURE_KEYS[0]
        self.fascia.set_feature_buttons(key, buttons)

    def register_feature_buttons(self, index: int, buttons: list[QWidget]) -> None:
        """Pre-register fascia buttons for a feature by index."""
        key = FEATURE_KEYS[index] if index < len(FEATURE_KEYS) else FEATURE_KEYS[0]
        self.fascia.set_feature_buttons(key, buttons)

    def set_status(self, left: str, right: str = "") -> None:
        self.status_bar.set_status(left, right)

    def update_theme_state(self, designator: str, seal_trunc: str) -> None:
        self.titulum.update_theme_state(designator, seal_trunc)

    def select_feature(self, index: int) -> None:
        self.codex.select(index)
