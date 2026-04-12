"""
Zone III — Fascia (52px tall)

Feature-keyed top toolbar strip. HELP button is the sole persistent element,
always rightmost. Each feature defines its own set of action buttons.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget,
)

from . import tokens


def _sep() -> QFrame:
    """Create a vertical button separator."""
    s = QFrame()
    s.setFrameShape(QFrame.Shape.VLine)
    s.setFixedWidth(1)
    s.setFixedHeight(22)
    s.setStyleSheet(f"background: {tokens.C_GOLD_DARK};")
    return s


def _btn(text: str, css_class: str = "", **kwargs) -> QPushButton:
    """Create a styled fascia button."""
    b = QPushButton(text)
    if css_class:
        b.setProperty("cssClass", css_class)
    b.setStyleSheet(
        f"font-size: 9px; letter-spacing: 1px; padding: 4px 10px; white-space: nowrap;"
    )
    return b


class _FasciaStrip(QWidget):
    """A single feature's toolbar content."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout_ = QHBoxLayout(self)
        self.layout_.setContentsMargins(12, 0, 12, 0)
        self.layout_.setSpacing(6)
        self._buttons: dict[str, QPushButton] = {}

    def add_zone_label(self) -> None:
        lbl = QLabel("FASCIA")
        lbl.setStyleSheet(
            f"font-size: 7px; letter-spacing: 2px; color: rgba(122,106,42,0.4); "
            f"font-family: {tokens.FONT_MONO}; padding: 0 8px;"
        )
        self.layout_.addWidget(lbl)

    def add_button(self, name: str, text: str, css_class: str = "") -> QPushButton:
        b = _btn(text, css_class)
        self._buttons[name] = b
        self.layout_.addWidget(b)
        return b

    def add_separator(self) -> None:
        self.layout_.addWidget(_sep())

    def add_label(self, text: str, style: str = "") -> QLabel:
        lbl = QLabel(text)
        if style:
            lbl.setStyleSheet(style)
        self.layout_.addWidget(lbl)
        return lbl

    def add_stretch(self) -> None:
        self.layout_.addStretch()

    def button(self, name: str) -> QPushButton | None:
        return self._buttons.get(name)


class Fascia(QFrame):
    """Zone III: feature-keyed action toolbar."""

    # Tabula signals
    new_canvas = pyqtSignal()
    open_canvas = pyqtSignal()
    save_canvas = pyqtSignal()
    save_canvas_as = pyqtSignal()
    undo = pyqtSignal()
    redo = pyqtSignal()
    delete_element = pyqtSignal()
    duplicate_element = pyqtSignal()
    group_element = pyqtSignal()
    # Armarium signals
    seal_canvas = pyqtSignal()
    refine = pyqtSignal()
    export_selected = pyqtSignal()
    # Specularium signals
    reconstruct = pyqtSignal()
    capture_image = pyqtSignal()
    toggle_window = pyqtSignal()
    # Codex signals
    copy_to_clipboard = pyqtSignal()
    save_to_file = pyqtSignal()
    validate_code = pyqtSignal()
    # Thema signals
    load_theme = pyqtSignal()
    apply_repaint = pyqtSignal()
    reset_theme = pyqtSignal()
    # Help
    help_requested = pyqtSignal()
    help_dismiss = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setObjectName("fascia")
        self._stack = QStackedWidget()
        self._strips: dict[str, _FasciaStrip] = {}
        self._canvas_name_label: QLabel | None = None
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(self._stack)

        self._build_tabula()
        self._build_armarium()
        self._build_specularium()
        self._build_codex()
        self._build_thema()
        self._build_auxilium()

    def _build_tabula(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_button("new", "Novum").clicked.connect(self.new_canvas.emit)
        s.add_button("open", "Aperi \u25be").clicked.connect(self.open_canvas.emit)
        s.add_separator()
        s.add_button("save", "Sigilla", "teal").clicked.connect(self.save_canvas.emit)
        s.add_button("save_as", "Sig. Ut").clicked.connect(self.save_canvas_as.emit)
        self._canvas_name_label = s.add_label(
            "",
            f"font-size: 9px; color: {tokens.C_GOLD_DIM}; padding: 0 6px; "
            f"font-style: italic; font-family: {tokens.FONT_MONO};",
        )
        s.add_separator()
        s.add_button("undo", "\u21a9").clicked.connect(self.undo.emit)
        s.add_button("redo", "\u21aa").clicked.connect(self.redo.emit)
        s.add_separator()
        s.add_button("delete", "Dele", "crimson").clicked.connect(self.delete_element.emit)
        s.add_button("duplicate", "Duplica").clicked.connect(self.duplicate_element.emit)
        s.add_button("group", "Congrega").clicked.connect(self.group_element.emit)
        s.add_stretch()
        s.add_button("help_tab", "? Auxilium").clicked.connect(self.help_requested.emit)
        self._strips["tabula"] = s
        self._stack.addWidget(s)

    def _build_armarium(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_button("seal", "\u2697 Sigilla Canvas", "teal").clicked.connect(self.seal_canvas.emit)
        s.add_button("refine", "\u2699 Refice").clicked.connect(self.refine.emit)
        s.add_separator()
        s.add_button("export_sel", "Exporta Selectum").clicked.connect(self.export_selected.emit)
        s.add_stretch()
        s.add_button("help_arm", "? Auxilium").clicked.connect(self.help_requested.emit)
        self._strips["armarium"] = s
        self._stack.addWidget(s)

    def _build_specularium(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_button("recon", "\u2699 Reconstruc").clicked.connect(self.reconstruct.emit)
        s.add_button("capture", "\U0001f732 Cape Imaginem", "teal").clicked.connect(self.capture_image.emit)
        s.add_separator()
        s.add_button("fenestra", "\u29c9 Fenestra").clicked.connect(self.toggle_window.emit)
        s.add_stretch()
        s.add_button("help_spec", "? Auxilium").clicked.connect(self.help_requested.emit)
        self._strips["specularium"] = s
        self._stack.addWidget(s)

    def _build_codex(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_button("clip", "\u2697 In Clipboard", "teal").clicked.connect(self.copy_to_clipboard.emit)
        s.add_button("file", "\U0001f732 In Fasciculum").clicked.connect(self.save_to_file.emit)
        s.add_separator()
        s.add_button("validate", "\u2699 Valida").clicked.connect(self.validate_code.emit)
        s.add_stretch()
        s.add_button("help_codex", "? Auxilium").clicked.connect(self.help_requested.emit)
        self._strips["codex"] = s
        self._stack.addWidget(s)

    def _build_thema(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_button("load", "Onus theme.json").clicked.connect(self.load_theme.emit)
        s.add_button("apply", "\u2699 Applica & Repinge", "teal").clicked.connect(self.apply_repaint.emit)
        s.add_button("reset", "Reset", "crimson").clicked.connect(self.reset_theme.emit)
        s.add_stretch()
        s.add_button("help_thema", "? Auxilium").clicked.connect(self.help_requested.emit)
        self._strips["thema"] = s
        self._stack.addWidget(s)

    def _build_auxilium(self) -> None:
        s = _FasciaStrip()
        s.add_zone_label()
        s.add_label(
            "\u2726  AUXILIUM",
            f"font-size: 10px; color: {tokens.C_GOLD}; letter-spacing: 2px; padding: 0 8px;",
        )
        s.add_stretch()
        s.add_button("dismiss", "\u2715 Dimitte", "crimson").clicked.connect(self.help_dismiss.emit)
        self._strips["auxilium"] = s
        self._stack.addWidget(s)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"Fascia {{ background: {tokens.C_PANEL}; "
            f"border-bottom: 1px solid {tokens.C_GOLD_DARK}; }}"
        )

    def switch_to(self, feature_key: str) -> None:
        """Switch fascia to the given feature's toolbar."""
        strip = self._strips.get(feature_key)
        if strip:
            self._stack.setCurrentWidget(strip)

    def set_canvas_name(self, name: str) -> None:
        if self._canvas_name_label:
            self._canvas_name_label.setText(name)
