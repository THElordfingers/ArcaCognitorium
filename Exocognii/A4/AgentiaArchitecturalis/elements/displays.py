# Agentia Architecturalis — elements/displays.py
# v1.0.0
"""Display elements: QLabel variants, QProgressBar."""

from PyQt6.QtWidgets import QLabel, QProgressBar, QWidget
from PyQt6.QtCore import Qt

from .base import CanvasElement


class LabelElement(CanvasElement):
    """Configurable QLabel — gold, dim, and micro variants."""

    VARIANT_DEFAULTS = {
        'QLabel_gold': {'text_token': 'c_gold', 'font_size': 14, 'font_bold': True, 'micro_label': False},
        'QLabel_dim':  {'text_token': 'c_gold_dim', 'font_size': 10, 'font_bold': False, 'micro_label': False},
        'QLabel_micro': {'text_token': 'c_gold_dim', 'font_size': 9, 'font_bold': False, 'micro_label': True, 'letter_spacing': 2},
    }

    def __init__(self, variant: str = 'QLabel_gold'):
        self._variant = variant
        super().__init__(variant, 'display')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update(self.VARIANT_DEFAULTS.get(self._variant, {}))
        d['variable_name'] = 'label_1'
        d['label_text'] = 'Label Text'
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'text_token', 'font_size',
                'font_bold', 'font_italic', 'micro_label', 'letter_spacing',
                'alignment']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        lbl = QLabel(p.get('label_text', 'Label'))
        color = tokens.get(p.get('text_token', 'c_text'), '#c8b88a')
        size = p.get('font_size', 11)
        weight = 'bold' if p.get('font_bold') else 'normal'
        style = 'italic' if p.get('font_italic') else 'normal'
        extra = ''
        if p.get('micro_label'):
            extra = f'text-transform: uppercase; letter-spacing: {p.get("letter_spacing", 2)}px;'
        lbl.setStyleSheet(
            f'QLabel {{ color: {color}; font-size: {size}px; '
            f'font-weight: {weight}; font-style: {style}; '
            f'font-family: Georgia, serif; {extra} background: transparent; }}'
        )
        if p.get('micro_label'):
            lbl.setText(p.get('label_text', 'LABEL').upper())
        align = p.get('alignment', 'left')
        if align == 'center':
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif align == 'right':
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        return lbl

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'label')
        pad = '    ' * indent
        text = p.get('label_text', 'Label')
        if p.get('micro_label'):
            text = text.upper()
        token_name = p.get('text_token', 'c_text').upper()
        lines = [
            f"{pad}self.{var} = QLabel('{text}')",
            f"{pad}self.{var}.setStyleSheet(",
            f"{pad}    f'QLabel {{ color: {{C_{token_name}}}; font-size: {p.get('font_size', 11)}px; "
            f"font-family: Georgia, serif; background: transparent; }}'",
            f"{pad})",
        ]
        if p.get('font_bold'):
            lines.append(f"{pad}self.{var}.setStyleSheet(self.{var}.styleSheet() + ' font-weight: bold;')")
        return lines


class ProgressBarElement(CanvasElement):
    def __init__(self):
        super().__init__('QProgressBar', 'display')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'progress_1', 'width': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'text_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        bar = QProgressBar()
        bar.setValue(65)
        bar.setFixedHeight(16)
        if self.properties.get('width'):
            bar.setFixedWidth(self.properties['width'])
        return bar

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'progress')
        pad = '    ' * indent
        return [f"{pad}self.{var} = QProgressBar()"]
