#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/ui/panes/active_chat.py
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════




from __future__ import annotations

from typing import Optional, Dict

from textual.containers import Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import TextArea


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


class ChatInput(TextArea):
    """
    Invocation Field — the Wizard's primary input.

    Key behaviour:
      Enter            — submit message
      Shift+Enter      — insert newline (multi-line messages)
      Configured key   — also submits (F2 by default)
      Ctrl+Up/Down     — resize input area (increase/decrease height)
      Ctrl+arrows      — passed through for text navigation (not intercepted)
      Focus keys       — pane focus switching
    """

    MIN_HEIGHT = 3
    MAX_HEIGHT = 30

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, str] = {}
        self._input_height: int = 6  # matches CSS default

    def set_keymap(
        self,
        *,
        submit: str,
        focus_left: str,
        focus_middle: str,
        focus_right: str,
        copy_last: Optional[str] = None,
    ) -> None:
        self._keys = {
            "submit": _norm(submit),
            "focus_left": _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right": _norm(focus_right),
            "copy_last": _norm(copy_last or ""),
        }

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)

        # Shift+Enter — insert newline, do NOT submit
        if k == "shift+enter":
            self.insert("\n")
            event.stop()
            if hasattr(event, "prevent_default"):
                event.prevent_default()
            return

        # Enter alone — submit
        if k == "enter":
            self.app.action_submit_message()
            event.stop()
            if hasattr(event, "prevent_default"):
                event.prevent_default()
            return

        # Configured submit key (F2 etc)
        if k and k == self._keys.get("submit"):
            self.app.action_submit_message()
            event.stop()
            if hasattr(event, "prevent_default"):
                event.prevent_default()
            return

        # Ctrl+Up — increase input height
        if k == "ctrl+up":
            self._input_height = min(self.MAX_HEIGHT, self._input_height + 2)
            self.styles.height = self._input_height
            event.stop()
            return

        # Ctrl+Down — decrease input height
        if k == "ctrl+down":
            self._input_height = max(self.MIN_HEIGHT, self._input_height - 2)
            self.styles.height = self._input_height
            event.stop()
            return

        # Ctrl+Left / Ctrl+Right — word navigation, pass through to TextArea
        # Do NOT intercept — let Textual handle these natively

        # Pane focus switching
        if k and k == self._keys.get("focus_left"):
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return

        # Copy last
        if self._keys.get("copy_last") and k == self._keys.get("copy_last"):
            if hasattr(self.app, "action_copy_last"):
                self.app.action_copy_last()
            event.stop()
            return


class ScrollableChat(VerticalScroll):
    """
    Chat pane scroll container.
    Supports keyboard scroll shortcuts when focused.
    Page Up/Down and Home/End scroll the current turn view.
    """

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)
        if k == "pageup":
            self.scroll_page_up(animate=False)
            event.stop()
            return
        if k == "pagedown":
            self.scroll_page_down(animate=False)
            event.stop()
            return
        if k == "home":
            self.scroll_home(animate=False)
            event.stop()
            return
        if k == "end":
            self.scroll_end(animate=False)
            event.stop()
            return


class ActiveChatPane(Vertical):
    def compose(self):
        self.current_turn = ScrollableChat(id="current_turn")
        self.chat_input = ChatInput(id="chat_input")
        yield self.current_turn
        yield self.chat_input

    def clear_current_turn(self) -> None:
        self.current_turn.remove_children()

    def get_chat_text(self) -> str:
        return self.chat_input.text

    def set_chat_text(self, text: str) -> None:
        self.chat_input.text = text

    def focus_input(self) -> None:
        self.chat_input.focus()

    def scroll_to_bottom(self) -> None:
        self.current_turn.scroll_end(animate=False)
