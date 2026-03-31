# Agentia Architecturalis — elements/inputs.py
# v1.0.0
"""Input elements: QLineEdit, QComboBox, QSlider, QSpinBox."""

from PyQt6.QtWidgets import QLineEdit, QComboBox, QSlider, QSpinBox, QWidget
from PyQt6.QtCore import Qt
from .base import CanvasElement


class LineEditElement(CanvasElement):
    def __init__(self):
        super().__init__('QLineEdit', 'input')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'input_1', 'placeholder_text': 'Inscriptio...',
                  'width': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'placeholder_text', 'width', 'bg_token',
                'text_token', 'border_token', 'font_size']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        edit = QLineEdit()
        edit.setPlaceholderText(p.get('placeholder_text', ''))
        if p.get('width'):
            edit.setFixedWidth(p['width'])
        return edit

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'input')
        pad = '    ' * indent
        lines = [f"{pad}self.{var} = QLineEdit()"]
        if p.get('placeholder_text'):
            lines.append(f"{pad}self.{var}.setPlaceholderText('{p['placeholder_text']}')")
        return lines


class ComboBoxElement(CanvasElement):
    def __init__(self):
        super().__init__('QComboBox', 'input')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'combo_1', 'width': 180})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'bg_token', 'text_token', 'border_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        combo = QComboBox()
        combo.addItems(['Selectio Prima', 'Selectio Altera'])
        if self.properties.get('width'):
            combo.setFixedWidth(self.properties['width'])
        return combo

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'combo')
        pad = '    ' * indent
        return [f"{pad}self.{var} = QComboBox()"]


class SliderElement(CanvasElement):
    def __init__(self):
        super().__init__('QSlider', 'input')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'slider_1', 'width': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(50)
        if self.properties.get('width'):
            slider.setFixedWidth(self.properties['width'])
        return slider

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'slider')
        pad = '    ' * indent
        return [f"{pad}self.{var} = QSlider(Qt.Orientation.Horizontal)"]


class SpinBoxElement(CanvasElement):
    def __init__(self):
        super().__init__('QSpinBox', 'input')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'spinbox_1', 'width': 80})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'bg_token', 'text_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        spin = QSpinBox()
        if self.properties.get('width'):
            spin.setFixedWidth(self.properties['width'])
        return spin

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'spinbox')
        pad = '    ' * indent
        return [f"{pad}self.{var} = QSpinBox()"]
