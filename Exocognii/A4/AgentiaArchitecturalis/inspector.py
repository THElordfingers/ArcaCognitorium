# Agentia Architecturalis — inspector.py
# v1.0.0
"""Property inspector for the selected canvas element."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QFrame, QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt

from .constants import TOKEN_NAMES
from .elements.base import CanvasElement


# Property type definitions for the inspector UI
_PROP_TYPES = {
    'variable_name': 'text', 'label_text': 'text', 'placeholder_text': 'text',
    'width': 'int', 'height': 'int', 'min_width': 'int', 'min_height': 'int',
    'font_size': 'int', 'letter_spacing': 'int', 'spacing': 'int',
    'padding': 'int', 'border_width': 'int',
    'margin_top': 'int', 'margin_right': 'int',
    'margin_bottom': 'int', 'margin_left': 'int',
    'font_bold': 'bool', 'font_italic': 'bool', 'micro_label': 'bool',
    'read_only': 'bool',
    'bg_token': 'token', 'text_token': 'token', 'border_token': 'token',
    'accent_token': 'token',
    'layout_type': 'choice:vertical,horizontal,grid,none',
    'alignment': 'choice:left,center,right,fill',
    'border_style': 'choice:solid,none',
    'button_accent': 'choice:gold,teal,crimson',
}

# Readable labels
_PROP_LABELS = {
    'variable_name': 'NOMEN', 'label_text': 'TEXT', 'width': 'W',
    'height': 'H', 'bg_token': 'BG', 'text_token': 'TEXT COLOR',
    'border_token': 'BORDER', 'layout_type': 'LAYOUT', 'spacing': 'SPACING',
    'padding': 'PADDING', 'alignment': 'ALIGN', 'font_size': 'SIZE',
    'font_bold': 'BOLD', 'font_italic': 'ITALIC', 'micro_label': 'MICRO',
    'letter_spacing': 'LETTER SP', 'border_width': 'BORDER W',
    'border_style': 'BORDER STYLE', 'button_accent': 'ACCENT',
    'placeholder_text': 'PLACEHOLDER', 'read_only': 'READ ONLY',
    'margin_top': 'T', 'margin_right': 'R', 'margin_bottom': 'B', 'margin_left': 'L',
}


class PropertyInspector(QScrollArea):
    """Context-sensitive property editor for the selected element."""

    property_changed = pyqtSignal(str, str, object)  # element_id, prop_name, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setMinimumWidth(220)
        self.setMaximumWidth(300)

        self._inner = QWidget()
        self._layout = QVBoxLayout(self._inner)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(6)
        self._layout.addStretch()
        self.setWidget(self._inner)

        self._current_element: CanvasElement | None = None
        self._widgets: dict[str, QWidget] = {}
        self._updating = False

        self._show_empty()

    def _show_empty(self):
        self._clear()
        lbl = QLabel('No element selected')
        lbl.setProperty('role', 'dim')
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.insertWidget(0, lbl)

    def _clear(self):
        while self._layout.count() > 0:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._widgets.clear()
        self._layout.addStretch()

    def set_element(self, element: CanvasElement | None):
        """Populate inspector with the element's configurable properties."""
        self._current_element = element
        self._clear()

        if element is None:
            self._show_empty()
            return

        # Header
        type_lbl = QLabel(f'ELEMENTUM: {element.element_type}')
        type_lbl.setProperty('role', 'micro')
        self._layout.insertWidget(0, type_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        self._layout.insertWidget(1, sep)

        idx = 2
        props = element.configurable_properties()
        current_section = None

        for prop in props:
            # Section grouping
            section = self._get_section(prop)
            if section and section != current_section:
                current_section = section
                sec_lbl = QLabel(section)
                sec_lbl.setProperty('role', 'micro')
                self._layout.insertWidget(idx, sec_lbl)
                idx += 1

            prop_type = _PROP_TYPES.get(prop, 'text')
            label = _PROP_LABELS.get(prop, prop.upper())
            value = element.properties.get(prop, '')

            row = QHBoxLayout()
            row.setSpacing(4)
            lbl = QLabel(label)
            lbl.setFixedWidth(70)
            lbl.setProperty('role', 'dim')
            row.addWidget(lbl)

            widget = self._create_widget(prop, prop_type, value)
            row.addWidget(widget, 1)
            self._widgets[prop] = widget

            container = QWidget()
            container.setLayout(row)
            self._layout.insertWidget(idx, container)
            idx += 1

    def _get_section(self, prop: str) -> str | None:
        if prop in ('variable_name', 'label_text'):
            return 'NOMEN'
        if prop in ('width', 'height', 'min_width', 'min_height'):
            return 'AMPLITUDO'
        if prop in ('bg_token', 'text_token', 'border_token', 'accent_token'):
            return 'COLORES'
        if prop in ('layout_type', 'spacing', 'padding', 'alignment'):
            return 'DISPOSITIO'
        if prop in ('margin_top', 'margin_right', 'margin_bottom', 'margin_left'):
            return 'MARGINES'
        if prop in ('font_size', 'font_bold', 'font_italic', 'micro_label', 'letter_spacing'):
            return 'TYPOGRAPHIA'
        return None

    def _create_widget(self, prop: str, prop_type: str, value) -> QWidget:
        if prop_type == 'text':
            w = QLineEdit(str(value or ''))
            w.editingFinished.connect(
                lambda p=prop, w=w: self._on_text_changed(p, w.text()))
            return w

        if prop_type == 'int':
            w = QSpinBox()
            w.setRange(0, 9999)
            w.setValue(int(value or 0))
            w.valueChanged.connect(
                lambda v, p=prop: self._on_value_changed(p, v))
            return w

        if prop_type == 'bool':
            w = QCheckBox()
            w.setChecked(bool(value))
            w.stateChanged.connect(
                lambda s, p=prop: self._on_value_changed(p, s == Qt.CheckState.Checked.value))
            return w

        if prop_type == 'token':
            w = QComboBox()
            w.addItems(TOKEN_NAMES)
            if value in TOKEN_NAMES:
                w.setCurrentText(str(value))
            w.currentTextChanged.connect(
                lambda v, p=prop: self._on_value_changed(p, v))
            return w

        if prop_type.startswith('choice:'):
            choices = prop_type.split(':')[1].split(',')
            w = QComboBox()
            w.addItems(choices)
            if str(value) in choices:
                w.setCurrentText(str(value))
            w.currentTextChanged.connect(
                lambda v, p=prop: self._on_value_changed(p, v))
            return w

        # Fallback
        w = QLineEdit(str(value or ''))
        w.editingFinished.connect(
            lambda p=prop, w=w: self._on_text_changed(p, w.text()))
        return w

    def _on_text_changed(self, prop: str, value: str):
        if self._updating or not self._current_element:
            return
        self._current_element.update_property(prop, value)
        self.property_changed.emit(self._current_element.id, prop, value)

    def _on_value_changed(self, prop: str, value):
        if self._updating or not self._current_element:
            return
        self._current_element.update_property(prop, value)
        self.property_changed.emit(self._current_element.id, prop, value)
