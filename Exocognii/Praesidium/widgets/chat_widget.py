#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈   ██████ ██   ██  █████  ████████      ██     ██ ██ ██████   ██████  ███████ ████████ ▍
🮈  ██      ██   ██ ██   ██    ██         ██     ██ ██ ██   ██ ██       ██         ██    ▍
🮈  ██      ███████ ███████    ██         ██  █  ██ ██ ██   ██ ██   ███ █████      ██    ▍
🮈  ██      ██   ██ ██   ██    ██         ██ ███ ██ ██ ██   ██ ██    ██ ██         ██    ▍
🮈   ██████ ██   ██ ██   ██    ██ ███████  ███ ███  ██ ██████   ██████  ███████    ██    ▍
🮈                                                                                       ▍
🮈                                                                                       ▍
🮈                                    Python Script                                      ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
█████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
█🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
█🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
█      PRAESIDIUM · widgets/chat_widget.py  ▍
█▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/chat_widget.py
# Claude conversation widget with ClaudeBox streaming integration.
# Project-aware system prompt injection. Token usage forwarded via signal.
# version: 1.0.0
#
# Threading model:
#   send_threaded() runs in a daemon thread.
#   on_token / on_complete / on_error fire in that thread.
#   We use pyqtSignal to safely cross back to the Qt main thread
#   before touching any widgets.

import sys
from pathlib import Path

# Cross-app token ledger
sys.path.insert(0, str(Path.home() / ".arca"))
try:
    from token_logger import log_usage as _log_usage
except ImportError:
    def _log_usage(*a, **kw): pass

from PyQt6.QtWidgets import (
    QTextEdit, QLineEdit, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QComboBox, QScrollBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor

from widget_base import ArcaneWidget
from configuus import Configuus
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_WHITE, C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

SESSION_ID = "praesidium_chat"

CONTEXT_OPTIONS = [
    ("Tower",    "ArcaCognitorium"),
    ("Praesidium", "Praesidium"),
    ("General",  None),
]


# ---------------------------------------------------------------------------
# Thread-safe signal relay
# We can't emit signals from a non-QObject, and the ClaudeBox callbacks
# fire in a background thread. This relay object lives on the main thread
# and marshals data across via Qt's queued connection mechanism.
# ---------------------------------------------------------------------------

class _Relay(QObject):
    token_received    = pyqtSignal(str)
    response_complete = pyqtSignal(object)   # ClaudeResponse
    error_occurred    = pyqtSignal(str)


# ---------------------------------------------------------------------------
# ChatWidget
# ---------------------------------------------------------------------------

class ChatWidget(ArcaneWidget):
    """
    Claude conversation widget.
    - Streams tokens into the display as they arrive
    - Injects project context into system prompt based on selected context
    - Emits token_used for TokenTracker
    - Clears context on ↺ CLEAR
    """

    token_used = pyqtSignal(str, int, int, str)   # model, input, output, session_id

    def __init__(self, widget_id: str, configuus: Configuus, parent=None):
        super().__init__(widget_id, "Chat — Project Aware", parent)
        self._cfg   = configuus
        self._box   = None
        self._relay = _Relay()
        self._streaming = False
        self._current_response_start = 0   # cursor position where assistant reply begins

        self._relay.token_received.connect(self._on_token_main)
        self._relay.response_complete.connect(self._on_complete_main)
        self._relay.error_occurred.connect(self._on_error_main)

        self._build_body()
        self._init_box()
        self.set_status("idle", "Awaiting the Wizard.")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Chat display
        self._display = QTextEdit()
        self._display.setReadOnly(True)
        self._display.setStyleSheet(
            f"QTextEdit {{"
            f"  background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK};"
            f"  font-family: Georgia, Constantia, serif; font-size: 11px;"
            f"  padding: 6px;"
            f"}}"
        )
        L.addWidget(self._display, 1)

        # Input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter your query…")
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK};"
            f"  font-family: Georgia, serif; font-size: 11px; padding: 5px 8px;"
            f"}}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._input.returnPressed.connect(self.send)
        L.addWidget(self._input)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self._btn_send  = arcane_button("⚗ SEND",   accent=C_TEAL)
        self._btn_clear = arcane_button("🜲 CLEAR",  accent=C_GOLD_DIM)

        self._btn_send.setFixedHeight(26)
        self._btn_clear.setFixedHeight(26)
        self._btn_send.clicked.connect(self.send)
        self._btn_clear.clicked.connect(self.clear_history)

        btn_row.addWidget(self._btn_send)
        btn_row.addWidget(self._btn_clear)
        btn_row.addStretch()

        # Context selector
        lbl_ctx = micro_label("context")
        btn_row.addWidget(lbl_ctx)
        self._ctx_combo = QComboBox()
        self._ctx_combo.setStyleSheet(
            f"QComboBox {{"
            f"  background: {C_BG}; color: {C_GOLD};"
            f"  border: 1px solid {C_GOLD_DARK};"
            f"  font-family: Georgia, serif; font-size: 10px; padding: 2px 6px;"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"  background: {C_PANEL}; color: {C_TEXT}; selection-background-color: {C_GOLD_DARK};"
            f"}}"
        )
        for label, _ in CONTEXT_OPTIONS:
            self._ctx_combo.addItem(label)
        self._ctx_combo.currentIndexChanged.connect(self._on_context_changed)
        btn_row.addWidget(self._ctx_combo)

        L.addLayout(btn_row)

    # ------------------------------------------------------------------
    # ClaudeBox initialisation
    # ------------------------------------------------------------------

    def _init_box(self) -> None:
        claudebox_path = self._cfg.claudebox_path()
        if str(claudebox_path) not in sys.path:
            sys.path.insert(0, str(claudebox_path))
        # Also try parent of claudebox_path (common layout)
        parent = str(claudebox_path.parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)

        try:
            from claudebox import ClaudeBox
            self._box = ClaudeBox()
            self._box.create_session(
                session_id=SESSION_ID,
                system_prompt=self._build_system_prompt(),
            )
            self.set_status("ok", "Connected.")
            self._append_system("The Council is assembled. The Tower listens.")
        except ImportError as e:
            self.set_status("error", f"ClaudeBox not found: {e}")
            self._append_system(f"✕  ClaudeBox import failed.\n{e}\n\nCheck configuus.claudebox_path().")
        except Exception as e:
            self.set_status("error", str(e)[:80])
            self._append_system(f"✕  Initialisation error: {e}")

    def _build_system_prompt(self) -> str:
        idx      = self._ctx_combo.currentIndex() if hasattr(self, "_ctx_combo") else 0
        _, ctx   = CONTEXT_OPTIONS[idx]
        repo     = str(self._cfg.arca_repo_path)
        name     = ctx or "General"

        base = (
            f"You are a knowledgeable assistant integrated into PRAESIDIUM, "
            f"the ambient command centre of the Arca Cognitorium workflow.\n"
            f"Active context: {name}.\n"
            f"Repository root: {repo}.\n"
            f"Respond concisely and with precision. "
            f"You are aware of the Arca Cognitorium project structure and conventions."
        )

        if ctx == "ArcaCognitorium":
            base += (
                f"\n\nYou have deep knowledge of the Arca Cognitorium codebase: "
                f"the Council entities, memory systems (Grimoire, Chronicle, Distillation, EntityMemory), "
                f"the Textual TUI architecture, ClaudeBox integration, and the Exocognii toolchain. "
                f"Refer to the Wizard (LordFingers) in second person."
            )
        elif ctx == "Praesidium":
            base += (
                f"\n\nYou are assisting with the PRAESIDIUM application itself — "
                f"a PyQt6 ambient dashboard. You know its widget architecture, "
                f"ArcaneWidget base class, layout persistence, and ClaudeBox integration."
            )
        return base

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    def send(self) -> None:
        if self._box is None:
            self._append_system("✕  ClaudeBox not initialised.")
            return
        if self._streaming:
            return

        text = self._input.text().strip()
        if not text:
            return

        self._input.clear()
        self._input.setEnabled(False)
        self._btn_send.setEnabled(False)
        self._streaming = True
        self.set_status("warn", "Streaming…")

        self._append_user(text)

        # Mark where the assistant reply will start
        self._display.moveCursor(QTextCursor.MoveOperation.End)
        self._append_label("TOWER  ")
        self._current_response_start = self._display.textCursor().position()

        relay = self._relay

        def on_token(token) -> None:
            t = token.text if hasattr(token, "text") else str(token)
            relay.token_received.emit(t)

        def on_complete(response) -> None:
            # Deregister persistent token handler before signalling complete
            try:
                self._box.off("token", on_token)
            except Exception:
                pass
            try:
                u = response.usage
                _log_usage(
                    app="praesidium",
                    model=getattr(response, "model", "unknown"),
                    input_tokens=getattr(u, "input_tokens", 0),
                    output_tokens=getattr(u, "output_tokens", 0),
                    session_id=SESSION_ID,
                )
            except Exception:
                pass
            relay.response_complete.emit(response)

        def on_error(exc: Exception) -> None:
            try:
                self._box.off("token", on_token)
            except Exception:
                pass
            relay.error_occurred.emit(str(exc))

        # Register as persistent subscription (bus.on, not bus.once)
        # so every token chunk fires, not just the first.
        self._box.on("token", on_token)

        self._box.send_threaded(
            text,
            session_id=SESSION_ID,
            on_complete=on_complete,
            on_error=on_error,
        )

    # ------------------------------------------------------------------
    # Thread → main thread handlers
    # ------------------------------------------------------------------

    def _on_token_main(self, text: str) -> None:
        cursor = self._display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self._display.setTextCursor(cursor)
        self._display.ensureCursorVisible()

    def _on_complete_main(self, response) -> None:
        self._streaming = False
        self._input.setEnabled(True)
        self._btn_send.setEnabled(True)
        self._input.setFocus()

        # Newline after response
        cursor = self._display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText("\n\n")
        self._display.setTextCursor(cursor)

        self.set_status("ok", "Response received.")

        # Forward usage
        usage = response.usage
        self.token_used.emit(
            response.model,
            usage.input_tokens,
            usage.output_tokens,
            SESSION_ID,
        )

    def _on_error_main(self, msg: str) -> None:
        self._streaming = False
        self._input.setEnabled(True)
        self._btn_send.setEnabled(True)
        self._append_system(f"✕  Error: {msg}")
        self.set_status("error", msg[:60])

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _append_user(self, text: str) -> None:
        cursor = self._display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(
            f'<span style="color:{C_GOLD}; font-family:Georgia,serif; font-size:10px; '
            f'letter-spacing:2px;">WIZARD  </span>'
            f'<span style="color:{C_WHITE}; font-family:Georgia,serif; font-size:11px;">'
            f'{text}</span><br><br>'
        )
        self._display.setTextCursor(cursor)
        self._display.ensureCursorVisible()

    def _append_label(self, label: str) -> None:
        cursor = self._display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(
            f'<span style="color:{C_TEAL}; font-family:Georgia,serif; font-size:10px; '
            f'letter-spacing:2px;">{label}</span>'
        )
        self._display.setTextCursor(cursor)

    def _append_system(self, text: str) -> None:
        cursor = self._display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(
            f'<span style="color:{C_GOLD_DIM}; font-family:Georgia,serif; font-size:10px; '
            f'font-style:italic;">{text}</span><br><br>'
        )
        self._display.setTextCursor(cursor)
        self._display.ensureCursorVisible()

    # ------------------------------------------------------------------
    # Context change
    # ------------------------------------------------------------------

    def _on_context_changed(self, _idx: int) -> None:
        if self._box is None:
            return
        # Rebuild session with new system prompt — clears history
        try:
            self._box.delete_session(SESSION_ID)
        except Exception:
            pass
        self._box.create_session(
            session_id=SESSION_ID,
            system_prompt=self._build_system_prompt(),
        )
        ctx_label = self._ctx_combo.currentText()
        self._append_system(f"✦  Context switched to: {ctx_label}")

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def clear_history(self) -> None:
        if self._box:
            try:
                self._box.clear_history(SESSION_ID)
            except Exception:
                pass
        self._display.clear()
        self._append_system("✦  History cleared.")
        self.set_status("idle", "Awaiting the Wizard.")
