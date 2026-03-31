# Agentia Architecturalis — elements/text.py
# v1.0.0
"""Text display elements: QTextEdit, QPlainTextEdit."""

from PyQt6.QtWidgets import QTextEdit, QPlainTextEdit, QWidget
from .base import CanvasElement


class TextEditElement(CanvasElement):
    def __init__(self):
        super().__init__('QTextEdit', 'input')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'text_edit_1', 'read_only': False,
                  'width': 250, 'height': 120, 'label_text': ''})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'height', 'read_only',
                'bg_token', 'text_token', 'border_token', 'font_size']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        edit = QTextEdit()
        edit.setReadOnly(p.get('read_only', False))
        edit.setPlaceholderText('Lore text...')
        if p.get('width'):
            edit.setFixedWidth(p['width'])
        if p.get('height'):
            edit.setFixedHeight(p['height'])
        return edit

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'text_edit')
        pad = '    ' * indent
        lines = [f"{pad}self.{var} = QTextEdit()"]
        if p.get('read_only'):
            lines.append(f"{pad}self.{var}.setReadOnly(True)")
        return lines
