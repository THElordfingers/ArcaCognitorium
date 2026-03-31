# Agentia Architecturalis — elements/buttons.py
# v1.0.0
"""Button elements: arcane variants and toggle."""

from PyQt6.QtWidgets import QPushButton, QWidget
from .base import CanvasElement


class ArcaneButtonElement(CanvasElement):
    ACCENT_MAP = {
        'ArcaneButton_gold': 'gold',
        'ArcaneButton_teal': 'teal',
        'ArcaneButton_crimson': 'crimson',
    }
    ACCENT_TOKENS = {
        'gold': 'c_gold', 'teal': 'c_teal', 'crimson': 'c_crimson',
    }

    def __init__(self, variant: str = 'ArcaneButton_gold'):
        self._variant = variant
        super().__init__(variant, 'button')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        accent = self.ACCENT_MAP.get(self._variant, 'gold')
        d.update({
            'variable_name': 'btn_1',
            'label_text': 'Action',
            'button_accent': accent,
            'text_token': self.ACCENT_TOKENS.get(accent, 'c_gold'),
        })
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'button_accent',
                'bg_token', 'text_token', 'border_token',
                'font_size', 'letter_spacing', 'padding']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        btn = QPushButton(p.get('label_text', 'Action'))
        accent = p.get('button_accent', 'gold')
        btn.setProperty('accent', accent)
        return btn

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'btn')
        pad = '    ' * indent
        accent = p.get('button_accent', 'gold')
        lines = [f"{pad}self.{var} = QPushButton('{p.get('label_text', 'Action')}')"]
        if accent != 'gold':
            lines.append(f"{pad}self.{var}.setProperty('accent', '{accent}')")
        return lines


class ToggleButtonElement(CanvasElement):
    def __init__(self):
        super().__init__('ToggleButton', 'button')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'toggle_1', 'label_text': 'Toggle'})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'text_token', 'bg_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        btn = QPushButton(self.properties.get('label_text', 'Toggle'))
        btn.setCheckable(True)
        return btn

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'toggle')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QPushButton('{p.get('label_text', 'Toggle')}')",
            f"{pad}self.{var}.setCheckable(True)",
        ]
