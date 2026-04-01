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
from datetime import datetime, timezone
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

LOG_PATH = Path.home() / '.arca' / 'token_log.jsonl'


def _write_token_log(session_id: str, model: str, input_tokens: int, output_tokens: int) -> None:
    """Append one record to the shared cross-app token ledger."""
    record = {
        "ts":            datetime.now(timezone.utc).isoformat(),
        "app":           "dolium",
        "model":         model,
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "session_id":    session_id,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
    except OSError:
        pass


# ── AmbientWorker ─────────────────────────────────────────────────────────────

class AmbientWorker(QThread):
    """
    Fires an ambient whisper after debounce. Created fresh per debounce event.
    Uses the idea's ClaudeBox session — shares history with ConversationWorker.

    Lifecycle:
        Created in ChamberPanel.on_whisper_requested()
        Started immediately after creation
        Cleaned up via finished.connect(deleteLater) in ChamberPanel

    Uses box.stream() generator directly — avoids bus.once() single-token
    limitation of send_threaded().
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
            for token in self._box.stream(
                self._content,
                session_id = self._session_id,
                system     = self._system,
            ):
                self.token_received.emit(token)

            # Log token usage after stream completes
            try:
                usage = self._box.get_token_usage(self._session_id)
                model = self._box.config_snapshot().model
                _write_token_log(self._session_id, model, usage.input_tokens, usage.output_tokens)
            except Exception:
                pass

            self.complete.emit()
        except Exception as e:
            self.error.emit(str(e))
            self.complete.emit()


# ── ConversationWorker ────────────────────────────────────────────────────────

class ConversationWorker(QThread):
    """
    Fires an explicit conversation message. Created per Send action.
    Uses the same ClaudeBox session as AmbientWorker — shared history.

    ChamberPanel sets _conv_active=True before starting this worker,
    and clears it on complete() — AmbientWorker checks this flag.

    Uses box.stream() generator directly — avoids bus.once() single-token
    limitation of send_threaded().
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
            for token in self._box.stream(
                self._content,
                session_id = self._session_id,
                system     = self._system,
            ):
                self.token_received.emit(token)

            # Log token usage after stream completes
            try:
                usage = self._box.get_token_usage(self._session_id)
                model = self._box.config_snapshot().model
                _write_token_log(self._session_id, model, usage.input_tokens, usage.output_tokens)
            except Exception:
                pass

            self.complete.emit()
        except Exception as e:
            self.error.emit(str(e))
            self.complete.emit()
