# Agentia Architecturalis — elements/decorative.py
# v1.0.0
"""Decorative elements: Separator, Spacer, RuleLine."""

from PyQt6.QtWidgets import QFrame, QWidget, QSizePolicy
from .base import CanvasElement


class SeparatorElement(CanvasElement):
    def __init__(self):
        super().__init__('Separator', 'decorative')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'sep_1'})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'border_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        color = tokens.get(self.properties.get('border_token', 'c_gold_dark'), '#3a2e10')
        sep.setStyleSheet(f'color: {color};')
        return sep

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'sep')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QFrame()",
            f"{pad}self.{var}.setFrameShape(QFrame.Shape.HLine)",
        ]


class SpacerElement(CanvasElement):
    def __init__(self):
        super().__init__('Spacer', 'decorative')

    def _default_properties(self) -> dict:
        return {'variable_name': 'spacer_1', 'height': 16}

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'height']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        w = QWidget()
        h = self.properties.get('height', 16)
        w.setFixedHeight(h)
        w.setStyleSheet('background: transparent;')
        return w

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'spacer')
        h = self.properties.get('height', 16)
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QWidget()",
            f"{pad}self.{var}.setFixedHeight({h})",
        ]


class RuleLineElement(CanvasElement):
    def __init__(self):
        super().__init__('RuleLine', 'decorative')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'rule_1', 'border_token': 'c_gold_dim'})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'border_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        color = tokens.get(self.properties.get('border_token', 'c_gold_dim'), '#7a6a2a')
        rule.setStyleSheet(f'color: {color};')
        rule.setFixedHeight(2)
        return rule

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'rule')
        pad = '    ' * indent
        return [
            f"{pad}self.{var} = QFrame()",
            f"{pad}self.{var}.setFrameShape(QFrame.Shape.HLine)",
            f"{pad}self.{var}.setFixedHeight(2)",
        ]
