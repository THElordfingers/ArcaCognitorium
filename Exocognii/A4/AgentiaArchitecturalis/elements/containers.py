# Agentia Architecturalis — elements/containers.py
# v1.0.0
"""Container elements: QFrame, QGroupBox, QSplitter, QTabWidget."""

from PyQt6.QtWidgets import (
    QFrame, QGroupBox, QSplitter, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtCore import Qt

from .base import CanvasElement


class FrameElement(CanvasElement):
    def __init__(self):
        super().__init__('QFrame', 'container')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'frame_1', 'width': 280, 'height': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'height', 'bg_token', 'border_token',
                'layout_type', 'spacing', 'padding', 'alignment',
                'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
                'border_width', 'border_style']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        frame = QFrame()
        bg = tokens.get(p.get('bg_token', 'c_panel'), '#0a0a12')
        border = tokens.get(p.get('border_token', 'c_gold_dark'), '#3a2e10')
        bw = p.get('border_width', 1)
        frame.setStyleSheet(
            f'QFrame {{ background: {bg}; border: {bw}px solid {border}; }}'
        )
        layout_type = p.get('layout_type', 'vertical')
        if layout_type == 'horizontal':
            layout = QHBoxLayout(frame)
        elif layout_type == 'grid':
            layout = QGridLayout(frame)
        else:
            layout = QVBoxLayout(frame)
        layout.setSpacing(p.get('spacing', 16))
        layout.setContentsMargins(
            p.get('padding', 8), p.get('padding', 8),
            p.get('padding', 8), p.get('padding', 8),
        )
        for child in self.children:
            w = child.create_preview_widget(tokens)
            if w:
                layout.addWidget(w)
        if p.get('width'):
            frame.setFixedWidth(p['width'])
        if p.get('height'):
            frame.setFixedHeight(p['height'])
        return frame

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'frame')
        pad = '    ' * indent
        lines = [
            f"{pad}self.{var} = QFrame()",
            f"{pad}self.{var}.setStyleSheet(",
            f"{pad}    f'QFrame {{ background: {{C_{p.get('bg_token','c_panel').upper()}}}; "
            f"border: {p.get('border_width',1)}px solid {{C_{p.get('border_token','c_gold_dark').upper()}}};  }}'",
            f"{pad})",
        ]
        lt = p.get('layout_type', 'vertical')
        layout_cls = 'QHBoxLayout' if lt == 'horizontal' else 'QVBoxLayout'
        lines.append(f"{pad}{var}_layout = {layout_cls}(self.{var})")
        lines.append(f"{pad}{var}_layout.setSpacing({p.get('spacing', 16)})")
        pad_val = p.get('padding', 8)
        lines.append(f"{pad}{var}_layout.setContentsMargins({pad_val}, {pad_val}, {pad_val}, {pad_val})")
        for child in self.children:
            child_lines = child.generate_code(tokens, indent)
            lines.extend(child_lines)
            child_var = child.properties.get('variable_name', 'widget')
            lines.append(f"{pad}{var}_layout.addWidget(self.{child_var})")
        return lines


class GroupBoxElement(CanvasElement):
    def __init__(self):
        super().__init__('QGroupBox', 'container')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'group_1', 'label_text': 'GROUP',
                  'width': 280, 'height': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'label_text', 'width', 'height',
                'bg_token', 'border_token', 'layout_type', 'spacing', 'padding']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        group = QGroupBox(p.get('label_text', 'GROUP'))
        layout = QVBoxLayout(group)
        layout.setSpacing(p.get('spacing', 16))
        for child in self.children:
            w = child.create_preview_widget(tokens)
            if w:
                layout.addWidget(w)
        return group

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'group')
        pad = '    ' * indent
        lines = [
            f"{pad}self.{var} = QGroupBox('{p.get('label_text', 'GROUP')}')",
            f"{pad}{var}_layout = QVBoxLayout(self.{var})",
            f"{pad}{var}_layout.setSpacing({p.get('spacing', 16)})",
        ]
        for child in self.children:
            child_lines = child.generate_code(tokens, indent)
            lines.extend(child_lines)
            child_var = child.properties.get('variable_name', 'widget')
            lines.append(f"{pad}{var}_layout.addWidget(self.{child_var})")
        return lines


class SplitterElement(CanvasElement):
    def __init__(self):
        super().__init__('QSplitter', 'container')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'splitter_1', 'layout_type': 'horizontal',
                  'width': 400, 'height': 300})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'height', 'layout_type']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        orient = (Qt.Orientation.Horizontal
                  if p.get('layout_type') == 'horizontal'
                  else Qt.Orientation.Vertical)
        splitter = QSplitter(orient)
        for child in self.children:
            w = child.create_preview_widget(tokens)
            if w:
                splitter.addWidget(w)
        return splitter

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'splitter')
        pad = '    ' * indent
        orient = 'Qt.Orientation.Horizontal' if p.get('layout_type') == 'horizontal' else 'Qt.Orientation.Vertical'
        lines = [f"{pad}self.{var} = QSplitter({orient})"]
        for child in self.children:
            child_lines = child.generate_code(tokens, indent)
            lines.extend(child_lines)
            child_var = child.properties.get('variable_name', 'widget')
            lines.append(f"{pad}self.{var}.addWidget(self.{child_var})")
        return lines


class TabWidgetElement(CanvasElement):
    def __init__(self):
        super().__init__('QTabWidget', 'container')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'tabs_1', 'width': 400, 'height': 300})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'height', 'bg_token', 'border_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        tabs = QTabWidget()
        for i, child in enumerate(self.children):
            w = child.create_preview_widget(tokens)
            if w:
                label = child.properties.get('label_text', f'Tab {i+1}')
                tabs.addTab(w, label)
        return tabs

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        p = self.properties
        var = p.get('variable_name', 'tabs')
        pad = '    ' * indent
        lines = [f"{pad}self.{var} = QTabWidget()"]
        for i, child in enumerate(self.children):
            child_lines = child.generate_code(tokens, indent)
            lines.extend(child_lines)
            child_var = child.properties.get('variable_name', 'widget')
            label = child.properties.get('label_text', f'Tab {i+1}')
            lines.append(f"{pad}self.{var}.addTab(self.{child_var}, '{label}')")
        return lines
