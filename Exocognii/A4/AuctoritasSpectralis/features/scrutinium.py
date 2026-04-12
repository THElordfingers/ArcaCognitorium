"""
AUCTORITAS SPECTRALIS — v1.0.0
features/scrutinium.py — Feature II: SCRUTINIUM

Contrast audit workspace.
Parium Colorum: single pair display with headline WCAG + five secondary metrics.
Contrast Matrix: FG × BG token grid, metric-switchable, cell tooltips.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame, QSizePolicy, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont

from AuctoritasSpectralis.engine.contrast import score_pair, score_matrix
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

FG_TOKENS = ["c_gold", "c_text", "c_white", "c_gold_dim", "c_crimson", "c_teal"]
BG_TOKENS = ["c_bg", "c_panel", "c_subtle", "c_gold_dark"]

METRIC_KEYS = [
    ("wcag21",          "WCAG 2.1"),
    ("apca_lc",         "APCA Lc"),
    ("delta_e",         "ΔE (OKLAB)"),
    ("luminance_ratio", "Lum Ratio"),
    ("chroma_distance", "Chroma Δ"),
    ("hue_distance",    "Hue Δ (°)"),
]


def _mono(text: str, size: int = 9, color: str = C_GOLD_DIM) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-family: 'Share Tech Mono', monospace; font-size: {size}px; "
        f"color: {color}; background: transparent; letter-spacing: 0.5px;"
    )
    return lbl


def _badge(text: str, passed: bool) -> QLabel:
    lbl = QLabel(text)
    bg  = C_PASS if passed else C_FAIL
    fg  = C_PASS_T if passed else C_FAIL_T
    lbl.setStyleSheet(
        f"font-family: 'Share Tech Mono', monospace; font-size: 8px; "
        f"font-weight: bold; padding: 3px 7px; background: {bg}; color: {fg}; "
        f"border: 1px solid {bg};"
    )
    lbl.setFixedWidth(42)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lbl


# ── Parium Colorum panel ─────────────────────────────────────────────────

class PariumColorum(QWidget):
    """Single FG/BG pair display with headline WCAG and five secondary metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fg_key = "c_gold"
        self._bg_key = "c_bg"
        self._palette: dict[str, str] = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Selectors
        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)
        sel_row.addWidget(_mono("FG", size=8))

        self._fg_combo = QComboBox()
        for k in FG_TOKENS:
            self._fg_combo.addItem(k)
        self._fg_combo.setFixedWidth(130)
        self._fg_combo.currentTextChanged.connect(self._refresh)
        sel_row.addWidget(self._fg_combo)

        sel_row.addSpacing(16)
        sel_row.addWidget(_mono("BG", size=8))

        self._bg_combo = QComboBox()
        for k in BG_TOKENS:
            self._bg_combo.addItem(k)
        self._bg_combo.setFixedWidth(130)
        self._bg_combo.currentTextChanged.connect(self._refresh)
        sel_row.addWidget(self._bg_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # Pair display
        pair_frame = QFrame()
        pair_frame.setStyleSheet(
            f"border: 1px solid {C_GOLD_DARK}; background: transparent;"
        )
        pair_layout = QHBoxLayout(pair_frame)
        pair_layout.setContentsMargins(0, 0, 0, 0)
        pair_layout.setSpacing(0)

        # FG half
        self._fg_half = QWidget()
        self._fg_half.setMinimumHeight(90)
        fg_layout = QVBoxLayout(self._fg_half)
        fg_layout.setContentsMargins(12, 10, 12, 10)
        self._fg_role_lbl = _mono("FG", size=7, color=C_GOLD_DIM)
        self._fg_hex_lbl  = _mono("#000000", size=12, color=C_GOLD)
        fg_layout.addWidget(self._fg_role_lbl)
        fg_layout.addStretch()
        fg_layout.addWidget(self._fg_hex_lbl)

        # BG half
        self._bg_half = QWidget()
        self._bg_half.setMinimumHeight(90)
        bg_layout = QVBoxLayout(self._bg_half)
        bg_layout.setContentsMargins(12, 10, 12, 10)
        self._bg_role_lbl = _mono("BG", size=7, color=C_GOLD_DIM)
        self._bg_hex_lbl  = _mono("#000000", size=12, color=C_GOLD)
        bg_layout.addWidget(self._bg_role_lbl)
        bg_layout.addStretch()
        bg_layout.addWidget(self._bg_hex_lbl)

        pair_layout.addWidget(self._fg_half, stretch=1)
        pair_layout.addWidget(self._bg_half, stretch=1)
        layout.addWidget(pair_frame)

        # Score block: headline WCAG
        score_frame = QFrame()
        score_frame.setStyleSheet(
            f"background: {C_OBSIDIAN}; border: 1px solid {C_GOLD_DARK};"
        )
        score_layout = QHBoxLayout(score_frame)
        score_layout.setContentsMargins(14, 12, 14, 12)
        score_layout.setSpacing(14)

        self._big_score = QLabel("—")
        self._big_score.setStyleSheet(
            f"font-family: 'Cinzel', 'Georgia', serif; font-size: 32px; "
            f"font-weight: 900; color: {C_GOLD}; background: transparent; "
            f"line-height: 1;"
        )
        score_layout.addWidget(self._big_score)

        # Secondary metrics column
        self._metrics_col = QVBoxLayout()
        self._metrics_col.setSpacing(2)
        self._metric_labels: dict[str, QLabel] = {}
        for key, label in METRIC_KEYS[1:]:
            lbl = _mono(f"{label}: —", size=9, color=C_GOLD_DIM)
            self._metrics_col.addWidget(lbl)
            self._metric_labels[key] = lbl
        score_layout.addLayout(self._metrics_col, stretch=1)

        # Badges
        badge_col = QVBoxLayout()
        badge_col.setSpacing(4)
        self._aa_badge  = _badge("AA",  False)
        self._aaa_badge = _badge("AAA", False)
        badge_col.addWidget(self._aa_badge)
        badge_col.addWidget(self._aaa_badge)
        badge_col.addStretch()
        score_layout.addLayout(badge_col)

        layout.addWidget(score_frame)
        layout.addStretch()

    def set_palette(self, palette: dict[str, str]) -> None:
        self._palette = palette
        self._refresh()

    def _refresh(self) -> None:
        if not self._palette:
            return
        fg_key = self._fg_combo.currentText()
        bg_key = self._bg_combo.currentText()
        fg_hex = self._palette.get(fg_key, "#ffffff")
        bg_hex = self._palette.get(bg_key, "#000000")

        # Update pair display colours
        self._fg_half.setStyleSheet(f"background: {fg_hex};")
        self._bg_half.setStyleSheet(f"background: {bg_hex};")
        self._fg_hex_lbl.setText(fg_hex)
        self._bg_hex_lbl.setText(bg_hex)
        self._fg_role_lbl.setText(fg_key)
        self._bg_role_lbl.setText(bg_key)

        scores = score_pair(fg_hex, bg_hex)
        self._big_score.setText(f"{scores['wcag21']:.1f}:1")

        self._metric_labels["apca_lc"].setText(
            f"APCA Lc: {scores['apca_lc']:.1f}{'  ✓' if scores['apca_pass'] else '  ✗'}"
        )
        self._metric_labels["delta_e"].setText(
            f"ΔE (OKLAB): {scores['delta_e']:.1f}"
        )
        self._metric_labels["luminance_ratio"].setText(
            f"Lum Ratio: {scores['luminance_ratio']:.2f}"
        )
        self._metric_labels["chroma_distance"].setText(
            f"Chroma Δ: {scores['chroma_distance']:.4f}"
        )
        self._metric_labels["hue_distance"].setText(
            f"Hue Δ: {scores['hue_distance']:.1f}°"
        )

        self._aa_badge  = self._refresh_badge(self._aa_badge,  "AA",  scores["wcag21_aa"])
        self._aaa_badge = self._refresh_badge(self._aaa_badge, "AAA", scores["wcag21_aaa"])

    def _refresh_badge(self, old: QLabel, text: str, passed: bool) -> QLabel:
        bg = C_PASS if passed else C_FAIL
        fg = C_PASS_T if passed else C_FAIL_T
        old.setStyleSheet(
            f"font-family: 'Share Tech Mono', monospace; font-size: 8px; "
            f"font-weight: bold; padding: 3px 7px; background: {bg}; "
            f"color: {fg}; border: 1px solid {bg};"
        )
        return old


# ── Contrast Matrix ──────────────────────────────────────────────────────

class ContrastMatrix(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette: dict[str, str] = {}
        self._metric_key = "wcag21"
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        micro = _mono("CONTRAST MATRIX", size=8, color=C_GOLD_DIM)
        micro.setStyleSheet(micro.styleSheet() + " letter-spacing: 3px; text-transform: uppercase;")
        layout.addWidget(micro)

        self._table = QTableWidget()
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._table.setShowGrid(True)
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {C_VOID}; color: {C_GOLD_DIM}; "
            f"border: 1px solid {C_GOLD_DARK}; gridline-color: {C_GOLD_DARK}; "
            f"font-family: 'Share Tech Mono', monospace; font-size: 9px; }}"
            f"QHeaderView::section {{ background: {C_OBSIDIAN}; color: {C_GOLD}; "
            f"border: 1px solid {C_GOLD_DARK}; font-family: 'Share Tech Mono', monospace; "
            f"font-size: 7px; letter-spacing: 1px; padding: 4px 8px; font-weight: normal; }}"
            f"QTableWidget::item {{ padding: 4px 9px; text-align: center; }}"
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self._table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self._table, stretch=1)

    def set_palette(self, palette: dict[str, str]) -> None:
        self._palette = palette
        self._refresh()

    def set_metric(self, metric_key: str) -> None:
        self._metric_key = metric_key
        self._refresh()

    def _refresh(self) -> None:
        if not self._palette:
            return
        matrix = score_matrix(self._palette)
        fg_keys = [k for k in FG_TOKENS if k in self._palette]
        bg_keys = [k for k in BG_TOKENS if k in self._palette]

        self._table.setRowCount(len(fg_keys))
        self._table.setColumnCount(len(bg_keys) + 1)  # +1 for row header

        headers = ["FG \\ BG"] + bg_keys
        self._table.setHorizontalHeaderLabels(headers)
        self._table.verticalHeader().setVisible(False)

        for r, fg in enumerate(fg_keys):
            # Row label cell
            label_item = QTableWidgetItem(fg)
            label_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label_item.setForeground(QBrush(QColor(C_PARCHMENT)))
            font = label_item.font()
            font.setFamily("IM Fell English")
            font.setPointSize(9)
            font.setItalic(True)
            label_item.setFont(font)
            label_item.setBackground(QBrush(QColor(C_OBSIDIAN)))
            self._table.setItem(r, 0, label_item)

            for c, bg in enumerate(bg_keys):
                scores = matrix.get((fg, bg))
                if scores is None:
                    item = QTableWidgetItem("—")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self._table.setItem(r, c + 1, item)
                    continue

                val = scores.get(self._metric_key, 0.0)
                val_str = f"{val:.1f}"

                # Determine pass/fail for colouring
                passed: bool | None = None
                if self._metric_key == "wcag21":
                    passed = scores.get("wcag21_aa", False)
                elif self._metric_key == "apca_lc":
                    passed = scores.get("apca_pass", False)

                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                tooltip_lines = [
                    f"FG: {fg}  ({self._palette.get(fg, '?')})",
                    f"BG: {bg}  ({self._palette.get(bg, '?')})",
                    f"─────────────────",
                ]
                for k, label in METRIC_KEYS:
                    v = scores.get(k, 0.0)
                    tooltip_lines.append(f"{label}: {v}")
                item.setToolTip("\n".join(tooltip_lines))

                if passed is True:
                    item.setForeground(QBrush(QColor(C_PASS_T)))
                    item.setBackground(QBrush(QColor(C_PASS)))
                elif passed is False:
                    item.setForeground(QBrush(QColor(C_FAIL_T)))
                    item.setBackground(QBrush(QColor(C_FAIL)))

                self._table.setItem(r, c + 1, item)


# ── SCRUTINIUM main widget ────────────────────────────────────────────────

class ScrutiniumFeature(QWidget):
    status_message = pyqtSignal(str, str)
    export_requested = pyqtSignal(dict)  # scores dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette: dict[str, str] = {}
        self._active_metric = "wcag21"
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {C_GOLD_DARK}; width: 1px; }}"
        )

        self._parium = PariumColorum()
        splitter.addWidget(self._parium)

        self._matrix = ContrastMatrix()
        splitter.addWidget(self._matrix)

        splitter.setSizes([340, 600])
        layout.addWidget(splitter, stretch=1)

    def set_palette(self, palette: dict[str, str]) -> None:
        self._palette = palette
        self._parium.set_palette(palette)
        self._matrix.set_palette(palette)
        self.status_message.emit("Scrutinium — palette loaded.", f"Scrutinium")

    def set_metric(self, metric_key: str) -> None:
        self._active_metric = metric_key
        self._matrix.set_metric(metric_key)

    def get_fascia_buttons(self, mode: str = "LAT") -> list[QWidget]:
        from AuctoritasSpectralis.shell import FasciaButton

        self._metric_combo = QComboBox()
        for key, label in METRIC_KEYS:
            self._metric_combo.addItem(label, key)
        self._metric_combo.setFixedWidth(140)
        self._metric_combo.currentIndexChanged.connect(
            lambda: self.set_metric(self._metric_combo.currentData())
        )
        self._fascia_export_btn = FasciaButton(t("btn.export_report", mode), "normal")
        self._fascia_export_btn.clicked.connect(lambda: self.export_requested.emit(self._palette))

        return [self._metric_combo, self._fascia_export_btn]

    def set_mode(self, mode: str) -> None:
        if hasattr(self, "_fascia_export_btn"):
            self._fascia_export_btn.setText(t("btn.export_report", mode))
