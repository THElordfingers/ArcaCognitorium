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


_INPUT_HEIGHT_MIN = 3
_INPUT_HEIGHT_MAX = 20
_INPUT_HEIGHT_DEFAULT = 6


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


class ChatInput(TextArea):
    """
    TextArea that:
      - Intercepts configured hotkeys and forwards to the App
      - Ctrl+Up expands its own height
      - Ctrl+Down shrinks its own height
      - Resize only adjusts this widget — the current_turn scroll above it
        absorbs the change via 1fr layout.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, str] = {}
        self._input_height: int = _INPUT_HEIGHT_DEFAULT

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

    def _set_height(self, h: int) -> None:
        self._input_height = max(_INPUT_HEIGHT_MIN, min(_INPUT_HEIGHT_MAX, h))
        self.styles.height = self._input_height

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)

        # Ctrl+Up — grow input
        if k == "ctrl+up":
            self._set_height(self._input_height + 1)
            event.stop()
            return

        # Ctrl+Down — shrink input
        if k == "ctrl+down":
            self._set_height(self._input_height - 1)
            event.stop()
            return

        if k and k == self._keys.get("submit"):
            self.app.action_submit_message()
            event.stop()
            if hasattr(event, "prevent_default"):
                event.prevent_default()
            return

        if k and k == self._keys.get("focus_left"):
            self.app.action_focus_left()
            event.stop()
            return

        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle()
            event.stop()
            return

        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right()
            event.stop()
            return

        if self._keys.get("copy_last") and k == self._keys.get("copy_last"):
            if hasattr(self.app, "action_copy_last"):
                self.app.action_copy_last()
            event.stop()
            return


class ActiveChatPane(Vertical):
    def compose(self):
        self.current_turn = VerticalScroll(id="current_turn")
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
