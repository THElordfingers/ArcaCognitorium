"""
Zone I — Titulum (220px fixed)

Bureau identity, live context display, LAT/EN toggle, dirty state ring ◌.
"""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)

from . import tokens

_STORAGE = Path(__file__).resolve().parent / "storage"
_CONFIG  = _STORAGE / "config.json"

DIRTY_RING = "\u25CC"  # ◌ — ratified dirty state indicator


class Titulum(QFrame):
    """Zone I: Bureau identity panel, 220px fixed width."""

    lang_changed = pyqtSignal(str)  # "lat" or "en"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setObjectName("titulum")
        self._lang = self._load_lang()
        self._canvas_name = ""
        self._theme_name = "Nox Aurum"
        self._dirty = False
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 12)
        layout.setSpacing(3)

        # Overline
        overline = QLabel("Triumviratus · Bureau II")
        overline.setObjectName("zt-overline")
        overline.setStyleSheet(
            f"font-size: 7px; letter-spacing: 3px; text-transform: uppercase; "
            f"color: {tokens.C_GOLD_DIM};"
        )
        layout.addWidget(overline)

        # Title
        title = QLabel("\u2726 AGENTIA\nARCHITECTURALIS \u2726")
        title.setObjectName("zt-title")
        title.setStyleSheet(
            f"font-size: 12px; color: {tokens.C_GOLD}; "
            f"letter-spacing: 1px; font-weight: bold; line-height: 1.3;"
        )
        layout.addWidget(title)

        # English name
        en_name = QLabel("Architectural Alignment\nEnforcement Agency")
        en_name.setObjectName("zt-en")
        en_name.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; letter-spacing: 1px;"
        )
        layout.addWidget(en_name)

        # Motto
        motto = QLabel("In Linea \u00b7 In Parallelo \u00b7 In Perpetuum")
        motto.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; font-style: italic;"
        )
        layout.addWidget(motto)

        # Rule
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet(f"color: {tokens.C_GOLD_DARK}; background: {tokens.C_GOLD_DARK};")
        rule.setFixedHeight(1)
        layout.addWidget(rule)

        # Description
        desc = QLabel(
            "The sovereign bureau of component\n"
            "design. It does not build software.\n"
            "It legislates its appearance."
        )
        desc.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_TEXT}; font-style: italic;"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Live context
        self._theme_label = QLabel()
        self._canvas_label = QLabel()
        ctx = QWidget()
        ctx_layout = QVBoxLayout(ctx)
        ctx_layout.setContentsMargins(0, 5, 0, 0)
        ctx_layout.setSpacing(0)
        self._theme_label.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; letter-spacing: 0.5px;"
        )
        self._canvas_label.setStyleSheet(
            f"font-size: 8px; color: {tokens.C_GOLD_DIM}; letter-spacing: 0.5px;"
        )
        ctx_layout.addWidget(self._theme_label)
        ctx_layout.addWidget(self._canvas_label)
        layout.addWidget(ctx)
        self._update_context_labels()

        # LAT/EN toggle
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(0, 7, 0, 0)
        lang_row.setSpacing(0)

        self._btn_lat = QPushButton("LAT")
        self._btn_en = QPushButton("EN")
        for btn in (self._btn_lat, self._btn_en):
            btn.setFixedHeight(20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_lat.clicked.connect(lambda: self._set_lang("lat"))
        self._btn_en.clicked.connect(lambda: self._set_lang("en"))
        lang_row.addWidget(self._btn_lat)
        lang_row.addWidget(self._btn_en)
        lang_row.addStretch()
        layout.addLayout(lang_row)
        self._refresh_lang_buttons()

        layout.addStretch()

        # Zone label
        zone_lbl = QLabel("ZONE I \u00b7 TITULUM")
        zone_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        zone_lbl.setStyleSheet(
            f"font-size: 7px; letter-spacing: 2px; "
            f"color: rgba(122,106,42,0.5); font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(zone_lbl)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"Titulum {{ background: {tokens.C_PANEL}; "
            f"border-right: 1px solid {tokens.C_GOLD_DARK}; "
            f"border-bottom: 1px solid {tokens.C_GOLD_DARK}; }}"
        )

    def _update_context_labels(self) -> None:
        dirty_mark = f"  {DIRTY_RING}" if self._dirty else ""
        self._theme_label.setText(f"THEME  \u00b7 {self._theme_name}")
        self._canvas_label.setText(f"CANVAS \u00b7 {self._canvas_name or '(none)'}{dirty_mark}")

    def set_canvas_name(self, name: str) -> None:
        self._canvas_name = name
        self._update_context_labels()

    def set_theme_name(self, name: str) -> None:
        self._theme_name = name
        self._update_context_labels()

    def set_dirty(self, dirty: bool) -> None:
        self._dirty = dirty
        self._update_context_labels()

    def _set_lang(self, lang: str) -> None:
        self._lang = lang
        self._save_lang(lang)
        self._refresh_lang_buttons()
        self.lang_changed.emit(lang)

    def _refresh_lang_buttons(self) -> None:
        active_style = (
            f"background: {tokens.C_GOLD_DARK}; color: {tokens.C_GOLD}; "
            f"border: 1px solid {tokens.C_GOLD_DARK}; font-size: 8px; "
            f"letter-spacing: 1px; padding: 2px 7px;"
        )
        inactive_style = (
            f"background: transparent; color: {tokens.C_GOLD_DIM}; "
            f"border: 1px solid {tokens.C_GOLD_DARK}; font-size: 8px; "
            f"letter-spacing: 1px; padding: 2px 7px;"
        )
        self._btn_lat.setStyleSheet(active_style if self._lang == "lat" else inactive_style)
        self._btn_en.setStyleSheet(active_style if self._lang == "en" else inactive_style)

    def _load_lang(self) -> str:
        try:
            cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
            return cfg.get("lang", "lat")
        except (FileNotFoundError, json.JSONDecodeError):
            return "lat"

    def _save_lang(self, lang: str) -> None:
        _STORAGE.mkdir(parents=True, exist_ok=True)
        try:
            cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            cfg = {}
        cfg["lang"] = lang
        _CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
