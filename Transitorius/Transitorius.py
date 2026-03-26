"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ████████ ██████   █████  ███    ██ ███████ ██ ████████  ██████  ██████  ██ ██    ██ ███████ ▍
🮈     ██    ██   ██ ██   ██ ████   ██ ██      ██    ██    ██    ██ ██   ██ ██ ██    ██ ██      ▍
🮈     ██    ██████  ███████ ██ ██  ██ ███████ ██    ██    ██    ██ ██████  ██ ██    ██ ███████ ▍
🮈     ██    ██   ██ ██   ██ ██  ██ ██      ██ ██    ██    ██    ██ ██   ██ ██ ██    ██      ██ ▍
🮈     ██    ██   ██ ██   ██ ██   ████ ███████ ██    ██     ██████  ██   ██ ██  ██████  ███████ ▍
🮈                                                                                              ▍
🮈                                                                                              ▍
🮈                                        Python Script                                         ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          transitorius.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# v1.0 — Migration shell. Three-pane layout. Palette. Typography. No logic.
"""



import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSplitter, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QFontDatabase

# ── Palette ───────────────────────────────────────────────────────────────────

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"
C_WHITE     = "#e8e0cc"

# ── Global stylesheet ─────────────────────────────────────────────────────────

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QSplitter::handle {{
    background-color: {C_GOLD_DARK};
    width: 1px;
}}
QScrollBar:vertical {{
    background: {C_PANEL}; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {C_PANEL}; height: 8px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK}; border-radius: 4px;
}}
QToolTip {{
    background: {C_PANEL}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
"""

# ── Widget factories ──────────────────────────────────────────────────────────

def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    lbl.setFont(QFont("Georgia", size, weight))
    lbl.setStyleSheet(f"color: {C_GOLD}; background: transparent;")
    return lbl

def dim_label(text: str, size: int = 10) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Georgia", size))
    lbl.setStyleSheet(f"color: {C_GOLD_DIM}; background: transparent;")
    return lbl

def micro_label(text: str) -> QLabel:
    """Engraved micro-label. Uppercase, letter-spaced, dim."""
    lbl = QLabel(text.upper())
    lbl.setFont(QFont("Georgia", 9))
    lbl.setStyleSheet(f"""
        color: {C_GOLD_DIM};
        background: transparent;
        letter-spacing: 2px;
    """)
    return lbl

def separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {C_GOLD_DARK}; background: {C_GOLD_DARK}; max-height: 1px;")
    return line

def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {C_PANEL};
            color: {accent};
            border: 1px solid {C_GOLD_DARK};
            font-family: Georgia, serif;
            font-size: 11px;
            padding: 6px 14px;
            letter-spacing: 1px;
        }}
        QPushButton:hover  {{ background: {C_GOLD_DARK}; border-color: {accent}; }}
        QPushButton:pressed {{ background: {C_SUBTLE}; }}
        QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
    """)
    return btn

# ── TopBar ────────────────────────────────────────────────────────────────────

class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-bottom: 1px solid {C_GOLD_DARK};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_GOLD_DIM};
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{ color: {C_GOLD}; }}
        """)
        layout.addWidget(self.toggle_btn)

        title = gold_label("✦  ARCA COGNITORIUM  ✦", size=14, bold=True)
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)

        layout.addStretch()

        self.status_lbl = dim_label("Transitorius · Migration Shell · v1.0")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.status_lbl)

# ── StatusBar ─────────────────────────────────────────────────────────────────

class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-top: 1px solid {C_GOLD_DARK};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        self.left_lbl = dim_label("The Tower awaits.")
        layout.addWidget(self.left_lbl)
        layout.addStretch()
        self.right_lbl = dim_label("Ordo Discordia · Cosmos Inania")
        layout.addWidget(self.right_lbl)

# ── Left pane — Navigation ────────────────────────────────────────────────────

class NavPane(QFrame):
    """Left pane. Menu navigation. Fixed width, scrollable."""

    NAV_ITEMS = [
        ("FILUM",          "Threads"),
        ("FOLIOS",         "Projects"),
        ("THE COUNCIL",    "Counsel"),
        ("GRIMOIRE",       "Identity"),
        ("ARX ARCANA",     "Workshop"),
        ("REFERENTIA",     "Reference"),
        ("EGO MANIFESTUS", "The Wizard"),
        ("NEXUS ARCHIVUM", "Library"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setMaximumWidth(260)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-right: 1px solid {C_GOLD_DARK};
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Pane header
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet(f"background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.addWidget(micro_label("navigatio"))
        outer.addWidget(header)

        # Scrollable nav list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        nav_widget = QWidget()
        nav_widget.setStyleSheet(f"background: {C_PANEL};")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(0)

        for key, sub in self.NAV_ITEMS:
            item = NavItem(key, sub)
            nav_layout.addWidget(item)

        nav_layout.addStretch()
        scroll.setWidget(nav_widget)
        outer.addWidget(scroll)

class NavItem(QFrame):
    def __init__(self, label: str, sublabel: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False
        self._apply_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(1)

        self.main_lbl = QLabel(label)
        self.main_lbl.setFont(QFont("Georgia", 10, QFont.Weight.Bold))
        self.main_lbl.setStyleSheet(f"color: {C_GOLD}; background: transparent; letter-spacing: 1px;")

        self.sub_lbl = QLabel(sublabel)
        self.sub_lbl.setFont(QFont("Georgia", 8))
        self.sub_lbl.setStyleSheet(f"color: {C_GOLD_DIM}; background: transparent;")

        layout.addWidget(self.main_lbl)
        layout.addWidget(self.sub_lbl)

    def _apply_style(self):
        bg = C_GOLD_DARK if self._active else "transparent"
        border = f"border-left: 2px solid {C_GOLD};" if self._active else f"border-left: 2px solid transparent;"
        self.setStyleSheet(f"QFrame {{ background: {bg}; {border} }}")

    def enterEvent(self, event):
        if not self._active:
            self.setStyleSheet(f"QFrame {{ background: {C_GOLD_DARK}; border-left: 2px solid {C_GOLD_DIM}; }}")

    def leaveEvent(self, event):
        self._apply_style()

# ── Centre pane — Content ─────────────────────────────────────────────────────

class ContentPane(QFrame):
    """Centre pane. Primary content surface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Pane header
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet(f"background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.addWidget(micro_label("specularium"))
        h_layout.addStretch()
        layout.addWidget(header)

        # Placeholder body
        body = QWidget()
        body.setStyleSheet(f"background: {C_BG};")
        body_layout = QVBoxLayout(body)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder = gold_label("✦", size=32)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(placeholder)

        sub = dim_label("Content surface. Awaiting assembly.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(sub)

        layout.addWidget(body)

# ── Right pane — Context ──────────────────────────────────────────────────────

class ContextPane(QFrame):
    """Right pane. Entity context, metadata, ancillary information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(160)
        self.setMaximumWidth(300)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-left: 1px solid {C_GOLD_DARK};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Pane header
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet(f"background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.addWidget(micro_label("contextus"))
        layout.addWidget(header)

        # Placeholder content
        body = QWidget()
        body.setStyleSheet(f"background: {C_PANEL};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 16, 16, 16)
        body_layout.setSpacing(12)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        body_layout.addWidget(micro_label("entity"))
        body_layout.addWidget(gold_label("—", size=11))
        body_layout.addWidget(separator())
        body_layout.addWidget(micro_label("status"))
        body_layout.addWidget(dim_label("Dormant"))
        body_layout.addWidget(separator())
        body_layout.addWidget(micro_label("session"))
        body_layout.addWidget(dim_label("No active thread."))
        body_layout.addStretch()

        layout.addWidget(body)

# ── Main window ───────────────────────────────────────────────────────────────

class TransitoriusApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transitorius · Arca Cognitorium")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TopBar
        self.topbar = TopBar()
        self.topbar.toggle_btn.clicked.connect(self._toggle_nav)
        root.addWidget(self.topbar)

        # Three-pane body
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background: {C_GOLD_DARK}; }}")

        self.nav_pane     = NavPane()
        self.content_pane = ContentPane()
        self.context_pane = ContextPane()

        self.splitter.addWidget(self.nav_pane)
        self.splitter.addWidget(self.content_pane)
        self.splitter.addWidget(self.context_pane)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        self.splitter.setSizes([220, 820, 240])

        root.addWidget(self.splitter)

        # StatusBar
        self.statusbar_widget = StatusBar()
        root.addWidget(self.statusbar_widget)

        # Nav toggle state
        self._nav_visible = True

    def _toggle_nav(self):
        sizes = self.splitter.sizes()
        if self._nav_visible:
            self.splitter.setSizes([0, sizes[1] + sizes[0], sizes[2]])
        else:
            self.splitter.setSizes([220, sizes[1] - 220, sizes[2]])
        self._nav_visible = not self._nav_visible

# ── Entry ─────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    window = TransitoriusApp()
    window.show()
    sys.exit(app.exec())
