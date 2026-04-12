"""
ui/main_window.py — Dolium v2
DoliumWindow: main QMainWindow. Three-panel QSplitter.
Owns ClaudeBox instance and IdeaStore. Wires all inter-panel signals.
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QHBoxLayout,
    QStatusBar, QMenuBar, QMenu,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QAction

import style
from store import IdeaStore
from models import Idea
from chambers import GateEngine
from export import ExportEngine
from ui.pipeline_panel import PipelinePanel
from ui.workspace_panel import WorkspacePanel
from ui.chamber_panel import ChamberPanel
from ui.dialogs import (
    NewIdeaDialog, AdvanceDialog, ReturnToDialog, CullDialog,
    DeclarationDialog, ExportDialog, CullRegisterDialog,
)
from nuntius_emit import emit_event

# ── ClaudeBox import ──────────────────────────────────────────────────────────
_config_file = Path.home() / '.arca' / 'config.json'
_repo_path   = str(Path.home() / 'ArcaCognitorium')
try:
    with _config_file.open() as _f:
        _arca_cfg = json.load(_f)
    _repo_path = _arca_cfg.get('arca_repo_path', _repo_path)
except (OSError, json.JSONDecodeError):
    pass
if _repo_path not in sys.path:
    sys.path.insert(0, _repo_path)

try:
    from claudebox import ClaudeBox
    _CLAUDEBOX_OK = True
except ImportError:
    _CLAUDEBOX_OK = False


class DoliumWindow(QMainWindow):

    def __init__(self, store: IdeaStore, storage_dir: Path):
        super().__init__()
        self._store       = store
        self._storage_dir = storage_dir
        self._active_idea: Idea | None = None
        self._box = None
        self._sessions: dict[str, str] = {}  # idea_id → session_id (same as idea_id)

        self._init_claudebox()
        self._build_ui()
        self._build_menu()
        self._wire_signals()

        self.setWindowTitle("◆  The Dolium")
        self.setMinimumSize(QSize(1050, 680))
        self.resize(1280, 800)

        # Report any load errors
        if store.load_error:
            self._status.showMessage(f"⚠  {store.load_error}", 8000)
        elif not _CLAUDEBOX_OK:
            self._status.showMessage(
                "ClaudeBox not found — conversation disabled. Set CLAUDE_API_KEY and check ArcaCognitorium path.",
                10000,
            )
        else:
            self._status.showMessage("The Dolium attends.", 3000)

    # ── Init ──────────────────────────────────────────────────────────────────

    def _init_claudebox(self) -> None:
        if not _CLAUDEBOX_OK:
            return
        api_key = os.environ.get("CLAUDE_API_KEY")
        if not api_key:
            return
        try:
            self._box = ClaudeBox(
                system_prompt = "You are the entity of The Dolium.",
                api_key       = api_key,
            )
        except Exception as e:
            self._box = None

    def _build_ui(self) -> None:
        # Central widget + outer layout
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Three-panel splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setChildrenCollapsible(False)

        self._pipeline = PipelinePanel(self._store)
        self._workspace = WorkspacePanel(self._store)
        self._chamber   = ChamberPanel(self._store)

        if self._box:
            self._chamber.set_box(self._box)

        self._splitter.addWidget(self._pipeline)
        self._splitter.addWidget(self._workspace)
        self._splitter.addWidget(self._chamber)
        self._splitter.setSizes([260, 580, 340])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 3)
        self._splitter.setStretchFactor(2, 1)

        outer.addWidget(self._splitter)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.setStyleSheet(f"""
            QStatusBar {{
                background-color: {style.C_PANEL};
                color: {style.C_DIM};
                border-top: 1px solid {style.C_BORDER};
                font-family: Georgia, Constantia, serif;
                font-size: 10px;
                padding: 2px 8px;
            }}
        """)

    def _build_menu(self) -> None:
        bar = self.menuBar()
        bar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                border-bottom: 1px solid {style.C_BORDER};
                font-family: Georgia, Constantia, serif;
                font-size: 10px;
            }}
            QMenuBar::item:selected {{
                background-color: {style.C_GOLD_DARK};
                color: {style.C_GOLD};
            }}
            QMenu {{
                background-color: {style.C_PANEL};
                color: {style.C_TEXT};
                border: 1px solid {style.C_BORDER};
            }}
            QMenu::item:selected {{
                background-color: {style.C_GOLD_DARK};
                color: {style.C_GOLD};
            }}
        """)

        # Idea menu
        idea_menu = bar.addMenu("Idea")

        act_new = QAction("New Idea", self)
        act_new.setShortcut(QKeySequence("Ctrl+N"))
        act_new.triggered.connect(self._on_new_idea)
        idea_menu.addAction(act_new)

        act_advance = QAction("Advance", self)
        act_advance.setShortcut(QKeySequence("Ctrl+A"))
        act_advance.triggered.connect(self._on_advance)
        idea_menu.addAction(act_advance)

        act_return = QAction("Return to Chamber...", self)
        act_return.triggered.connect(self._on_return_to)
        idea_menu.addAction(act_return)

        act_cull = QAction("Cull Idea", self)
        act_cull.triggered.connect(self._on_cull)
        idea_menu.addAction(act_cull)

        idea_menu.addSeparator()

        act_export = QAction("Export...", self)
        act_export.setShortcut(QKeySequence("Ctrl+E"))
        act_export.triggered.connect(self._on_export)
        idea_menu.addAction(act_export)

        # View menu
        view_menu = bar.addMenu("View")

        act_culls = QAction("Cull Register", self)
        act_culls.triggered.connect(self._on_cull_register)
        view_menu.addAction(act_culls)

    def _wire_signals(self) -> None:
        self._pipeline.idea_selected.connect(self._on_idea_selected)
        self._pipeline.new_idea_clicked.connect(self._on_new_idea)

        self._workspace.field_changed.connect(self._on_field_changed)
        self._workspace.whisper_requested.connect(self._chamber.on_whisper_requested)
        self._workspace.advance_requested.connect(self._on_advance)
        self._workspace.return_requested.connect(self._on_return_to)
        self._workspace.cull_requested.connect(self._on_cull)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_idea_selected(self, idea_id: str) -> None:
        idea = self._store.get(idea_id)
        if not idea:
            return
        self._active_idea = idea
        self._workspace.load_idea(idea)
        self._chamber.load_idea(idea)
        self._status.showMessage(
            f"The Dolium attends.  {idea.chamber_name()}  ·  {idea.title or '(untitled)'}",
            0
        )

    def _on_new_idea(self) -> None:
        dlg = NewIdeaDialog(self)
        if dlg.exec() and dlg.title:
            idea = self._store.create(dlg.title)
            self._pipeline.refresh(select_id=idea.id)
            self._on_idea_selected(idea.id)
            self._status.showMessage(f"New idea: '{idea.title}'", 3000)

    def _on_advance(self) -> None:
        if not self._active_idea:
            return

        from models import CHAMBER_CODEX
        if self._active_idea.chamber == CHAMBER_CODEX:
            result = GateEngine.gate_declaration(self._active_idea)
            dlg = DeclarationDialog(self._active_idea, result, self)
            if dlg.exec():
                self._on_export()
            return

        result = GateEngine.gate_for_current_chamber(self._active_idea)
        dlg = AdvanceDialog(self._active_idea, result, self)
        if dlg.exec() and result.passed:
            from_chamber = self._active_idea.chamber
            self._store.advance(self._active_idea)
            emit_event("idea_graduated", {
                "idea_id": self._active_idea.id,
                "from_chamber": from_chamber,
                "to_chamber": self._active_idea.chamber,
                "title": self._active_idea.title or "",
            })
            self._pipeline.refresh(select_id=self._active_idea.id)
            self._workspace.load_idea(self._active_idea)
            self._chamber.load_idea(self._active_idea)
            self._status.showMessage(
                f"Advanced to {self._active_idea.chamber_name()}", 3000
            )

    def _on_return_to(self) -> None:
        if not self._active_idea or self._active_idea.chamber <= 1:
            return
        dlg = ReturnToDialog(self._active_idea, self)
        if dlg.exec() and dlg.selected_chamber:
            self._store.return_to(self._active_idea, dlg.selected_chamber)
            self._pipeline.refresh(select_id=self._active_idea.id)
            self._workspace.load_idea(self._active_idea)
            self._chamber.load_idea(self._active_idea)

    def _on_cull(self) -> None:
        if not self._active_idea:
            return
        dlg = CullDialog(self._active_idea, self)
        if dlg.exec():
            self._store.cull(self._active_idea, dlg.reason)
            self._active_idea = None
            self._workspace.clear()
            self._chamber.clear()
            self._pipeline.refresh()
            self._status.showMessage("Idea culled.", 3000)

    def _on_export(self) -> None:
        if not self._active_idea:
            return
        engine  = ExportEngine(self._storage_dir / "exports")
        results = engine.export_all(self._active_idea)
        emit_event("documentum_aedificii_complete", {
            "idea_id": self._active_idea.id,
            "title": self._active_idea.title or "",
            "output_path": str(next((v for v in results.values() if v), "")),
        })
        dlg     = ExportDialog(self._active_idea, results, self)
        dlg.exec()

    def _on_cull_register(self) -> None:
        culled = self._store.all_culled()
        dlg    = CullRegisterDialog(culled, self)
        if dlg.exec() and dlg.selected_id:
            resurrected = self._store.resurrect(dlg.selected_id)
            if resurrected:
                self._pipeline.refresh(select_id=resurrected.id)
                self._on_idea_selected(resurrected.id)
                self._status.showMessage(
                    f"Resurrected: '{resurrected.title}'", 3000
                )

    def _on_field_changed(self, field_name: str, text: str) -> None:
        # Refresh pipeline if title changed
        if field_name == "title" and self._active_idea:
            self._pipeline.refresh(select_id=self._active_idea.id)
