#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / ui/pipeline.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, Static

from models import Idea, CHAMBER_NAMES, chamber_color


# ── Messages ──────────────────────────────────────────────────────────────────

class IdeaSelected(Message):
    """Fired when the user clicks an idea entry."""
    def __init__(self, idea_id: str) -> None:
        super().__init__()
        self.idea_id = idea_id


# ── IdeaEntry ─────────────────────────────────────────────────────────────────

class IdeaEntry(Static):
    """A single clickable idea row in the pipeline."""

    def __init__(self, idea: Idea, is_active: bool = False) -> None:
        self.idea       = idea
        self.is_active  = is_active
        classes = f"idea-entry idea-entry-{idea.chamber}"
        if is_active:
            classes += " active"
        # Truncate title to fit the pane
        title = idea.title if idea.title.strip() else "(untitled)"
        if len(title) > 22:
            title = title[:20] + "…"
        super().__init__(title, classes=classes)

    def on_click(self) -> None:
        self.post_message(IdeaSelected(self.idea.id))


# ── ChamberSection ────────────────────────────────────────────────────────────

class ChamberSection(Vertical):
    """
    One collapsible chamber block.
    Header shows chamber name + idea count.
    Body lists IdeaEntry widgets.
    """

    def __init__(self, chamber: int, ideas: list[Idea], active_id: str | None) -> None:
        self.chamber   = chamber
        self.ideas     = ideas
        self.active_id = active_id
        super().__init__(classes=f"chamber-section chamber-section-{chamber}")

    def compose(self) -> ComposeResult:
        name, latin = CHAMBER_NAMES[self.chamber]
        count       = len(self.ideas)
        numeral     = ["I", "II", "III", "IV"][self.chamber - 1]

        yield Static(
            f" {numeral}  {name}  [{count}]",
            classes=f"chamber-header chamber-header-{self.chamber}",
        )

        if not self.ideas:
            if self.chamber == 1:
                yield Static(
                    "  Press n to add an idea",
                    classes="chamber-empty pipeline-new-cta",
                )
            else:
                yield Static("  — empty —", classes="chamber-empty")
        else:
            for idea in self.ideas:
                yield IdeaEntry(idea, is_active=(idea.id == self.active_id))


# ── PipelineNav ───────────────────────────────────────────────────────────────

class PipelineNav(Vertical):
    """
    Left pane. Four chamber sections stacked vertically.
    Owns the search input. Refreshes on store mutation via refresh_ideas().
    """

    BINDINGS = [
        ("n", "new_idea",   "New idea"),
        ("a", "advance",    "Advance"),
        ("r", "return_to",  "Return"),
        ("c", "cull",       "Cull"),
        ("g", "cull_register", "Cull register"),
    ]

    def __init__(self, ideas: list[Idea], active_id: str | None = None) -> None:
        self._all_ideas = ideas
        self._active_id = active_id
        self._filter    = ""
        super().__init__(id="pipeline")

    def compose(self) -> ComposeResult:
        yield Static(
            "◆  THE DOLIUM",
            id="pipeline-title",
            classes="pipeline-title",
        )
        yield Static(
            "  ^n=new  ·  ^a=advance  ·  ^r=return  ·  ^x=cull",
            id="pipeline-hint",
            classes="pipeline-hint",
        )
        yield Input(
            placeholder="  / search…",
            id="pipeline-search",
            classes="pipeline-search",
        )
        yield from self._build_sections(self._all_ideas)

    # ── Public ────────────────────────────────────────────────────────────────

    def refresh_ideas(self, ideas: list[Idea], active_id: str | None = None) -> None:
        """Called by ChainScreen after any store mutation."""
        self._all_ideas = ideas
        self._active_id = active_id
        self._rebuild()

    def set_active(self, idea_id: str | None) -> None:
        self._active_id = idea_id
        self._rebuild()

    # ── Events ────────────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "pipeline-search":
            self._filter = event.value.strip().lower()
            self._rebuild()

    def on_key(self, event) -> None:
        # Let the search input consume keypresses when focused
        if self.query_one("#pipeline-search").has_focus:
            return

    def action_new_idea(self)        -> None: self.app.action_new_idea()
    def action_advance(self)         -> None: self.app.action_advance()
    def action_return_to(self)       -> None: self.app.action_return_to()
    def action_cull(self)            -> None: self.app.action_cull()
    def action_cull_register(self)   -> None: self.app.action_cull_register()

    # ── Private ───────────────────────────────────────────────────────────────

    def _filtered(self, ideas: list[Idea]) -> list[Idea]:
        if not self._filter:
            return ideas
        return [i for i in ideas if self._filter in i.title.lower()]

    def _by_chamber(self, ideas: list[Idea], chamber: int) -> list[Idea]:
        return [i for i in ideas if i.chamber == chamber]

    def _build_sections(self, ideas: list[Idea]):
        filtered = self._filtered(ideas)
        for chamber in [1, 2, 3, 4]:
            yield ChamberSection(
                chamber   = chamber,
                ideas     = self._by_chamber(filtered, chamber),
                active_id = self._active_id,
            )

    def _rebuild(self) -> None:
        """Remove and remount all chamber sections below the search input."""
        # Remove existing sections
        for section in self.query(".chamber-section").results():
            section.remove()
        # Mount new sections
        for section in self._build_sections(self._all_ideas):
            self.mount(section)
