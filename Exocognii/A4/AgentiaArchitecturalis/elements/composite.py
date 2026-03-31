# Agentia Architecturalis — elements/composite.py
# v1.0.0
"""Pre-built ModusArcanus widget patterns."""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget,
)
from PyQt6.QtCore import Qt
from .base import CanvasElement


class TopBarElement(CanvasElement):
    def __init__(self):
        super().__init__('TopBar', 'composite')

    def _default_properties(self) -> dict:
        return {
            'variable_name': 'topbar', 'label_text': '\u2726  APP TITLE  \u2726',
            'bg_token': 'c_panel', 'border_token': 'c_gold_dark',
            'text_token': 'c_gold', 'height': 52,
        }

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'height', 'bg_token',
                'border_token', 'text_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        frame = QFrame()
        frame.setFixedHeight(p.get('height', 52))
        bg = tokens.get(p.get('bg_token', 'c_panel'), '#0a0a12')
        border = tokens.get(p.get('border_token', 'c_gold_dark'), '#3a2e10')
        frame.setStyleSheet(
            f'QFrame {{ background: {bg}; border-bottom: 1px solid {border}; }}'
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 0, 16, 0)
        title = QLabel(p.get('label_text', '\u2726  APP  \u2726'))
        color = tokens.get(p.get('text_token', 'c_gold'), '#d4af37')
        title.setStyleSheet(
            f'color: {color}; font-weight: bold; font-size: 14px; '
            f'font-family: Georgia, serif; background: transparent;'
        )
        layout.addWidget(title)
        layout.addStretch()
        return frame

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'topbar')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QFrame()",
            f"{pad}self.{var}.setFixedHeight({p.get('height', 52)})",
            f"{pad}self.{var}.setStyleSheet(",
            f"{pad}    f'QFrame {{ background: {{C_{p.get('bg_token','c_panel').upper()}}}; "
            f"border-bottom: 1px solid {{C_{p.get('border_token','c_gold_dark').upper()}}};  }}'",
            f"{pad})",
            f"{pad}{var}_layout = QHBoxLayout(self.{var})",
            f"{pad}{var}_layout.setContentsMargins(16, 0, 16, 0)",
            f"{pad}{var}_title = QLabel('{p.get('label_text', 'APP')}')",
            f"{pad}{var}_title.setStyleSheet(",
            f"{pad}    f'color: {{C_{p.get('text_token','c_gold').upper()}}}; font-weight: bold; "
            f"font-size: 14px; font-family: Georgia, serif; background: transparent;'",
            f"{pad})",
            f"{pad}{var}_layout.addWidget({var}_title)",
            f"{pad}{var}_layout.addStretch()",
        ]


class StatusBarElement(CanvasElement):
    def __init__(self):
        super().__init__('StatusBar', 'composite')

    def _default_properties(self) -> dict:
        return {
            'variable_name': 'statusbar', 'label_text': 'Status awaits.',
            'bg_token': 'c_panel', 'border_token': 'c_gold_dark',
            'text_token': 'c_gold_dim', 'height': 28,
        }

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'height', 'bg_token',
                'border_token', 'text_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        frame = QFrame()
        frame.setFixedHeight(p.get('height', 28))
        bg = tokens.get(p.get('bg_token', 'c_panel'), '#0a0a12')
        border = tokens.get(p.get('border_token', 'c_gold_dark'), '#3a2e10')
        frame.setStyleSheet(
            f'QFrame {{ background: {bg}; border-top: 1px solid {border}; }}'
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 0, 12, 0)
        msg = QLabel(p.get('label_text', 'Status awaits.'))
        color = tokens.get(p.get('text_token', 'c_gold_dim'), '#7a6a2a')
        msg.setStyleSheet(
            f'color: {color}; font-size: 10px; font-family: Georgia, serif; background: transparent;'
        )
        layout.addWidget(msg)
        layout.addStretch()
        return frame

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'statusbar')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QFrame()",
            f"{pad}self.{var}.setFixedHeight({p.get('height', 28)})",
            f"{pad}self.{var}.setStyleSheet(",
            f"{pad}    f'QFrame {{ background: {{C_{p.get('bg_token','c_panel').upper()}}}; "
            f"border-top: 1px solid {{C_{p.get('border_token','c_gold_dark').upper()}}};  }}'",
            f"{pad})",
            f"{pad}{var}_layout = QHBoxLayout(self.{var})",
            f"{pad}{var}_layout.setContentsMargins(12, 0, 12, 0)",
        ]


class ControlPanelElement(CanvasElement):
    def __init__(self):
        super().__init__('ControlPanel', 'composite')

    def _default_properties(self) -> dict:
        return {
            'variable_name': 'control_panel', 'width': 280,
            'bg_token': 'c_panel', 'border_token': 'c_gold_dark',
            'layout_type': 'vertical', 'spacing': 12, 'padding': 12,
        }

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'bg_token', 'border_token',
                'spacing', 'padding']

    def accepts_children(self) -> bool:
        return True

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        frame = QFrame()
        if p.get('width'):
            frame.setFixedWidth(p['width'])
        bg = tokens.get(p.get('bg_token', 'c_panel'), '#0a0a12')
        border = tokens.get(p.get('border_token', 'c_gold_dark'), '#3a2e10')
        frame.setStyleSheet(
            f'QFrame {{ background: {bg}; border-right: 1px solid {border}; }}'
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(p.get('spacing', 12))
        pad = p.get('padding', 12)
        layout.setContentsMargins(pad, pad, pad, pad)
        for child in self.children:
            w = child.create_preview_widget(tokens)
            if w:
                layout.addWidget(w)
        layout.addStretch()
        return frame

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'control_panel')
        pad_str = '    ' * indent
        lines = [
            f"{pad_str}self.{var} = QFrame()",
            f"{pad_str}self.{var}.setFixedWidth({p.get('width', 280)})",
            f"{pad_str}{var}_layout = QVBoxLayout(self.{var})",
            f"{pad_str}{var}_layout.setSpacing({p.get('spacing', 12)})",
        ]
        for child in self.children:
            child_lines = child.generate_code(tokens, indent)
            lines.extend(child_lines)
            child_var = child.properties.get('variable_name', 'widget')
            lines.append(f"{pad_str}{var}_layout.addWidget(self.{child_var})")
        lines.append(f"{pad_str}{var}_layout.addStretch()")
        return lines


class SectionHeaderElement(CanvasElement):
    def __init__(self):
        super().__init__('SectionHeader', 'composite')

    def _default_properties(self) -> dict:
        return {
            'variable_name': 'section_header', 'label_text': '\u2726  Section  \u2726',
            'text_token': 'c_gold', 'font_size': 14, 'font_bold': True,
        }

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'text_token', 'font_size',
                'font_bold', 'alignment']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        lbl = QLabel(p.get('label_text', '\u2726  Section  \u2726'))
        color = tokens.get(p.get('text_token', 'c_gold'), '#d4af37')
        lbl.setStyleSheet(
            f'color: {color}; font-size: {p.get("font_size", 14)}px; '
            f'font-weight: bold; font-family: Georgia, serif; background: transparent;'
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'section_header')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QLabel('{p.get('label_text', 'Section')}')",
            f"{pad}self.{var}.setProperty('role', 'title')",
            f"{pad}self.{var}.setAlignment(Qt.AlignmentFlag.AlignCenter)",
        ]


class SwatchStripElement(CanvasElement):
    def __init__(self):
        super().__init__('SwatchStrip', 'composite')

    def _default_properties(self) -> dict:
        return {'variable_name': 'swatch_strip', 'width': 200}

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        from ..constants import TOKEN_NAMES
        frame = QWidget()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        for name in TOKEN_NAMES[:5]:
            row = QHBoxLayout()
            swatch = QLabel()
            swatch.setFixedSize(18, 14)
            hex_val = tokens.get(name, '#000000')
            swatch.setStyleSheet(f'background: {hex_val}; border: 1px solid #3a2e10;')
            row.addWidget(swatch)
            lbl = QLabel(name)
            lbl.setStyleSheet('color: #7a6a2a; font-size: 9px; background: transparent;')
            row.addWidget(lbl)
            row.addStretch()
            layout.addLayout(row)
        return frame

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'swatch_strip')
        pad = '    ' * indent
        return [
            f"{pad}# SwatchStrip — implement per application needs",
            f"{pad}self.{var} = QWidget()",
        ]
