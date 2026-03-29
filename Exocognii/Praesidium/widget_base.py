#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widget_base.py                                                 ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widget_base.py
# ArcaneWidget — draggable, resizable, titled widget container.
# version: 1.3.0
# Changes: per-widget font size control, animated blind collapse,
#          font_size_changed signal, get/set_font_size API

from PyQt6.QtWidgets import (
    QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QWidget, QApplication,
)
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QMouseEvent, QResizeEvent, QCursor, QFont

from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_PANEL, C_BG,
    C_STATUS_OK, C_STATUS_WARN, C_STATUS_ERROR, C_STATUS_IDLE,
)

HEADER_H   = 28
MIN_W      = 180
MIN_H      = 100
EDGE_GRIP  = 6
FONT_MIN   = 8
FONT_MAX   = 18
FONT_DEF   = 11
ANIM_MS    = 180   # blind animation duration

_LEFT   = 1
_RIGHT  = 2
_TOP    = 4
_BOTTOM = 8

_CURSOR_MAP = {
    _LEFT:              Qt.CursorShape.SizeHorCursor,
    _RIGHT:             Qt.CursorShape.SizeHorCursor,
    _TOP:               Qt.CursorShape.SizeVerCursor,
    _BOTTOM:            Qt.CursorShape.SizeVerCursor,
    _LEFT  | _TOP:      Qt.CursorShape.SizeFDiagCursor,
    _RIGHT | _BOTTOM:   Qt.CursorShape.SizeFDiagCursor,
    _RIGHT | _TOP:      Qt.CursorShape.SizeBDiagCursor,
    _LEFT  | _BOTTOM:   Qt.CursorShape.SizeBDiagCursor,
}


def _hit_edges(pos: QPoint, rect: QRect, margin: int) -> int:
    edges = 0
    if pos.x() <= margin:                  edges |= _LEFT
    if pos.x() >= rect.width()  - margin:  edges |= _RIGHT
    if pos.y() <= margin:                  edges |= _TOP
    if pos.y() >= rect.height() - margin:  edges |= _BOTTOM
    return edges


class ArcaneWidget(QFrame):
    position_changed   = pyqtSignal(str, int, int)
    size_changed       = pyqtSignal(str, int, int)
    status_changed     = pyqtSignal(str, str, str)
    visibility_changed = pyqtSignal(str, bool)
    lock_changed       = pyqtSignal(str, bool)
    font_size_changed  = pyqtSignal(str, int)   # widget_id, size

    def __init__(self, widget_id: str, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.widget_id   = widget_id
        self._title      = title
        self._locked     = False
        self._font_size  = FONT_DEF
        self._minimised  = False
        self._anim: QPropertyAnimation | None = None

        self._drag_pos:          QPoint | None = None
        self._resize_edges:      int           = 0
        self._resize_origin:     QPoint | None = None
        self._resize_start_geom: QRect  | None = None

        self.setMinimumSize(MIN_W, MIN_H)
        self.setMouseTracking(True)
        self.setStyleSheet(
            f"ArcaneWidget {{ background-color: {C_PANEL}; border: 1px solid {C_GOLD_DARK}; }}"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._header = self._build_header()
        outer.addWidget(self._header)

        self._body = QFrame()
        self._body.setObjectName("body_frame")
        self._body.setStyleSheet(
            f"QFrame#body_frame {{ background: {C_BG}; border: none; }}"
        )
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(8, 8, 8, 8)
        self._body_layout.setSpacing(6)
        outer.addWidget(self._body, 1)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("header_bar")
        bar.setFixedHeight(HEADER_H)
        bar.setMouseTracking(True)
        bar.setStyleSheet(
            f"QFrame#header_bar {{"
            f"  background-color: {C_PANEL};"
            f"  border-bottom: 1px solid {C_GOLD_DARK};"
            f"}}"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(2)

        self._title_label = QLabel(self._title.upper())
        self._title_label.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; "
            "font-size: 10px; font-weight: bold; letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(self._title_label)
        layout.addStretch()

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(
            f"color: {C_STATUS_IDLE}; font-size: 10px; background: transparent;"
        )
        layout.addWidget(self._status_dot)

        # Font size controls
        for symbol, delta in (("𝖠⁻", -1), ("𝖠⁺", +1)):
            btn = QPushButton(symbol)
            btn.setFixedSize(20, 20)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {C_GOLD_DIM}; border: none; font-size: 9px; }}"
                f"QPushButton:hover {{ color: {C_GOLD}; }}"
            )
            d = delta
            btn.clicked.connect(lambda _, d=d: self._adjust_font(d))
            layout.addWidget(btn)

        # Lock
        self._btn_lock = QPushButton("🔓")
        self._btn_lock.setFixedSize(20, 20)
        self._btn_lock.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_lock.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_GOLD_DIM}; border: none; font-size: 10px; }}"
            f"QPushButton:hover {{ color: {C_GOLD}; }}"
        )
        self._btn_lock.clicked.connect(self._on_toggle_lock)
        layout.addWidget(self._btn_lock)

        # Minimise / close
        for symbol, slot in (("─", self._on_minimise), ("✕", self._on_close)):
            btn = QPushButton(symbol)
            btn.setFixedSize(20, 20)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {C_GOLD_DIM}; border: none; font-size: 10px; }}"
                f"QPushButton:hover {{ color: {C_GOLD}; }}"
            )
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        return bar

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def set_status(self, status: str, message: str = "") -> None:
        colour_map = {
            "ok":    C_STATUS_OK,
            "warn":  C_STATUS_WARN,
            "error": C_STATUS_ERROR,
            "idle":  C_STATUS_IDLE,
        }
        colour = colour_map.get(status, C_STATUS_IDLE)
        self._status_dot.setStyleSheet(
            f"color: {colour}; font-size: 10px; background: transparent;"
        )
        self.status_changed.emit(self.widget_id, status, message)

    # ------------------------------------------------------------------
    # Font size
    # ------------------------------------------------------------------

    def get_font_size(self) -> int:
        return self._font_size

    def set_font_size(self, size: int) -> None:
        size = max(FONT_MIN, min(FONT_MAX, size))
        if size == self._font_size:
            return
        self._font_size = size
        self._apply_font_size(size)
        self.font_size_changed.emit(self.widget_id, size)

    def _adjust_font(self, delta: int) -> None:
        self.set_font_size(self._font_size + delta)

    def _apply_font_size(self, size: int) -> None:
        """
        Walk all QLabel and QTextEdit children in the body and update font size.
        Subclasses can override for finer control.
        """
        from PyQt6.QtWidgets import QLabel, QTextEdit, QLineEdit
        for child in self._body.findChildren((QLabel, QTextEdit, QLineEdit)):
            font = child.font()
            font.setPointSize(size)
            child.setFont(font)

    # ------------------------------------------------------------------
    # Lock
    # ------------------------------------------------------------------

    def set_locked(self, locked: bool) -> None:
        self._locked = locked
        self._btn_lock.setText("🔒" if locked else "🔓")
        self._btn_lock.setStyleSheet(
            f"QPushButton {{ background: transparent; "
            f"color: {'#d4af37' if locked else C_GOLD_DIM}; "
            f"border: none; font-size: 10px; }}"
            f"QPushButton:hover {{ color: {C_GOLD}; }}"
        )
        self.lock_changed.emit(self.widget_id, locked)

    def _on_toggle_lock(self) -> None:
        self.set_locked(not self._locked)

    # ------------------------------------------------------------------
    # Mouse — drag + resize
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        if self._locked:
            super().mousePressEvent(event)
            return

        pos   = event.position().toPoint()
        edges = _hit_edges(pos, self.rect(), EDGE_GRIP)

        if edges:
            self._resize_edges       = edges
            self._resize_origin      = event.globalPosition().toPoint()
            self._resize_start_geom  = self.geometry()
            event.accept()
        elif self._header.geometry().contains(pos):
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._locked:
            super().mouseMoveEvent(event)
            return

        pos = event.position().toPoint()

        if self._resize_origin is not None:
            delta = event.globalPosition().toPoint() - self._resize_origin
            geo   = QRect(self._resize_start_geom)
            e     = self._resize_edges
            if e & _RIGHT:  geo.setRight( geo.right()  + delta.x())
            if e & _BOTTOM: geo.setBottom(geo.bottom() + delta.y())
            if e & _LEFT:   geo.setLeft(  geo.left()   + delta.x())
            if e & _TOP:    geo.setTop(   geo.top()    + delta.y())
            if geo.width()  < MIN_W: geo.setWidth(MIN_W)
            if geo.height() < MIN_H: geo.setHeight(MIN_H)
            self.setGeometry(geo)
            event.accept()
            return

        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            if self.parent():
                pr = self.parent().rect()
                new_pos.setX(max(0, min(new_pos.x(), pr.width()  - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), pr.height() - self.height())))
            self.move(new_pos)
            self.position_changed.emit(self.widget_id, new_pos.x(), new_pos.y())
            event.accept()
            return

        edges  = _hit_edges(pos, self.rect(), EDGE_GRIP)
        cursor = _CURSOR_MAP.get(edges, Qt.CursorShape.ArrowCursor)
        self.setCursor(QCursor(cursor))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos          = None
        self._resize_origin     = None
        self._resize_edges      = 0
        self._resize_start_geom = None
        if not self._locked:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Resize signal
    # ------------------------------------------------------------------

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.size_changed.emit(self.widget_id, self.width(), self.height())

    # ------------------------------------------------------------------
    # Header buttons — minimise with animation, close
    # ------------------------------------------------------------------

    def _on_minimise(self) -> None:
        if self._minimised:
            self._expand()
        else:
            self._collapse()

    def _collapse(self) -> None:
        self._minimised = True
        target_h = HEADER_H + 2

        if self._anim:
            self._anim.stop()

        self._anim = QPropertyAnimation(self, b"maximumHeight")
        self._anim.setDuration(ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.setStartValue(self.height())
        self._anim.setEndValue(target_h)
        self._anim.finished.connect(lambda: (
            self._body.hide(),
            self.setFixedHeight(target_h),
        ))
        self._anim.start()

    def _expand(self) -> None:
        self._minimised = False
        self._body.show()
        self.setMinimumHeight(MIN_H)
        self.setMaximumHeight(16777215)

        if self._anim:
            self._anim.stop()

        self._anim = QPropertyAnimation(self, b"maximumHeight")
        self._anim.setDuration(ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.setStartValue(HEADER_H + 2)
        self._anim.setEndValue(max(MIN_H, self.height()))
        self._anim.start()

    def _on_close(self) -> None:
        self.hide()
        self.visibility_changed.emit(self.widget_id, False)
