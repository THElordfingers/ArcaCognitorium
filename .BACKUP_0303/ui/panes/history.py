#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/panes/history.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

from typing import Dict, List, Tuple

from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.events import Key
from textual.widgets import Input, Button, Static


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


class HistorySearchInput(Input):
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


class ThreadTabsBar(Horizontal):
    """
    Tabs implemented as Buttons (Textual 2.1.2-safe).

    IMPORTANT:
      - Do NOT define a method named _render on a Textual widget.
        Textual uses Widget._render internally for painting.
    """

    ID_PREFIX = "threadtab-"
    EMPTY_ID = "threadtabs-empty"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tabs: List[Tuple[str, str, bool]] = []

    def set_tabs(self, tabs: List[Tuple[str, str, bool]]) -> None:
        self._tabs = tabs
        self._sync_tabs()

    def _existing_tab_buttons(self) -> Dict[str, Button]:
        """Returns mapping tid -> Button for currently mounted threadtab buttons."""
        out: Dict[str, Button] = {}
        for child in list(self.children):
            if isinstance(child, Button) and (child.id or "").startswith(self.ID_PREFIX):
                tid = (child.id or "")[len(self.ID_PREFIX) :]
                if tid:
                    out[tid] = child
        return out

    def _remove_empty_placeholder(self) -> None:
        for child in list(self.children):
            if isinstance(child, Static) and child.id == self.EMPTY_ID:
                child.remove()

    def _sync_tabs(self) -> None:
        # Case: no threads
        if not self._tabs:
            for child in list(self.children):
                child.remove()
            self.mount(Static("Threads: (none)", id=self.EMPTY_ID, markup=False))
            return

        # We have tabs: ensure placeholder is gone
        self._remove_empty_placeholder()

        existing = self._existing_tab_buttons()
        desired_tids = [tid for tid, _name, _active in self._tabs]

        # Update existing / mount missing
        for tid, name, active in self._tabs:
            label = name or tid
            variant = "primary" if active else "default"

            btn = existing.get(tid)
            if btn is None:
                # Textual-safe id: only letters/numbers/_/-
                btn = Button(label, id=f"{self.ID_PREFIX}{tid}", variant=variant)
                self.mount(btn)
                continue

            # Update in place (avoids remove+readd races)
            try:
                btn.label = label
            except Exception:
                pass
            try:
                btn.variant = variant
            except Exception:
                pass

        # Remove buttons that are no longer desired
        desired_set = set(desired_tids)
        for tid, btn in existing.items():
            if tid not in desired_set:
                btn.remove()


class HistoryPane(Vertical):
    def compose(self):
        self.tabs_bar = ThreadTabsBar(id="history_tabs")
        self.history_view = VerticalScroll(id="history_view")
        self.history_input = HistorySearchInput(placeholder="History search", id="history_input")
        yield self.tabs_bar
        yield self.history_view
        yield self.history_input

    def clear_history(self) -> None:
        self.history_view.remove_children()

    def set_tabs(self, tabs: List[Tuple[str, str, bool]]) -> None:
        # Tabs changes must not wipe history.
        self.tabs_bar.set_tabs(tabs)

    def focus_input(self) -> None:
        self.history_input.focus()
