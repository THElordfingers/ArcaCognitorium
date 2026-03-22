#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/ui/panes/history.py  
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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, str] = {}

    def set_keymap(self, *, focus_left: str, focus_middle: str, focus_right: str) -> None:
        self._keys = {
            "focus_left":   _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right":  _norm(focus_right),
        }

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)
        if k and k == self._keys.get("focus_left"):
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return


class SmartScrollHistory(VerticalScroll):
    """
    History scroll container with automatic brake behaviour.

    Brake engages automatically when the Wizard scrolls up.
    Brake releases automatically when the Wizard scrolls back to the bottom.
    No manual toggle needed. Works like standard chat UX.
    """

    BOTTOM_TOLERANCE = 3

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._braked: bool = False

    @property
    def is_braked(self) -> bool:
        return self._braked

    def _at_bottom(self) -> bool:
        try:
            return self.scroll_y >= self.max_scroll_y - self.BOTTOM_TOLERANCE
        except Exception:
            return True

    def on_scroll_up(self, event) -> None:
        self._braked = True

    def on_scroll_down(self, event) -> None:
        if self._at_bottom():
            self._braked = False

    def scroll_to_bottom(self) -> None:
        if not self._braked:
            self.scroll_end(animate=False)

    def force_scroll_to_bottom(self) -> None:
        self._braked = False
        self.scroll_end(animate=False)


class ThreadTabsBar(Horizontal):
    ID_PREFIX = "threadtab-"
    EMPTY_ID = "threadtabs-empty"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tabs: List[Tuple[str, str, bool]] = []

    def set_tabs(self, tabs: List[Tuple[str, str, bool]]) -> None:
        self._tabs = tabs
        self._sync_tabs()

    def _existing_tab_buttons(self) -> Dict[str, Button]:
        out: Dict[str, Button] = {}
        for child in list(self.children):
            if isinstance(child, Button) and (child.id or "").startswith(self.ID_PREFIX):
                tid = (child.id or "")[len(self.ID_PREFIX):]
                if tid:
                    out[tid] = child
        return out

    def _remove_empty_placeholder(self) -> None:
        for child in list(self.children):
            if isinstance(child, Static) and child.id == self.EMPTY_ID:
                child.remove()

    def _sync_tabs(self) -> None:
        if not self._tabs:
            for child in list(self.children):
                child.remove()
            self.mount(Static("", id=self.EMPTY_ID, markup=False))
            return
        self._remove_empty_placeholder()
        existing = self._existing_tab_buttons()
        desired_tids = [tid for tid, _name, _active in self._tabs]
        for tid, name, active in self._tabs:
            label = name or tid
            variant = "primary" if active else "default"
            btn = existing.get(tid)
            if btn is None:
                self.mount(Button(label, id=f"{self.ID_PREFIX}{tid}", variant=variant))
                continue
            try: btn.label = label
            except Exception: pass
            try: btn.variant = variant
            except Exception: pass
        desired_set = set(desired_tids)
        for tid, btn in existing.items():
            if tid not in desired_set:
                btn.remove()


class HistoryPane(Vertical):
    def compose(self):
        self.tabs_bar = ThreadTabsBar(id="history_tabs")
        self.history_view = SmartScrollHistory(id="history_view")
        self.history_input = HistorySearchInput(
            placeholder="Search history",
            id="history_input"
        )
        yield self.tabs_bar
        yield self.history_view
        yield self.history_input

    def clear_history(self) -> None:
        self.history_view.remove_children()

    def set_tabs(self, tabs: List[Tuple[str, str, bool]]) -> None:
        self.tabs_bar.set_tabs(tabs)

    def focus_input(self) -> None:
        self.history_input.focus()

    def scroll_to_bottom(self) -> None:
        self.history_view.scroll_to_bottom()

    def force_scroll_to_bottom(self) -> None:
        self.history_view.force_scroll_to_bottom()

    @property
    def is_braked(self) -> bool:
        return self.history_view.is_braked
