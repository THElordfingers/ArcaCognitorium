"""
Preview Renderer — builds real PyQt6 widget hierarchy from ElementNode tree.

Token-based colours. Render log tracks clean/stub/error per element.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QComboBox, QSlider, QSpinBox,
    QProgressBar, QGroupBox, QTabWidget, QTableView, QTextEdit,
    QCheckBox, QRadioButton, QScrollArea,
)

from ...models import ElementNode
from ... import tokens


@dataclass
class RenderLogEntry:
    element_type: str
    var_name: str
    status: str  # "clean", "stub", "error"
    message: str = ""


class PreviewRenderer(QWidget):
    """Builds live PyQt6 widgets from the design tree."""

    DEBOUNCE_MS = 200

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._render_log: list[RenderLogEntry] = []
        self._token_dict: dict[str, str] = dict(tokens.DEFAULTS)
        self._elements: list[ElementNode] = []
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(self.DEBOUNCE_MS)
        self._debounce.timeout.connect(self._do_rebuild)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    @property
    def render_log(self) -> list[RenderLogEntry]:
        return list(self._render_log)

    def schedule_rebuild(self, elements: list[ElementNode], token_dict: dict[str, str]) -> None:
        """Queue a rebuild with debounce."""
        self._elements = elements
        self._token_dict = dict(token_dict)
        self._debounce.start()

    def _do_rebuild(self) -> None:
        self._render_log.clear()
        # Clear old widgets
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._elements:
            placeholder = QLabel("No elements to preview.")
            placeholder.setStyleSheet(
                f"color: {tokens.C_GOLD_DIM}; font-style: italic; padding: 20px;"
            )
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(placeholder)
            return

        for node in self._elements:
            widget = self._build_widget(node)
            if widget:
                self._layout.addWidget(widget)

        self._layout.addStretch()

    def _build_widget(self, node: ElementNode) -> QWidget | None:
        """Build a real widget from an ElementNode."""
        t = self._token_dict
        etype = node.element_type
        props = node.properties

        try:
            widget = self._create_widget(etype, props, t)
            if widget is None:
                self._log(etype, node.var_name, "error", f"Unknown element type: {etype}")
                return None

            # Handle children for containers
            if node.children and hasattr(widget, "layout") and widget.layout():
                for child_node in node.children:
                    child_widget = self._build_widget(child_node)
                    if child_widget:
                        widget.layout().addWidget(child_widget)

            self._log(etype, node.var_name, "clean", "rendered clean")
            return widget

        except Exception as e:
            self._log(etype, node.var_name, "error", str(e))
            return None

    def _create_widget(self, etype: str, props: dict, t: dict) -> QWidget | None:
        bg = t.get(props.get("bg_token", "C_PANEL"), t.get("C_PANEL", tokens.C_PANEL))
        border = t.get(props.get("border_token", "C_GOLD_DARK"), t.get("C_GOLD_DARK", tokens.C_GOLD_DARK))
        text_color = t.get("C_TEXT", tokens.C_TEXT)
        gold = t.get("C_GOLD", tokens.C_GOLD)

        if etype == "QFrame":
            f = QFrame()
            f.setStyleSheet(f"QFrame {{ background: {bg}; border: 1px solid {border}; }}")
            layout = QVBoxLayout(f) if props.get("layout_type", "vertical") == "vertical" else QHBoxLayout(f)
            layout.setSpacing(props.get("spacing", 8))
            return f

        elif etype == "QGroupBox":
            g = QGroupBox(props.get("text_content", "Group"))
            g.setStyleSheet(f"QGroupBox {{ background: {bg}; border: 1px solid {border}; color: {gold}; }}")
            QVBoxLayout(g)
            return g

        elif etype == "QTabWidget":
            tw = QTabWidget()
            tw.addTab(QWidget(), "Tab 1")
            return tw

        elif etype == "QSplitter":
            f = QFrame()
            f.setStyleSheet(f"QFrame {{ background: {bg}; border: 1px solid {border}; }}")
            QHBoxLayout(f)
            return f

        elif etype == "QLineEdit":
            le = QLineEdit()
            le.setPlaceholderText(props.get("placeholder", ""))
            le.setText(props.get("text_content", ""))
            return le

        elif etype == "QComboBox":
            cb = QComboBox()
            cb.addItems(["Option 1", "Option 2", "Option 3"])
            return cb

        elif etype == "QSlider":
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(props.get("min_val", 0), props.get("max_val", 100))
            return s

        elif etype == "QSpinBox":
            sb = QSpinBox()
            sb.setRange(props.get("min_val", 0), props.get("max_val", 100))
            return sb

        elif etype == "QTextEdit":
            te = QTextEdit()
            te.setPlainText(props.get("text_content", ""))
            return te

        elif etype == "QCheckBox":
            return QCheckBox(props.get("text_content", "Checkbox"))

        elif etype == "QRadioButton":
            return QRadioButton(props.get("text_content", "Radio"))

        elif etype.startswith("QLabel"):
            lbl = QLabel(props.get("text_content", etype))
            variant = etype.split("_")[-1] if "_" in etype else "gold"
            if variant == "gold":
                lbl.setStyleSheet(f"color: {gold}; font-size: {props.get('font_size', 10)}px;")
            elif variant == "dim":
                lbl.setStyleSheet(f"color: {t.get('C_GOLD_DIM', tokens.C_GOLD_DIM)}; font-size: {props.get('font_size', 9)}px;")
            elif variant == "micro":
                lbl.setStyleSheet(f"color: {text_color}; font-size: {props.get('font_size', 7)}px; letter-spacing: 2px;")
            return lbl

        elif etype == "QProgressBar":
            pb = QProgressBar()
            pb.setValue(45)
            return pb

        elif etype.startswith("ArcaneButton"):
            variant = etype.split("_")[-1]
            btn = QPushButton(props.get("text_content", f"Button ({variant})"))
            if variant == "gold":
                btn.setStyleSheet(f"QPushButton {{ color: {gold}; border: 1px solid {border}; background: {bg}; padding: 5px 12px; }}")
            elif variant == "teal":
                btn.setProperty("cssClass", "teal")
                btn.setStyleSheet(f"QPushButton {{ color: #3aacac; border: 1px solid {t.get('C_TEAL', tokens.C_TEAL)}; background: {bg}; padding: 5px 12px; }}")
            elif variant == "crimson":
                btn.setProperty("cssClass", "crimson")
                btn.setStyleSheet(f"QPushButton {{ color: #c04040; border: 1px solid {t.get('C_CRIMSON', tokens.C_CRIMSON)}; background: {bg}; padding: 5px 12px; }}")
            return btn

        elif etype == "ToggleButton":
            btn = QPushButton(props.get("text_content", "Toggle"))
            btn.setCheckable(True)
            return btn

        elif etype == "QTableView":
            tv = QTableView()
            self._log(etype, props.get("var_name", "table"), "stub", "preview stub (no data supplied)")
            return tv

        elif etype == "TopBar":
            bar = QFrame()
            bar.setStyleSheet(f"QFrame {{ background: {bg}; border: 1px solid {border}; }}")
            bl = QHBoxLayout(bar)
            bl.addWidget(QLabel("\u2726  TOP BAR"))
            return bar

        elif etype == "StatusBar":
            bar = QFrame()
            bar.setFixedHeight(26)
            bar.setStyleSheet(f"QFrame {{ background: {bg}; border: 1px solid {border}; }}")
            bl = QHBoxLayout(bar)
            bl.addWidget(QLabel("Status"))
            return bar

        elif etype == "ControlPanel":
            f = QFrame()
            f.setStyleSheet(f"QFrame {{ background: {bg}; border: 1px solid {border}; }}")
            QVBoxLayout(f)
            return f

        elif etype == "SectionHeader":
            lbl = QLabel(props.get("text_content", "Section Header"))
            lbl.setStyleSheet(f"color: {gold}; font-size: 10px; letter-spacing: 2px; padding: 7px 12px; border: 1px solid {border}; background: {bg};")
            return lbl

        elif etype == "SwatchStrip":
            f = QFrame()
            f.setFixedHeight(24)
            fl = QHBoxLayout(f)
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setSpacing(2)
            for tok_name in tokens.TOKEN_NAMES:
                swatch = QFrame()
                swatch.setFixedSize(24, 20)
                swatch.setStyleSheet(f"background: {t.get(tok_name, '#000')};")
                fl.addWidget(swatch)
            return f

        elif etype == "Separator":
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFixedHeight(2)
            sep.setStyleSheet(f"background: {border};")
            return sep

        elif etype == "Spacer":
            spacer = QWidget()
            spacer.setFixedHeight(props.get("height", 40))
            return spacer

        elif etype == "RuleLine":
            rule = QFrame()
            rule.setFrameShape(QFrame.Shape.HLine)
            rule.setFixedHeight(2)
            rule.setStyleSheet(f"background: {gold}; opacity: 0.3;")
            return rule

        return None

    def _log(self, etype: str, var_name: str, status: str, message: str) -> None:
        self._render_log.append(RenderLogEntry(etype, var_name, status, message))
