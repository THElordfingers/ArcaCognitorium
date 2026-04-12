#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ              bridge/builder_signal_bridge.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import sys
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

sys.path.insert(0, str(Path("~/ArcaCognitorium").expanduser()))
try:
    import token_logger
    _LEDGER_AVAILABLE = True
except ImportError:
    _LEDGER_AVAILABLE = False

logger = logging.getLogger("arx.bridge")

_TOKEN_EVENT = "token"
_USAGE_EVENT = "token_usage"
_SESSION_ID  = "arx_main"


class BuilderSignalBridge(QObject):
    """
    Bridges ClaudeBox callbacks and bus events to Qt signals.

    Conversation history strategy
    ------------------------------
    ClaudeBox.send() accepts a single content string, not a messages array.
    We use box._conversation.replace_history() to load all prior turns into
    a named session, then send only the final user message as a plain string.

    Token streaming pattern
    -----------------------
    box.on("token", handler) registered before each send, removed on complete/error.

    TOKEN_USAGE pattern
    -------------------
    Persistent box.on("token_usage", ...) on __init__. Fires once per response.
    """

    token_received       = pyqtSignal(str)
    response_complete    = pyqtSignal(str)
    error_occurred       = pyqtSignal(str)
    token_usage_updated  = pyqtSignal(int, int)
    phase_changed        = pyqtSignal(str)
    compression_complete = pyqtSignal(str)
    send_started         = pyqtSignal()
    send_finished        = pyqtSignal()

    def __init__(self, box, parent=None) -> None:
        super().__init__(parent)
        self._box = box
        self._active = False
        self._box.on(_USAGE_EVENT, self._on_token_usage)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def send(self, system_block: str, messages_array: list[dict]) -> None:
        """
        Load history into ClaudeBox session, dispatch send_threaded with
        final user message as plain string. Returns immediately.
        """
        if self._active:
            logger.warning("send() called while in flight — ignored.")
            return

        if not messages_array:
            logger.warning("send() called with empty messages_array — ignored.")
            return

        self._active = True

        # All turns except the last go into session history.
        # Last turn must be role=user — becomes send() content.
        history   = messages_array[:-1]
        last_turn = messages_array[-1]
        content   = last_turn.get("content", "")

        # Load history into named session.
        try:
            self._box._conversation.replace_history(_SESSION_ID, history)
        except Exception as exc:
            logger.debug("replace_history failed (%s) — creating session.", exc)
            try:
                self._box.create_session(_SESSION_ID)
                self._box._conversation.replace_history(_SESSION_ID, history)
            except Exception as exc2:
                logger.error("Could not load session history: %s", exc2)

        self._box.on(_TOKEN_EVENT, self._on_token)

        self._box.send_threaded(
            content=content,
            system=system_block,
            session_id=_SESSION_ID,
            on_complete=self._on_complete,
            on_error=self._on_error,
        )

        self.send_started.emit()

    def emit_compression_complete(self, summary_preview: str) -> None:
        self.compression_complete.emit(summary_preview)

    def is_active(self) -> bool:
        return self._active

    def teardown(self) -> None:
        self._box.off(_USAGE_EVENT, self._on_token_usage)
        if self._active:
            self._box.off(_TOKEN_EVENT, self._on_token)
            self._active = False

    # -----------------------------------------------------------------------
    # Callbacks — background thread
    # -----------------------------------------------------------------------

    def _on_token(self, token_obj) -> None:
        text = token_obj.text if hasattr(token_obj, "text") else str(token_obj)
        self.token_received.emit(text)

    def _on_complete(self, response) -> None:
        self._box.off(_TOKEN_EVENT, self._on_token)
        self._active = False
        text = response.text if hasattr(response, "text") else str(response)
        self.response_complete.emit(text or "")
        self.send_finished.emit()

    def _on_error(self, error: Exception) -> None:
        self._box.off(_TOKEN_EVENT, self._on_token)
        self._active = False
        self.error_occurred.emit(str(error))
        self.send_finished.emit()

    def _on_token_usage(self, usage_obj) -> None:
        input_n  = getattr(usage_obj, "input_tokens",  0)
        output_n = getattr(usage_obj, "output_tokens", 0)
        self.token_usage_updated.emit(input_n, output_n)
        if _LEDGER_AVAILABLE:
            try:
                token_logger.write(
                    app="arx_aedificarix",
                    input_tokens=input_n,
                    output_tokens=output_n,
                )
            except Exception as exc:
                logger.debug("Ledger write failed (non-fatal): %s", exc)
