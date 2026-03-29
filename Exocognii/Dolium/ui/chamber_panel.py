"""
ui/chamber_panel.py — Dolium v2
ChamberPanel: right panel with whisper stream (top) and conversation (bottom).
Manages AmbientWorker and ConversationWorker lifecycle.
_conv_active flag prevents QThread collision.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit,
    QLineEdit, QPushButton, QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont

import style
from models import Idea, ConversationTurn
from store import IdeaStore
from workers import AmbientWorker, ConversationWorker, CLAUDEBOX_AVAILABLE
from prompts import get_system_prompt, build_user_message, build_whisper_context, WHISPER_SYSTEM


class ChamberPanel(QWidget):

    message_sent = pyqtSignal(str)

    def __init__(self, store: IdeaStore, parent=None):
        super().__init__(parent)
        self._store       = store
        self._idea: Idea | None = None
        self._box         = None  # ClaudeBox instance — set by main window
        self._session_id  = ""
        self._conv_active = False
        self._ambient_worker: AmbientWorker | None = None
        self._conv_worker:   ConversationWorker | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Splitter: whisper stream (top) / conversation (bottom) ────────────
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {style.C_BORDER};
            }}
        """)

        # ── Whisper stream ────────────────────────────────────────────────────
        whisper_container = QWidget()
        whisper_container.setStyleSheet(f"background-color: {style.C_BG};")
        w_layout = QVBoxLayout(whisper_container)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setSpacing(0)

        whisper_header = QWidget()
        whisper_header.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-bottom: 1px solid {style.C_BORDER};
        """)
        wh_layout = QHBoxLayout(whisper_header)
        wh_layout.setContentsMargins(10, 5, 10, 5)
        lbl = style.dim_label("WHISPERS", size=8)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {style.C_DIM};
                font-family: Georgia, Constantia, serif;
                font-size: 8px;
                letter-spacing: 2px;
            }}
        """)
        wh_layout.addWidget(lbl)
        wh_layout.addStretch()
        w_layout.addWidget(whisper_header)

        self._whisper_edit = style.whisper_text_edit()
        self._whisper_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        w_layout.addWidget(self._whisper_edit)
        splitter.addWidget(whisper_container)

        # ── Conversation ──────────────────────────────────────────────────────
        conv_container = QWidget()
        conv_container.setStyleSheet(f"background-color: {style.C_BG};")
        c_layout = QVBoxLayout(conv_container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        conv_header = QWidget()
        conv_header.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-bottom: 1px solid {style.C_BORDER};
        """)
        ch_layout = QHBoxLayout(conv_header)
        ch_layout.setContentsMargins(10, 5, 10, 5)
        conv_lbl = style.dim_label("CONVERSATION", size=8)
        conv_lbl.setStyleSheet(f"""
            QLabel {{
                color: {style.C_DIM};
                font-family: Georgia, Constantia, serif;
                font-size: 8px;
                letter-spacing: 2px;
            }}
        """)
        ch_layout.addWidget(conv_lbl)
        ch_layout.addStretch()
        self._entity_label = style.dim_label("", size=8)
        ch_layout.addWidget(self._entity_label)
        c_layout.addWidget(conv_header)

        self._conv_edit = style.conversation_text_edit()
        self._conv_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        c_layout.addWidget(self._conv_edit)

        # Input row
        input_row = QWidget()
        input_row.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-top: 1px solid {style.C_BORDER};
        """)
        i_layout = QHBoxLayout(input_row)
        i_layout.setContentsMargins(8, 6, 8, 6)
        i_layout.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("speak to the chamber...")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {style.C_BG};
                color: {style.C_TEXT};
                border: 1px solid {style.C_BORDER};
                border-radius: 2px;
                padding: 5px 8px;
                font-family: Georgia, Constantia, serif;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border-color: {style.C_GOLD_DIM};
            }}
        """)
        self._input.returnPressed.connect(self._on_send)

        self._send_btn = style.arcane_button("Send")
        self._send_btn.setFixedWidth(50)
        self._send_btn.clicked.connect(self._on_send)

        i_layout.addWidget(self._input)
        i_layout.addWidget(self._send_btn)
        c_layout.addWidget(input_row)
        splitter.addWidget(conv_container)

        splitter.setSizes([200, 400])
        layout.addWidget(splitter)

        self._set_input_enabled(False)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_box(self, box) -> None:
        """Receives ClaudeBox instance from main window."""
        self._box = box

    def load_idea(self, idea: Idea) -> None:
        """Switch to a different idea. Replays conversation history."""
        self._idea      = idea
        self._session_id = idea.id
        self._conv_active = False

        self._whisper_edit.clear()
        self._conv_edit.clear()

        # Replay stored conversation
        for turn in idea.conversation:
            if turn.is_whisper:
                self._append_whisper_history(turn.content)
            else:
                self._append_conv_turn(turn.role, turn.content)

        # Update entity label
        from models import CHAMBER_NAMES
        self._entity_label.setText(f"The {CHAMBER_NAMES.get(idea.chamber, '')}")

        self._set_input_enabled(True)

    def clear(self) -> None:
        self._idea = None
        self._session_id = ""
        self._whisper_edit.clear()
        self._conv_edit.clear()
        self._set_input_enabled(False)

    # ── Whisper handling ──────────────────────────────────────────────────────

    def on_whisper_requested(self, field_name: str, text: str, idea: Idea) -> None:
        """Called from WorkspacePanel when debounce fires."""
        if self._conv_active:
            return  # Conversation in progress — suppress whisper

        if self._ambient_worker and self._ambient_worker.isRunning():
            self._ambient_worker.terminate()
            self._ambient_worker.wait(200)

        context = build_whisper_context(idea, field_name, text)

        self._ambient_worker = AmbientWorker(
            box        = self._box,
            session_id = self._session_id,
            content    = context,
            system     = WHISPER_SYSTEM,
        )
        self._ambient_worker.token_received.connect(self._on_whisper_token)
        self._ambient_worker.complete.connect(self._on_whisper_complete)
        self._ambient_worker.error.connect(self._on_whisper_error)
        self._ambient_worker.finished.connect(self._ambient_worker.deleteLater)

        # Mark start of new whisper
        self._append_whisper_separator()
        self._ambient_worker.start()

    def _on_whisper_token(self, token: str) -> None:
        cursor = self._whisper_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_DIM))
        cursor.setCharFormat(fmt)
        cursor.insertText(token)

        self._whisper_edit.setTextCursor(cursor)
        self._whisper_edit.ensureCursorVisible()

    def _on_whisper_complete(self) -> None:
        # Store the whisper in conversation history
        if self._idea:
            whisper_text = self._get_last_whisper_text()
            if whisper_text.strip():
                turn = ConversationTurn(
                    role="assistant", content=whisper_text, is_whisper=True
                )
                self._idea.conversation.append(turn)
                self._store.update(self._idea)

    def _on_whisper_error(self, msg: str) -> None:
        cursor = self._whisper_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_CRIMSON))
        cursor.setCharFormat(fmt)
        cursor.insertText(f" [—]")
        self._whisper_edit.setTextCursor(cursor)

    # ── Conversation handling ─────────────────────────────────────────────────

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text or not self._idea:
            return
        if self._conv_active:
            return

        self._input.clear()
        self._conv_active = True
        self._set_input_enabled(False)

        # Append user turn
        self._append_conv_turn("user", text)

        # Persist user turn
        turn = ConversationTurn(role="user", content=text)
        self._idea.conversation.append(turn)
        self._store.update(self._idea)

        # Build full context message
        full_content = build_user_message(self._idea, text)
        system       = get_system_prompt(self._idea.chamber)

        self._conv_worker = ConversationWorker(
            box        = self._box,
            session_id = self._session_id,
            content    = full_content,
            system     = system,
        )
        self._conv_worker.token_received.connect(self._on_conv_token)
        self._conv_worker.complete.connect(self._on_conv_complete)
        self._conv_worker.error.connect(self._on_conv_error)
        self._conv_worker.finished.connect(self._conv_worker.deleteLater)

        # Start assistant bubble
        self._start_assistant_bubble()
        self._conv_worker.start()
        self.message_sent.emit(text)

    def _on_conv_token(self, token: str) -> None:
        cursor = self._conv_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_TEXT))
        cursor.setCharFormat(fmt)
        cursor.insertText(token)

        self._conv_edit.setTextCursor(cursor)
        self._conv_edit.ensureCursorVisible()

    def _on_conv_complete(self) -> None:
        self._conv_active = False
        self._set_input_enabled(True)

        # Persist assistant turn
        if self._idea:
            assistant_text = self._get_last_conv_text()
            if assistant_text.strip():
                turn = ConversationTurn(role="assistant", content=assistant_text)
                self._idea.conversation.append(turn)
                self._store.update(self._idea)

    def _on_conv_error(self, msg: str) -> None:
        self._conv_active = False
        self._set_input_enabled(True)
        cursor = self._conv_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_CRIMSON))
        cursor.setCharFormat(fmt)
        cursor.insertText(f"\n[error: {msg}]\n")
        self._conv_edit.setTextCursor(cursor)

    # ── Text helpers ──────────────────────────────────────────────────────────

    def _append_whisper_separator(self) -> None:
        cursor = self._whisper_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if not self._whisper_edit.toPlainText().strip():
            cursor.insertText("")
            return
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_BORDER))
        cursor.setCharFormat(fmt)
        cursor.insertText("\n · \n")
        self._whisper_edit.setTextCursor(cursor)

    def _append_whisper_history(self, text: str) -> None:
        cursor = self._whisper_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if self._whisper_edit.toPlainText().strip():
            cursor.insertText("\n · \n")
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(style.C_DIM))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self._whisper_edit.setTextCursor(cursor)

    def _append_conv_turn(self, role: str, content: str) -> None:
        cursor = self._conv_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if self._conv_edit.toPlainText().strip():
            cursor.insertText("\n\n")

        # Role label
        fmt_role = QTextCharFormat()
        if role == "user":
            fmt_role.setForeground(QColor(style.C_GOLD_DIM))
            label = "Wizard"
        else:
            fmt_role.setForeground(QColor(style.C_GOLD))
            label = self._get_entity_name()
        cursor.setCharFormat(fmt_role)
        cursor.insertText(f"{label}\n")

        # Content
        fmt_text = QTextCharFormat()
        fmt_text.setForeground(QColor(style.C_TEXT))
        cursor.setCharFormat(fmt_text)
        cursor.insertText(content)

        self._conv_edit.setTextCursor(cursor)
        self._conv_edit.ensureCursorVisible()

    def _start_assistant_bubble(self) -> None:
        cursor = self._conv_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if self._conv_edit.toPlainText().strip():
            cursor.insertText("\n\n")

        fmt_role = QTextCharFormat()
        fmt_role.setForeground(QColor(style.C_GOLD))
        cursor.setCharFormat(fmt_role)
        cursor.insertText(f"{self._get_entity_name()}\n")

        fmt_text = QTextCharFormat()
        fmt_text.setForeground(QColor(style.C_TEXT))
        cursor.setCharFormat(fmt_text)

        self._conv_edit.setTextCursor(cursor)

    def _get_last_whisper_text(self) -> str:
        """Extract the text of the most recent whisper from the stream."""
        full = self._whisper_edit.toPlainText()
        parts = full.split(" · ")
        return parts[-1].strip() if parts else ""

    def _get_last_conv_text(self) -> str:
        """Extract the last assistant response from the conversation display."""
        full = self._conv_edit.toPlainText()
        # Find last entity label and extract text after it
        entity = self._get_entity_name()
        idx = full.rfind(f"{entity}\n")
        if idx >= 0:
            return full[idx + len(entity) + 1:].strip()
        return ""

    def _get_entity_name(self) -> str:
        if self._idea:
            from models import CHAMBER_NAMES
            return CHAMBER_NAMES.get(self._idea.chamber, "The Chamber")
        return "The Chamber"

    def _set_input_enabled(self, enabled: bool) -> None:
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)
        if enabled:
            self._input.setFocus()
