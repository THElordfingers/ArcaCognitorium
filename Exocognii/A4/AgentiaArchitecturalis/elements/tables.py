# Agentia Architecturalis — elements/tables.py
# v1.0.0
"""Table elements: QTableView."""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget
from .base import CanvasElement


class TableViewElement(CanvasElement):
    def __init__(self):
        super().__init__('QTableView', 'table')

    def _default_properties(self) -> dict:
        d = self._base_defaults()
        d.update({'variable_name': 'table_1', 'width': 300, 'height': 200})
        return d

    def configurable_properties(self) -> list[str]:
        return ['variable_name', 'width', 'height', 'bg_token', 'text_token', 'border_token']

    def create_preview_widget(self, tokens: dict) -> QWidget:
        p = self.properties
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(['Col A', 'Col B', 'Col C'])
        for r in range(3):
            for c in range(3):
                table.setItem(r, c, QTableWidgetItem(f'{r},{c}'))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if p.get('width'):
            table.setFixedWidth(p['width'])
        if p.get('height'):
            table.setFixedHeight(p['height'])
        return table

    def generate_code(self, tokens: dict, indent: int = 0) -> list[str]:
        var = self.properties.get('variable_name', 'table')
        pad = '    ' * indent
        return [f"{pad}self.{var} = QTableWidget()"]
