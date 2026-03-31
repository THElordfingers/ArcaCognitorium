# Auctoritas Spectralis — widgets/contrast_grid.py
# v1.0.0
"""Scrutinium contrast matrix widget — NxN grid of token pair ratios."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..constants import FG_TOKENS, BG_TOKENS, TOKEN_LABELS


class ContrastGrid(QWidget):
    """Contrast matrix: foreground tokens (rows) × background tokens (cols)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Title
        title = QLabel('CONTRAST MATRIX')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        # Table
        self._table = QTableWidget(len(FG_TOKENS), len(BG_TOKENS))
        self._table.setHorizontalHeaderLabels(
            [TOKEN_LABELS.get(n, n)[:5] for n in BG_TOKENS]
        )
        self._table.setVerticalHeaderLabels(
            [TOKEN_LABELS.get(n, n)[:5] for n in FG_TOKENS]
        )
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )
        self._table.verticalHeader().setDefaultSectionSize(26)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self._table)

        # Summary line
        self._summary_frame = QHBoxLayout()
        self._aa_label = QLabel('WCAG AA: —')
        self._aa_label.setProperty('role', 'dim')
        self._summary_frame.addWidget(self._aa_label)

        self._aaa_label = QLabel('AAA: —')
        self._aaa_label.setProperty('role', 'dim')
        self._summary_frame.addWidget(self._aaa_label)

        self._apca_label = QLabel('APCA Lc min: —')
        self._apca_label.setProperty('role', 'dim')
        self._summary_frame.addWidget(self._apca_label)

        self._summary_frame.addStretch()
        layout.addLayout(self._summary_frame)

    def update_matrix(self, matrix: list[dict], audit: dict):
        """Populate the grid with contrast data."""
        # Build lookup: (fg_token, bg_token) -> entry
        lookup = {}
        for entry in matrix:
            lookup[(entry['fg_token'], entry['bg_token'])] = entry

        for row_idx, fg_name in enumerate(FG_TOKENS):
            for col_idx, bg_name in enumerate(BG_TOKENS):
                entry = lookup.get((fg_name, bg_name))
                if entry is None:
                    item = QTableWidgetItem('—')
                    self._table.setItem(row_idx, col_idx, item)
                    continue

                ratio = entry['wcag_ratio']
                item = QTableWidgetItem(f'{ratio:.1f}')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color coding: green = AA+AAA, gold = AA only, red = fail
                if entry['passes_aaa']:
                    item.setForeground(QColor('#1a5a5a'))
                elif entry['passes_aa']:
                    item.setForeground(QColor('#d4af37'))
                else:
                    item.setForeground(QColor('#8b1a1a'))
                    item.setBackground(QColor('#1a0808'))

                self._table.setItem(row_idx, col_idx, item)

        # Summary
        aa = audit.get('passes_aa', False)
        aaa = audit.get('passes_aaa', False)
        min_lc = audit.get('min_apca_lc', 0)

        self._aa_label.setText(
            f"WCAG AA: {'✦ PASS' if aa else '⌬ FAIL'}"
        )
        self._aaa_label.setText(
            f"AAA: {'✦' if aaa else '⌬'}"
        )
        self._apca_label.setText(f"APCA Lc min: {min_lc:.1f}")

        # Style the labels based on pass/fail
        self._aa_label.setStyleSheet(
            f"color: {'#1a5a5a' if aa else '#8b1a1a'};"
        )
        self._aaa_label.setStyleSheet(
            f"color: {'#1a5a5a' if aaa else '#7a6a2a'};"
        )
