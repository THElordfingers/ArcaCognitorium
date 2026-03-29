"""
workers.py — Dolium v2
AmbientWorker: debounced ambient whisper thread.
ConversationWorker: explicit user message thread.
Both emit token_received(str), complete(), error(str).
Both use the same ClaudeBox session per idea (shared history).
"""

from __future__ import annotations

import sys
import json
import os
from pathlib import Path

# ── ClaudeBox path resolution ─────────────────────────────────────────────────
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
    CLAUDEBOX_AVAILABLE = True
except ImportError:
    CLAUDEBOX_AVAILABLE = False

from PyQt6.QtCore import QThread, pyqtSignal


# ── AmbientWorker ─────────────────────────────────────────────────────────────

class AmbientWorker(QThread):
    """
    Fires an ambient whisper after debounce. Created fresh per debounce event.
    Uses the idea's ClaudeBox session — shares history with ConversationWorker.

    Lifecycle:
        Created in WorkspacePanel._on_debounce_fire()
        Started immediately after creation
        Cleaned up via finished signal in ChamberPanel
    """

    token_received = pyqtSignal(str)
    complete       = pyqtSignal()
    error          = pyqtSignal(str)

    def __init__(
        self,
        box:        "ClaudeBox | None",
        session_id: str,
        content:    str,
        system:     str,
    ):
        super().__init__()
        self._box        = box
        self._session_id = session_id
        self._content    = content
        self._system     = system

    def run(self) -> None:
        if not CLAUDEBOX_AVAILABLE or self._box is None:
            self.error.emit("ClaudeBox not available")
            self.complete.emit()
            return

        # Suppress whisper if content is too thin
        if len(self._content.strip()) < 60:
            self.complete.emit()
            return

        try:
            self._box.send_threaded(
                content    = self._content,
                session_id = self._session_id,
                system     = self._system,
                on_token   = self._on_token,
                on_complete= self._on_complete,
                on_error   = self._on_error,
            )
        except Exception as e:
            self.error.emit(str(e))
            self.complete.emit()

    def _on_token(self, token: str) -> None:
        self.token_received.emit(token)

    def _on_complete(self) -> None:
        self.complete.emit()

    def _on_error(self, msg: str) -> None:
        self.error.emit(msg)
        self.complete.emit()


# ── ConversationWorker ────────────────────────────────────────────────────────

class ConversationWorker(QThread):
    """
    Fires an explicit conversation message. Created per Send action.
    Uses the same ClaudeBox session as AmbientWorker — shared history.

    ChamberPanel sets _conv_active=True before starting this worker,
    and clears it on complete() — AmbientWorker checks this flag.
    """

    token_received = pyqtSignal(str)
    complete       = pyqtSignal()
    error          = pyqtSignal(str)

    def __init__(
        self,
        box:        "ClaudeBox | None",
        session_id: str,
        content:    str,
        system:     str,
    ):
        super().__init__()
        self._box        = box
        self._session_id = session_id
        self._content    = content
        self._system     = system

    def run(self) -> None:
        if not CLAUDEBOX_AVAILABLE or self._box is None:
            self.error.emit("ClaudeBox not available")
            self.complete.emit()
            return

        try:
            self._box.send_threaded(
                content    = self._content,
                session_id = self._session_id,
                system     = self._system,
                on_token   = self._on_token,
                on_complete= self._on_complete,
                on_error   = self._on_error,
            )
        except Exception as e:
            self.error.emit(str(e))
            self.complete.emit()

    def _on_token(self, token: str) -> None:
        self.token_received.emit(token)

    def _on_complete(self) -> None:
        self.complete.emit()

    def _on_error(self, msg: str) -> None:
        self.error.emit(msg)
        self.complete.emit()
