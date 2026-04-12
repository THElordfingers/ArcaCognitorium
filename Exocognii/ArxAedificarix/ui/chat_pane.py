#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                               ui/chat_pane.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.token_gauge import TokenGauge

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


class _InputField(QPlainTextEdit):
    """QPlainTextEdit that submits on Ctrl+Return."""

    submit_requested = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.submit_requested.emit()
            return
        super().keyPressEvent(event)


class _Bubble(QWidget):
    """Single chat message bubble."""

    def __init__(self, role: str, text: str = "", parent=None) -> None:
        super().__init__(parent)
        self._role = role
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        # Role label
        role_label = QLabel(role.upper())
        role_label.setStyleSheet(f"""
            color: {'C_GOLD' if role == 'assistant' else C_GOLD_DIM};
            font-family: Georgia, serif;
            font-size: 9px;
            letter-spacing: 2px;
            font-weight: bold;
        """.replace("'C_GOLD'", C_GOLD))
        layout.addWidget(role_label)

        # Content label
        self._content = QLabel(text)
        self._content.setWordWrap(True)
        self._content.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._content.setStyleSheet(f"""
            color: {C_TEXT if role == 'user' else C_WHITE};
            font-family: Georgia, serif;
            font-size: 11px;
            line-height: 1.5;
        """)
        self._content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        layout.addWidget(self._content)

        bg = C_PANEL if role == "assistant" else C_BG
        border = f"border-left: 2px solid {C_GOLD};" if role == "assistant" else ""
        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                {border}
            }}
        """)

    def append_text(self, text: str) -> None:
        self._content.setText((self._content.text() or "") + text)

    def set_text(self, text: str) -> None:
        self._content.setText(text)

    def text(self) -> str:
        return self._content.text()


class _NoticeWidget(QWidget):
    """Non-bubble informational line (compression notice, errors)."""

    def __init__(self, text: str, colour: str, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {colour};
            font-family: Georgia, serif;
            font-size: 10px;
            font-style: italic;
        """)
        layout.addWidget(label)
        self.setStyleSheet(f"background: {C_BG};")


class ChatPane(QWidget):
    """
    Centre pane. Streaming chat display, phase indicator, attachment chips,
    input field with real-time token estimate.

    Signals
    -------
    send_requested(text, attachment_ids)
        Emitted when Wizard submits a message. MainWindow wires this to
        the send pipeline.
    attachment_add_requested()
        Emitted when Wizard clicks [+] to open AttachmentDialog.
    """

    send_requested          = pyqtSignal(str, list)   # text, active_attachment_ids
    attachment_add_requested = pyqtSignal()

    def __init__(self, token_gauge: TokenGauge, parent=None) -> None:
        super().__init__(parent)
        self._gauge = token_gauge
        self._active_attachment_ids: list[str] = []
        self._streaming_bubble: _Bubble | None = None
        self._last_user_text: str = ""
        self._build_ui()

    # -----------------------------------------------------------------------
    # Public API — message display
    # -----------------------------------------------------------------------

    def append_user_message(self, text: str) -> None:
        """Add a user bubble to the history."""
        bubble = _Bubble("user", text)
        self._insert_widget(bubble)
        self._scroll_to_bottom()

    def append_token(self, text: str) -> None:
        """Append a streaming token to the active assistant bubble."""
        if self._streaming_bubble is None:
            self._streaming_bubble = _Bubble("assistant")
            self._insert_widget(self._streaming_bubble)
        self._streaming_bubble.append_text(text)
        self._scroll_to_bottom()

    def finalise_stream(self, prose: str | None) -> None:
        """
        Called on response_complete. Finalises or removes the streaming bubble.
        prose=None means The Builder produced only file blocks — suppress prose.
        """
        if self._streaming_bubble is not None:
            if prose is None:
                self._messages_layout.removeWidget(self._streaming_bubble)
                self._streaming_bubble.deleteLater()
            else:
                self._streaming_bubble.set_text(prose)
            self._streaming_bubble = None
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)

    def load_history(self, messages: list) -> None:
        """
        Populate chat history from stored messages on conversation restore.
        Clears existing display first.
        """
        self.clear()
        for msg in messages:
            if msg.compressed:
                continue  # compressed turns not shown individually
            if msg.role == "user":
                self.append_user_message(msg.content)
            else:
                bubble = _Bubble("assistant", msg.content)
                self._insert_widget(bubble)
        self._scroll_to_bottom()

    def clear(self) -> None:
        """Remove all message widgets. Called on conversation switch."""
        self._streaming_bubble = None
        while self._messages_layout.count() > 1:  # keep stretch
            item = self._messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # -----------------------------------------------------------------------
    # Public API — state display
    # -----------------------------------------------------------------------

    def set_phase(self, phase: str) -> None:
        """Update phase indicator bar."""
        if phase == "BUILDING":
            self._phase_bar.setText("  ▌ BUILDING")
            self._phase_bar.setStyleSheet(
                f"background: {C_PANEL}; color: {C_GOLD}; "
                f"font-family: Georgia, serif; font-size: 11px; "
                f"font-weight: bold; padding: 4px 0px; "
                f"border-bottom: 1px solid {C_GOLD_DARK};"
            )
        else:
            self._phase_bar.setText("  ▌ DISCUSSION")
            self._phase_bar.setStyleSheet(
                f"background: {C_PANEL}; color: {C_TEAL}; "
                f"font-family: Georgia, serif; font-size: 11px; "
                f"font-weight: bold; padding: 4px 0px; "
                f"border-bottom: 1px solid {C_GOLD_DARK};"
            )

    def show_error(self, message: str) -> None:
        """Render error notice in C_CRIMSON."""
        # Remove incomplete streaming bubble if present
        if self._streaming_bubble is not None:
            self._messages_layout.removeWidget(self._streaming_bubble)
            self._streaming_bubble.deleteLater()
            self._streaming_bubble = None

        notice = _NoticeWidget(
            f"[ connection error — {message} ]", C_CRIMSON
        )
        retry_row = QWidget()
        retry_layout = QHBoxLayout(retry_row)
        retry_layout.setContentsMargins(8, 0, 8, 4)
        retry_btn = QPushButton("↺  Retry")
        retry_btn.setFixedHeight(22)
        retry_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL}; color: {C_CRIMSON};
                border: 1px solid {C_CRIMSON};
                font-family: Georgia, serif; font-size: 10px;
                padding: 2px 10px;
            }}
            QPushButton:hover {{ background: {C_CRIMSON}; color: {C_WHITE}; }}
        """)
        retry_btn.clicked.connect(self._on_retry)
        retry_layout.addWidget(retry_btn)
        retry_layout.addStretch()

        self._insert_widget(notice)
        self._insert_widget(retry_row)
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)
        self._scroll_to_bottom()

    def show_compression_notice(self, summary_preview: str) -> None:
        """Render context compression notice in C_GOLD_DIM italic."""
        n_text = f"[ context compressed — {summary_preview} ]"
        notice = _NoticeWidget(n_text, C_GOLD_DIM)
        self._insert_widget(notice)
        self._scroll_to_bottom()

    def add_attachment_chip(self, attachment) -> None:
        """Add a dismissible chip to the chips row above the input."""
        chip = QPushButton(f"📎 {attachment.filename}  ✕")
        chip.setFixedHeight(22)
        chip.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL}; color: {C_GOLD_DIM};
                border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif; font-size: 10px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{ color: {C_CRIMSON}; border-color: {C_CRIMSON}; }}
        """)
        att_id = attachment.id
        chip.clicked.connect(lambda: self._dismiss_chip(att_id, chip))
        self._chips_layout.addWidget(chip)
        if att_id not in self._active_attachment_ids:
            self._active_attachment_ids.append(att_id)

    def set_send_enabled(self, enabled: bool) -> None:
        self._send_btn.setEnabled(enabled)
        self._input.setEnabled(enabled)

    # -----------------------------------------------------------------------
    # Private — build
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Phase indicator
        self._phase_bar = QLabel("  ▌ DISCUSSION")
        self._phase_bar.setStyleSheet(
            f"background: {C_PANEL}; color: {C_TEAL}; "
            f"font-family: Georgia, serif; font-size: 11px; "
            f"font-weight: bold; padding: 4px 0px; "
            f"border-bottom: 1px solid {C_GOLD_DARK};"
        )
        layout.addWidget(self._phase_bar)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: {C_BG}; border: none; }}
            QScrollBar:vertical {{
                background: {C_PANEL}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self._messages_widget = QWidget()
        self._messages_widget.setStyleSheet(f"background: {C_BG};")
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setContentsMargins(0, 0, 0, 0)
        self._messages_layout.setSpacing(1)
        self._messages_layout.addStretch()
        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll, stretch=1)

        # Attachment chips row
        chips_container = QWidget()
        chips_container.setStyleSheet(f"background: {C_BG};")
        self._chips_layout = QHBoxLayout(chips_container)
        self._chips_layout.setContentsMargins(8, 4, 8, 4)
        self._chips_layout.setSpacing(4)

        add_btn = QPushButton("[+]")
        add_btn.setFixedHeight(22)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL}; color: {C_GOLD_DIM};
                border: 1px solid {C_SUBTLE};
                font-family: Georgia, serif; font-size: 10px;
                padding: 2px 6px;
            }}
            QPushButton:hover {{ color: {C_GOLD}; border-color: {C_GOLD_DARK}; }}
        """)
        add_btn.clicked.connect(self.attachment_add_requested.emit)
        self._chips_layout.addWidget(add_btn)
        self._chips_layout.addStretch()
        layout.addWidget(chips_container)

        # Input separator
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C_GOLD_DARK};")
        layout.addWidget(sep)

        # Input field
        self._input = _InputField()
        self._input.setMaximumHeight(84)
        self._input.setMinimumHeight(52)
        self._input.setPlaceholderText("Address the Builder…")
        self._input.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C_PANEL};
                color: {C_TEXT};
                border: none;
                font-family: Georgia, serif;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.submit_requested.connect(self._on_send)
        layout.addWidget(self._input)

        # Send row
        send_row = QWidget()
        send_row.setStyleSheet(f"background: {C_PANEL}; border-top: 1px solid {C_SUBTLE};")
        send_layout = QHBoxLayout(send_row)
        send_layout.setContentsMargins(8, 4, 8, 4)

        self._token_label = QLabel("0 tok")
        self._token_label.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 10px;"
        )
        send_layout.addWidget(self._token_label)
        send_layout.addStretch()

        self._send_btn = QPushButton("Send")
        self._send_btn.setFixedHeight(26)
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TEAL}; color: {C_WHITE};
                border: 1px solid {C_TEAL};
                font-family: Georgia, serif; font-size: 11px;
                padding: 3px 18px; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: #1f6e6e; border-color: #1f6e6e; }}
            QPushButton:pressed {{ background: #154f4f; }}
            QPushButton:disabled {{ background: {C_SUBTLE}; color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
        """)
        self._send_btn.clicked.connect(self._on_send)
        send_layout.addWidget(self._send_btn)
        layout.addWidget(send_row)

    # -----------------------------------------------------------------------
    # Private — helpers
    # -----------------------------------------------------------------------

    def _insert_widget(self, widget: QWidget) -> None:
        """Insert before the trailing stretch."""
        count = self._messages_layout.count()
        self._messages_layout.insertWidget(count - 1, widget)

    def _scroll_to_bottom(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _on_text_changed(self) -> None:
        text = self._input.toPlainText()
        self._gauge.update_draft(text)
        est = int(len(text.split()) * 1.3)
        self._token_label.setText(f"~{est} tok")

    def _on_send(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        self._last_user_text = text
        self._input.clear()
        self._send_btn.setEnabled(False)
        self._input.setEnabled(False)
        self.send_requested.emit(text, list(self._active_attachment_ids))

    def _on_retry(self) -> None:
        """Re-emit the last user message for retry on API failure."""
        if self._last_user_text:
            self._send_btn.setEnabled(False)
            self._input.setEnabled(False)
            self.send_requested.emit(
                self._last_user_text, list(self._active_attachment_ids)
            )

    def _dismiss_chip(self, att_id: str, chip: QPushButton) -> None:
        """Remove chip from the row; remove id from active list."""
        if att_id in self._active_attachment_ids:
            self._active_attachment_ids.remove(att_id)
        chip.deleteLater()
