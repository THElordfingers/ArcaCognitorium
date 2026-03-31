#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                            lore_book.py    ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
# LORE BOOK — Textual Modal Widget
# v1.0
#
# Displays a ratified Exloricum as a rendered manuscript page.
# Callable from Tower and any Textual-based Exocognii component.
#
# Usage:
#   from Shared.widgets.lore_book import LoreBookScreen
#   await self.app.push_screen(LoreBookScreen(entry_id="uuid"))
#
# Or with a pre-loaded entry dict + prose string:
#   await self.app.push_screen(LoreBookScreen.from_data(entry, prose))
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

from __future__ import annotations

import re
import sys
import json
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, ScrollView, Label
from textual.reactive import reactive

# Resolve Shared/ on the path so lore_corpus is importable
_config_path = Path.home() / ".arca" / "config.json"
_repo_root   = Path.home() / "ArcaCognitorium"
try:
    with _config_path.open() as _f:
        _cfg = json.load(_f)
    _repo_root = Path(_cfg.get("arca_repo_path", _repo_root))
except (OSError, json.JSONDecodeError):
    pass
_shared = str(_repo_root / "Shared")
if _shared not in sys.path:
    sys.path.insert(0, _shared)

try:
    import lore_corpus as _corpus
    _CORPUS_AVAILABLE = True
except ImportError:
    _CORPUS_AVAILABLE = False


# ── CSS ───────────────────────────────────────────────────────────────────────

LORE_BOOK_CSS = """
LoreBookScreen {
    align: center middle;
    background: #050507 80%;
}

#book-shell {
    width: 80;
    height: 90%;
    background: #0a0a12;
    border: tall #3a2e10;
    padding: 0;
}

#book-header {
    background: #0a0a12;
    border-bottom: tall #3a2e10;
    padding: 1 3;
    height: auto;
}

#book-title {
    color: #d4af37;
    text-style: bold;
}

#book-meta {
    color: #7a6a2a;
}

#book-scroll {
    background: #050507;
    padding: 1 3;
    border: none;
    scrollbar-color: #3a2e10;
    scrollbar-color-hover: #7a6a2a;
}

#book-body {
    color: #c8b88a;
    background: #050507;
}

#book-footer {
    background: #0a0a12;
    border-top: tall #3a2e10;
    padding: 0 3;
    height: 1;
    color: #7a6a2a;
}

#book-ratified {
    color: #7a6a2a;
}

#book-dismiss {
    color: #3a2e10;
    text-align: right;
}
"""


# ── Prose renderer ────────────────────────────────────────────────────────────

def _render_prose(raw: str) -> str:
    """
    Convert raw .md prose to Rich markup for terminal display.
    Handles headings, bold, italic, horizontal rules.
    Strips YAML frontmatter if present.
    Does not attempt full Markdown parsing — targets Exloricum prose style.
    """
    # Strip YAML frontmatter
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            raw = parts[2].strip()

    lines   = raw.splitlines()
    output  = []

    for line in lines:
        # H1
        if line.startswith("# "):
            text = line[2:].strip()
            output.append(f"[bold #d4af37]✦  {text}[/bold #d4af37]")
        # H2
        elif line.startswith("## "):
            text = line[3:].strip()
            output.append(f"[bold #7a6a2a]{text}[/bold #7a6a2a]")
        # H3
        elif line.startswith("### "):
            text = line[4:].strip()
            output.append(f"[#7a6a2a]{text}[/#7a6a2a]")
        # Horizontal rule
        elif re.match(r"^[-*_]{3,}$", line.strip()):
            output.append("[#3a2e10]" + ("─" * 54) + "[/#3a2e10]")
        # Normal line — inline bold/italic
        else:
            line = re.sub(r"\*\*(.+?)\*\*", r"[bold #e8e0cc]\1[/bold #e8e0cc]", line)
            line = re.sub(r"\*(.+?)\*",     r"[italic #c8b88a]\1[/italic #c8b88a]", line)
            line = re.sub(r"_(.+?)_",       r"[italic #c8b88a]\1[/italic #c8b88a]", line)
            output.append(line)

    return "\n".join(output)


def _format_date(iso: str | None) -> str:
    """Return a readable date string from ISO timestamp, or empty string."""
    if not iso:
        return ""
    try:
        return iso[:10]
    except Exception:
        return str(iso)


# ── Widget ────────────────────────────────────────────────────────────────────

class LoreBookScreen(ModalScreen):
    """
    Modal manuscript overlay for displaying a ratified Exloricum.

    Open via:
        await self.app.push_screen(LoreBookScreen(entry_id="uuid"))

    Or with pre-loaded data (avoids a second corpus read):
        await self.app.push_screen(LoreBookScreen.from_data(entry, prose))
    """

    CSS = LORE_BOOK_CSS

    BINDINGS = [
        Binding("escape", "dismiss", "Revertere"),
        Binding("q",      "dismiss", "Exire", show=False),
    ]

    def __init__(
        self,
        entry_id:  str  | None = None,
        _entry:    dict | None = None,
        _prose:    str  | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._entry_id = entry_id
        self._entry    = _entry
        self._prose    = _prose

    @classmethod
    def from_data(cls, entry: dict, prose: str) -> "LoreBookScreen":
        """
        Construct a LoreBookScreen from pre-loaded data.
        Skips corpus read entirely.
        """
        return cls(_entry=entry, _prose=prose)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        """Load entry from corpus if not already supplied."""
        if self._entry is None and self._entry_id is not None:
            if _CORPUS_AVAILABLE:
                self._entry = _corpus.get_entry(self._entry_id)
                self._prose = _corpus.get_exloricum(self._entry_id)
            else:
                self._entry = None
                self._prose = None
        self._populate()

    def _populate(self) -> None:
        """Push content into the rendered widgets."""
        entry = self._entry or {}
        prose = self._prose or ""

        title     = entry.get("title",       "Untitled Entry")
        domain    = entry.get("domain",      "")
        tags      = entry.get("tags",        [])
        ratified  = _format_date(entry.get("ratified_at"))

        # Header
        self.query_one("#book-title",   Label).update(f"✦  {title}")
        meta_parts = [domain] + tags if domain else tags
        self.query_one("#book-meta",    Label).update("  ·  ".join(meta_parts))

        # Body
        if prose:
            rendered = _render_prose(prose)
        elif not _CORPUS_AVAILABLE:
            rendered = "[#8b1a1a]Corpus reader unavailable — PyYAML not installed.[/#8b1a1a]"
        elif not self._entry_id and not self._entry:
            rendered = "[#7a6a2a]No entry specified.[/#7a6a2a]"
        else:
            rendered = "[#7a6a2a]No prose found for this entry.[/#7a6a2a]"

        self.query_one("#book-body", Static).update(rendered)

        # Footer
        date_str = f"ratified {ratified}" if ratified else ""
        self.query_one("#book-ratified", Label).update(date_str)

    # ── Composition ───────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical(id="book-shell"):
            # Header band
            with Vertical(id="book-header"):
                yield Label("", id="book-title")
                yield Label("", id="book-meta")
            # Scrollable body
            with ScrollView(id="book-scroll"):
                yield Static("", id="book-body", markup=True)
            # Footer bar
            with Horizontal(id="book-footer"):
                yield Label("", id="book-ratified")
                yield Label("esc · Revertere", id="book-dismiss")

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_dismiss(self) -> None:
        """Dismiss the book overlay."""
        self.dismiss()
