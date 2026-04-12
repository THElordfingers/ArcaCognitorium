"""
Inspector Proprietatum — per-element property editor.

Displays and edits: var_name, width/height (live resize), colour_token
(QComboBox with token names only), layout_type, font_size, text_content.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QComboBox, QFrame, QScrollArea,
)

from ... import tokens
from ...features.tabula.canvas_element import CanvasElement


class InspectorFeature(QFrame):
    """Property inspector panel (right side of Tabula)."""

    property_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(170)
        self.setObjectName("inspector")
        self._current: CanvasElement | None = None
        self._widgets: dict[str, QWidget] = {}
        self._updating = False
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        head = QLabel("Inspector Proprietatum")
        head.setStyleSheet(
            f"font-size: 7px; letter-spacing: 2px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; border-bottom: 1px solid {tokens.C_GOLD_DARK}; "
            f"padding: 10px 9px 5px;"
        )
        outer.addWidget(head)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(9, 8, 9, 8)
        self._content_layout.setSpacing(3)

        self._empty_label = QLabel("No element selected.")
        self._empty_label.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; font-style: italic; padding: 20px 0;"
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(self._empty_label)
        self._content_layout.addStretch()

        scroll.setWidget(self._content)
        outer.addWidget(scroll, 1)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"InspectorFeature {{ background: {tokens.C_PANEL}; "
            f"border-left: 1px solid {tokens.C_GOLD_DARK}; "
            f"font-family: {tokens.FONT_MONO}; font-size: 8.5px; }}"
        )

    def set_element(self, element: CanvasElement | None) -> None:
        """Display properties for the given element."""
        self._current = element
        self._clear_properties()

        if element is None:
            self._empty_label.setVisible(True)
            return

        self._empty_label.setVisible(False)
        self._updating = True

        # Section: NOMEN
        self._add_section("NOMEN")
        self._add_text_prop("var_name", "var_name", element.var_name)
        self._add_readonly_prop("type", element.element_type)

        # Section: AMPLITUDO
        self._add_section("AMPLITUDO")
        self._add_int_prop("width", "width", element.properties.get("width", 200), 16, 2000)
        self._add_int_prop("height", "height", element.properties.get("height", 100), 16, 2000)

        # Section: COLORES
        self._add_section("COLORES")
        self._add_token_prop("bg_token", "bg_token", element.properties.get("bg_token", "C_PANEL"))
        self._add_token_prop("border", "border_token", element.properties.get("border_token", "C_GOLD_DARK"))

        # Section: DISPOSITIO (containers only)
        if element.accepts_children():
            self._add_section("DISPOSITIO")
            self._add_choice_prop(
                "layout", "layout_type",
                element.properties.get("layout_type", "vertical"),
                ["vertical", "horizontal", "none"],
            )
            self._add_int_prop("spacing", "spacing", element.properties.get("spacing", 8), 0, 100)

        # Section: TYPOGRAPHIA (text elements)
        if element.element_type.startswith("QLabel") or element.element_type in ("QLineEdit", "QTextEdit"):
            self._add_section("TYPOGRAPHIA")
            self._add_text_prop("text", "text_content", element.properties.get("text_content", ""))
            self._add_int_prop("font_size", "font_size", element.properties.get("font_size", 9), 6, 36)

        # Children list
        if element.children:
            self._add_rule()
            self._add_section(f"Children ({len(element.children)})")
            for child in element.children:
                lbl = QLabel(f"  \u25b8 {child.var_name}")
                lbl.setStyleSheet(f"color: {tokens.C_TEXT}; font-size: 8px; padding: 1px 0 1px 8px; border-left: 1px solid {tokens.C_GOLD_DARK};")
                self._content_layout.addWidget(lbl)

        self._content_layout.addStretch()
        self._updating = False

    def _clear_properties(self) -> None:
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w and w is not self._empty_label:
                w.deleteLater()
        self._widgets.clear()
        self._content_layout.addWidget(self._empty_label)

    def _add_section(self, title: str) -> None:
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"font-size: 7px; letter-spacing: 1px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; margin-top: 6px; margin-bottom: 2px;"
        )
        self._content_layout.addWidget(lbl)

    def _add_rule(self) -> None:
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {tokens.C_GOLD_DARK};")
        self._content_layout.addWidget(rule)

    def _add_readonly_prop(self, label: str, value: str) -> None:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        k = QLabel(label)
        k.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8px; min-width: 68px;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {tokens.C_TEXT}; font-size: 8px;")
        rl.addWidget(k)
        rl.addWidget(v, 1)
        self._content_layout.addWidget(row)

    def _add_text_prop(self, label: str, prop_key: str, value: str) -> None:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        k = QLabel(label)
        k.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8px; min-width: 68px;")
        v = QLineEdit(value)
        v.setStyleSheet(f"color: {tokens.C_GOLD}; font-size: 8px; padding: 1px 3px;")
        v.textChanged.connect(lambda text, pk=prop_key: self._on_prop_changed(pk, text))
        rl.addWidget(k)
        rl.addWidget(v, 1)
        self._content_layout.addWidget(row)
        self._widgets[prop_key] = v

    def _add_int_prop(self, label: str, prop_key: str, value: int, min_v: int, max_v: int) -> None:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        k = QLabel(label)
        k.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8px; min-width: 68px;")
        v = QSpinBox()
        v.setRange(min_v, max_v)
        v.setValue(value)
        v.setStyleSheet(f"color: {tokens.C_GOLD}; font-size: 8px;")
        v.valueChanged.connect(lambda val, pk=prop_key: self._on_prop_changed(pk, val))
        rl.addWidget(k)
        rl.addWidget(v, 1)
        self._content_layout.addWidget(row)
        self._widgets[prop_key] = v

    def _add_token_prop(self, label: str, prop_key: str, value: str) -> None:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        k = QLabel(label)
        k.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8px; min-width: 68px;")
        v = QComboBox()
        v.addItems(tokens.TOKEN_NAMES)
        if value in tokens.TOKEN_NAMES:
            v.setCurrentText(value)
        v.currentTextChanged.connect(lambda text, pk=prop_key: self._on_prop_changed(pk, text))
        rl.addWidget(k)
        rl.addWidget(v, 1)
        self._content_layout.addWidget(row)
        self._widgets[prop_key] = v

    def _add_choice_prop(self, label: str, prop_key: str, value: str, choices: list[str]) -> None:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        k = QLabel(label)
        k.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8px; min-width: 68px;")
        v = QComboBox()
        v.addItems(choices)
        if value in choices:
            v.setCurrentText(value)
        v.currentTextChanged.connect(lambda text, pk=prop_key: self._on_prop_changed(pk, text))
        rl.addWidget(k)
        rl.addWidget(v, 1)
        self._content_layout.addWidget(row)
        self._widgets[prop_key] = v

    def _on_prop_changed(self, prop_key: str, value) -> None:
        if self._updating or not self._current:
            return

        if prop_key == "var_name":
            self._current.update_var_name(str(value))
        elif prop_key in ("width", "height"):
            w = self._current.properties.get("width", 200)
            h = self._current.properties.get("height", 100)
            if prop_key == "width":
                w = int(value)
            else:
                h = int(value)
            self._current.resize(w, h)
        else:
            self._current.properties[prop_key] = value

        self.property_changed.emit()
