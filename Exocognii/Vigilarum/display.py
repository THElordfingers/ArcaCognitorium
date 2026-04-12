# display.py — Vigilarum Omnia v2
# Usage: python3 display.py <N> [--bare]
# Free-float canvas. Widgets are draggable and resizable.
# Position/size persists to display_N.json.

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PyQt6.QtGui import QColor, QPalette, QFont, QPainter, QPen, QCursor

from data import (MAX_DISPLAYS, C_BG, C_PANEL, C_GOLD, C_GOLD_DIM,
                  C_TEXT, C_TEXT_DIM, C_BORDER, FONT_BODY, FONT_SIZE, FONT_SMALL)
from state import read_state, read_display, write_display
from widgets import make_widget

POLL_MS   = 1_000
HANDLE_H  = 18    # drag handle height px
GRIP_SIZE = 12    # resize grip square px
MIN_W     = 160
MIN_H     = 100
DEFAULT_W = 280
DEFAULT_H = 200


# =============================================================================
# FloatingCard — draggable, resizable wrapper around an ArcaneCard
# =============================================================================

class FloatingCard(QWidget):
    def __init__(self, widget_id, display_name, inner_card, canvas, x, y, w, h):
        super().__init__(canvas)
        self.widget_id    = widget_id
        self.display_name = display_name
        self._card        = inner_card
        self._canvas      = canvas

        self._dragging  = False
        self._resizing  = False
        self._drag_off  = QPoint()

        self.setGeometry(x, y, w, h)
        self.setMinimumSize(MIN_W, MIN_H)
        self.show()

        # inner card fills below handle
        inner_card.setParent(self)
        inner_card.setGeometry(0, HANDLE_H, w, h - HANDLE_H)
        inner_card.show()

        self.setMouseTracking(True)

    # ------------------------------------------------------------------ paint

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Handle bar
        p.fillRect(0, 0, self.width(), HANDLE_H, QColor(C_PANEL))
        pen = QPen(QColor(C_BORDER)); pen.setWidth(1); p.setPen(pen)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Widget name in handle
        p.setFont(QFont(FONT_BODY, FONT_SMALL - 1))
        p.setPen(QColor(C_GOLD_DIM))
        p.drawText(6, 0, self.width() - 20, HANDLE_H,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self.display_name)

        # Resize grip — bright gold, clearly visible
        gx = self.width() - GRIP_SIZE
        gy = self.height() - GRIP_SIZE
        # Fill grip zone background
        p.fillRect(gx, gy, GRIP_SIZE, GRIP_SIZE, QColor("#1A1A2E"))
        # Draw grip lines
        grip_pen = QPen(QColor(C_GOLD)); grip_pen.setWidth(2); p.setPen(grip_pen)
        for i in range(2, 5):
            offset = i * 4
            p.drawLine(self.width() - offset, self.height() - 2,
                       self.width() - 2,      self.height() - offset)
        p.end()

    # ------------------------------------------------------------------ resize inner

    def resizeEvent(self, event):
        w, h = self.width(), self.height()
        self._card.setGeometry(0, HANDLE_H, w, h - HANDLE_H)
        super().resizeEvent(event)

    # ------------------------------------------------------------------ mouse

    def _in_grip(self, pos) -> bool:
        return (pos.x() >= self.width()  - GRIP_SIZE and
                pos.y() >= self.height() - GRIP_SIZE)

    def _in_handle(self, pos) -> bool:
        return pos.y() < HANDLE_H

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event); return
        pos = event.pos()
        if self._in_grip(pos):
            self._resizing = True
            self._resize_origin = event.globalPosition().toPoint()
            self._resize_start  = QSize(self.width(), self.height())
        elif self._in_handle(pos):
            self._dragging = True
            self._drag_off = pos
        self.raise_()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self._resizing:
            gpos  = event.globalPosition().toPoint()
            delta = gpos - self._resize_origin
            new_w = max(MIN_W, self._resize_start.width()  + delta.x())
            new_h = max(MIN_H, self._resize_start.height() + delta.y())
            self.resize(new_w, new_h)
        elif self._dragging:
            gpos   = event.globalPosition().toPoint()
            new_pos = self.mapToParent(pos - self._drag_off)
            # clamp to canvas
            cx = max(0, min(new_pos.x(), self._canvas.width()  - self.width()))
            cy = max(0, min(new_pos.y(), self._canvas.height() - self.height()))
            self.move(cx, cy)
        else:
            # cursor feedback
            if self._in_grip(pos):
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif self._in_handle(pos):
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event):
        if self._dragging or self._resizing:
            self._dragging = False; self._resizing = False
            self._canvas.save_layout()
        super().mouseReleaseEvent(event)

    def update_data(self, state):
        self._card.update_data(state)

    def geometry_dict(self) -> dict:
        return {"x": self.x(), "y": self.y(),
                "w": self.width(), "h": self.height()}


# =============================================================================
# FreeCanvas — absolute-position container for FloatingCards
# =============================================================================

class FreeCanvas(QWidget):
    def __init__(self, display_id, parent=None):
        super().__init__(parent)
        self._did   = display_id
        self._cards: dict[str, FloatingCard] = {}   # widget_id → FloatingCard
        self.setStyleSheet(f"background:{C_BG};")

    def mount(self, widget_ids: list[str], layout_data: dict):
        """
        Build or reconcile floating cards from widget_ids.
        layout_data: dict of widget_id → {x,y,w,h}
        New widgets get auto-positioned; removed widgets are deleted.
        """
        current = set(self._cards.keys())
        incoming = set(widget_ids)

        # Remove cards no longer assigned
        for wid in current - incoming:
            self._cards[wid].deleteLater()
            del self._cards[wid]

        # Add new cards
        for i, wid in enumerate(widget_ids):
            if wid in self._cards:
                continue
            geo = layout_data.get(wid)
            if geo:
                x, y, w, h = geo["x"], geo["y"], geo["w"], geo["h"]
            else:
                # Auto-position: cascade from top-left
                offset = len(self._cards) * 24
                x, y, w, h = offset, offset, DEFAULT_W, DEFAULT_H

            from data import WIDGET_BY_ID
            entry = WIDGET_BY_ID.get(wid)
            display_name = entry[1] if entry else wid

            inner = make_widget(wid, self)
            card  = FloatingCard(wid, display_name, inner, self, x, y, w, h)
            self._cards[wid] = card

    def push_state(self, state):
        for card in self._cards.values():
            card.update_data(state)

    def save_layout(self):
        """Write current positions/sizes back to display_N.json."""
        cfg = read_display(self._did)
        layout = cfg.get("layout", {})
        for wid, card in self._cards.items():
            layout[wid] = card.geometry_dict()
        cfg["layout"] = layout
        write_display(self._did, cfg)

    def current_ids(self) -> list[str]:
        return list(self._cards.keys())


# =============================================================================
# Chrome widgets
# =============================================================================

class SummaryBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(f"background:{C_PANEL};border-bottom:1px solid {C_GOLD_DIM};")
        hl = QHBoxLayout(self); hl.setContentsMargins(12, 0, 12, 0); hl.setSpacing(16)
        self._sky  = self._l("", C_TEXT_DIM)
        self._time = self._l("", C_GOLD_DIM)
        hl.addWidget(self._sky, stretch=1); hl.addWidget(self._time)

    def _l(self, t, c):
        l = QLabel(t); l.setFont(QFont(FONT_BODY, FONT_SMALL))
        l.setStyleSheet(f"color:{c};background:transparent;"); return l

    def update_state(self, state):
        if not state:
            self._sky.setText("Awaiting engine\u2026"); self._time.setText(""); return
        self._sky.setText(state.get("sky_summary", ""))
        self._time.setText(state.get("time_local", ""))


class StatusLine(QWidget):
    def __init__(self, did, parent=None):
        super().__init__(parent)
        self._did = did; self.setFixedHeight(20)
        self.setStyleSheet(f"background:{C_PANEL};border-top:1px solid {C_GOLD_DIM};")
        hl = QHBoxLayout(self); hl.setContentsMargins(12, 0, 12, 0)
        self._msg = QLabel(f"Display {did}  \u00b7  Awaiting state\u2026")
        self._msg.setFont(QFont(FONT_BODY, FONT_SMALL - 1))
        self._msg.setStyleSheet(f"color:{C_TEXT_DIM};background:transparent;")
        hl.addWidget(self._msg)

    def update_state(self, state, n):
        if not state:
            self._msg.setText(f"Display {self._did}  \u00b7  No state"); return
        self._msg.setText(
            f"Display {self._did}  \u00b7  {n} widget{'s' if n != 1 else ''}  \u00b7  "
            f"{state.get('time_local', '')}  \u00b7  "
            f"{state.get('season', '')}  \u00b7  "
            f"{state.get('moon_phase_name', '')}")


# =============================================================================
# DisplayWindow
# =============================================================================

class DisplayWindow(QMainWindow):
    def __init__(self, did, bare=False):
        super().__init__()
        self._did         = did
        self._bare        = bare
        self._last_ids    = []
        self._last_state  = None

        self.setWindowTitle(f"Vigilarum \u2014 Display {did}" +
                            (" (bare)" if bare else ""))
        self.setMinimumSize(400, 300)
        self._build_ui()
        self.setStyleSheet(
            f"QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};"
            f"font-family:Georgia;font-size:{FONT_SIZE}pt;}}"
        )
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor(C_BG)); self.setPalette(pal)

        t = QTimer(self); t.setInterval(POLL_MS)
        t.timeout.connect(self._poll); t.start()
        self._poll()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        if not self._bare:
            self._sumbar = SummaryBar(); root.addWidget(self._sumbar)

        self._canvas = FreeCanvas(self._did)
        root.addWidget(self._canvas, stretch=1)

        if not self._bare:
            self._statline = StatusLine(self._did); root.addWidget(self._statline)

    def _poll(self):
        cfg      = read_display(self._did)
        ids      = cfg.get("widgets", [])
        layout   = cfg.get("layout", {})

        if ids != self._last_ids:
            self._canvas.mount(ids, layout)
            self._last_ids = list(ids)

        state = read_state(); self._last_state = state
        self._canvas.push_state(state)

        if not self._bare:
            self._sumbar.update_state(state)
            self._statline.update_state(state, len(ids))


# =============================================================================
# Entry
# =============================================================================

def main():
    args = sys.argv[1:]
    bare = "--bare" in args
    args = [a for a in args if a != "--bare"]

    if not args:
        print("Usage: python3 display.py <N> [--bare]")
        sys.exit(1)

    try:
        did = int(args[0])
        if not (1 <= did <= MAX_DISPLAYS):
            raise ValueError
    except ValueError:
        print(f"Display ID must be 1\u2013{MAX_DISPLAYS}")
        sys.exit(1)

    app = QApplication(sys.argv)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(C_TEXT))
    app.setPalette(pal)

    w = DisplayWindow(did, bare=bare); w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
