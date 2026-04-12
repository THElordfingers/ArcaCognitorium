#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                             ui/token_gauge.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QWidget

# ModusArcanus colours
C_GOLD     = "#d4af37"
C_GOLD_DIM = "#7a6a2a"
C_CRIMSON  = "#8b1a1a"
C_PANEL    = "#0a0a12"
C_TEXT     = "#c8b88a"
C_BG       = "#050507"


class TokenGauge(QWidget):
    """
    Self-contained reusable context fill bar widget.
    Zero Arx-specific imports — can be dropped into any PyQt6 application.

    Two update paths:
        update_exact(input_tokens, output_tokens)
            Called after TOKEN_USAGE event. Resets draft estimate.
        update_draft(text)
            Called on input field textChanged. Adds heuristic estimate
            of draft tokens on top of the last exact count.

    Colour thresholds (ModusArcanus):
        < 60%  → C_GOLD    (Aurum)
        60–85% → C_GOLD_DIM (Aurum Dimmus)
        > 85%  → C_CRIMSON  (Sanguis)
    """

    def __init__(self, total: int = 200_000, parent=None) -> None:
        super().__init__(parent)
        self._current: int = 0         # exact tokens from last response
        self._total: int = max(total, 1)
        self._draft_estimate: int = 0  # heuristic from current input draft
        self.setMinimumWidth(240)
        self.setFixedHeight(32)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def update_exact(self, input_tokens: int, output_tokens: int) -> None:
        """Update with exact token counts from TOKEN_USAGE event."""
        self._current = max(0, input_tokens + output_tokens)
        self._draft_estimate = 0
        self.update()

    def update_draft(self, text: str) -> None:
        """Update draft estimate from current input field content."""
        self._draft_estimate = int(len(text.split()) * 1.3)
        self.update()

    def reset(self) -> None:
        """Reset to zero. Called on new conversation."""
        self._current = 0
        self._draft_estimate = 0
        self.update()

    def set_total(self, total: int) -> None:
        """Update the context limit (e.g. if config changes)."""
        self._total = max(total, 1)
        self.update()

    def fill_ratio(self) -> float:
        """Return current fill ratio [0.0–1.0]. Useful for threshold checks."""
        effective = self._current + self._draft_estimate
        return min(effective / self._total, 1.0)

    # -----------------------------------------------------------------------
    # Paint
    # -----------------------------------------------------------------------

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ratio  = self.fill_ratio()
        colour = self._bar_colour(ratio)
        pct    = int(ratio * 100)

        w = self.width()

        # Background
        painter.fillRect(self.rect(), QColor(C_BG))

        # "CONTEXT" label
        painter.setFont(QFont("Georgia", 9))
        painter.setPen(QColor(C_TEXT))
        painter.drawText(
            QRect(4, 0, 72, 32),
            Qt.AlignmentFlag.AlignVCenter,
            "CONTEXT",
        )

        # Bar track
        bar_x     = 80
        bar_w     = w - bar_x - 50  # leave room for percentage label
        bar_rect  = QRect(bar_x, 11, bar_w, 10)
        painter.fillRect(bar_rect, QColor(C_PANEL))

        # Bar fill
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            painter.fillRect(QRect(bar_x, 11, fill_w, 10), QColor(colour))

        # Percentage label
        painter.setFont(QFont("Georgia", 9))
        painter.setPen(QColor(colour))
        painter.drawText(
            QRect(w - 46, 0, 44, 32),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
            f"{pct}%",
        )

        painter.end()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def _bar_colour(ratio: float) -> str:
        if ratio < 0.60:
            return C_GOLD
        if ratio < 0.85:
            return C_GOLD_DIM
        return C_CRIMSON
