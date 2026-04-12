"""
AUCTORITAS SPECTRALIS — v1.0.0
ceremony/inductio.py — Inductio Chromatica

The first-launch opening ceremony. Runs exactly once.
Controlled by the inductio_completed flag in user config.

Sequence (~8 seconds total):
  - Canvas dark
  - Titulum lines fade in: title → subtitle → motto
    (each from opacity 0 → 1 over 600ms, 600ms gap between)
  - Feature Codex items light up top-to-bottom
    (400ms intervals, Aurum Nox → Aurum Dimmus → Aurum)
  - Canvas populates COLORES feature
  - Default palette silently derived
  - Token rows appear with 60ms stagger top-to-bottom
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    QObject, QTimer, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup,
    pyqtSignal, Qt
)

import AuctoritasSpectralis.config as cfg


C_VOID      = "#050507"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"


class InductioDirector(QObject):
    """
    Orchestrates the Inductio Chromatica ceremony.
    Emits signals at ceremony milestones for the shell to act on.
    """

    # Emitted when the ceremony is fully complete
    ceremony_complete = pyqtSignal()

    # Emitted to trigger each Codex item lighting up (0-indexed)
    codex_light = pyqtSignal(int)

    # Emitted to trigger COLORES canvas population
    show_canvas = pyqtSignal()

    # Emitted to stagger each token row (0-indexed)
    token_appear = pyqtSignal(int)

    def __init__(self, titulum_labels: list[QLabel], parent=None):
        super().__init__(parent)
        self._titulum_labels = titulum_labels
        self._timers: list[QTimer] = []

    def begin(self) -> None:
        """Start the ceremony sequence."""
        # Phase 1: fade in Titulum lines
        # Each line: 600ms fade, 600ms gap after
        offsets_ms = [0, 1200, 2400]  # start time of each line fade
        for i, lbl in enumerate(self._titulum_labels[:3]):
            self._fade_in_label(lbl, delay_ms=offsets_ms[i], duration_ms=600)

        # Phase 2: Codex items light up (starts after Titulum phase ~3600ms)
        codex_start = 3600
        for i in range(5):
            t = QTimer(self)
            t.setSingleShot(True)
            t.timeout.connect(lambda idx=i: self.codex_light.emit(idx))
            t.start(codex_start + i * 400)
            self._timers.append(t)

        # Phase 3: show canvas (after Codex ~5600ms)
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(self.show_canvas)
        t.start(5600)
        self._timers.append(t)

        # Phase 4: token stagger (starts ~6000ms, 60ms per row, 10 rows)
        token_start = 6000
        for i in range(10):
            t = QTimer(self)
            t.setSingleShot(True)
            t.timeout.connect(lambda idx=i: self.token_appear.emit(idx))
            t.start(token_start + i * 60)
            self._timers.append(t)

        # Phase 5: complete (~7200ms)
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(self._on_complete)
        t.start(7800)
        self._timers.append(t)

    def _fade_in_label(self, label: QLabel, delay_ms: int, duration_ms: int) -> None:
        effect = QGraphicsOpacityEffect(label)
        effect.setOpacity(0.0)
        label.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration_ms)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        def _start():
            anim.start()

        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(_start)
        t.start(delay_ms)
        self._timers.append(t)
        # Keep anim alive
        self._timers.append(anim)  # type: ignore[arg-type]

    def _on_complete(self) -> None:
        cfg.mark_inductio_complete()
        self.ceremony_complete.emit()
