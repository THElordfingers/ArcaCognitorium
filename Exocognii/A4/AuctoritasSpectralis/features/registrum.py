"""
AUCTORITAS SPECTRALIS — v1.0.0
features/registrum.py — Feature V: REGISTRUM

The permanent ledger. Full SQLite registry as a sortable, filterable table.
Row click opens detail panel. Read only. Not editable. Not deletable.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QSplitter, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QBrush

import AuctoritasSpectralis.registry.db as db
from AuctoritasSpectralis.i18n import t
from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER

C_VOID      = "#050507"
C_OBSIDIAN  = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_PARCHMENT = "#c8b88a"
C_PASS      = "#1a5a5a"
C_FAIL      = "#6b1212"
C_PASS_T    = "#a0d0c0"
C_FAIL_T    = "#e08080"

COLUMNS = [
    ("#",          "id",           50),
    ("Designator", "designator",   200),
    ("Sealed",     "sealed_at",    120),
    ("WCAG Min",   "wcag_min",     80),
    ("APCA Min",   "apca_min",     80),
    ("AA",         "aa_pass",      50),
    ("AAA",        "aaa_pass",     50),
    ("Seal Hash",  "seal",         120),
    ("Notes",      "notes",        140),
]


def _mono(text: str, size: int = 9, color: str = C_GOLD_DIM) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-family: 'Share Tech Mono', monospace; font-size: {size}px; "
        f"color: {color}; background: transparent; letter-spacing: 0.5px;"
    )
    return lbl


# ── Record detail panel ───────────────────────────────────────────────────

class RecordDetail(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._title = QLabel("—")
        self._title.setStyleSheet(
            f"font-family: 'Cinzel', Georgia, serif; font-size: 14px; "
            f"color: {C_GOLD}; letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(self._title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK}; background: {C_GOLD_DARK};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Two-column split: tokens left, record meta right
        cols = QHBoxLayout()
        cols.setSpacing(14)

        # Token hexes
        tok_w = QWidget()
        tok_l = QVBoxLayout(tok_w)
        tok_l.setContentsMargins(0, 0, 0, 0)
        tok_l.setSpacing(2)
        micro = _mono("TOKEN HEXES", size=7, color=C_GOLD_DIM)
        micro.setStyleSheet(micro.styleSheet() + " letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;")
        tok_l.addWidget(micro)

        self._tok_rows: dict[str, tuple[QLabel, QLabel, QLabel]] = {}
        for key in TOKEN_ORDER:
            row_w   = QWidget()
            row_l   = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 1, 0, 1)
            row_l.setSpacing(7)

            sw = QLabel()
            sw.setFixedSize(18, 14)
            sw.setStyleSheet(f"background: #000; border: 1px solid {C_GOLD_DARK};")

            key_lbl = _mono(key, size=8)
            key_lbl.setFixedWidth(90)

            hex_lbl = _mono("—", size=8, color=C_GOLD_DIM)

            row_l.addWidget(sw)
            row_l.addWidget(key_lbl)
            row_l.addWidget(hex_lbl)
            row_l.addStretch()

            self._tok_rows[key] = (sw, key_lbl, hex_lbl)
            tok_l.addWidget(row_w)
        tok_l.addStretch()
        cols.addWidget(tok_w, stretch=1)

        # Record meta
        meta_w = QWidget()
        meta_l = QVBoxLayout(meta_w)
        meta_l.setContentsMargins(0, 0, 0, 0)
        meta_l.setSpacing(3)
        micro2 = _mono("RECORD", size=7, color=C_GOLD_DIM)
        micro2.setStyleSheet(micro2.styleSheet() + " letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;")
        meta_l.addWidget(micro2)

        self._meta_labels: dict[str, QLabel] = {}
        for key in ["id", "designator", "sealed_at", "seal", "wcag_min", "apca_min", "aa_pass", "aaa_pass", "notes"]:
            lbl = _mono("—", size=8, color=C_PARCHMENT)
            self._meta_labels[key] = lbl
            meta_l.addWidget(lbl)
        meta_l.addStretch()
        cols.addWidget(meta_w, stretch=1)

        layout.addLayout(cols, stretch=1)

    def load_record(self, record: dict) -> None:
        tokens = record.get("tokens", {})
        self._title.setText(record.get("designator", "—"))

        for key in TOKEN_ORDER:
            hex_val = tokens.get(key, "#000000")
            sw, key_lbl, hex_lbl = self._tok_rows[key]
            sw.setStyleSheet(f"background: {hex_val}; border: 1px solid {C_GOLD_DARK};")
            hex_lbl.setText(hex_val)

        for key, lbl in self._meta_labels.items():
            val = record.get(key, "—")
            if key in ("aa_pass", "aaa_pass"):
                val = "✓" if val else "✗"
            elif key == "seal":
                val = str(val)[:8] + "…" if val else "—"
            elif key == "sealed_at":
                val = str(val)[:19]
            lbl.setText(f"{key}: {val}")
            if key in ("aa_pass", "aaa_pass"):
                color = C_PASS_T if record.get(key) else C_FAIL_T
                lbl.setStyleSheet(
                    f"font-family: 'Share Tech Mono', monospace; font-size: 8px; "
                    f"color: {color}; background: transparent;"
                )


# ── REGISTRUM main widget ────────────────────────────────────────────────

class RegistrumFeature(QWidget):
    export_requested = pyqtSignal()
    status_message   = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records: list[dict] = []
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {C_GOLD_DARK}; height: 1px; }}"
        )

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(COLUMNS))
        self._table.setHorizontalHeaderLabels([c[0] for c in COLUMNS])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {C_VOID}; color: {C_GOLD_DIM}; "
            f"border: 1px solid {C_GOLD_DARK}; gridline-color: {C_GOLD_DARK}; "
            f"font-family: 'Share Tech Mono', monospace; font-size: 9px; "
            f"alternate-background-color: rgba(10,10,18,0.5); "
            f"selection-background-color: rgba(212,175,55,0.08); "
            f"selection-color: {C_GOLD}; }}"
            f"QHeaderView::section {{ background: {C_OBSIDIAN}; color: {C_GOLD}; "
            f"border: 1px solid {C_GOLD_DARK}; font-family: 'Share Tech Mono', monospace; "
            f"font-size: 7px; letter-spacing: 1px; padding: 4px 8px; font-weight: normal; "
            f"text-align: left; }}"
        )
        hh = self._table.horizontalHeader()
        for i, (_, _, width) in enumerate(COLUMNS):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            self._table.setColumnWidth(i, width)
        hh.setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(26)

        self._table.itemSelectionChanged.connect(self._on_row_selected)
        splitter.addWidget(self._table)

        # Detail panel
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setStyleSheet("border: none; background: transparent;")
        self._detail = RecordDetail()
        detail_scroll.setWidget(self._detail)
        splitter.addWidget(detail_scroll)

        splitter.setSizes([360, 280])
        layout.addWidget(splitter, stretch=1)

    def refresh(self) -> None:
        self._records = db.fetch_all()
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(self._records))

        for row_idx, record in enumerate(self._records):
            for col_idx, (_, key, _) in enumerate(COLUMNS):
                val = record.get(key, "")
                if key in ("aa_pass", "aaa_pass"):
                    passed = bool(val)
                    item = QTableWidgetItem("✓" if passed else "✗")
                    item.setForeground(QBrush(QColor(C_PASS_T if passed else C_FAIL_T)))
                    item.setBackground(QBrush(QColor(C_PASS if passed else C_FAIL)))
                elif key == "seal":
                    item = QTableWidgetItem(str(val)[:8] + "…" if val else "—")
                elif key == "designator":
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QBrush(QColor(C_GOLD)))
                    font = item.font()
                    font.setFamily("IM Fell English")
                    font.setItalic(True)
                    font.setPointSize(10)
                    item.setFont(font)
                elif key == "sealed_at":
                    item = QTableWidgetItem(str(val)[:10] if val else "—")
                else:
                    item = QTableWidgetItem(str(val))

                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(row_idx, col_idx, item)

        self._table.setSortingEnabled(True)
        count = len(self._records)
        self.status_message.emit(
            "⚙ Registrum — read only.",
            f"{count} record{'s' if count != 1 else ''} · chromatic_registry.db",
        )

    def _on_row_selected(self) -> None:
        rows = self._table.selectedItems()
        if not rows:
            return
        row_idx = self._table.currentRow()
        # Map display row back to record (table may be sorted)
        id_item = self._table.item(row_idx, 0)
        if id_item is None:
            return
        try:
            record_id = int(id_item.text())
        except ValueError:
            return
        record = db.fetch_by_id(record_id)
        if record:
            self._detail.load_record(record)
            self.status_message.emit(
                f"⚙ {record.get('designator', '—')} — read only.",
                f"{len(self._records)} records · chromatic_registry.db",
            )

    def get_fascia_buttons(self, mode: str = "LAT") -> list[QWidget]:
        from AuctoritasSpectralis.shell import FasciaButton
        self._fb_export = FasciaButton(t("btn.export_reg", mode), "normal")
        self._fb_export.clicked.connect(self.export_requested)
        return [self._fb_export]

    def set_mode(self, mode: str) -> None:
        if hasattr(self, "_fb_export"):
            self._fb_export.setText(t("btn.export_reg", mode))
