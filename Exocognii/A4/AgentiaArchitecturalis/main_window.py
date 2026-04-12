"""
A4 Common Shell — Main Window

Four ratified zones:
  Zone I   — Titulum (220px, fixed)
  Zone II  — Feature Codex (220px, scrollable)
  Zone III — Fascia (52px, feature-keyed)
  Zone IV  — Scriptorium Canvas (full remainder)

Feature switching is an instant stack swap — no animation.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QStatusBar, QSplitter,
)

from . import tokens
from .titulum import Titulum
from .feature_codex import FeatureCodex
from .fascia import Fascia
from .theme_manager import ThemeManager

_STORAGE = Path(__file__).resolve().parent / "storage"

# Feature index mapping (order matters for QStackedWidget)
FEATURE_INDEX = {
    "tabula": 0,
    "armarium": 1,
    "specularium": 2,
    "codex": 3,
    "thema": 4,
    "auxilium": 5,
}


class MainWindow(QMainWindow):
    """A4 Common Shell for Bureau II."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("\u2726 Agentia Architecturalis \u2726")
        self.setMinimumSize(1024, 700)

        self.theme_manager = ThemeManager()
        self._active_feature = "tabula"
        self._previous_feature = "tabula"

        # Ensure storage exists
        _STORAGE.mkdir(parents=True, exist_ok=True)
        (_STORAGE / "canvases").mkdir(exist_ok=True)

        self._build_shell()
        self._wire_signals()
        self._apply_theme()

        # Default state
        self.feature_codex.set_active("tabula")
        self.fascia.switch_to("tabula")

    def _build_shell(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Horizontal splitter: left column | right column ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {tokens.C_GOLD_DARK}; }}"
        )

        # ── Left column: Zone I + Zone II ──
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.titulum = Titulum()
        self.feature_codex = FeatureCodex()

        left_layout.addWidget(self.titulum)
        left_layout.addWidget(self.feature_codex, 1)
        left_col.setMinimumWidth(180)
        left_col.setMaximumWidth(360)
        splitter.addWidget(left_col)

        # ── Right column: Zone III + Zone IV ──
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.fascia = Fascia()
        right_layout.addWidget(self.fascia)

        # Zone IV: Scriptorium Canvas (stacked feature pages)
        self.scriptorium = QStackedWidget()
        self.scriptorium.setObjectName("scriptorium")

        # Placeholder pages — replaced by real features in later sessions
        self._feature_pages: dict[str, QWidget] = {}
        for key, idx in FEATURE_INDEX.items():
            page = self._make_placeholder(key)
            self._feature_pages[key] = page
            self.scriptorium.addWidget(page)

        right_layout.addWidget(self.scriptorium, 1)

        # Status bar
        self._status_bar = QStatusBar()
        self._status_bar.setFixedHeight(26)
        self._status_bar.setStyleSheet(
            f"QStatusBar {{ background: {tokens.C_PANEL}; "
            f"border-top: 1px solid {tokens.C_GOLD_DARK}; "
            f"font-size: 8.5px; color: {tokens.C_GOLD_DIM}; "
            f"font-family: {tokens.FONT_MONO}; letter-spacing: 0.5px; }}"
        )
        self._status_left = QLabel("\u2699 Agentia Architecturalis awaits alignment.")
        self._status_left.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8.5px;")
        self._status_right = QLabel("")
        self._status_right.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-size: 8.5px;")
        self._status_bar.addWidget(self._status_left, 1)
        self._status_bar.addPermanentWidget(self._status_right)
        right_layout.addWidget(self._status_bar)

        splitter.addWidget(right_col)
        splitter.setStretchFactor(0, 0)  # left col: no stretch
        splitter.setStretchFactor(1, 1)  # right col: takes remainder
        splitter.setSizes([220, 800])    # default 220px left
        root.addWidget(splitter, 1)

    def _make_placeholder(self, key: str) -> QWidget:
        """Create a placeholder page for a feature not yet built."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.setStyleSheet(f"background: {tokens.C_BG};")

        icon = QLabel("\u229e")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size: 24px; color: {tokens.C_GOLD}; opacity: 0.3;")
        layout.addWidget(icon)

        label_text = key.replace("_", " ").upper()
        label = QLabel(f"Scriptorium Canvas\n{label_text} Active")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"font-size: 8px; letter-spacing: 3px; color: {tokens.C_GOLD_DIM}; "
            f"text-transform: uppercase;"
        )
        layout.addWidget(label)

        zone_lbl = QLabel("ZONE IV \u00b7 SCRIPTORIUM CANVAS")
        zone_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        zone_lbl.setStyleSheet(
            f"font-size: 7px; letter-spacing: 2px; color: rgba(122,106,42,0.3); "
            f"font-family: {tokens.FONT_MONO};"
        )
        layout.addWidget(zone_lbl)

        return page

    def _wire_signals(self) -> None:
        self.feature_codex.feature_selected.connect(self._on_feature_selected)
        self.fascia.help_requested.connect(lambda: self._on_feature_selected("auxilium"))
        self.fascia.help_dismiss.connect(lambda: self._on_feature_selected(self._previous_feature))
        self.theme_manager.theme_reloaded.connect(lambda _: self._apply_theme())

    def _on_feature_selected(self, key: str) -> None:
        if key != "auxilium":
            self._previous_feature = self._active_feature
        self._active_feature = key
        idx = FEATURE_INDEX.get(key, 0)
        self.scriptorium.setCurrentIndex(idx)
        self.fascia.switch_to(key)
        self.feature_codex.set_active(key)

    def _apply_theme(self) -> None:
        qss = self.theme_manager.build_qss()
        app = self.window()
        if app:
            from PyQt6.QtWidgets import QApplication
            qapp = QApplication.instance()
            if qapp:
                qapp.setStyleSheet(qss)
        self.titulum.set_theme_name(self.theme_manager.theme_name)

    def set_feature_page(self, key: str, widget: QWidget) -> None:
        """Replace a placeholder with a real feature page."""
        idx = FEATURE_INDEX.get(key)
        if idx is None:
            return
        old = self.scriptorium.widget(idx)
        self.scriptorium.removeWidget(old)
        old.deleteLater()
        self.scriptorium.insertWidget(idx, widget)
        self._feature_pages[key] = widget

    def set_status(self, left: str = "", right: str = "") -> None:
        if left:
            self._status_left.setText(left)
        if right:
            self._status_right.setText(right)
