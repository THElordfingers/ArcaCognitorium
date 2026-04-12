# GNOSIUM EXANIMA — ui/conversation_view.py
# v1.0.0
"""
Chat bubble area for the conversation. Handles streaming token append,
wizard-right / entity-left layout, [EntityName] prefix colouring,
manual-scroll pause, and inline system messages.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from ..constants import (
    C_BG, C_CRIMSON, C_GOLD, C_GOLD_DARK, C_GOLD_DIM, C_PANEL,
    C_SUBTLE, C_TEAL, C_TEXT, FONT_STACK,
)


class ConversationView(QScrollArea):
    """Scrollable chat bubble stack."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(
            f"QScrollArea {{ background: {C_BG}; border: none; }}"
            f"QScrollBar:vertical {{ background: {C_PANEL}; width: 10px; }}"
            f"QScrollBar::handle:vertical {{ background: {C_GOLD_DARK}; min-height: 32px; }}"
        )

        self._host = QWidget()
        self._host.setStyleSheet(f"background: {C_BG};")
        self._layout = QVBoxLayout(self._host)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(10)
        self._layout.addStretch(1)
        self.setWidget(self._host)

        self._auto_scroll = True
        self._streaming_bubble: Optional[_Bubble] = None
        self._empty_label: Optional[QLabel] = None

        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

    # ── Public API ───────────────────────────────────────────────
    def clear(self) -> None:
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        if self._empty_label is not None:
            self._empty_label.deleteLater()
            self._empty_label = None

    def show_empty_state(self, text: str) -> None:
        self.clear()
        self._empty_label = QLabel(text)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.setStyleSheet(
            f"color: {C_GOLD_DIM}; background: {C_BG}; "
            f"font-family: {FONT_STACK}; font-size: 11pt; padding: 40px;"
        )
        self._layout.insertWidget(self._layout.count() - 1, self._empty_label)

    def append_wizard(self, text: str) -> None:
        self._finalise_streaming_bubble()
        bubble = _Bubble(role="wizard")
        bubble.set_text(text)
        self._insert_bubble(bubble)

    def append_entity(self, text: str) -> None:
        """Finalised (non-streamed) entity message."""
        self._finalise_streaming_bubble()
        bubble = _Bubble(role="entity")
        bubble.set_text(text)
        self._insert_bubble(bubble)

    def append_system(self, text: str) -> None:
        """Inline system notice — e.g. Cognosis failure."""
        self._finalise_streaming_bubble()
        bubble = _Bubble(role="system")
        bubble.set_text(text)
        self._insert_bubble(bubble)

    def begin_streaming_entity_bubble(self) -> None:
        self._finalise_streaming_bubble()
        self._streaming_bubble = _Bubble(role="entity")
        self._insert_bubble(self._streaming_bubble)

    def append_streaming_token(self, token: str) -> None:
        if self._streaming_bubble is None:
            self.begin_streaming_entity_bubble()
        assert self._streaming_bubble is not None
        self._streaming_bubble.append_token(token)
        self._maybe_autoscroll()

    def finalise_streaming_bubble(self, full_text: Optional[str] = None) -> None:
        if self._streaming_bubble is None:
            return
        if full_text is not None:
            self._streaming_bubble.set_text(full_text)
        self._streaming_bubble = None

    # ── Internals ────────────────────────────────────────────────
    def _insert_bubble(self, bubble: "_Bubble") -> None:
        if self._empty_label is not None:
            self._empty_label.deleteLater()
            self._empty_label = None
        # Insert before the trailing stretch
        self._layout.insertWidget(self._layout.count() - 1, bubble)
        self._maybe_autoscroll()

    def _finalise_streaming_bubble(self) -> None:
        self._streaming_bubble = None

    def _on_scroll(self, value: int) -> None:
        sb = self.verticalScrollBar()
        at_bottom = value >= sb.maximum() - 4
        self._auto_scroll = at_bottom

    def _maybe_autoscroll(self) -> None:
        if not self._auto_scroll:
            return
        QTimer.singleShot(
            0,
            lambda: self.verticalScrollBar().setValue(
                self.verticalScrollBar().maximum()
            ),
        )


class _Bubble(QFrame):
    """A single chat message bubble."""

    def __init__(self, role: str):
        super().__init__()
        self.role = role
        self._text = ""
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMaximumWidth(720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        self._label = QLabel("")
        self._label.setWordWrap(True)
        self._label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._label.setFont(QFont("Georgia", 10))
        layout.addWidget(self._label)

        self._apply_style()

        self._timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.setToolTip(self._timestamp)

    def _apply_style(self) -> None:
        if self.role == "wizard":
            self.setStyleSheet(
                f"QFrame {{ background: {C_PANEL}; border: 1px solid {C_GOLD_DARK}; }}"
                f"QLabel {{ color: {C_GOLD}; font-family: Georgia, serif; }}"
            )
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        elif self.role == "entity":
            self.setStyleSheet(
                f"QFrame {{ background: {C_PANEL}; border: 1px solid {C_TEAL}; }}"
                f"QLabel {{ color: {C_TEAL}; font-family: Georgia, serif; }}"
            )
        else:  # system
            self.setStyleSheet(
                f"QFrame {{ background: {C_BG}; border: 1px dashed {C_SUBTLE}; }}"
                f"QLabel {{ color: {C_GOLD_DIM}; font-family: Georgia, serif; "
                f"font-style: italic; }}"
            )

    def set_text(self, text: str) -> None:
        self._text = text
        self._label.setText(_format_with_prefix(text, self.role))

    def append_token(self, token: str) -> None:
        self._text += token
        self._label.setText(_format_with_prefix(self._text, self.role))


def _format_with_prefix(text: str, role: str) -> str:
    """
    Entity responses may begin with [Entity Name] — render the prefix
    in C_CRIMSON bold using Qt rich-text.
    """
    if role != "entity":
        return _escape(text)

    import re
    pattern = re.compile(r"\[([^\]]+)\]")
    out: list[str] = []
    last_end = 0
    for match in pattern.finditer(text):
        out.append(_escape(text[last_end:match.start()]))
        name = _escape(match.group(1))
        out.append(
            f'<span style="color:{C_CRIMSON};font-weight:bold;">[{name}]</span>'
        )
        last_end = match.end()
    out.append(_escape(text[last_end:]))
    return "".join(out).replace("\n", "<br>")


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
