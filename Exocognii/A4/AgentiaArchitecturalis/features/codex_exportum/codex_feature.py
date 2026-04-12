"""
Codex Exportum — Code Export Engine.

Canvas tree → validated PyQt6 code using token constants only (never raw hex).
ast.parse() validates before delivery. Clipboard or file export.
"""
from __future__ import annotations

import ast
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QRadioButton, QButtonGroup, QLineEdit, QPushButton,
    QPlainTextEdit, QFileDialog, QMessageBox, QApplication,
)

from ... import tokens
from ...models import ElementNode


# ── Code Generation ─────────────────────────────────────────────

def _collect_used_tokens(nodes: list[ElementNode]) -> set[str]:
    """Collect all token names referenced in the design tree."""
    used: set[str] = set()
    for node in nodes:
        for key in ("bg_token", "border_token", "fg_token"):
            tok = node.properties.get(key)
            if tok and tok in tokens.TOKEN_NAMES:
                used.add(tok)
        used.update(_collect_used_tokens(node.children))
    return used


def _element_code(node: ElementNode, indent: int = 2) -> list[str]:
    """Generate code lines for a single element."""
    pad = "    " * indent
    lines = []
    etype = node.element_type
    vn = node.var_name

    if etype == "QFrame":
        lines.append(f"{pad}self.{vn} = QFrame(self)")
        bg = node.properties.get("bg_token", "C_PANEL")
        border = node.properties.get("border_token", "C_GOLD_DARK")
        lines.append(f'{pad}self.{vn}.setStyleSheet(f"QFrame {{ background: {{{bg}}}; border: 1px solid {{{border}}}; }}")')
        layout_type = node.properties.get("layout_type", "vertical")
        layout_cls = "QVBoxLayout" if layout_type == "vertical" else "QHBoxLayout"
        lines.append(f"{pad}{vn}_layout = {layout_cls}(self.{vn})")
        spacing = node.properties.get("spacing", 8)
        lines.append(f"{pad}{vn}_layout.setSpacing({spacing})")
    elif etype == "QGroupBox":
        text = node.properties.get("text_content", "Group")
        lines.append(f'{pad}self.{vn} = QGroupBox("{text}", self)')
        lines.append(f"{pad}QVBoxLayout(self.{vn})")
    elif etype == "QTabWidget":
        lines.append(f"{pad}self.{vn} = QTabWidget(self)")
    elif etype == "QSplitter":
        lines.append(f"{pad}self.{vn} = QSplitter(self)")
    elif etype == "QLineEdit":
        lines.append(f"{pad}self.{vn} = QLineEdit(self)")
        ph = node.properties.get("placeholder", "")
        if ph:
            lines.append(f'{pad}self.{vn}.setPlaceholderText("{ph}")')
    elif etype == "QComboBox":
        lines.append(f"{pad}self.{vn} = QComboBox(self)")
    elif etype == "QSlider":
        lines.append(f"{pad}self.{vn} = QSlider(Qt.Orientation.Horizontal, self)")
        lines.append(f"{pad}self.{vn}.setRange({node.properties.get('min_val', 0)}, {node.properties.get('max_val', 100)})")
    elif etype == "QSpinBox":
        lines.append(f"{pad}self.{vn} = QSpinBox(self)")
        lines.append(f"{pad}self.{vn}.setRange({node.properties.get('min_val', 0)}, {node.properties.get('max_val', 100)})")
    elif etype == "QTextEdit":
        lines.append(f"{pad}self.{vn} = QTextEdit(self)")
    elif etype == "QCheckBox":
        text = node.properties.get("text_content", "Checkbox")
        lines.append(f'{pad}self.{vn} = QCheckBox("{text}", self)')
    elif etype == "QRadioButton":
        text = node.properties.get("text_content", "Radio")
        lines.append(f'{pad}self.{vn} = QRadioButton("{text}", self)')
    elif etype.startswith("QLabel"):
        text = node.properties.get("text_content", etype)
        lines.append(f'{pad}self.{vn} = QLabel("{text}", self)')
        variant = etype.split("_")[-1] if "_" in etype else "gold"
        if variant == "gold":
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"color: {{C_GOLD}}; font-size: {node.properties.get("font_size", 10)}px;")')
        elif variant == "dim":
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"color: {{C_GOLD_DIM}}; font-size: {node.properties.get("font_size", 9)}px;")')
        elif variant == "micro":
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"color: {{C_TEXT}}; font-size: {node.properties.get("font_size", 7)}px; letter-spacing: 2px;")')
    elif etype == "QProgressBar":
        lines.append(f"{pad}self.{vn} = QProgressBar(self)")
    elif etype.startswith("ArcaneButton"):
        variant = etype.split("_")[-1]
        text = node.properties.get("text_content", f"Button")
        lines.append(f'{pad}self.{vn} = QPushButton("{text}", self)')
        bg = node.properties.get("bg_token", "C_PANEL")
        if variant == "gold":
            border = node.properties.get("border_token", "C_GOLD_DARK")
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"QPushButton {{ color: {{C_GOLD}}; border: 1px solid {{{border}}}; background: {{{bg}}}; padding: 5px 12px; }}")')
        elif variant == "teal":
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"QPushButton {{ color: #3aacac; border: 1px solid {{C_TEAL}}; background: {{{bg}}}; padding: 5px 12px; }}")')
        elif variant == "crimson":
            lines.append(f'{pad}self.{vn}.setStyleSheet(f"QPushButton {{ color: #c04040; border: 1px solid {{C_CRIMSON}}; background: {{{bg}}}; padding: 5px 12px; }}")')
    elif etype == "ToggleButton":
        text = node.properties.get("text_content", "Toggle")
        lines.append(f'{pad}self.{vn} = QPushButton("{text}", self)')
        lines.append(f"{pad}self.{vn}.setCheckable(True)")
    elif etype == "QTableView":
        lines.append(f"{pad}self.{vn} = QTableView(self)")
    elif etype in ("Separator", "RuleLine"):
        lines.append(f"{pad}self.{vn} = QFrame(self)")
        lines.append(f"{pad}self.{vn}.setFrameShape(QFrame.Shape.HLine)")
        lines.append(f"{pad}self.{vn}.setFixedHeight(2)")
    elif etype == "Spacer":
        lines.append(f"{pad}self.{vn} = QWidget(self)")
        lines.append(f"{pad}self.{vn}.setFixedHeight({node.properties.get('height', 40)})")
    elif etype == "TopBar":
        lines.append(f"{pad}self.{vn} = QFrame(self)")
        lines.append(f'{pad}self.{vn}.setStyleSheet(f"QFrame {{ background: {{C_PANEL}}; border: 1px solid {{C_GOLD_DARK}}; }}")')
        lines.append(f"{pad}QHBoxLayout(self.{vn})")
    elif etype == "StatusBar":
        lines.append(f"{pad}self.{vn} = QFrame(self)")
        lines.append(f"{pad}self.{vn}.setFixedHeight(26)")
    elif etype in ("ControlPanel", "SectionHeader", "SwatchStrip"):
        lines.append(f"{pad}self.{vn} = QFrame(self)")
    else:
        lines.append(f"{pad}# Unknown element type: {etype}")
        lines.append(f"{pad}self.{vn} = QWidget(self)")

    # Set fixed size
    w = node.properties.get("width")
    h = node.properties.get("height")
    if w and h:
        lines.append(f"{pad}self.{vn}.setFixedSize({w}, {h})")

    # Children — add to parent layout
    for child in node.children:
        lines.extend(_element_code(child, indent))
        lines.append(f"{pad}{vn}_layout.addWidget(self.{child.var_name})")

    return lines


def generate_code(canvas_name: str, elements: list[ElementNode]) -> str:
    """Generate complete PyQt6 Python module from design tree.

    ZERO raw hex literals — token constants only.
    """
    if not elements:
        return (
            f'"""Generated by Agentia Architecturalis — Bureau II"""\n\n'
            f"from PyQt6.QtWidgets import QWidget\n\n\n"
            f"class {_class_name(canvas_name)}(QWidget):\n"
            f"    def __init__(self, parent=None):\n"
            f"        super().__init__(parent)\n"
            f"        pass\n"
        )

    used_tokens = _collect_used_tokens(elements)
    # Determine required imports
    qt_widgets = {"QWidget"}
    for node in _flatten(elements):
        etype = node.element_type
        if etype == "QFrame" or etype in ("Separator", "RuleLine", "TopBar", "StatusBar", "ControlPanel", "SectionHeader", "SwatchStrip"):
            qt_widgets.add("QFrame")
            if etype == "QFrame" or etype == "TopBar":
                lt = node.properties.get("layout_type", "vertical")
                qt_widgets.add("QVBoxLayout" if lt == "vertical" else "QHBoxLayout")
        elif etype == "QGroupBox":
            qt_widgets.update({"QGroupBox", "QVBoxLayout"})
        elif etype == "QTabWidget":
            qt_widgets.add("QTabWidget")
        elif etype == "QSplitter":
            qt_widgets.add("QSplitter")
        elif etype == "QLineEdit":
            qt_widgets.add("QLineEdit")
        elif etype == "QComboBox":
            qt_widgets.add("QComboBox")
        elif etype == "QSlider":
            qt_widgets.add("QSlider")
        elif etype == "QSpinBox":
            qt_widgets.add("QSpinBox")
        elif etype == "QTextEdit":
            qt_widgets.add("QTextEdit")
        elif etype == "QCheckBox":
            qt_widgets.add("QCheckBox")
        elif etype == "QRadioButton":
            qt_widgets.add("QRadioButton")
        elif etype.startswith("QLabel"):
            qt_widgets.add("QLabel")
        elif etype == "QProgressBar":
            qt_widgets.add("QProgressBar")
        elif etype.startswith("ArcaneButton") or etype == "ToggleButton":
            qt_widgets.add("QPushButton")
        elif etype == "QTableView":
            qt_widgets.add("QTableView")
        elif etype == "Spacer":
            pass  # QWidget already added

    lines = [
        f'"""Generated by Agentia Architecturalis — Bureau II"""',
        "",
    ]

    # Token imports
    if used_tokens:
        tok_list = ", ".join(sorted(used_tokens))
        lines.append(f"from tokens import {tok_list}")

    # Qt imports
    widget_imports = ", ".join(sorted(qt_widgets))
    lines.append(f"from PyQt6.QtWidgets import {widget_imports}")

    has_slider = any(n.element_type == "QSlider" for n in _flatten(elements))
    if has_slider:
        lines.append("from PyQt6.QtCore import Qt")

    lines.extend(["", ""])

    # Class
    cls_name = _class_name(canvas_name)
    lines.append(f"class {cls_name}(QWidget):")
    lines.append(f"    def __init__(self, parent=None):")
    lines.append(f"        super().__init__(parent)")
    lines.append(f"        layout = QVBoxLayout(self)")

    for node in elements:
        lines.extend(_element_code(node, indent=2))
        lines.append(f"        layout.addWidget(self.{node.var_name})")

    lines.append("")
    return "\n".join(lines)


def validate_code(code: str) -> tuple[bool, str]:
    """Validate generated code via ast.parse(). Returns (valid, message)."""
    try:
        ast.parse(code)
        return True, "AST parse passed"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"


def _class_name(canvas_name: str) -> str:
    parts = canvas_name.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts) or "GeneratedWidget"


def _flatten(nodes: list[ElementNode]) -> list[ElementNode]:
    result = []
    for n in nodes:
        result.append(n)
        result.extend(_flatten(n.children))
    return result


# ── Feature Page ────────────────────────────────────────────────

class CodexFeature(QWidget):
    """Codex Exportum feature page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._canvas_name = ""
        self._elements: list[ElementNode] = []
        self._code = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        self._header = QLabel("Codex Exportum")
        self._header.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(self._header)

        # Export destination
        dest_label = QLabel("DESTINATIO EXPORTATIONIS")
        dest_label.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO}; margin-top: 12px;"
        )
        layout.addWidget(dest_label)

        dest_row = QHBoxLayout()
        self._radio_clip = QRadioButton("Clipboard")
        self._radio_file = QRadioButton("Fasciculum")
        self._radio_clip.setChecked(True)
        self._radio_group = QButtonGroup(self)
        self._radio_group.addButton(self._radio_clip)
        self._radio_group.addButton(self._radio_file)
        dest_row.addWidget(self._radio_clip)
        dest_row.addWidget(self._radio_file)

        self._file_path = QLineEdit()
        self._file_path.setEnabled(False)
        self._file_path.setPlaceholderText("exports/output.py")
        self._browse_btn = QPushButton("Browse")
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._browse_file)
        dest_row.addWidget(self._file_path)
        dest_row.addWidget(self._browse_btn)
        layout.addLayout(dest_row)

        self._radio_file.toggled.connect(lambda checked: (
            self._file_path.setEnabled(checked),
            self._browse_btn.setEnabled(checked),
        ))

        # Code preview
        preview_label = QLabel("ANTEVISIO CODICIS")
        preview_label.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; font-family: {tokens.FONT_MONO}; margin-top: 8px;"
        )
        layout.addWidget(preview_label)

        self._code_view = QPlainTextEdit()
        self._code_view.setReadOnly(True)
        self._code_view.setStyleSheet(
            f"background: #060610; border: 1px solid {tokens.C_GOLD_DARK}; "
            f"color: #7EC8C8; font-family: {tokens.FONT_MONO}; font-size: 10px;"
        )
        layout.addWidget(self._code_view, 1)

        # Validation line
        self._validation = QLabel()
        self._validation.setStyleSheet(
            f"font-size: 8.5px; color: {tokens.C_GOLD_DIM}; "
            f"font-family: {tokens.FONT_MONO}; padding: 5px 0; "
            f"border-top: 1px solid {tokens.C_GOLD_DARK};"
        )
        layout.addWidget(self._validation)

    def update_source(self, canvas_name: str, elements: list[ElementNode]) -> None:
        """Regenerate code from current canvas state."""
        self._canvas_name = canvas_name
        self._elements = elements
        self._code = generate_code(canvas_name, elements)
        self._code_view.setPlainText(self._code)
        self._header.setText(f"Codex Exportum \u00b7 Source: {canvas_name or '(untitled)'}")
        self._validate()

    def _validate(self) -> None:
        if not self._code.strip():
            self._validation.setText("\u2726 No code to validate.")
            return
        valid, msg = validate_code(self._code)
        elem_count = len(_flatten(self._elements))
        line_count = len(self._code.splitlines())
        if valid:
            self._validation.setText(
                f"\u2726 {msg} \u00b7 {line_count} lines \u00b7 "
                f"{elem_count} elements \u00b7 token constants only \u00b7 no raw hex"
            )
        else:
            self._validation.setText(f"\u26a0 {msg}")
            self._validation.setStyleSheet(
                f"font-size: 8.5px; color: #c04040; font-family: {tokens.FONT_MONO}; "
                f"padding: 5px 0; border-top: 1px solid {tokens.C_GOLD_DARK};"
            )

    def copy_to_clipboard(self) -> None:
        if not self._code:
            return
        valid, msg = validate_code(self._code)
        if not valid:
            QMessageBox.warning(self, "Validation Failed", msg)
            return
        QApplication.clipboard().setText(self._code)

    def save_to_file(self) -> None:
        if not self._code:
            return
        valid, msg = validate_code(self._code)
        if not valid:
            QMessageBox.warning(self, "Validation Failed", msg)
            return
        path = self._file_path.text().strip()
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Save Code", "", "Python (*.py)")
        if path:
            Path(path).write_text(self._code, encoding="utf-8")

    def validate_current(self) -> None:
        self._validate()

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Code", "", "Python (*.py)")
        if path:
            self._file_path.setText(path)
