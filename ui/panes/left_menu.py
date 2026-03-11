#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/ui/panes/left_menu.py
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════




from __future__ import annotations

from typing import Dict, List, Optional

from textual.containers import Vertical
from textual.events import Key
from textual.widgets import Static, Input, TextArea


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


class MenuCmdInput(Input):
    """Input that intercepts focus hotkeys."""

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
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return


class MenuPageText(TextArea):
    """Read-only text area — menu content is selectable/copyable."""

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
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return


_NAV_DIVIDER = "─" * 24


def _build_home_nav(council_lines: Optional[List[str]] = None) -> str:
    """Build the home nav text, injecting current Council state."""
    council_block = _format_council_block(council_lines)
    return (
        "◆ THREADS\n"
        "◆ PROJECTS\n"
        "\n"
        + council_block
        + "\n"
        "◆ THE GRIMOIRE\n"
        + _NAV_DIVIDER + "\n"
        "◇ CONJURATION  (/conjure)\n"
        "◇ HELP         (/help)\n"
    )


def _format_council_block(council_lines: Optional[List[str]]) -> str:
    if not council_lines:
        return "◆ THE COUNCIL\n     The Council stirs…\n"
    lines = ["◆ THE COUNCIL"]
    for entry in council_lines:
        lines.append(f"     {entry}")
    return "\n".join(lines) + "\n"


class LeftMenuPane(Vertical):
    """
    Left navigation pane.

    Sections (top to bottom):
      legend      — machine state strip (Static, compact)
      menu_page   — lore-structured nav + page content (MenuPageText)
      menu_cmd    — slash-command input (MenuCmdInput)

    Public API used by app.py:
      set_legend(text)          — update the state strip
      set_page(text)            — replace full page content
      set_council(lines)        — update THE COUNCIL section silently
      focus_input()             — focus the command input
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._council_lines: List[str] = []

    def compose(self):
        self.legend = Static("", id="legend", markup=False)
        self.page = MenuPageText(id="menu_page")
        self.cmd = MenuCmdInput(
            placeholder="◇ /help · /new · /summon · /conjure …",
            id="menu_cmd",
        )
        yield self.legend
        yield self.page
        yield self.cmd

    def on_mount(self) -> None:
        self.page.text = _build_home_nav(self._council_lines)

    def set_legend(self, text: str) -> None:
        self.legend.update(text or "")

    def set_page(self, text: str) -> None:
        """Replace the full page content (used when navigating to sub-pages)."""
        self.page.text = text or ""

    def set_council(self, council_lines: List[str]) -> None:
        """
        Update THE COUNCIL section of the home nav with emerged Entity names.
        Called silently after emergence checks — no announcement.

        council_lines: list of display strings, e.g. ["◆ THE CONTRARIAN", "◆ THE ARCHIVIST"]
        """
        self._council_lines = council_lines or []
        # Only refresh if currently on the home nav
        current = self.page.text or ""
        if "◆ THE COUNCIL" in current and "◇ CONJURATION" in current:
            self.page.text = _build_home_nav(self._council_lines)

    def focus_input(self) -> None:
        self.cmd.focus()
