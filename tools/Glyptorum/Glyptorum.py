"""
GLYPTORUM — Glyph Arrangement Studio  v5
PyQt6 — fully dockable panels, floating windows, persistent layout.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QByteArray, QTimer
from PyQt6.QtGui import QUndoStack, QUndoCommand
from PyQt6.QtGui import (
    QFont, QFontDatabase, QTextCursor, QDrag, QPixmap, QPainter,
    QColor, QKeySequence, QShortcut, QTextBlockFormat, QTextCharFormat,
    QWheelEvent, QAction,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QTabWidget, QScrollArea, QFileDialog, QInputDialog,
    QMessageBox, QDialog, QDialogButtonBox, QTextEdit, QLineEdit,
    QSplitter, QFrame, QSizePolicy, QSpinBox, QPlainTextEdit, QMenu,
    QComboBox, QSlider, QToolBar, QStatusBar,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────

ARCA_DIR     = Path.home() / "ArcaCognitorium"
TOOLS_DIR    = ARCA_DIR / "tools"
ROOT_DIR     = TOOLS_DIR / "Glyptorum"
STORAGE_DIR  = ROOT_DIR / "Storage"
SETS_DIR     = STORAGE_DIR / "Glyph-Sets"
CANVAS_DIR   = STORAGE_DIR / "Canvas"
SHAPES_DIR   = STORAGE_DIR / "Shapes"
SESSION_DIR  = ROOT_DIR / "Session"
SESSION_FILE = SESSION_DIR / "session.json"

for _d in (SETS_DIR, CANVAS_DIR, SHAPES_DIR, SESSION_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Palette & Stylesheet
# ─────────────────────────────────────────────────────────────────────────────

BG_DEEP    = "#0a0a12"
BG_MID     = "#10101e"
BG_PANEL   = "#13131f"
BG_WIDGET  = "#1a1a2e"
BG_HOVER   = "#20203a"
BG_SEL     = "#2a1a4a"
FG_DIM     = "#4a4a7a"
FG_MED     = "#7070aa"
FG_BRIGHT  = "#aaaadd"
FG_WHITE   = "#ddddf0"
ACC_BLUE   = "#5566cc"
ACC_PURPLE = "#8844bb"
ACC_CYAN   = "#44aacc"
ACC_GOLD   = "#ccaa44"
ACC_GREEN  = "#44bb88"
ACC_RED    = "#cc4444"
BORDER     = "#2a2a4a"
BORDER_ACC = "#4444aa"

STYLESHEET = f"""
QWidget {{
    background: {BG_DEEP};
    color: {FG_BRIGHT};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
}}
QMainWindow {{ background: {BG_DEEP}; }}
QDialog     {{ background: {BG_MID};  }}

/* ── Dock widgets ── */
QDockWidget {{
    color: {FG_BRIGHT};
    font-size: 11px;
    letter-spacing: 1px;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background: {BG_MID};
    border-bottom: 1px solid {BORDER_ACC};
    padding: 4px 8px;
    text-align: left;
    color: {ACC_BLUE};
    letter-spacing: 2px;
    font-size: 10px;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    background: transparent;
    border: none;
    padding: 2px;
}}
QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
    background: {BG_HOVER};
}}

/* ── Toolbar ── */
QToolBar {{
    background: {BG_MID};
    border-bottom: 1px solid {BORDER};
    spacing: 4px;
    padding: 3px 6px;
}}
QToolBar::separator {{
    background: {BORDER_ACC};
    width: 1px;
    margin: 3px 4px;
}}

/* ── Buttons ── */
QPushButton {{
    background: {BG_WIDGET}; color: {FG_BRIGHT};
    border: 1px solid {BORDER_ACC}; padding: 4px 10px; min-height: 22px;
}}
QPushButton:hover {{ background: {BG_HOVER}; border-color: {ACC_BLUE}; color: {FG_WHITE}; }}
QPushButton:pressed {{ background: {BG_SEL}; border-color: {ACC_PURPLE}; }}

QPushButton#btn-danger  {{ border-color: #552222; color: #aa6666; }}
QPushButton#btn-danger:hover {{ border-color: {ACC_RED}; color: #ffaaaa; background: #1a0808; }}
QPushButton#btn-accent  {{ border-color: {ACC_CYAN};   color: {ACC_CYAN};   }}
QPushButton#btn-accent:hover  {{ background: #0d2a33; }}
QPushButton#btn-green   {{ border-color: {ACC_GREEN};  color: {ACC_GREEN};  }}
QPushButton#btn-green:hover   {{ background: #0a2a1a; }}
QPushButton#btn-gold    {{ border-color: {ACC_GOLD};   color: {ACC_GOLD};   }}
QPushButton#btn-gold:hover    {{ background: #1a1400; }}

QPushButton#btn-print {{
    background: {BG_WIDGET}; border-color: {ACC_PURPLE}; color: {ACC_PURPLE};
    min-width: 78px; max-width: 78px; font-size: 11px;
}}
QPushButton#btn-print:hover {{ background: #1a0a2e; color: #cc88ff; }}
QPushButton#btn-print-all {{
    background: #0a0a20; border: 1px solid {ACC_GOLD}; color: {ACC_GOLD};
    padding: 4px 16px; font-size: 12px; letter-spacing: 1px;
}}
QPushButton#btn-print-all:hover {{ background: #1a1400; }}
QPushButton#btn-sm {{
    background: {BG_WIDGET}; border: 1px solid {BORDER}; color: {FG_MED};
    min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px;
    padding: 0; font-size: 14px;
}}
QPushButton#btn-sm:hover {{ border-color: {ACC_BLUE}; color: {FG_WHITE}; }}

/* ── Glyph cells ── */
QPushButton#glyph-cell {{
    background: {BG_WIDGET}; border: 1px solid {BORDER}; color: {FG_WHITE};
    min-width: 34px; max-width: 34px; min-height: 34px; max-height: 34px;
    padding: 0; font-size: 17px;
}}
QPushButton#glyph-cell:hover {{ background: {BG_HOVER}; border-color: {ACC_CYAN}; color: {ACC_CYAN}; }}

/* ── Glyph slots ── */
QPushButton#glyph-slot {{
    background: {BG_WIDGET}; border: 1px solid {BORDER}; color: {FG_WHITE};
    min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px;
    padding: 0; font-size: 18px;
}}
QPushButton#glyph-slot:hover {{ background: {BG_HOVER}; border-color: {ACC_CYAN}; }}
QPushButton#glyph-slot[checked="true"] {{ background: {BG_SEL}; border-color: {ACC_PURPLE}; color: #cc88ff; }}
QPushButton#glyph-slot[empty="true"]   {{ color: {FG_DIM}; border-color: {BORDER}; font-size: 11px; }}

QSpinBox#count-spin {{
    background: {BG_WIDGET}; border: 1px solid {BORDER}; color: {FG_MED};
    min-width: 36px; max-width: 36px; max-height: 16px; font-size: 10px; padding: 0 2px;
}}
QSpinBox#count-spin::up-button, QSpinBox#count-spin::down-button {{ width:0; border:0; }}

/* ── Line frame ── */
QFrame#line-frame {{ background: {BG_PANEL}; border: 2px solid {BORDER}; border-radius: 2px; margin: 2px 4px; }}

/* ── Canvas ── */
QPlainTextEdit#canvas-output {{
    background: {BG_DEEP}; color: {FG_WHITE}; border: none; padding: 8px;
    selection-background-color: {BG_SEL};
}}

/* ── Tabs ── */
QTabWidget::pane {{ border: 1px solid {BORDER}; background: {BG_PANEL}; }}
QTabBar::tab {{ background: {BG_WIDGET}; color: {FG_DIM}; border: 1px solid {BORDER}; padding: 4px 12px; margin-right: 2px; }}
QTabBar::tab:selected {{ background: {BG_SEL}; color: {FG_WHITE}; border-bottom-color: {BG_SEL}; }}
QTabBar::tab:hover {{ background: {BG_HOVER}; color: {FG_BRIGHT}; }}

/* ── Lists ── */
QListWidget {{
    background: {BG_MID}; border: 1px solid {BORDER}; color: {FG_BRIGHT}; font-size: 11px;
}}
QListWidget::item:selected {{ background: {BG_SEL}; color: {FG_WHITE}; }}
QListWidget::item:hover {{ background: {BG_HOVER}; }}

/* ── Inputs ── */
QLineEdit, QTextEdit {{
    background: {BG_WIDGET}; border: 1px solid {BORDER_ACC}; color: {FG_WHITE};
    padding: 3px 6px; selection-background-color: {BG_SEL};
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {ACC_BLUE}; }}
QComboBox {{
    background: {BG_WIDGET}; border: 1px solid {BORDER_ACC}; color: {FG_WHITE};
    padding: 2px 6px; min-height: 22px;
}}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {BG_WIDGET}; border: 1px solid {BORDER_ACC};
    color: {FG_WHITE}; selection-background-color: {BG_SEL};
}}
QSlider::groove:horizontal {{ background: {BG_WIDGET}; height: 4px; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {ACC_BLUE}; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }}
QSlider::sub-page:horizontal {{ background: {ACC_BLUE}; border-radius: 2px; }}

/* ── Scrollbars ── */
QScrollBar:vertical {{ background: {BG_MID}; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER_ACC}; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {BG_MID}; height: 8px; }}
QScrollBar::handle:horizontal {{ background: {BORDER_ACC}; min-width: 20px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QSplitter::handle {{ background: {BORDER}; width: 3px; height: 3px; }}

/* ── Labels ── */
QLabel#section-lbl {{
    color: {ACC_BLUE}; font-size: 10px; letter-spacing: 2px;
    padding: 4px 6px 2px; border-bottom: 1px solid {BORDER};
}}
QLabel#canvas-hint {{
    color: {FG_DIM}; font-size: 10px; padding: 2px 8px;
    border-bottom: 1px solid {BORDER};
}}
QLabel#logo-lbl {{
    color: {ACC_BLUE}; font-size: 20px; font-weight: bold;
    letter-spacing: 5px; padding: 8px; qproperty-alignment: AlignCenter;
}}
QLabel#dim-lbl {{ color: {FG_DIM}; font-size: 10px; padding: 0 2px; }}

/* ── Status bar ── */
QStatusBar {{ background: {BG_MID}; color: {FG_DIM}; font-size: 10px; border-top: 1px solid {BORDER}; }}

/* ── Context menu ── */
QMenu {{ background: {BG_WIDGET}; border: 1px solid {BORDER_ACC}; color: {FG_WHITE}; padding: 4px; }}
QMenu::item {{ padding: 4px 20px; }}
QMenu::item:selected {{ background: {BG_SEL}; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 3px 0; }}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Data Models
# ─────────────────────────────────────────────────────────────────────────────

class GlyphSet:
    def __init__(self, name: str, glyphs: list[str] | None = None):
        self.name   = name
        self.glyphs: list[str] = glyphs or []

    def to_dict(self)  -> dict: return {"name": self.name, "glyphs": self.glyphs}

    @classmethod
    def from_dict(cls, d: dict) -> "GlyphSet":
        return cls(d["name"], d.get("glyphs", []))

    @classmethod
    def from_file(cls, path: str) -> "GlyphSet":
        p    = Path(path)
        text = p.read_text(encoding="utf-8").strip()
        if text.startswith("{"):
            return cls.from_dict(json.loads(text))
        seen, glyphs = set(), []
        for ch in text:
            if ch not in seen and ch.strip():
                seen.add(ch); glyphs.append(ch)
        return cls(p.stem, glyphs)

    def save(self, path: Path | str | None = None):
        p = Path(path) if path else SETS_DIR / f"{self.name}.json"
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


class Shape:
    def __init__(self, name: str, lines: list[dict] | None = None):
        self.name  = name
        self.lines = lines or []

    def to_dict(self) -> dict: return {"name": self.name, "lines": self.lines}

    @classmethod
    def from_dict(cls, d: dict) -> "Shape":
        return cls(d["name"], d.get("lines", []))

    def save(self, path: Path | str | None = None):
        p = Path(path) if path else SHAPES_DIR / f"{self.name}.gshape"
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def from_file(cls, path: str) -> "Shape":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# ─────────────────────────────────────────────────────────────────────────────
#  Dialogs
# ─────────────────────────────────────────────────────────────────────────────

class CreateSetDialog(QDialog):
    def __init__(self, parent=None, existing: GlyphSet | None = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Glyph Set" if existing else "Create Glyph Set")
        self.setMinimumWidth(440)
        lay = QVBoxLayout(self); lay.setSpacing(8)
        lay.addWidget(QLabel("Set name:"))
        self.name_edit = QLineEdit(existing.name if existing else "")
        self.name_edit.setPlaceholderText("e.g. Arcane Sigils")
        lay.addWidget(self.name_edit)
        lay.addWidget(QLabel("Glyphs (each unique non-whitespace character is one glyph):"))
        self.glyph_edit = QTextEdit()
        self.glyph_edit.setPlaceholderText("☽ ☾ ⛤ ♆ ⚸ …")
        if existing: self.glyph_edit.setPlainText("".join(existing.glyphs))
        self.glyph_edit.setMinimumHeight(120)
        lay.addWidget(self.glyph_edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def get_set(self) -> Optional[GlyphSet]:
        name = self.name_edit.text().strip()
        if not name: return None
        text = self.glyph_edit.toPlainText()
        seen, glyphs = set(), []
        for ch in text:
            if ch not in seen and ch.strip():
                seen.add(ch); glyphs.append(ch)
        return GlyphSet(name, glyphs)


class RenameDialog(QDialog):
    def __init__(self, title: str, current: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Name:"))
        self.edit = QLineEdit(current)
        lay.addWidget(self.edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def get_name(self) -> str: return self.edit.text().strip()


class SaveShapeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Shape")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Shape name:"))
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("e.g. Top Border")
        lay.addWidget(self.edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def get_name(self) -> str: return self.edit.text().strip()


# ─────────────────────────────────────────────────────────────────────────────
#  Draggable Glyph Button
# ─────────────────────────────────────────────────────────────────────────────

class DraggableGlyphBtn(QPushButton):
    drag_move = pyqtSignal(int, int)

    def __init__(self, glyph: str, index: int, parent=None):
        super().__init__(glyph, parent)
        self.setObjectName("glyph-cell")
        self.glyph = glyph
        self.index = index
        self.setToolTip(f"U+{ord(glyph):04X}  {glyph}\nDrag to reorder · Right-click to remove")
        self.setAcceptDrops(True)
        self._drag_start: Optional[QPoint] = None

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_start = QPoint(e.pos())
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._drag_start = None
        super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        if (self._drag_start is not None
                and (e.buttons() & Qt.MouseButton.LeftButton)
                and (e.pos() - self._drag_start).manhattanLength() > 12):
            start = QPoint(self._drag_start)
            self._drag_start = None
            drag = QDrag(self)
            mime = QMimeData(); mime.setText(str(self.index)); drag.setMimeData(mime)
            px = QPixmap(self.size()); px.fill(QColor(42, 26, 74, 200))
            p = QPainter(px); p.setFont(self.font()); p.setPen(QColor(FG_WHITE))
            p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, self.glyph); p.end()
            drag.setPixmap(px); drag.setHotSpot(start)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText(): e.acceptProposedAction()

    def dropEvent(self, e):
        try:
            fi = int(e.mimeData().text())
            if fi != self.index: self.drag_move.emit(fi, self.index)
        except ValueError: pass
        e.acceptProposedAction()


# ─────────────────────────────────────────────────────────────────────────────
#  Glyph Grid
# ─────────────────────────────────────────────────────────────────────────────

class GlyphGrid(QScrollArea):
    glyph_selected = pyqtSignal(str)
    COLS = 10

    def __init__(self, glyph_set: GlyphSet, art_font: QFont, parent=None):
        super().__init__(parent)
        self.glyph_set = glyph_set
        self._art_font = QFont(art_font)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(3); self._grid.setContentsMargins(6, 6, 6, 6)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setWidget(self._container)
        self._build()

    def set_art_font(self, font: QFont, smooth: bool = True):
        f = QFont(font)
        if smooth:
            f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
        else:
            f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.ForceIntegerMetrics)
        self._art_font = f
        for i in range(self._grid.count()):
            w = self._grid.itemAt(i).widget()
            if w: w.setFont(self._art_font)

    def _build(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for i, glyph in enumerate(self.glyph_set.glyphs):
            btn = DraggableGlyphBtn(glyph, i)
            btn.setFont(self._art_font)
            btn.clicked.connect(lambda _, g=glyph: self.glyph_selected.emit(g))
            btn.drag_move.connect(self._on_drag_move)
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, b=btn: self._glyph_ctx(pos, b))
            self._grid.addWidget(btn, i // self.COLS, i % self.COLS)

    def _on_drag_move(self, fi: int, ti: int):
        g = self.glyph_set.glyphs; g.insert(ti, g.pop(fi)); self._build()

    def _glyph_ctx(self, pos: QPoint, btn: DraggableGlyphBtn):
        menu = QMenu(self)
        menu.addAction(f"Remove  '{btn.glyph}'").triggered.connect(
            lambda: (self.glyph_set.glyphs.pop(btn.index), self._build()))
        menu.exec(btn.mapToGlobal(pos))

    def refresh(self): self._build()


# ─────────────────────────────────────────────────────────────────────────────
#  Glyph Pane  (tab widget with nav arrows)
# ─────────────────────────────────────────────────────────────────────────────

class GlyphPane(QWidget):
    glyph_selected = pyqtSignal(str)

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self._art_font = QFont(art_font)
        root = QVBoxLayout(self); root.setContentsMargins(2, 2, 2, 2); root.setSpacing(0)

        nav = QHBoxLayout(); nav.setContentsMargins(4, 2, 4, 2); nav.setSpacing(3)
        self.btn_prev  = QPushButton("◀"); self.btn_prev.setObjectName("btn-sm")
        self.btn_next  = QPushButton("▶"); self.btn_next.setObjectName("btn-sm")
        self.tab_label = QLabel("—")
        self.tab_label.setStyleSheet(f"color:{FG_MED};font-size:11px;padding:0 4px;")
        self.btn_prev.clicked.connect(self._prev_tab)
        self.btn_next.clicked.connect(self._next_tab)
        nav.addWidget(self.btn_prev); nav.addWidget(self.btn_next)
        nav.addWidget(self.tab_label, stretch=1)
        root.addLayout(nav)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._tab_ctx)
        self.tabs.currentChanged.connect(self._update_label)
        root.addWidget(self.tabs)
        self._grids: list[GlyphGrid] = []

    # ── tab management ───────────────────────────────────────────

    def add_tab(self, glyph_set: GlyphSet):
        grid = GlyphGrid(glyph_set, self._art_font)
        grid.glyph_selected.connect(self.glyph_selected)
        self._grids.append(grid)
        self.tabs.addTab(grid, glyph_set.name)
        self.tabs.setCurrentWidget(grid)

    def remove_active_tab(self):
        """Remove the currently visible tab — the 'highlighted' one."""
        idx = self.tabs.currentIndex()
        if idx < 0: return
        w = self.tabs.widget(idx); self.tabs.removeTab(idx)
        if w in self._grids: self._grids.remove(w)
        w.deleteLater(); self._update_label()

    def remove_tab_at(self, idx: int):
        if not (0 <= idx < self.tabs.count()): return
        w = self.tabs.widget(idx); self.tabs.removeTab(idx)
        if w in self._grids: self._grids.remove(w)
        w.deleteLater(); self._update_label()

    def current_grid(self) -> Optional[GlyphGrid]:
        w = self.tabs.currentWidget(); return w if isinstance(w, GlyphGrid) else None

    def tab_count(self) -> int: return self.tabs.count()

    def grids_for_set(self, gs: GlyphSet) -> list[GlyphGrid]:
        return [g for g in self._grids if g.glyph_set is gs]

    def set_art_font(self, font: QFont, smooth: bool = True):
        self._art_font = QFont(font)
        for g in self._grids: g.set_art_font(font, smooth)

    # ── navigation ───────────────────────────────────────────────

    def _prev_tab(self):
        i = self.tabs.currentIndex()
        if i > 0: self.tabs.setCurrentIndex(i - 1)

    def _next_tab(self):
        i = self.tabs.currentIndex()
        if i < self.tabs.count() - 1: self.tabs.setCurrentIndex(i + 1)

    def _update_label(self):
        idx = self.tabs.currentIndex(); total = self.tabs.count()
        self.tab_label.setText("—" if total == 0 else f"{self.tabs.tabText(idx)}  [{idx+1}/{total}]")
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setEnabled(idx < total - 1)

    # ── tab context menu ─────────────────────────────────────────

    def _tab_ctx(self, pos: QPoint):
        idx = self.tabs.tabBar().tabAt(pos)
        if idx < 0: return
        menu = QMenu(self)
        menu.addAction("Rename tab…").triggered.connect(lambda: self._rename_tab(idx))
        menu.addAction("Edit glyph set…").triggered.connect(lambda: self._edit_set(idx))
        menu.addSeparator()
        menu.addAction("Remove this tab").triggered.connect(lambda: self.remove_tab_at(idx))
        menu.exec(self.tabs.tabBar().mapToGlobal(pos))

    def _rename_tab(self, idx: int):
        dlg = RenameDialog("Rename Tab", self.tabs.tabText(idx), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_name()
            if name:
                self.tabs.setTabText(idx, name)
                g = self.tabs.widget(idx)
                if isinstance(g, GlyphGrid): g.glyph_set.name = name
                self._update_label()

    def _edit_set(self, idx: int):
        grid = self.tabs.widget(idx)
        if not isinstance(grid, GlyphGrid): return
        dlg = CreateSetDialog(self, existing=grid.glyph_set)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_set()
            if updated:
                grid.glyph_set.name = updated.name; grid.glyph_set.glyphs = updated.glyphs
                self.tabs.setTabText(idx, updated.name); grid.refresh(); self._update_label()


# ─────────────────────────────────────────────────────────────────────────────
#  Glyph Slot
# ─────────────────────────────────────────────────────────────────────────────

class GlyphSlot(QWidget):
    slot_clicked = pyqtSignal(object)
    SPACE_LABEL  = "·SPC"

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self.glyph = ""
        lay = QVBoxLayout(self); lay.setContentsMargins(1,1,1,1); lay.setSpacing(1)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn = QPushButton("")
        self.btn.setObjectName("glyph-slot")
        self.btn.setFont(art_font)
        self.btn.clicked.connect(lambda: self.slot_clicked.emit(self))
        lay.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.spin = QSpinBox(); self.spin.setObjectName("count-spin")
        self.spin.setRange(1, 999); self.spin.setValue(1)
        self.spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.spin, alignment=Qt.AlignmentFlag.AlignCenter)
        self._refresh_empty()

    def set_art_font(self, font: QFont): self.btn.setFont(font)

    def set_glyph(self, glyph: str):
        self.glyph = glyph; self.btn.setText(glyph); self._refresh_empty()

    def clear_glyph(self):
        self.glyph = ""; self.btn.setText(""); self._refresh_empty()

    def set_selected(self, sel: bool):
        self.btn.setProperty("checked", "true" if sel else "false")
        self.btn.style().unpolish(self.btn); self.btn.style().polish(self.btn)

    def render(self) -> str:
        return (self.glyph if self.glyph else " ") * self.spin.value()

    def to_dict(self) -> dict:
        return {"glyph": self.glyph, "count": self.spin.value()}

    def _refresh_empty(self):
        empty = not self.glyph
        self.btn.setProperty("empty", "true" if empty else "false")
        if empty: self.btn.setText(self.SPACE_LABEL)
        self.btn.style().unpolish(self.btn); self.btn.style().polish(self.btn)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Space, Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.clear_glyph()
        super().keyPressEvent(e)




# ─────────────────────────────────────────────────────────────────────────────
#  Undo Commands
# ─────────────────────────────────────────────────────────────────────────────

class CmdSetGlyph(QUndoCommand):
    """Assign or clear a glyph on a slot."""
    def __init__(self, slot, new_glyph: str, desc: str = "Set glyph"):
        super().__init__(desc)
        self._slot      = slot
        self._new_glyph = new_glyph
        self._old_glyph = slot.glyph

    def redo(self):
        if self._new_glyph: self._slot.set_glyph(self._new_glyph)
        else:               self._slot.clear_glyph()

    def undo(self):
        if self._old_glyph: self._slot.set_glyph(self._old_glyph)
        else:               self._slot.clear_glyph()


class CmdSetCount(QUndoCommand):
    """Change a slot's repeat count."""
    def __init__(self, slot, new_count: int):
        super().__init__("Set count")
        self._slot      = slot
        self._new_count = new_count
        self._old_count = slot.spin.value()

    def redo(self): self._slot.spin.setValue(self._new_count)
    def undo(self): self._slot.spin.setValue(self._old_count)


class CmdAddSlot(QUndoCommand):
    def __init__(self, line_widget, after_idx: int):
        super().__init__("Add slot")
        self._lw        = line_widget
        self._after_idx = after_idx

    def redo(self): self._lw._insert_slot_after(self._after_idx)
    def undo(self): self._lw._remove_slot_at(self._after_idx + 1)


class CmdRemoveSlot(QUndoCommand):
    def __init__(self, line_widget, idx: int):
        super().__init__("Remove slot")
        self._lw   = line_widget
        self._idx  = idx
        slot       = line_widget._slots[idx]
        self._data = slot.to_dict()

    def redo(self): self._lw._remove_slot_at(self._idx)

    def undo(self):
        self._lw._insert_slot_after(self._idx - 1)
        slot = self._lw._slots[self._idx]
        if self._data["glyph"]: slot.set_glyph(self._data["glyph"])
        slot.spin.setValue(self._data["count"])


class CmdAddLine(QUndoCommand):
    def __init__(self, stack, after_idx: int):
        super().__init__("Add line")
        self._stack     = stack
        self._after_idx = after_idx

    def redo(self): self._stack._insert_line_after(self._after_idx)
    def undo(self): self._stack._remove_line_at(self._after_idx + 1)


class CmdRemoveLine(QUndoCommand):
    def __init__(self, stack, idx: int):
        super().__init__("Remove line")
        self._stack = stack
        self._idx   = idx
        self._data  = stack._lines[idx].to_dict()

    def redo(self): self._stack._remove_line_at(self._idx)

    def undo(self):
        self._stack._insert_line_after(self._idx - 1)
        lw = self._stack._lines[self._idx]
        for i, sd in enumerate(self._data.get("slots", [])):
            if i >= len(lw._slots): lw._insert_slot_after(i - 1)
            slot = lw._slots[i]
            if sd["glyph"]: slot.set_glyph(sd["glyph"])
            slot.spin.setValue(sd["count"])
        if lw._slots: lw._activate(lw._slots[0])


class CmdLoadShape(QUndoCommand):
    def __init__(self, stack, shape):
        super().__init__("Load shape")
        self._stack    = stack
        self._shape    = shape
        self._old_data = stack.to_list()

    def redo(self): self._stack._load_shape_data(self._shape.lines)
    def undo(self): self._stack._load_shape_data(self._old_data)


class CmdPrintLine(QUndoCommand):
    """Single print-line operation on the canvas."""
    def __init__(self, canvas_out, row: int, new_text: str):
        super().__init__("Print line")
        self._canvas   = canvas_out
        self._row      = row
        doc            = canvas_out.document()
        if doc.blockCount() > row:
            self._old_text = doc.findBlockByNumber(row).text()
        else:
            self._old_text = None   # row didn't exist

    def redo(self): self._canvas._write_row(self._row, self._new_text if hasattr(self,'_new_text') else "")
    def undo(self):
        if self._old_text is None:
            self._canvas._delete_row(self._row)
        else:
            self._canvas._write_row(self._row, self._old_text)


class CmdPrintAll(QUndoCommand):
    """Print-all operation — saves full canvas state for undo."""
    def __init__(self, canvas_out, start_row: int, new_lines: list):
        super().__init__("Print all")
        self._canvas    = canvas_out
        self._start     = start_row
        self._new_lines = new_lines
        # snapshot existing rows
        doc = canvas_out.document()
        self._old_lines = []
        for i in range(start_row, min(start_row + len(new_lines), doc.blockCount())):
            self._old_lines.append(doc.findBlockByNumber(i).text())
        self._old_block_count = doc.blockCount()

    def redo(self):
        self._canvas._write_rows(self._start, self._new_lines)

    def undo(self):
        # Restore old rows, remove any that were added
        self._canvas._write_rows(self._start, self._old_lines)
        doc = self._canvas.document()
        # trim extra blocks if we added rows
        while doc.blockCount() > self._old_block_count:
            c = QTextCursor(doc.findBlockByNumber(doc.blockCount() - 1))
            c.select(QTextCursor.SelectionType.BlockUnderCursor)
            c.deletePreviousChar()

# ─────────────────────────────────────────────────────────────────────────────
#  Line Widget
# ─────────────────────────────────────────────────────────────────────────────

class LineWidget(QFrame):
    print_line     = pyqtSignal(str)
    line_activated = pyqtSignal(object)

    def __init__(self, art_font: QFont, undo_stack: QUndoStack | None = None, parent=None):
        super().__init__(parent)
        self._art_font    = QFont(art_font)
        self._undo_stack  = undo_stack
        self.setObjectName("line-frame")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._active_slot: Optional[GlyphSlot] = None
        self._slots: list[GlyphSlot] = []
        self._is_active = False
        self._is_target = False

        outer = QHBoxLayout(self); outer.setContentsMargins(6,4,6,4); outer.setSpacing(6)
        self.btn_print = QPushButton("Print Line"); self.btn_print.setObjectName("btn-print")
        self.btn_print.clicked.connect(self._do_print)
        outer.addWidget(self.btn_print, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.slot_area = QScrollArea(); self.slot_area.setWidgetResizable(True)
        self.slot_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.slot_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.slot_area.setFixedHeight(66)
        self.slot_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.slot_container = QWidget()
        self.slot_layout = QHBoxLayout(self.slot_container)
        self.slot_layout.setContentsMargins(2,2,2,2); self.slot_layout.setSpacing(3)
        self.slot_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.slot_area.setWidget(self.slot_container)
        outer.addWidget(self.slot_area)

        v = QVBoxLayout(); v.setSpacing(2); v.setContentsMargins(0,0,0,0)
        ba = QPushButton("+"); ba.setObjectName("btn-sm")
        ba.clicked.connect(self.add_slot_cmd)
        br = QPushButton("−"); br.setObjectName("btn-sm")
        br.clicked.connect(self.remove_slot_cmd)
        v.addWidget(ba); v.addWidget(br); outer.addLayout(v)
        self._init_slot()   # first slot, no undo

    # ── public ──────────────────────────────────────────────────

    def _init_slot(self):
        """Add the initial slot without touching the undo stack."""
        self._insert_slot_after(-1)

    def _make_slot(self) -> GlyphSlot:
        slot = GlyphSlot(self._art_font)
        slot.slot_clicked.connect(self._on_slot_click)
        return slot

    def _insert_slot_after(self, after_idx: int):
        """Low-level insert — used by undo commands and add_slot_cmd."""
        slot = self._make_slot()
        insert_pos = after_idx + 1
        self._slots.insert(insert_pos, slot)
        self.slot_layout.insertWidget(insert_pos, slot)
        self._activate(slot)

    def _remove_slot_at(self, idx: int):
        """Low-level remove — used by undo commands."""
        if len(self._slots) <= 1: return
        slot = self._slots.pop(idx)
        if slot is self._active_slot:
            new_idx = min(idx, len(self._slots) - 1)
            self._active_slot = self._slots[new_idx] if self._slots else None
            if self._active_slot: self._activate(self._active_slot)
        self.slot_layout.removeWidget(slot); slot.deleteLater()

    def add_slot_cmd(self):
        """Add slot after active — via undo stack if available."""
        idx = self.active_slot_index()
        if self._undo_stack:
            self._undo_stack.push(CmdAddSlot(self, idx))
        else:
            self._insert_slot_after(idx)

    def remove_slot_cmd(self):
        """Remove active slot — via undo stack if available."""
        idx = self.active_slot_index()
        if idx < 0 or len(self._slots) <= 1: return
        if self._undo_stack:
            self._undo_stack.push(CmdRemoveSlot(self, idx))
        else:
            self._remove_slot_at(idx)

    # keep bare add_slot for load_shape compatibility
    def add_slot(self): self._insert_slot_after(len(self._slots) - 1)

    def remove_slot(self):
        if len(self._slots) <= 1: return
        self._remove_slot_at(len(self._slots) - 1)

    def set_glyph_on_active(self, glyph: str):
        if not self._active_slot: return
        if self._undo_stack:
            self._undo_stack.push(CmdSetGlyph(self._active_slot, glyph))
        else:
            self._active_slot.set_glyph(glyph)
        # Auto-advance to next slot
        idx = self.active_slot_index()
        if idx < len(self._slots) - 1:
            self.select_slot_at(idx + 1)

    def render_line(self) -> str:
        return "".join(s.render() for s in self._slots)

    def to_dict(self) -> dict:
        return {"slots": [s.to_dict() for s in self._slots]}

    def set_art_font(self, font: QFont, smooth: bool = True):
        self._art_font = QFont(font)
        for s in self._slots: s.set_art_font(font)   # slots use system default

    def active_slot_index(self) -> int:
        if self._active_slot and self._active_slot in self._slots:
            return self._slots.index(self._active_slot)
        return -1

    def select_slot_at(self, idx: int):
        if 0 <= idx < len(self._slots): self._activate(self._slots[idx])

    def set_as_active_line(self, active: bool):
        self._is_active = active; self._refresh_frame()

    def set_as_target(self, yes: bool):
        self._is_target = yes; self._refresh_frame()
        self.btn_print.setStyleSheet(
            f"border-color:{ACC_GOLD};color:{ACC_GOLD};" if yes else "")

    def _refresh_frame(self):
        if self._is_target:   color = ACC_GOLD
        elif self._is_active: color = ACC_BLUE
        else:                 color = BORDER
        self.setStyleSheet(
            f"QFrame#line-frame {{ border: 2px solid {color}; "
            f"background: {BG_PANEL}; border-radius: 2px; margin: 2px 4px; }}"
        )

    # ── internals ───────────────────────────────────────────────

    def _activate(self, slot: GlyphSlot):
        if self._active_slot and self._active_slot is not slot:
            self._active_slot.set_selected(False)
        self._active_slot = slot; slot.set_selected(True)
        self.line_activated.emit(self)

    def _on_slot_click(self, slot: GlyphSlot): self._activate(slot)
    def _do_print(self): self.print_line.emit(self.render_line())

    def mousePressEvent(self, e):
        self.setFocus(); self.line_activated.emit(self); super().mousePressEvent(e)

    def keyPressEvent(self, e):
        key = e.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            idx = self.active_slot_index()
            if key == Qt.Key.Key_Left  and idx > 0:                        self.select_slot_at(idx - 1)
            elif key == Qt.Key.Key_Right and idx < len(self._slots) - 1:   self.select_slot_at(idx + 1)
            return
        if key in (Qt.Key.Key_Space, Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self._active_slot: self._active_slot.clear_glyph()
            return
        super().keyPressEvent(e)


# ─────────────────────────────────────────────────────────────────────────────
#  Line Stack
# ─────────────────────────────────────────────────────────────────────────────

class LineStack(QScrollArea):
    print_requested = pyqtSignal(str)

    def __init__(self, art_font: QFont, undo_stack: QUndoStack | None = None, parent=None):
        super().__init__(parent)
        self._art_font   = QFont(art_font)
        self._undo_stack = undo_stack
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0,4,0,4); self._layout.setSpacing(2)
        self._layout.addStretch(1); self.setWidget(self._container)
        self._lines: list[LineWidget] = []
        self._active: Optional[LineWidget] = None

    # ── low-level insert/remove (used by undo commands) ──────────

    def _make_line(self) -> LineWidget:
        lw = LineWidget(self._art_font, self._undo_stack)
        lw.print_line.connect(self.print_requested)
        lw.line_activated.connect(self._set_active)
        return lw

    def _insert_line_after(self, after_idx: int) -> LineWidget:
        lw = self._make_line()
        insert_pos = after_idx + 1
        self._lines.insert(insert_pos, lw)
        # layout position: insert_pos among widgets, before the stretch (+1 for stretch offset)
        self._layout.insertWidget(insert_pos, lw)
        self._set_active(lw)
        return lw

    def _remove_line_at(self, idx: int):
        if not (0 <= idx < len(self._lines)): return
        lw = self._lines.pop(idx)
        if lw is self._active:
            if self._lines:
                new_idx = min(idx, len(self._lines) - 1)
                self._active = None
                self._set_active(self._lines[new_idx])
            else:
                self._active = None
        self._layout.removeWidget(lw); lw.deleteLater()

    # ── public command-level API ──────────────────────────────────

    def add_line(self) -> LineWidget:
        """Add after active line — via undo stack if available."""
        after = self._lines.index(self._active) if self._active in self._lines else len(self._lines) - 1
        if self._undo_stack:
            self._undo_stack.push(CmdAddLine(self, after))
            return self._lines[after + 1]
        return self._insert_line_after(after)

    def remove_line(self):
        """Remove active line — via undo stack if available."""
        if not self._lines: return
        idx = self._lines.index(self._active) if self._active in self._lines else len(self._lines) - 1
        if self._undo_stack:
            self._undo_stack.push(CmdRemoveLine(self, idx))
        else:
            self._remove_line_at(idx)

    def clear_all(self):
        for lw in list(self._lines):
            self._layout.removeWidget(lw); lw.deleteLater()
        self._lines.clear(); self._active = None

    def set_glyph_on_active(self, glyph: str):
        if self._active: self._active.set_glyph_on_active(glyph)

    def render_all(self) -> list[str]:
        return [lw.render_line() for lw in self._lines]

    def to_list(self) -> list[dict]:
        return [lw.to_dict() for lw in self._lines]

    def load_shape(self, shape: Shape):
        if self._undo_stack:
            self._undo_stack.push(CmdLoadShape(self, shape))
        else:
            self._load_shape_data(shape.lines)

    def _load_shape_data(self, lines_data: list):
        self.clear_all()
        for line_data in lines_data:
            slots_data = line_data.get("slots", [])
            lw = self._insert_line_after(len(self._lines) - 1)
            for i, sd in enumerate(slots_data):
                if i >= len(lw._slots): lw.add_slot()
                slot = lw._slots[i]
                g = sd.get("glyph", "")
                slot.set_glyph(g) if g else slot.clear_glyph()
                slot.spin.setValue(max(1, sd.get("count", 1)))
            if lw._slots: lw._activate(lw._slots[0])

    def set_art_font(self, font: QFont, smooth: bool = True):
        self._art_font = QFont(font)
        for lw in self._lines: lw.set_art_font(font, smooth)

    def navigate_lines(self, direction: int):
        if not self._lines: return
        idx = self._lines.index(self._active) if self._active in self._lines else -1
        self._set_active(self._lines[max(0, min(len(self._lines)-1, idx+direction))])

    def _set_active(self, lw: LineWidget):
        if self._active and self._active is not lw:
            self._active.set_as_active_line(False); self._active.set_as_target(False)
        self._active = lw; lw.set_as_active_line(True); lw.set_as_target(True)
        self.ensureWidgetVisible(lw)


# ─────────────────────────────────────────────────────────────────────────────
#  Canvas Output
# ─────────────────────────────────────────────────────────────────────────────

class CanvasOutput(QPlainTextEdit):
    font_size_changed = pyqtSignal(int)

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self.setObjectName("canvas-output")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._line_spacing = 100
        self.set_art_font(art_font)

    def set_art_font(self, font: QFont, smooth: bool = True):
        f = QFont(font)
        if smooth:
            f.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
            f.setStyleStrategy(
                QFont.StyleStrategy.PreferAntialias |
                QFont.StyleStrategy.PreferQuality
            )
        else:
            f.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
            f.setStyleStrategy(
                QFont.StyleStrategy.PreferAntialias |
                QFont.StyleStrategy.PreferMatch |
                QFont.StyleStrategy.ForceIntegerMetrics
            )
        self.setFont(f)
        self._apply_spacing()

    def set_line_spacing(self, pct: int):
        self._line_spacing = pct; self._apply_spacing()

    def _apply_spacing(self):
        fmt = QTextBlockFormat()
        fmt.setLineHeight(self._line_spacing, 1)
        doc = self.document()
        cur = QTextCursor(doc)
        cur.beginEditBlock()
        cur.movePosition(QTextCursor.MoveOperation.Start)
        while True:
            cur.select(QTextCursor.SelectionType.BlockUnderCursor)
            cur.mergeBlockFormat(fmt)
            if not cur.movePosition(QTextCursor.MoveOperation.NextBlock): break
        cur.endEditBlock()

    def wheelEvent(self, e: QWheelEvent):
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            current = self.font().pointSize()
            new_size = max(6, min(72, current + (1 if e.angleDelta().y() > 0 else -1)))
            if new_size != current:
                f = QFont(self.font()); f.setPointSize(new_size)
                self.set_art_font(f); self.font_size_changed.emit(new_size)
            e.accept()
        else:
            super().wheelEvent(e)

    def selected_row(self) -> int: return self.textCursor().blockNumber()

    def _ensure_row(self, row: int):
        doc = self.document()
        while doc.blockCount() <= row:
            c = QTextCursor(doc); c.movePosition(QTextCursor.MoveOperation.End); c.insertBlock()
            fmt = QTextBlockFormat(); fmt.setLineHeight(self._line_spacing, 1)
            c.mergeBlockFormat(fmt)

    def print_at_row(self, text: str) -> int:
        row = self.selected_row(); self._ensure_row(row)
        block = self.document().findBlockByNumber(row)
        c = QTextCursor(block)
        c.select(QTextCursor.SelectionType.BlockUnderCursor)
        c.removeSelectedText(); c.insertText(text)
        next_row = row + 1; self._ensure_row(next_row)
        self.setTextCursor(QTextCursor(self.document().findBlockByNumber(next_row)))
        return next_row

    def print_all(self, lines: list[str]):
        """Print all lines starting from the current cursor row."""
        start = self.selected_row()
        self._write_rows(start, lines)

    def _write_row(self, row: int, text: str):
        self._ensure_row(row)
        block = self.document().findBlockByNumber(row)
        c = QTextCursor(block)
        c.select(QTextCursor.SelectionType.BlockUnderCursor)
        c.removeSelectedText(); c.insertText(text)

    def _write_rows(self, start: int, lines: list):
        for i, text in enumerate(lines):
            self._write_row(start + i, text)
        next_row = start + len(lines)
        self._ensure_row(next_row)
        self.setTextCursor(QTextCursor(self.document().findBlockByNumber(next_row)))

    def _delete_row(self, row: int):
        doc = self.document()
        if doc.blockCount() <= row: return
        block = doc.findBlockByNumber(row)
        c = QTextCursor(block)
        c.select(QTextCursor.SelectionType.BlockUnderCursor)
        c.deletePreviousChar()

    def new_canvas(self): self.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  Font Bar
# ─────────────────────────────────────────────────────────────────────────────

class FontBar(QToolBar):
    font_changed    = pyqtSignal(QFont)
    spacing_changed = pyqtSignal(int)

    MODE_MONO  = "Monospace only"
    MODE_ALL   = "All fonts"
    MODE_NONOTO= "Exclude Noto"

    def __init__(self, parent=None):
        super().__init__("Font", parent)
        self.setMovable(True)
        self.setFloatable(True)

        self.addWidget(QLabel("  Font: "))
        self.font_combo = QComboBox(); self.font_combo.setMinimumWidth(180)
        self.addWidget(self.font_combo)

        self.filter_combo = QComboBox(); self.filter_combo.setFixedWidth(140)
        self.filter_combo.addItems([self.MODE_MONO, self.MODE_ALL, self.MODE_NONOTO])
        self.addWidget(self.filter_combo)
        self.addSeparator()

        self.addWidget(QLabel("  Size: "))
        self.size_spin = QSpinBox(); self.size_spin.setRange(6, 72); self.size_spin.setValue(16)
        self.size_spin.setFixedWidth(52)
        self.addWidget(self.size_spin)
        self.addSeparator()

        self.addWidget(QLabel("  Spacing %: "))
        self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.spacing_slider.setRange(60, 200); self.spacing_slider.setValue(100)
        self.spacing_slider.setFixedWidth(110)
        self.spacing_val = QLabel("100"); self.spacing_val.setObjectName("dim-lbl")
        self.spacing_val.setFixedWidth(28)
        self.addWidget(self.spacing_slider); self.addWidget(self.spacing_val)
        self.addSeparator()

        self.btn_smooth = QPushButton("Smooth"); self.btn_smooth.setCheckable(True)
        self.btn_smooth.setChecked(True)
        self.btn_smooth.setToolTip("Toggle subpixel / full hinting")
        self.btn_smooth.setFixedWidth(64)
        self.addWidget(self.btn_smooth)
        self.btn_smooth.toggled.connect(lambda _: self._emit_font())

        self._all_families: list[str] = []
        self._populate_all_fonts()
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        self.font_combo.currentTextChanged.connect(self._emit_font)
        self.size_spin.valueChanged.connect(self._emit_font)
        self.spacing_slider.valueChanged.connect(self._emit_spacing)
        self._apply_filter(self.MODE_MONO)

    def _populate_all_fonts(self):
        self._all_families = sorted(QFontDatabase.families())

    def _apply_filter(self, mode: str):
        current = self.font_combo.currentText()
        self.font_combo.blockSignals(True); self.font_combo.clear()
        if mode == self.MODE_MONO:
            families = [f for f in self._all_families if QFontDatabase.isFixedPitch(f)]
        elif mode == self.MODE_NONOTO:
            families = [f for f in self._all_families if not f.lower().startswith("noto")]
        else:
            families = self._all_families
        self.font_combo.addItems(families)
        idx = self.font_combo.findText(current)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            for pref in ("Consolas","Cascadia Mono","JetBrains Mono","Fira Code","DejaVu Sans Mono","Courier New"):
                i2 = self.font_combo.findText(pref)
                if i2 >= 0: self.font_combo.setCurrentIndex(i2); break
        self.font_combo.blockSignals(False); self._emit_font()

    def set_size(self, size: int):
        self.size_spin.blockSignals(True); self.size_spin.setValue(size); self.size_spin.blockSignals(False)

    def current_font(self) -> QFont:
        f = QFont(self.font_combo.currentText()); f.setPointSize(self.size_spin.value()); return f

    def is_smooth(self) -> bool:
        return self.btn_smooth.isChecked()

    def _emit_font(self): self.font_changed.emit(self.current_font())

    def _emit_spacing(self, val: int):
        self.spacing_val.setText(str(val)); self.spacing_changed.emit(val)

    def state(self) -> dict:
        return {"family": self.font_combo.currentText(), "size": self.size_spin.value(),
                "spacing": self.spacing_slider.value(), "filter": self.filter_combo.currentText(),
                "smooth": self.btn_smooth.isChecked()}

    def restore(self, d: dict):
        if "filter" in d:
            fi = self.filter_combo.findText(d["filter"])
            if fi >= 0:
                self.filter_combo.blockSignals(True); self.filter_combo.setCurrentIndex(fi)
                self.filter_combo.blockSignals(False); self._apply_filter(d["filter"])
        if "family"  in d:
            idx = self.font_combo.findText(d["family"])
            if idx >= 0: self.font_combo.setCurrentIndex(idx)
        if "size"    in d: self.size_spin.setValue(d["size"])
        if "spacing" in d: self.spacing_slider.setValue(d["spacing"])
        if "smooth"  in d: self.btn_smooth.setChecked(d["smooth"])


# ─────────────────────────────────────────────────────────────────────────────
#  Glyph Set Panel  (dockable)
# ─────────────────────────────────────────────────────────────────────────────

class GlyphSetPanel(QWidget):
    """Manages the set list + panes. Lives inside a dock."""

    glyph_selected = pyqtSignal(str)

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self._art_font = QFont(art_font)

        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        logo = QLabel("GLYPTORUM"); logo.setObjectName("logo-lbl")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter); root.addWidget(logo)

        # ── Set list ──
        lbl = QLabel("Ⅰ  GLYPH SETS"); lbl.setObjectName("section-lbl"); root.addWidget(lbl)
        self.set_list = QListWidget(); self.set_list.setMaximumHeight(110)
        self.set_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.set_list.customContextMenuRequested.connect(self._set_list_ctx)
        root.addWidget(self.set_list)

        # ── Set buttons ──
        lbl2 = QLabel("Ⅱ  MANAGE SETS"); lbl2.setObjectName("section-lbl"); root.addWidget(lbl2)
        row1 = QHBoxLayout(); row1.setContentsMargins(6,4,6,2); row1.setSpacing(3)
        self.btn_load   = QPushButton("Load");   self.btn_load.setToolTip("Load set from file")
        self.btn_create = QPushButton("Create"); self.btn_create.setToolTip("Create new set")
        self.btn_edit   = QPushButton("Edit");   self.btn_edit.setObjectName("btn-accent")
        self.btn_edit.setToolTip("Edit highlighted set")
        for b in (self.btn_load, self.btn_create, self.btn_edit): row1.addWidget(b)
        root.addLayout(row1)

        row2 = QHBoxLayout(); row2.setContentsMargins(6,2,6,4); row2.setSpacing(3)
        self.btn_save_s = QPushButton("Save");   self.btn_save_s.setObjectName("btn-green")
        self.btn_save_s.setToolTip("Save active tab's set")
        self.btn_del_s  = QPushButton("Delete"); self.btn_del_s.setObjectName("btn-danger")
        self.btn_del_s.setToolTip("Delete highlighted set")
        for b in (self.btn_save_s, self.btn_del_s): row2.addWidget(b)
        root.addLayout(row2)

        # ── Panes ──
        lbl3 = QLabel("Ⅲ  GLYPH PANES"); lbl3.setObjectName("section-lbl"); root.addWidget(lbl3)
        pane_scroll = QScrollArea(); pane_scroll.setWidgetResizable(True)
        pane_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        pane_container = QWidget()
        self._pane_layout = QVBoxLayout(pane_container)
        self._pane_layout.setContentsMargins(4,4,4,4); self._pane_layout.setSpacing(6)
        self._pane_layout.addStretch(1)
        pane_scroll.setWidget(pane_container); root.addWidget(pane_scroll, stretch=1)

        # ── Pane controls ──
        lbl4 = QLabel("Ⅳ  PANE CONTROLS"); lbl4.setObjectName("section-lbl"); root.addWidget(lbl4)

        sel_row = QHBoxLayout(); sel_row.setContentsMargins(6,2,6,0); sel_row.setSpacing(4)
        sel_row.addWidget(QLabel("Pane:"))
        self.pane_combo = QComboBox()
        self.pane_combo.setToolTip("Active pane for tab operations")
        sel_row.addWidget(self.pane_combo, stretch=1); root.addLayout(sel_row)

        row3 = QHBoxLayout(); row3.setContentsMargins(6,4,6,6); row3.setSpacing(3)
        self.btn_add_tab  = QPushButton("+ Tab")
        self.btn_rem_tab  = QPushButton("− Tab");  self.btn_rem_tab.setObjectName("btn-danger")
        self.btn_rem_tab.setToolTip("Remove active tab from selected pane")
        self.btn_add_pane = QPushButton("+ Pane")
        self.btn_rem_pane = QPushButton("− Pane"); self.btn_rem_pane.setObjectName("btn-danger")
        self.btn_rem_pane.setToolTip("Remove selected pane")
        for b in (self.btn_add_tab, self.btn_rem_tab, self.btn_add_pane, self.btn_rem_pane):
            row3.addWidget(b)
        root.addLayout(row3)

        # Wire
        self.btn_load.clicked.connect(self._load_set)
        self.btn_create.clicked.connect(self._create_set)
        self.btn_edit.clicked.connect(self._edit_highlighted_set)
        self.btn_save_s.clicked.connect(self._save_set)
        self.btn_del_s.clicked.connect(self._delete_set)
        self.btn_add_tab.clicked.connect(self._add_tab)
        self.btn_rem_tab.clicked.connect(self._remove_tab)
        self.btn_add_pane.clicked.connect(self._add_pane)
        self.btn_rem_pane.clicked.connect(self._remove_pane)

        self._glyph_sets: list[GlyphSet] = []
        self._panes: list[GlyphPane] = []
        self._add_pane()
        self._load_sets_from_disk()

    # ── helpers ─────────────────────────────────────────────────

    def _active_pane(self) -> Optional[GlyphPane]:
        idx = self.pane_combo.currentIndex()
        if 0 <= idx < len(self._panes): return self._panes[idx]
        return self._panes[-1] if self._panes else None

    def _rebuild_combo(self):
        self.pane_combo.blockSignals(True)
        prev = self.pane_combo.currentIndex(); self.pane_combo.clear()
        for i in range(len(self._panes)): self.pane_combo.addItem(f"Pane {i+1}")
        self.pane_combo.setCurrentIndex(max(0, min(prev, len(self._panes)-1)))
        self.pane_combo.blockSignals(False)

    def set_art_font(self, font: QFont, smooth: bool = True):
        self._art_font = QFont(font)
        for p in self._panes: p.set_art_font(font, smooth)

    # ── pane management ─────────────────────────────────────────

    def _add_pane(self):
        pane = GlyphPane(self._art_font)
        pane.glyph_selected.connect(self.glyph_selected)
        pane.setMinimumHeight(180)
        self._panes.append(pane)
        self._pane_layout.insertWidget(self._pane_layout.count()-1, pane)
        self._rebuild_combo(); self.pane_combo.setCurrentIndex(len(self._panes)-1)

    def _remove_pane(self):
        if len(self._panes) <= 1:
            QMessageBox.information(self, "Glyptorum", "Cannot remove the last pane."); return
        idx = self.pane_combo.currentIndex()
        if not (0 <= idx < len(self._panes)): idx = len(self._panes)-1
        pane = self._panes.pop(idx)
        self._pane_layout.removeWidget(pane); pane.deleteLater(); self._rebuild_combo()

    def _add_tab(self):
        pane = self._active_pane()
        if not pane: return
        if not self._glyph_sets:
            QMessageBox.information(self, "Glyptorum", "Load or create a glyph set first."); return
        names = [gs.name for gs in self._glyph_sets]
        name, ok = QInputDialog.getItem(self, "Add Tab", "Glyph set:", names, 0, False)
        if ok and name:
            gs = next(g for g in self._glyph_sets if g.name == name)
            pane.add_tab(gs)

    def _remove_tab(self):
        """Remove the active (highlighted) tab from the selected pane."""
        pane = self._active_pane()
        if pane: pane.remove_active_tab()

    # ── set management ──────────────────────────────────────────

    def _load_sets_from_disk(self):
        for p in sorted(SETS_DIR.glob("*.json")):
            try:
                gs = GlyphSet.from_file(str(p))
                self._glyph_sets.append(gs); self.set_list.addItem(gs.name)
            except Exception: pass

    def _load_set(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Glyph Set", "",
            "Glyph Sets (*.json *.txt);;All files (*)")
        if not path: return
        try: self._register_set(GlyphSet.from_file(path), auto_save=True)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _create_set(self):
        dlg = CreateSetDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            gs = dlg.get_set()
            if gs is None: QMessageBox.warning(self, "Glyptorum", "Name cannot be empty.")
            else: self._register_set(gs, auto_save=True)

    def _edit_highlighted_set(self):
        """Edit the set highlighted in the list."""
        idx = self.set_list.currentRow()
        if not (0 <= idx < len(self._glyph_sets)):
            QMessageBox.information(self, "Glyptorum", "Select a set in the list first."); return
        self._edit_set_at(idx)

    def _register_set(self, gs: GlyphSet, auto_save=False):
        self._glyph_sets.append(gs); self.set_list.addItem(gs.name)
        if auto_save: gs.save()
        pane = self._active_pane()
        if pane: pane.add_tab(gs)

    def _save_set(self):
        pane = self._active_pane(); grid = pane.current_grid() if pane else None
        if not grid: QMessageBox.information(self, "Glyptorum", "No active glyph set."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save Glyph Set",
            str(SETS_DIR / f"{grid.glyph_set.name}.json"), "Glyph Sets (*.json)")
        if path:
            try: grid.glyph_set.save(path)
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _delete_set(self):
        """Delete the set highlighted in the list."""
        idx = self.set_list.currentRow()
        if not (0 <= idx < len(self._glyph_sets)):
            QMessageBox.information(self, "Glyptorum", "Select a set in the list first."); return
        gs = self._glyph_sets[idx]
        refs = []
        for pi, pane in enumerate(self._panes):
            for grid in pane.grids_for_set(gs):
                ti = pane.tabs.indexOf(grid)
                refs.append(f"Pane {pi+1} → '{pane.tabs.tabText(ti)}'")
        if refs:
            msg = (f"'{gs.name}' is open in:\n  " + "\n  ".join(refs) +
                   "\n\nRemove those tabs and delete the set?")
            reply = QMessageBox.warning(self, "Set In Use", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
            if reply != QMessageBox.StandardButton.Yes: return
            for pane in self._panes:
                for grid in pane.grids_for_set(gs):
                    pane.remove_tab_at(pane.tabs.indexOf(grid))
        else:
            reply = QMessageBox.question(self, "Delete Set", f"Delete '{gs.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes: return
        p = SETS_DIR / f"{gs.name}.json"
        if p.exists(): p.unlink()
        self._glyph_sets.pop(idx); self.set_list.takeItem(idx)

    def _set_list_ctx(self, pos: QPoint):
        item = self.set_list.itemAt(pos)
        if not item: return
        idx  = self.set_list.row(item)
        menu = QMenu(self)
        menu.addAction("Edit…").triggered.connect(lambda: self._edit_set_at(idx))
        menu.addSeparator()
        menu.addAction("Delete").triggered.connect(self._delete_set)
        menu.exec(self.set_list.mapToGlobal(pos))

    def _edit_set_at(self, idx: int):
        gs = self._glyph_sets[idx]
        dlg = CreateSetDialog(self, existing=gs)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_set()
            if updated:
                old_path = SETS_DIR / f"{gs.name}.json"
                gs.name = updated.name; gs.glyphs = updated.glyphs
                if old_path.exists(): old_path.unlink()
                gs.save(); self.set_list.item(idx).setText(gs.name)
                for pane in self._panes:
                    for grid in pane.grids_for_set(gs):
                        pane.tabs.setTabText(pane.tabs.indexOf(grid), gs.name)
                        grid.refresh()


# ─────────────────────────────────────────────────────────────────────────────
#  Shape Library Panel  (dockable)
# ─────────────────────────────────────────────────────────────────────────────

class ShapeLibraryPanel(QWidget):
    load_shape_requested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        lbl = QLabel("◈  SHAPES"); lbl.setObjectName("section-lbl"); lay.addWidget(lbl)
        self.shape_list = QListWidget()
        self.shape_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.shape_list.customContextMenuRequested.connect(self._list_ctx)
        self.shape_list.itemDoubleClicked.connect(self._load_selected)
        lay.addWidget(self.shape_list, stretch=1)

        lbl2 = QLabel("ACTIONS"); lbl2.setObjectName("section-lbl"); lay.addWidget(lbl2)

        r1 = QHBoxLayout(); r1.setContentsMargins(6,4,6,2); r1.setSpacing(4)
        self.btn_load_shp = QPushButton("↓ Load into Editor"); self.btn_load_shp.setObjectName("btn-accent")
        self.btn_load_shp.clicked.connect(self._load_selected); r1.addWidget(self.btn_load_shp)
        lay.addLayout(r1)

        r2 = QHBoxLayout(); r2.setContentsMargins(6,2,6,2); r2.setSpacing(4)
        self.btn_rename = QPushButton("Rename")
        self.btn_delete = QPushButton("Delete"); self.btn_delete.setObjectName("btn-danger")
        self.btn_delete.setToolTip("Delete highlighted shape")
        r2.addWidget(self.btn_rename); r2.addWidget(self.btn_delete); lay.addLayout(r2)

        r3 = QHBoxLayout(); r3.setContentsMargins(6,2,6,6); r3.setSpacing(4)
        self.btn_export = QPushButton("Export…"); self.btn_export.setObjectName("btn-green")
        self.btn_import = QPushButton("Import…")
        r3.addWidget(self.btn_export); r3.addWidget(self.btn_import); lay.addLayout(r3)

        self.btn_rename.clicked.connect(self._rename_selected)
        self.btn_delete.clicked.connect(self._delete_selected)
        self.btn_export.clicked.connect(self._export_selected)
        self.btn_import.clicked.connect(self._import_shape)

        self._shapes: list[Shape] = []
        self._load_all_from_disk()

    def add_shape(self, shape: Shape):
        shape.save(); self._shapes.append(shape); self.shape_list.addItem(shape.name)

    def _load_all_from_disk(self):
        for p in sorted(SHAPES_DIR.glob("*.gshape")):
            try:
                s = Shape.from_file(str(p)); self._shapes.append(s); self.shape_list.addItem(s.name)
            except Exception: pass

    def _selected_idx(self) -> int: return self.shape_list.currentRow()

    def _load_selected(self):
        idx = self._selected_idx()
        if 0 <= idx < len(self._shapes): self.load_shape_requested.emit(self._shapes[idx])

    def _rename_selected(self):
        idx = self._selected_idx()
        if not (0 <= idx < len(self._shapes)): return
        s = self._shapes[idx]
        dlg = RenameDialog("Rename Shape", s.name, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_name()
            if name:
                old = SHAPES_DIR / f"{s.name}.gshape"
                s.name = name
                if old.exists(): old.unlink()
                s.save(); self.shape_list.item(idx).setText(name)

    def _delete_selected(self):
        """Delete the shape highlighted in the list."""
        idx = self._selected_idx()
        if not (0 <= idx < len(self._shapes)):
            QMessageBox.information(self, "Glyptorum", "Select a shape first."); return
        s = self._shapes[idx]
        reply = QMessageBox.question(self, "Delete Shape", f"Delete '{s.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            p = SHAPES_DIR / f"{s.name}.gshape"
            if p.exists(): p.unlink()
            self._shapes.pop(idx); self.shape_list.takeItem(idx)

    def _export_selected(self):
        idx = self._selected_idx()
        if not (0 <= idx < len(self._shapes)): return
        s = self._shapes[idx]
        path, _ = QFileDialog.getSaveFileName(self, "Export Shape",
            str(Path.home() / f"{s.name}.gshape"), "Shapes (*.gshape)")
        if path:
            try: s.save(path)
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _import_shape(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Shape", "", "Shapes (*.gshape);;All files (*)")
        if not path: return
        try:
            s = Shape.from_file(path)
            if s.name in [sh.name for sh in self._shapes]: s.name += "_imported"
            self.add_shape(s)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _list_ctx(self, pos: QPoint):
        idx = self.shape_list.indexAt(pos).row()
        if idx < 0: return
        menu = QMenu(self)
        menu.addAction("Load into Editor").triggered.connect(self._load_selected)
        menu.addAction("Rename…").triggered.connect(self._rename_selected)
        menu.addAction("Export…").triggered.connect(self._export_selected)
        menu.addSeparator()
        menu.addAction("Delete").triggered.connect(self._delete_selected)
        menu.exec(self.shape_list.mapToGlobal(pos))


# ─────────────────────────────────────────────────────────────────────────────
#  Line Editor Panel  (dockable)
# ─────────────────────────────────────────────────────────────────────────────

class LineEditorPanel(QWidget):
    save_shape_requested = pyqtSignal(object)

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self._undo_stack = QUndoStack(self)
        self._undo_stack.setUndoLimit(100)

        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # toolbar row
        tb = QHBoxLayout(); tb.setContentsMargins(6,4,6,4); tb.setSpacing(4)
        self.btn_add_ln    = QPushButton("+ Line")
        self.btn_rem_ln    = QPushButton("− Line"); self.btn_rem_ln.setObjectName("btn-danger")
        self.btn_rem_ln.setToolTip("Remove active line")
        self.btn_undo      = QPushButton("↩ Undo"); self.btn_undo.setObjectName("btn-gold")
        self.btn_undo.setToolTip("Undo last editor action  (Ctrl+Z)")
        self.btn_save_shp  = QPushButton("Save Shape"); self.btn_save_shp.setObjectName("btn-green")
        self.btn_print_all = QPushButton("▶  Print All"); self.btn_print_all.setObjectName("btn-print-all")
        for b in (self.btn_add_ln, self.btn_rem_ln, self.btn_undo, self.btn_save_shp, self.btn_print_all):
            tb.addWidget(b)
        tb.addStretch(1)
        lay.addLayout(tb)

        hint = QLabel("  ← → slots  ·  ↑ ↓ lines  ·  Space/Del clears  ·  + Line inserts after active")
        hint.setObjectName("canvas-hint"); lay.addWidget(hint)

        self.line_stack = LineStack(art_font, self._undo_stack)
        lay.addWidget(self.line_stack, stretch=1)

        self.btn_add_ln.clicked.connect(self.line_stack.add_line)
        self.btn_rem_ln.clicked.connect(self.line_stack.remove_line)
        self.btn_undo.clicked.connect(self._undo_stack.undo)
        self.btn_save_shp.clicked.connect(self._save_shape)
        self.btn_print_all.clicked.connect(self._print_all_requested)

        self._undo_stack.canUndoChanged.connect(
            lambda can: self.btn_undo.setEnabled(can))
        self.btn_undo.setEnabled(False)

        # Ctrl+Z undo within editor
        undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self.line_stack)
        undo_sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        undo_sc.activated.connect(self._undo_stack.undo)

        # Up/Down line navigation
        up   = QShortcut(QKeySequence(Qt.Key.Key_Up),   self.line_stack)
        down = QShortcut(QKeySequence(Qt.Key.Key_Down), self.line_stack)
        up.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        down.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        up.activated.connect(lambda: self.line_stack.navigate_lines(-1))
        down.activated.connect(lambda: self.line_stack.navigate_lines(1))

        self.line_stack._insert_line_after(-1)   # first line, no undo
        self._canvas_ref: Optional["CanvasPanel"] = None

    def set_canvas(self, canvas: "CanvasPanel"):
        self._canvas_ref = canvas
        self.line_stack.print_requested.connect(canvas.print_line)
        self.btn_print_all.clicked.disconnect()
        self.btn_print_all.clicked.connect(lambda: canvas.print_all(self.line_stack.render_all()))

    def receive_glyph(self, glyph: str): self.line_stack.set_glyph_on_active(glyph)
    def load_shape(self, shape: Shape): self.line_stack.load_shape(shape)
    def set_art_font(self, font: QFont, smooth: bool = True): self.line_stack.set_art_font(font, smooth)

    def _save_shape(self):
        dlg = SaveShapeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_name()
            if name: self.save_shape_requested.emit(Shape(name, self.line_stack.to_list()))

    def _print_all_requested(self):
        pass  # replaced when canvas is connected


# ─────────────────────────────────────────────────────────────────────────────
#  Canvas Panel  (central widget)
# ─────────────────────────────────────────────────────────────────────────────

class CanvasPanel(QWidget):
    font_size_changed = pyqtSignal(int)

    def __init__(self, art_font: QFont, parent=None):
        super().__init__(parent)
        self._undo_stack = QUndoStack(self)
        self._undo_stack.setUndoLimit(100)

        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        tb = QHBoxLayout(); tb.setContentsMargins(6,4,6,4); tb.setSpacing(4)
        self.btn_new      = QPushButton("New Canvas")
        self.btn_save_c   = QPushButton("Save Canvas"); self.btn_save_c.setObjectName("btn-accent")
        self.btn_export   = QPushButton("Export Render"); self.btn_export.setObjectName("btn-green")
        self.btn_export.setToolTip("Write canvas to file and open in terminal editor")
        self.btn_undo     = QPushButton("↩ Undo"); self.btn_undo.setObjectName("btn-gold")
        self.btn_undo.setToolTip("Undo last print operation  (Ctrl+Z)")
        for b in (self.btn_new, self.btn_save_c, self.btn_export, self.btn_undo):
            tb.addWidget(b)
        tb.addStretch(1)
        lay.addLayout(tb)

        hint = QLabel("  click row = print target  ·  Ctrl+scroll = font size  ·  Ctrl+Z = undo print")
        hint.setObjectName("canvas-hint"); lay.addWidget(hint)

        self.canvas = CanvasOutput(art_font)
        self.canvas.font_size_changed.connect(self.font_size_changed)
        lay.addWidget(self.canvas, stretch=1)

        self.btn_new.clicked.connect(self._new_canvas)
        self.btn_save_c.clicked.connect(self._save_canvas)
        self.btn_export.clicked.connect(self._export_render)
        self.btn_undo.clicked.connect(self._undo_stack.undo)
        self._undo_stack.canUndoChanged.connect(
            lambda can: self.btn_undo.setEnabled(can))
        self.btn_undo.setEnabled(False)

        # Ctrl+Z for canvas undo (text-edit Ctrl+Z still works inside canvas)
        self._undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        self._undo_sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._undo_sc.activated.connect(self._undo_stack.undo)

    def print_line(self, text: str):
        row = self.canvas.selected_row()
        cmd = CmdPrintLine(self.canvas, row, text)
        cmd._new_text = text
        self._undo_stack.push(cmd)
        self.canvas._write_row(row, text)
        next_row = row + 1
        self.canvas._ensure_row(next_row)
        self.canvas.setTextCursor(QTextCursor(self.canvas.document().findBlockByNumber(next_row)))

    def print_all(self, lines: list[str]):
        start = self.canvas.selected_row()
        cmd = CmdPrintAll(self.canvas, start, lines)
        self._undo_stack.push(cmd)
        self.canvas._write_rows(start, lines)

    def set_art_font(self, font: QFont, smooth: bool = True): self.canvas.set_art_font(font, smooth)
    def set_line_spacing(self, pct: int): self.canvas.set_line_spacing(pct)

    def _new_canvas(self):
        reply = QMessageBox.question(self, "New Canvas", "Clear canvas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._undo_stack.clear()
            self.canvas.new_canvas()

    def _save_canvas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Canvas",
            str(CANVAS_DIR / "canvas.txt"), "Text files (*.txt);;All files (*)")
        if path:
            try: Path(path).write_text(self.canvas.toPlainText(), encoding="utf-8")
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _export_render(self):
        """Save canvas to a temp file and open it in a terminal editor."""
        text = self.canvas.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Export Render", "Canvas is empty."); return

        # Write to Storage/Canvas with timestamp
        import datetime
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = CANVAS_DIR / f"render_{stamp}.txt"
        out_path.write_text(text, encoding="utf-8")

        # Detect terminal editor priority: micro > nano > vim > vi
        editor = None
        for e in ("micro", "nano", "vim", "vi"):
            if shutil.which(e):
                editor = e; break
        if not editor:
            QMessageBox.warning(self, "Export Render",
                f"Saved to:\n{out_path}\n\nNo terminal editor found (micro/nano/vim/vi)."); return

        # Detect terminal priority: konsole > kitty > gnome-terminal > xterm
        terminal_cmd = None
        if shutil.which("konsole"):
            terminal_cmd = ["konsole", "-e", editor, str(out_path)]
        elif shutil.which("kitty"):
            terminal_cmd = ["kitty", editor, str(out_path)]
        elif shutil.which("gnome-terminal"):
            terminal_cmd = ["gnome-terminal", "--", editor, str(out_path)]
        elif shutil.which("xfce4-terminal"):
            terminal_cmd = ["xfce4-terminal", "-e", f"{editor} {out_path}"]
        elif shutil.which("xterm"):
            terminal_cmd = ["xterm", "-e", editor, str(out_path)]
        else:
            QMessageBox.warning(self, "Export Render",
                f"Saved to:\n{out_path}\n\nNo supported terminal found."); return

        try:
            subprocess.Popen(terminal_cmd)
            mw = self.window()
            if hasattr(mw, "status"):
                mw.status.showMessage(
                    f"Opened {out_path.name} in {editor} via {terminal_cmd[0]}")
        except Exception as e:
            QMessageBox.critical(self, "Export Render", str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────────────────────────────────────

class GlyptorumWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLYPTORUM — Glyph Arrangement Studio")
        self.setMinimumSize(900, 560)
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks |
            QMainWindow.DockOption.AnimatedDocks
        )

        self._art_font = QFont("Consolas", 16)

        # ── Font toolbar (dockable too) ──────────────────────────
        self.font_bar = FontBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.font_bar)

        # ── Central widget: canvas ───────────────────────────────
        self.canvas_panel = CanvasPanel(self._art_font)
        self.setCentralWidget(self.canvas_panel)

        # ── Dock: Glyph Sets ─────────────────────────────────────
        self.glyph_set_panel = GlyphSetPanel(self._art_font)
        self.dock_sets = QDockWidget("GLYPH SETS  &  PANES", self)
        self.dock_sets.setObjectName("dock_sets")
        self.dock_sets.setWidget(self.glyph_set_panel)
        self.dock_sets.setMinimumWidth(260)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_sets)

        # ── Dock: Line Editor ────────────────────────────────────
        self.line_editor = LineEditorPanel(self._art_font)
        self.line_editor.set_canvas(self.canvas_panel)
        self.dock_editor = QDockWidget("LINE EDITOR", self)
        self.dock_editor.setObjectName("dock_editor")
        self.dock_editor.setWidget(self.line_editor)
        self.dock_editor.setMinimumHeight(120)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_editor)

        # ── Dock: Shape Library ──────────────────────────────────
        self.shape_panel = ShapeLibraryPanel()
        self.dock_shapes = QDockWidget("SHAPE LIBRARY", self)
        self.dock_shapes.setObjectName("dock_shapes")
        self.dock_shapes.setWidget(self.shape_panel)
        self.dock_shapes.setMinimumWidth(220)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_shapes)

        # ── View menu (toggle docks / toolbar) ───────────────────
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.dock_sets.toggleViewAction())
        view_menu.addAction(self.dock_editor.toggleViewAction())
        view_menu.addAction(self.dock_shapes.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction(self.font_bar.toggleViewAction())
        view_menu.addSeparator()
        reset_act = QAction("Reset Layout", self)
        reset_act.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_act)

        # ── Status bar ───────────────────────────────────────────
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("GLYPTORUM  ready")

        # ── Signal wiring ────────────────────────────────────────
        self.glyph_set_panel.glyph_selected.connect(self.line_editor.receive_glyph)
        self.line_editor.save_shape_requested.connect(self.shape_panel.add_shape)
        self.shape_panel.load_shape_requested.connect(self.line_editor.load_shape)
        self.canvas_panel.font_size_changed.connect(self.font_bar.set_size)
        self.font_bar.font_changed.connect(self._on_font_changed)
        self.font_bar.spacing_changed.connect(self.canvas_panel.set_line_spacing)

        # ── Shortcuts ────────────────────────────────────────────
        QShortcut(QKeySequence("Ctrl+L"),       self, self.glyph_set_panel._load_set)
        QShortcut(QKeySequence("Ctrl+N"),       self, self.glyph_set_panel._create_set)
        QShortcut(QKeySequence("Ctrl+S"),       self, self.canvas_panel._save_canvas)
        QShortcut(QKeySequence("Ctrl+Return"),  self, self._print_all)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.line_editor._save_shape)

        self._restore_session()
        QTimer.singleShot(0, self.font_bar._emit_font)

    # ── font ────────────────────────────────────────────────────

    def _on_font_changed(self, font: QFont):
        self._art_font = font
        smooth = self.font_bar.is_smooth()
        self.glyph_set_panel.set_art_font(font, smooth)
        self.line_editor.set_art_font(font, smooth)
        self.canvas_panel.set_art_font(font, smooth)

    def _print_all(self):
        self.canvas_panel.print_all(self.line_editor.line_stack.render_all())

    # ── layout ──────────────────────────────────────────────────

    def _reset_layout(self):
        self.dock_sets.setFloating(False)
        self.dock_editor.setFloating(False)
        self.dock_shapes.setFloating(False)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,   self.dock_sets)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_editor)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,  self.dock_shapes)
        for d in (self.dock_sets, self.dock_editor, self.dock_shapes): d.show()

    # ── session ─────────────────────────────────────────────────

    def _save_session(self):
        try:
            data = {
                "geometry":  self.saveGeometry().toBase64().data().decode(),
                "state":     self.saveState().toBase64().data().decode(),
                "font":      self.font_bar.state(),
            }
            SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception: pass

    def _restore_session(self):
        if not SESSION_FILE.exists(): return
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            if "geometry" in data:
                self.restoreGeometry(QByteArray.fromBase64(data["geometry"].encode()))
            if "font" in data:
                self.font_bar.restore(data["font"])
            # Restore dock/toolbar state last so geometry is already set
            if "state" in data:
                QTimer.singleShot(50, lambda:
                    self.restoreState(QByteArray.fromBase64(data["state"].encode())))
        except Exception: pass

    def closeEvent(self, event):
        self._save_session(); super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Glyptorum")
    app.setStyleSheet(STYLESHEET)
    win = GlyptorumWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
