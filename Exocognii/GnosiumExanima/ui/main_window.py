# GNOSIUM EXANIMA — ui/main_window.py
# v1.0.0
"""
Main window — stitches together entity panel, conversation view, input
bar, status strip, token warning bar, and the ClaudeBoxManager.

This is the orchestration layer. Rules it enforces:
  - One ClaudeBoxManager per mode. Switching mode swaps the manager.
  - Every entity toggle, mode switch, or session switch destroys and
    rebuilds the ClaudeBox instance via manager.rebuild() with a fresh
    composite prompt and reloaded history.
  - Every wizard message and every entity response goes through the
    store before it is rendered, so a reload after crash replays the
    entire conversation.
  - Streaming callbacks thread-hop back onto the GUI thread via
    invokeMethod-style Qt signals.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QInputDialog, QMainWindow, QMenu, QMessageBox,
    QVBoxLayout, QWidget,
)

from .. import __version__
from ..config import GnosiumConfig
from ..constants import (
    APP_NAME, APP_SUBTITLE, C_BG, C_GOLD, C_GOLD_DARK, C_PANEL,
    DEFAULT_WINDOW_H, DEFAULT_WINDOW_W, MIN_WINDOW_H, MIN_WINDOW_W,
    MODE_CHAMBER, MODE_SOLO, RAW_TAIL_MESSAGES,
)
from ..entity.models import EntityPackage
from ..entity.vault_scanner import scan_vault
from ..prompt.composite import build_chamber_prompt, build_solo_prompt
from ..prompt.tokens import estimate_tokens
from ..claudebox_manager.box_manager import (
    ClaudeBoxManager, ClaudeBoxUnavailable,
)
from ..claudebox_manager.distiller import Distiller
from ..session.manager import SessionManager
from ..session.store import SessionStore, SessionRow
from ..connectivity.nuntius_emit import emit_event
from ..connectivity.mundana import MundanaWatcher
from ..connectivity.cognosis import CognosisClient, CognosisError
from ..connectivity.context_assembler import ContextAssembler

from .conversation_view import ConversationView
from .entity_panel import EntityPanel
from .input_bar import InputBar
from .session_dialog import SessionDialog
from .status_strip import StatusStrip
from .token_warning_bar import TokenWarningBar

logger = logging.getLogger("gnosium.ui")


# ─── Qt-thread bridge ──────────────────────────────────────────────
class _StreamBridge(QObject):
    """
    ClaudeBox callbacks fire on worker threads. This bridge emits Qt
    signals that the main window connects to with auto-connection,
    which marshals them back onto the GUI thread.
    """
    token_received   = pyqtSignal(str)
    stream_complete  = pyqtSignal(object)
    stream_failed    = pyqtSignal(object)


# ─── Main window ───────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, config: GnosiumConfig):
        super().__init__()
        self._cfg = config
        self._mode = MODE_CHAMBER
        self._entities: list[EntityPackage] = []
        self._entities_by_id: dict[str, EntityPackage] = {}

        # Persistence + managers
        self._store = SessionStore(self._cfg.sqlite_path)
        self._session_mgr = SessionManager(self._store)
        try:
            self._claudebox = ClaudeBoxManager(self._cfg.arca_repo_path)
            self._claudebox_error: Optional[str] = None
        except ClaudeBoxUnavailable as exc:
            self._claudebox = None  # type: ignore
            self._claudebox_error = str(exc)
            logger.error("ClaudeBox unavailable: %s", exc)
        self._distiller = Distiller()
        self._cognosis = CognosisClient(
            exvacua_loricum_url=self._cfg.exvacua_loricum_api,
            perpetuum_aedificare_url=self._cfg.perpetuum_aedificare_api,
            praesidium_url=self._cfg.praesidium_api,
        )

        self._context_assembler = ContextAssembler(self._cognosis)

        # Ambient state
        self._mundana_watcher = MundanaWatcher(
            self._cfg.mundana_state_file,
            poll_seconds=self._cfg.mundana_poll_seconds,
            parent=self,
        )
        self._mundana_summary: Optional[str] = None
        self._mundana_dirty = False  # inject into next prompt rebuild

        # Streaming bridge
        self._bridge = _StreamBridge(self)
        self._bridge.token_received.connect(self._on_token_received)
        self._bridge.stream_complete.connect(self._on_stream_complete)
        self._bridge.stream_failed.connect(self._on_stream_failed)

        # Current-session cursors
        self._current_session: Optional[SessionRow] = None
        self._current_response_accumulator: str = ""

        self._build_ui()
        self._wire_signals()
        self._restore_geometry()
        self._load_vault()
        self._boot_current_session()
        self._start_mundana()

    # ── Construction ─────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE}")
        self.setMinimumSize(MIN_WINDOW_W, MIN_WINDOW_H)
        self.resize(DEFAULT_WINDOW_W, DEFAULT_WINDOW_H)
        self.setStyleSheet(f"background: {C_BG}; color: {C_GOLD};")

        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet(f"background: {C_BG};")

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ─── Central horizontal split ────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # LEFT: entity panel + token warning bar (stacked)
        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(0)
        self._entity_panel = EntityPanel()
        self._token_warning = TokenWarningBar()
        left_col.addWidget(self._entity_panel, 1)
        left_col.addWidget(self._token_warning, 0)
        left_wrap = QWidget()
        left_wrap.setLayout(left_col)
        left_wrap.setStyleSheet(f"background: {C_BG};")
        body.addWidget(left_wrap)

        # RIGHT: conversation + input
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(0)
        self._conversation = ConversationView()
        self._input_bar = InputBar()
        right_col.addWidget(self._conversation, 1)
        right_col.addWidget(self._input_bar, 0)
        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        right_wrap.setStyleSheet(f"background: {C_BG};")
        body.addWidget(right_wrap, 1)

        outer.addLayout(body, 1)

        # Status strip
        self._status = StatusStrip()
        outer.addWidget(self._status, 0)

        self._build_menu()

    def _build_menu(self) -> None:
        mbar = self.menuBar()
        mbar.setStyleSheet(
            f"QMenuBar {{ background: {C_PANEL}; color: {C_GOLD}; border-bottom: 1px solid {C_GOLD_DARK}; }}"
            f"QMenuBar::item:selected {{ background: {C_GOLD_DARK}; }}"
            f"QMenu {{ background: {C_PANEL}; color: {C_GOLD}; border: 1px solid {C_GOLD_DARK}; }}"
            f"QMenu::item:selected {{ background: {C_GOLD_DARK}; }}"
        )

        session_menu: QMenu = mbar.addMenu("Session")
        session_menu.addAction(self._action("New session", self._action_new_session))
        session_menu.addAction(self._action("Switch…", self._action_switch_session))
        session_menu.addSeparator()
        session_menu.addAction(self._action("Rename current…", self._action_rename_session))

        cogno_menu: QMenu = mbar.addMenu("Cognosis")
        cogno_menu.addAction(self._action("Lore search…", self._action_lore_search))
        cogno_menu.addAction(self._action("Recent builds", self._action_recent_builds))
        cogno_menu.addAction(self._action("Praesidium status", self._action_praesidium_status))

        view_menu: QMenu = mbar.addMenu("View")
        view_menu.addAction(self._action("Reload vault", self._load_vault))

        about_menu: QMenu = mbar.addMenu("About")
        about_menu.addAction(self._action(f"Version {__version__}", lambda: None))

    def _action(self, label: str, callback) -> QAction:
        act = QAction(label, self)
        act.triggered.connect(callback)
        return act

    def _wire_signals(self) -> None:
        self._entity_panel.mode_changed.connect(self._on_mode_changed)
        self._entity_panel.selection_changed.connect(self._on_selection_changed)
        self._input_bar.submitted.connect(self._on_wizard_submit)
        self._mundana_watcher.state_changed.connect(self._on_mundana_update)
        self._mundana_watcher.connected.connect(
            lambda: self._status.set_mundana_state("connected", connected=True)
        )
        self._mundana_watcher.disconnected.connect(
            lambda reason: self._status.set_mundana_state(
                f"disconnected ({reason})", connected=False
            )
        )

    # ── Boot + persistence ───────────────────────────────────────
    def _restore_geometry(self) -> None:
        state_path = self._cfg.window_state_path
        if not state_path.exists():
            return
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            if "geometry" in data:
                x, y, w, h = data["geometry"]
                self.setGeometry(x, y, max(w, MIN_WINDOW_W), max(h, MIN_WINDOW_H))
            mode = data.get("mode")
            if mode in (MODE_CHAMBER, MODE_SOLO):
                self._mode = mode
                self._entity_panel.set_mode(mode)
        except Exception as exc:
            logger.warning("geometry restore failed: %s", exc)

    def _save_geometry(self) -> None:
        state_path = self._cfg.window_state_path
        try:
            g = self.geometry()
            state_path.write_text(json.dumps({
                "geometry": [g.x(), g.y(), g.width(), g.height()],
                "mode": self._mode,
            }, indent=2))
        except Exception as exc:
            logger.warning("geometry save failed: %s", exc)

    def closeEvent(self, event) -> None:
        self._save_geometry()
        self._mundana_watcher.stop()
        self._store.close()
        super().closeEvent(event)

    # ── Vault loading ────────────────────────────────────────────
    def _load_vault(self) -> None:
        result = scan_vault(
            self._cfg.vault_path_primary,
            self._cfg.vault_path_legacy,
        )
        self._entities = result.packages
        self._entities_by_id = {e.entity_id: e for e in result.packages}
        self._entity_panel.set_entities(result.packages)

        if not result.packages:
            self._conversation.show_empty_state(
                "No entity packages found in vault.\n\n"
                "Use ENTITEX to generate entity packages, then reload via "
                "the View menu."
            )
            self._input_bar.set_enabled(False)
            return

        self._input_bar.set_enabled(True)

    def _boot_current_session(self) -> None:
        if not self._entities:
            return

        # Default entity selection: first one only (safe)
        default_ids = [self._entities[0].entity_id]
        self._entity_panel.set_active(default_ids)

        current = self._session_mgr.get_or_create_current(self._mode, default_ids)
        self._current_session = current

        # If the session has prior messages with different active entities,
        # honour those instead
        if current.active_entities:
            self._entity_panel.set_active(current.active_entities)

        self._rebuild_for_current_session()
        self._replay_conversation()

    def _start_mundana(self) -> None:
        self._mundana_watcher.start()

    # ── Prompt rebuilds ──────────────────────────────────────────
    def _active_entities(self) -> list[EntityPackage]:
        ids = self._entity_panel.active_entity_ids()
        return [self._entities_by_id[i] for i in ids if i in self._entities_by_id]

    def _build_current_prompt(self) -> str:
        entities = self._active_entities()
        perpetuum = self._context_assembler.perpetuum_summary()
        exvacua = self._context_assembler.exvacua_summary()
        if self._mode == MODE_SOLO:
            if not entities:
                return ""
            return build_solo_prompt(
                entities[0],
                mundana_context=self._mundana_summary,
                perpetuum_context=perpetuum,
                exvacua_context=exvacua,
                tower_memory_root=self._cfg.tower_entity_memory_root,
            )
        return build_chamber_prompt(
            entities,
            mundana_context=self._mundana_summary,
            perpetuum_context=perpetuum,
            exvacua_context=exvacua,
            tower_memory_root=self._cfg.tower_entity_memory_root,
        )

    def _rebuild_for_current_session(self) -> None:
        if self._claudebox is None:
            self._conversation.show_empty_state(
                f"ClaudeBox unavailable: {self._claudebox_error}\n\n"
                "Check that ~/ArcaCognitorium/claudebox/ is present and "
                "CLAUDE_API_KEY is set in your environment."
            )
            self._input_bar.set_enabled(False)
            return

        if self._current_session is None:
            return

        prompt = self._build_current_prompt()
        if not prompt:
            self._input_bar.set_enabled(False)
            return

        history = self._store.load_messages(self._current_session.id)
        try:
            self._claudebox.rebuild(prompt, history=history)
        except Exception as exc:
            logger.exception("ClaudeBox rebuild failed")
            self._conversation.append_system(f"ClaudeBox rebuild failed: {exc}")
            self._input_bar.set_enabled(False)
            return

        self._check_token_budget(prompt)
        self._input_bar.set_enabled(True)

    def _replay_conversation(self) -> None:
        if self._current_session is None:
            return
        self._conversation.clear()
        for msg in self._store.load_messages(self._current_session.id):
            if msg.role == "wizard":
                self._conversation.append_wizard(msg.content)
            else:
                self._conversation.append_entity(msg.content)

    def _check_token_budget(self, prompt: str) -> None:
        tokens = estimate_tokens(prompt)
        ceiling = self._cfg.system_prompt_token_ceiling
        self._status.set_token_count(tokens)
        if tokens > ceiling:
            self._token_warning.show_warning(tokens, len(self._active_entities()))
        else:
            self._token_warning.clear()

    # ── Mode / selection handlers ────────────────────────────────
    def _on_mode_changed(self, mode: str) -> None:
        self._mode = mode
        # Load or create a current session for this mode
        active = self._entity_panel.active_entity_ids() or (
            [self._entities[0].entity_id] if self._entities else []
        )
        self._current_session = self._session_mgr.get_or_create_current(mode, active)
        self._entity_panel.set_active(self._current_session.active_entities or active)
        self._rebuild_for_current_session()
        self._replay_conversation()
        emit_event("session_lifecycle", {"event": "mode_switch", "mode": mode})

    def _on_selection_changed(self, active_ids: list) -> None:
        if self._current_session is None:
            return
        self._store.update_session(
            self._current_session.id, active_entities=list(active_ids),
        )
        self._current_session.active_entities = list(active_ids)
        for eid in active_ids:
            self._store.touch_entity(eid)
        self._rebuild_for_current_session()

    # ── Wizard input ─────────────────────────────────────────────
    def _on_wizard_submit(self, text: str) -> None:
        if self._current_session is None or self._claudebox is None:
            return
        if not self._claudebox.is_ready:
            self._rebuild_for_current_session()
            if not self._claudebox.is_ready:
                self._conversation.append_system("ClaudeBox not ready.")
                return

        # Persist and render the wizard message
        wizard_row = self._store.append_message(
            self._current_session.id, role="wizard", content=text,
        )
        self._conversation.append_wizard(text)

        # Auto-title on first message
        new_title = self._session_mgr.apply_auto_title_if_needed(
            self._current_session, text
        )
        if new_title:
            self.setWindowTitle(
                f"{APP_NAME} — {new_title}"
            )

        emit_event("conversation", {
            "event": "wizard_message",
            "session_id": self._current_session.id,
            "mode": self._mode,
            "message_id": wizard_row.id,
        })

        # Lock input during streaming
        self._input_bar.set_enabled(False)
        self._current_response_accumulator = ""
        self._conversation.begin_streaming_entity_bubble()

        self._claudebox.send(
            text,
            on_token=self._forward_token,
            on_complete=self._forward_complete,
            on_error=self._forward_error,
        )

    # ── Thread-safe forwards (called from worker threads) ───────
    def _forward_token(self, token) -> None:
        text = getattr(token, "text", None)
        if text is None:
            text = str(token)
        self._bridge.token_received.emit(text)

    def _forward_complete(self, response) -> None:
        self._bridge.stream_complete.emit(response)

    def _forward_error(self, exc) -> None:
        self._bridge.stream_failed.emit(exc)

    # ── GUI-thread slots ─────────────────────────────────────────
    def _on_token_received(self, text: str) -> None:
        self._current_response_accumulator += text
        self._conversation.append_streaming_token(text)

    def _on_stream_complete(self, response) -> None:
        final_text = (
            getattr(response, "text", None)
            or self._current_response_accumulator
        )
        self._conversation.finalise_streaming_bubble(full_text=final_text)

        if self._current_session is not None and final_text:
            row = self._store.append_message(
                self._current_session.id,
                role="entity",
                content=final_text,
                entity_id=None,   # composite response — entities self-prefix
            )
            emit_event("conversation", {
                "event": "entity_response",
                "session_id": self._current_session.id,
                "message_id": row.id,
            })
            # Log usage if the response carries it
            self._log_token_usage(response)
            self._maybe_distill()

        self._current_response_accumulator = ""
        self._input_bar.set_enabled(True)
        self._input_bar.set_focus()

    def _on_stream_failed(self, exc) -> None:
        partial = self._current_response_accumulator
        self._conversation.finalise_streaming_bubble(full_text=partial)
        self._conversation.append_system(f"Stream failed: {exc}")
        if partial and self._current_session is not None:
            self._store.append_message(
                self._current_session.id,
                role="entity",
                content=f"[partial] {partial}",
            )
        self._current_response_accumulator = ""
        self._input_bar.set_enabled(True)

    def _log_token_usage(self, response) -> None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        try:
            from token_logger import log_usage  # type: ignore
        except ImportError:
            return
        try:
            log_usage(
                app="gnosium_exanima",
                model=getattr(response, "model", "unknown"),
                input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
                output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
                session_id=self._current_session.id if self._current_session else "default",
            )
        except Exception:
            pass

    def _maybe_distill(self) -> None:
        if self._current_session is None:
            return
        threshold = self._cfg.distillation_threshold
        if self._store.message_count(self._current_session.id) <= threshold + RAW_TAIL_MESSAGES:
            return
        # Run distillation in a one-shot timer so we don't block GUI
        QTimer.singleShot(0, self._run_distillation)

    def _run_distillation(self) -> None:
        if self._current_session is None:
            return
        try:
            self._distiller.distill_if_needed(
                self._store, self._current_session.id,
                self._cfg.distillation_threshold,
            )
        except Exception as exc:
            logger.warning("distillation error: %s", exc)

    # ── Mundana ──────────────────────────────────────────────────
    def _on_mundana_update(self, data: dict) -> None:
        # Build a short summary string for the status strip and for the
        # optional mundana_context block in the next prompt rebuild
        try:
            cosmetic = data.get("cosmetic", {})
            behaviour = data.get("behaviour", {})
            summary = (
                f"pal={cosmetic.get('palette_key', '?')} "
                f"int={cosmetic.get('intensity', 0):.2f} "
                f"pot={behaviour.get('potency', 0):.2f}"
            )
        except Exception:
            summary = "active"
        self._mundana_summary = _format_mundana_block(data)
        self._status.set_mundana_state(summary, connected=True)

    # ── Session menu actions ─────────────────────────────────────
    def _action_new_session(self) -> None:
        active = self._entity_panel.active_entity_ids() or (
            [self._entities[0].entity_id] if self._entities else []
        )
        self._current_session = self._session_mgr.new_session(self._mode, active)
        self._entity_panel.set_active(active)
        self._rebuild_for_current_session()
        self._conversation.clear()
        emit_event("session_lifecycle", {
            "event": "session_created",
            "session_id": self._current_session.id,
            "mode": self._mode,
        })

    def _action_switch_session(self) -> None:
        dlg = SessionDialog(self._session_mgr, self._mode, parent=self)
        if dlg.exec() == 0:
            return
        if dlg.created_new_session:
            self._action_new_session()
            return
        if dlg.selected_session_id:
            row = self._session_mgr.switch_to(dlg.selected_session_id)
            if row is not None:
                self._current_session = row
                self._entity_panel.set_active(row.active_entities)
                self._rebuild_for_current_session()
                self._replay_conversation()

    def _action_rename_session(self) -> None:
        if self._current_session is None:
            return
        text, ok = QInputDialog.getText(
            self, "Rename session", "Title:",
            text=self._current_session.title or "",
        )
        if ok and text.strip():
            self._store.update_session(
                self._current_session.id, title=text.strip(),
            )
            self._current_session.title = text.strip()
            self.setWindowTitle(f"{APP_NAME} — {text.strip()}")

    # ── Cognosis menu actions ────────────────────────────────────
    def _action_lore_search(self) -> None:
        term, ok = QInputDialog.getText(self, "Lore search", "Term:")
        if not ok or not term.strip():
            return
        try:
            result = self._cognosis.lore_search(term.strip())
        except CognosisError as exc:
            self._conversation.append_system(f"Lore search failed: {exc}")
            return
        self._conversation.append_system(f"Lore search → {result}")

    def _action_recent_builds(self) -> None:
        try:
            result = self._cognosis.build_recent()
        except CognosisError as exc:
            self._conversation.append_system(f"Build query failed: {exc}")
            return
        self._conversation.append_system(f"Recent builds → {result}")

    def _action_praesidium_status(self) -> None:
        try:
            result = self._cognosis.praesidium_status()
        except CognosisError as exc:
            self._conversation.append_system(f"Praesidium status failed: {exc}")
            return
        self._conversation.append_system(f"Praesidium → {result}")


def _format_mundana_block(data: dict) -> str:
    """Convert the raw state dict into a compact prompt injection block."""
    meta = data.get("meta", {})
    cosmetic = data.get("cosmetic", {})
    behaviour = data.get("behaviour", {})
    lines = [
        "Ambient Mundana state:",
        f"  timestamp: {meta.get('ts', '?')}",
        f"  palette: {cosmetic.get('palette_key', '?')} "
        f"(sat={cosmetic.get('saturation', 0):.2f}, "
        f"int={cosmetic.get('intensity', 0):.2f})",
        f"  potency: {behaviour.get('potency', 0):.2f}",
        f"  dasha: {behaviour.get('dasha_planet', '?')}",
    ]
    if behaviour.get("disruptive"):
        lines.append("  status: DISRUPTIVE")
    return "\n".join(lines)
