#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/panes/left_menu.py
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

from typing import Dict

from textual.containers import Vertical
from textual.events import Key
from textual.widgets import Static, Input, TextArea


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


class MenuCmdInput(Input):
    """Input that intercepts focus hotkeys (Textual 2.1.2-safe)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, str] = {}

    def set_keymap(self, *, focus_left: str, focus_middle: str, focus_right: str) -> None:
        self._keys = {
            "focus_left": _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right": _norm(focus_right),
        }

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)

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


class MenuPageText(TextArea):
    """Read-only text area so menu content is selectable/copyable."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.read_only = True
        self.show_line_numbers = False
        self.wrap = True
        self._keys: Dict[str, str] = {}

    def set_keymap(self, *, focus_left: str, focus_middle: str, focus_right: str) -> None:
        self._keys = {
            "focus_left": _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right": _norm(focus_right),
        }

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)

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


class LeftMenuPane(Vertical):
    def compose(self):
        # Legend stays Static (compact / not usually selected)
        self.legend = Static("", id="legend", markup=False)
        # Menu page becomes selectable/copyable
        self.page = MenuPageText(id="menu_page")
        self.cmd = MenuCmdInput(placeholder="Menu/System commands… (/help)", id="menu_cmd")
        yield self.legend
        yield self.page
        yield self.cmd

    def set_legend(self, text: str) -> None:
        self.legend.update(text or "")

    def set_page(self, text: str) -> None:
        self.page.text = text or ""

    def focus_input(self) -> None:
        self.cmd.focus()
