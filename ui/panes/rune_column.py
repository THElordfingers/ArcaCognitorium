# ╔════════════════════════════════════════════════════════════════════════════════════════════
# ║  ArcaCognitorium / ui / panes / rune_column.py
# ╚════════════════════════════════════════════════════════════════════════════════════════════
"""
RuneColumnPane -- dedicated side-rune widget.

3 chars wide. Flanks the main pane layout as its own Textual widget.
Left  side:  ╔ / ║ᚱ / ╚
Right side:  ╗ / ᚱ║ / ╝

Glyphs loaded from glyphs/rune-glyphs.txt; baked-in fallback if absent.
Rebuilds sequence on every resize so it always fills the column exactly.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Literal

from textual.widget import Widget
from rich.text import Text
from rich.style import Style

Side = Literal["left", "right"]

_TL, _TR = "\u2554", "\u2557"
_BL, _BR = "\u255a", "\u255d"
_VL      = "\u2551"

_C_RUNE   = "#C9A84C"
_C_CORNER = "#C9A84C"
_C_PIPE   = "#2A2535"

_FALLBACK = list(
    "\u16a2\u16a6\u16a8\u16a9\u16b1\u16b2\u16b7\u16b9"
    "\u16c1\u16c3\u16c7\u16ca\u16cf\u16d2\u16d6\u16df\u16e0"
)


def _load_runes() -> list:
    for candidate in [Path("glyphs/rune-glyphs.txt"), Path("rune-glyphs.txt")]:
        try:
            raw   = candidate.read_text(encoding="utf-8")
            chars = [ch for ch in raw if ch.strip() and ch not in ("\n", "\t", "\r")]
            if len(chars) >= 6:
                return chars
        except Exception:
            pass
    return _FALLBACK


class RuneColumnPane(Widget):
    """Narrow column of runic glyphs with box-drawing corners."""

    DEFAULT_CSS = """
    RuneColumnPane {
        width: 3;
        height: 100%;
        background: #0D0B0E;
    }
    """

    def __init__(self, side: Side = "left", **kwargs) -> None:
        super().__init__(**kwargs)
        self._side  = side
        self._runes = _load_runes()
        self._seq: list = []

    def on_mount(self) -> None:
        self._rebuild()

    def on_resize(self) -> None:
        self._rebuild()
        self.refresh()

    def _rebuild(self) -> None:
        h        = max(self.size.height, 4)
        interior = h - 2
        pool     = self._runes[:]
        random.shuffle(pool)
        seq: list = []
        while len(seq) < interior:
            seq.extend(pool)
        self._seq = seq[:interior]

    def render(self) -> Text:
        h   = max(self.size.height, 4)
        seq = self._seq or (["\u16b1"] * (h - 2))
        t   = Text()

        top = _TL if self._side == "left" else _TR
        bot = _BL if self._side == "left" else _BR

        t.append(top, style=Style(color=_C_CORNER))
        t.append("\n")

        for rune in seq:
            if self._side == "left":
                t.append(_VL,  style=Style(color=_C_PIPE))
                t.append(rune, style=Style(color=_C_RUNE))
            else:
                t.append(rune, style=Style(color=_C_RUNE))
                t.append(_VL,  style=Style(color=_C_PIPE))
            t.append("\n")

        t.append(bot, style=Style(color=_C_CORNER))
        return t
