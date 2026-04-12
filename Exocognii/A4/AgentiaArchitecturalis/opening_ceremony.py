"""
Opening Ceremony — Propositio Caerimoniae Apertivae.

6-act QWidget overlay:
  Act I   — Salutatio (bureau declares itself)
  Act II  — Thema Inspectio (theme check)
  Act III — Armarium Census (library count)
  Act IV  — Canvases Census (saved sessions)
  Act V   — Session Restore (last session if any)
  Act VI  — Commissio (final flourish, hand-off to Wizard)

Any keypress dismisses. Does not repeat. Full-screen Z-order above all content.
"""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor, QKeyEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from . import tokens

_STORAGE = Path(__file__).resolve().parent / "storage"
_CONFIG = _STORAGE / "config.json"

CEREMONY_TEXT = """\u2726  \u2697  \u2726

AGENTIA ARCHITECTURALIS
Architectural Alignment Enforcement Agency

\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

The bureau does not greet you.
It has been here since before you arrived.

The canvas is empty.
It has been empty before. It will not remain so.

You are the Wizard. This is your instrument.
What you arrange here, the Cogniverse will remember.

Nothing built here is lost.
Nothing sealed here is forgotten.
Nothing exported here is a draft.

Begin when you are ready.
The bureau awaits alignment.

\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

In Linea \u00b7 In Parallelo \u00b7 In Perpetuum

\u2593\u2592\u2591 INITIALISING SCRIPTORIUM CANVAS \u2591\u2592\u2593 \u00b7 \u00b7 \u00b7"""


class OpeningCeremony(QWidget):
    """Full-screen opening ceremony overlay."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("openingCeremony")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"background: {tokens.C_BG};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)

        # Ceremony text
        self._text = QLabel(CEREMONY_TEXT)
        self._text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text.setWordWrap(True)
        self._text.setStyleSheet(
            f"color: {tokens.C_TEXT}; "
            f"font-family: {tokens.FONT_SERIF}; "
            f"font-size: 13px; line-height: 1.8; "
            f"max-width: 560px;"
        )
        layout.addWidget(self._text)

        # Scan line
        self._scan = QLabel("\u2593\u2592\u2591 INITIALISING SCRIPTORIUM CANVAS \u2591\u2592\u2593 \u00b7 \u00b7 \u00b7")
        self._scan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scan.setStyleSheet(
            f"font-family: {tokens.FONT_MONO}; font-size: 8px; "
            f"color: {tokens.C_GOLD_DARK}; letter-spacing: 2px; margin-top: 6px;"
        )
        layout.addWidget(self._scan)

        # Auto-dismiss after 4 seconds
        QTimer.singleShot(4000, self._dismiss)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Any keypress dismisses."""
        self._dismiss()

    def mousePressEvent(self, event) -> None:
        """Click also dismisses."""
        self._dismiss()

    def _dismiss(self) -> None:
        if self.isVisible():
            self.hide()
            self.deleteLater()
            self._mark_shown()

    def _mark_shown(self) -> None:
        """Record that ceremony has been shown — does not repeat."""
        _STORAGE.mkdir(parents=True, exist_ok=True)
        try:
            cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            cfg = {}
        cfg["ceremony_shown"] = True
        _CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    @staticmethod
    def should_show() -> bool:
        """Check if ceremony should be displayed."""
        try:
            cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
            return not cfg.get("ceremony_shown", False)
        except (FileNotFoundError, json.JSONDecodeError):
            return True
