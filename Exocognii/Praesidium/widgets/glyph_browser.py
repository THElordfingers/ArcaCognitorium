#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/glyph_browser.py                                       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/glyph_browser.py
# Local glyph sheet browser. Load JSON glyph sets, click to copy.
# Also reads from Glyptorum Storage/ if available.
# version: 1.0.0

import json
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QWidget, QComboBox, QLineEdit,
    QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL,
    arcane_button, micro_label,
)

GLYPTORUM_STORAGE = Path.home() / "ArcaCognitorium" / "tools" / "Glyptorum" / "Storage" / "Glyph-Sets"
COLS = 8   # glyphs per row in grid


class GlyphBrowser(ArcaneWidget):
    """
    Glyph sheet browser.
    - Loads JSON glyph set files (Glyptorum format or simple list)
    - Click any glyph to copy to clipboard
    - Filter by search
    - Load custom sheets or pick from Glyptorum storage
    """

    glyph_copied = pyqtSignal(str)   # the glyph character

    def __init__(self, widget_id: str, configuus=None, parent=None):
        super().__init__(widget_id, "Glyph Browser", parent)
        self._cfg          = configuus
        self._current_set: list[dict] = []   # [{glyph, name}]
        self._filtered:    list[dict] = []
        self._build_body()
        self._discover_sheets()
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Sheet selector row
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        row1.addWidget(micro_label("sheet"))

        self._sheet_combo = QComboBox()
        self._sheet_combo.setStyleSheet(
            f"QComboBox {{ background: {C_BG}; color: {C_GOLD};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 2px 6px; }}"
            f"QComboBox QAbstractItemView {{"
            f"  background: {C_PANEL}; color: {C_TEXT};"
            f"  selection-background-color: {C_GOLD_DARK}; }}"
        )
        self._sheet_combo.currentIndexChanged.connect(self._on_sheet_changed)
        row1.addWidget(self._sheet_combo, 1)

        btn_reload = arcane_button("↺")
        btn_reload.setFixedHeight(22)
        btn_reload.clicked.connect(self._discover_sheets)
        row1.addWidget(btn_reload)
        L.addLayout(row1)

        # Search / filter
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter glyphs…")
        self._search.setStyleSheet(
            f"QLineEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 3px 6px; }}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._search.textChanged.connect(self._apply_filter)
        L.addWidget(self._search)

        # Copy indicator
        self._copy_lbl = QLabel("")
        self._copy_lbl.setStyleSheet(
            f"color: {C_TEAL}; font-family: Georgia, serif; font-size: 10px;"
        )
        L.addWidget(self._copy_lbl)

        L.addWidget(self._sep())

        # Glyph grid scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet(f"background: {C_BG};")
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll.setWidget(self._grid_widget)
        L.addWidget(self._scroll, 1)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Sheet discovery
    # ------------------------------------------------------------------

    def _discover_sheets(self) -> None:
        self._sheet_combo.blockSignals(True)
        self._sheet_combo.clear()
        self._sheet_paths: dict[str, Path] = {}

        # Glyptorum storage
        if GLYPTORUM_STORAGE.exists():
            for p in sorted(GLYPTORUM_STORAGE.glob("*.json")):
                name = p.stem
                self._sheet_combo.addItem(f"⚗ {name}")
                self._sheet_paths[f"⚗ {name}"] = p

        # Custom local sheets (beside this widget's storage)
        local_dir = Path.home() / ".arca" / "glyph-sheets"
        if local_dir.exists():
            for p in sorted(local_dir.glob("*.json")):
                name = p.stem
                key  = f"✦ {name}"
                self._sheet_combo.addItem(key)
                self._sheet_paths[key] = p

        self._sheet_combo.blockSignals(False)

        count = self._sheet_combo.count()
        if count > 0:
            self._on_sheet_changed(0)
            self.set_status("ok", f"{count} sheet(s)")
        else:
            self._load_fallback()
            self.set_status("idle", "No sheets found — showing built-in")

    def _on_sheet_changed(self, idx: int) -> None:
        key = self._sheet_combo.currentText()
        path = self._sheet_paths.get(key)
        if path:
            self._load_sheet(path)

    def _load_sheet(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            self.set_status("error", str(e)[:60])
            return

        glyphs = []
        # Glyptorum format: {"glyphs": [{"char": "⚗", "name": "alembic"}, ...]}
        # Simple format: ["⚗", "⛨", ...] or {"glyphs": ["⚗", ...]}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    glyphs.append({"glyph": item, "name": item})
                elif isinstance(item, dict):
                    glyphs.append({
                        "glyph": item.get("char") or item.get("glyph", "?"),
                        "name":  item.get("name", ""),
                    })
        elif isinstance(data, dict):
            raw = data.get("glyphs", [])
            for item in raw:
                if isinstance(item, str):
                    glyphs.append({"glyph": item, "name": item})
                elif isinstance(item, dict):
                    glyphs.append({
                        "glyph": item.get("char") or item.get("glyph", "?"),
                        "name":  item.get("name", ""),
                    })

        self._current_set = glyphs
        self._apply_filter(self._search.text())
        self.set_status("ok", f"{len(glyphs)} glyphs")

    def _load_fallback(self) -> None:
        """Built-in set of useful Unicode/Nerd Font symbols."""
        fallback = [
            "⚗","⛨","✦","✕","⊞","⊟","⊙","◈","⎇","⬆","⬇","↺","☐","☑",
            "●","○","◉","▲","▼","◀","▶","★","☆","♦","♠","♣","♥",
            "═","║","╔","╗","╚","╝","╠","╣","╦","╩","╬",
            "🮃","🮈","🭅","🭐","█","▓","▒","░",
            "α","β","γ","δ","ε","π","σ","Ω","∞","∑","∫","√","≈","≠","≤","≥",
        ]
        self._current_set = [{"glyph": g, "name": g} for g in fallback]
        self._apply_filter("")

    # ------------------------------------------------------------------
    # Filter + render
    # ------------------------------------------------------------------

    def _apply_filter(self, query: str) -> None:
        q = query.strip().lower()
        if q:
            self._filtered = [
                g for g in self._current_set
                if q in g["name"].lower() or q in g["glyph"]
            ]
        else:
            self._filtered = list(self._current_set)
        self._render_grid()

    def _render_grid(self) -> None:
        # Clear grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        font = QFont("excalib-nf", 14)

        for i, entry in enumerate(self._filtered):
            glyph = entry["glyph"]
            name  = entry.get("name", glyph)
            btn   = GlyphButton(glyph, name, font)
            btn.clicked_glyph.connect(self._on_glyph_click)
            self._grid_layout.addWidget(btn, i // COLS, i % COLS)

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def _on_glyph_click(self, glyph: str, name: str) -> None:
        # xclip first, Qt clipboard fallback
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=glyph, text=True, timeout=3,
            )
        except Exception:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(glyph)

        self._copy_lbl.setText(f"✦  copied: {glyph}  {name}")
        self.glyph_copied.emit(glyph)
        self.set_status("ok", f"copied: {glyph}")

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self._copy_lbl.setText(""))


class GlyphButton(QLabel):
    """Single clickable glyph cell."""

    clicked_glyph = pyqtSignal(str, str)

    def __init__(self, glyph: str, name: str, font: QFont, parent=None):
        super().__init__(glyph, parent)
        self._glyph = glyph
        self._name  = name
        self.setFont(font)
        self.setFixedSize(32, 32)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(False)

    def _apply_style(self, hover: bool) -> None:
        bg = "#1a1a2a" if hover else C_BG
        self.setStyleSheet(
            f"QLabel {{ color: {C_GOLD}; background: {bg};"
            f"  border: 1px solid {'#3a2e10' if hover else 'transparent'};"
            f"  border-radius: 2px; font-size: 14px; }}"
        )

    def enterEvent(self, event) -> None:
        self._apply_style(True)

    def leaveEvent(self, event) -> None:
        self._apply_style(False)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_glyph.emit(self._glyph, self._name)
