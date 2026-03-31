# Auctoritas Spectralis — widgets/registry_drawer.py
# v1.0.0
"""Registrum Chromaticum — collapsible bottom drawer for ratified palettes."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor


class RegistryDrawer(QWidget):
    """Collapsible drawer displaying all ratified palettes from the registry."""

    load_requested = pyqtSignal(int)    # registry_id to load into Compositio
    export_requested = pyqtSignal(int)  # registry_id to export

    COLLAPSED_HEIGHT = 32
    EXPANDED_HEIGHT = 220

    def __init__(self, parent=None):
        super().__init__(parent)
        self._expanded = False
        self.setMaximumHeight(self.COLLAPSED_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header bar ──
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)

        title = QLabel('REGISTRUM CHROMATICUM')
        title.setProperty('role', 'micro')
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._toggle_btn = QPushButton('\u25b2')
        self._toggle_btn.setFixedSize(28, 24)
        self._toggle_btn.clicked.connect(self.toggle)
        header_layout.addWidget(self._toggle_btn)

        layout.addWidget(header)

        # ── Table ──
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ['#', 'Designator', 'Sealed', 'AA', 'AAA', 'Actions']
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self._table)

    def toggle(self):
        target = self.EXPANDED_HEIGHT if not self._expanded else self.COLLAPSED_HEIGHT
        anim = QPropertyAnimation(self, b"maximumHeight", self)
        anim.setDuration(220)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.setStartValue(self.maximumHeight())
        anim.setEndValue(target)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._expanded = not self._expanded
        self._toggle_btn.setText('\u25bc' if self._expanded else '\u25b2')

    def populate(self, palettes: list[dict]):
        """Fill table from registry query results."""
        self._table.setRowCount(len(palettes))
        for row, p in enumerate(palettes):
            self._table.setItem(row, 0, QTableWidgetItem(str(p.get('id', ''))))

            self._table.setItem(row, 1, QTableWidgetItem(p.get('designator', '')))

            sealed = p.get('created_at', '')[:10]
            self._table.setItem(row, 2, QTableWidgetItem(sealed))

            aa = '\u2726' if p.get('passes_aa') else '\u2334'
            aa_item = QTableWidgetItem(aa)
            aa_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, aa_item)

            aaa = '\u2726' if p.get('passes_aaa') else '\u2334'
            aaa_item = QTableWidgetItem(aaa)
            aaa_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, aaa_item)

            # Action buttons in a container widget
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(2, 0, 2, 0)
            actions_layout.setSpacing(4)

            rid = p.get('id')
            load_btn = QPushButton('Load')
            load_btn.setFixedHeight(22)
            load_btn.clicked.connect(lambda _, r=rid: self.load_requested.emit(r))
            actions_layout.addWidget(load_btn)

            exp_btn = QPushButton('Exp')
            exp_btn.setFixedHeight(22)
            exp_btn.clicked.connect(lambda _, r=rid: self.export_requested.emit(r))
            actions_layout.addWidget(exp_btn)

            self._table.setCellWidget(row, 5, actions)
