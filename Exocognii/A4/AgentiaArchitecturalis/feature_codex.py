"""
Zone II — Feature Codex (220px, scrollable)

Left rail navigation. Six features. Instant QStackedWidget swap — no animation.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
)

from . import tokens


FEATURES = [
    ("tabula",       "\u25C8  Tabula",          "Tabula Designandi"),
    ("armarium",     "\u25C8  Armarium",         "Armarium Componentium"),
    ("specularium",  "\u25C8  Specularium",      "Specularium Vivum"),
    ("codex",        "\u25C8  Codex Exportum",   "Codex Exportum"),
    ("thema",        "\u25C8  Thema",            "Thema"),
]

UTILITY_FEATURES = [
    ("auxilium",     "\u25CE  Auxilium",          "Auxilium"),
]


class _CodexItem(QLabel):
    """A clickable item in the Feature Codex."""

    clicked = pyqtSignal()

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False
        self._refresh_style()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value
        self._refresh_style()

    def _refresh_style(self) -> None:
        if self._active:
            self.setStyleSheet(
                f"padding: 7px 14px; font-size: 10px; letter-spacing: 1px; "
                f"color: {tokens.C_GOLD}; "
                f"border-left: 2px solid {tokens.C_GOLD}; "
                f"background: rgba(212,175,55,0.06);"
            )
        else:
            self.setStyleSheet(
                f"padding: 7px 14px; font-size: 10px; letter-spacing: 1px; "
                f"color: {tokens.C_GOLD_DIM}; "
                f"border-left: 2px solid transparent; "
                f"background: transparent;"
            )

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        if not self._active:
            self.setStyleSheet(
                f"padding: 7px 14px; font-size: 10px; letter-spacing: 1px; "
                f"color: {tokens.C_TEXT}; "
                f"border-left: 2px solid transparent; "
                f"background: rgba(212,175,55,0.03);"
            )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._refresh_style()
        super().leaveEvent(event)


class FeatureCodex(QFrame):
    """Zone II: left rail feature navigation."""

    feature_selected = pyqtSignal(str)  # emits feature key

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setObjectName("featureCodex")
        self._items: dict[str, _CodexItem] = {}
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(0)

        # Header
        head = QLabel("Feature Codex")
        head.setStyleSheet(
            f"font-size: 7px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase; padding: 0 14px 6px; "
            f"border-bottom: 1px solid {tokens.C_GOLD_DARK};"
        )
        layout.addWidget(head)

        # Main features
        for key, label, _desc in FEATURES:
            item = _CodexItem(label)
            item.clicked.connect(lambda k=key: self._on_select(k))
            layout.addWidget(item)
            self._items[key] = item

        # Separator
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {tokens.C_GOLD_DARK}; margin: 5px 14px;")
        layout.addWidget(rule)

        # Utility features
        for key, label, _desc in UTILITY_FEATURES:
            item = _CodexItem(label)
            item.clicked.connect(lambda k=key: self._on_select(k))
            layout.addWidget(item)
            self._items[key] = item

        layout.addStretch()

        # Zone label
        zone_lbl = QLabel("ZONE II \u00b7 FEATURE CODEX")
        zone_lbl.setStyleSheet(
            f"padding: 6px 14px; font-size: 7px; letter-spacing: 2px; "
            f"color: rgba(122,106,42,0.4); font-family: {tokens.FONT_MONO}; "
            f"border-top: 1px solid #1a1408;"
        )
        layout.addWidget(zone_lbl)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"FeatureCodex {{ background: {tokens.C_PANEL}; "
            f"border-right: 1px solid {tokens.C_GOLD_DARK}; }}"
        )

    def _on_select(self, key: str) -> None:
        for k, item in self._items.items():
            item.active = (k == key)
        self.feature_selected.emit(key)

    def set_active(self, key: str) -> None:
        """Programmatically set the active feature."""
        for k, item in self._items.items():
            item.active = (k == key)
