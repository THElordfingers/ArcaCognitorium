#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / ui/workspace.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Static, TextArea

from chambers import gate_for_advance, GateResult
from models import Idea, chamber_latin, chamber_name


# ── Messages ──────────────────────────────────────────────────────────────────

class IdeaSaved(Message):
    def __init__(self, idea: Idea) -> None:
        super().__init__()
        self.idea = idea


# ── WorkspaceField ────────────────────────────────────────────────────────────

class WorkspaceField(Vertical):

    def __init__(self, label, field_id, value="", multiline=True, required=False):
        self._label     = label
        self._field_id  = field_id
        self._value     = value
        self._multiline = multiline
        self._required  = required
        super().__init__(classes="workspace-field")

    def compose(self) -> ComposeResult:
        marker = " ◆" if self._required else ""
        yield Static(
            f"{self._label}{marker}",
            classes="field-label required" if self._required else "field-label",
        )
        if self._multiline:
            yield TextArea(self._value, id=self._field_id, classes="field-textarea")
        else:
            yield Input(value=self._value, id=self._field_id, classes="field-input")


# ── GateBar ───────────────────────────────────────────────────────────────────

class GateBar(Horizontal):
    """
    No fixed ID — instantiated fresh on every rebuild.
    Buttons identified by CSS class to avoid DuplicateIds.
    """

    def __init__(self, idea: Idea) -> None:
        self._idea = idea
        super().__init__(classes="gate-bar-container")

    def compose(self) -> ComposeResult:
        result, label, css = self._evaluate()
        yield Static(label, classes=f"gate-status {css}")
        yield Button("Advance", classes="btn-gate btn-advance", disabled=not result.passed)
        yield Button("Return",  classes="btn-gate btn-return",  disabled=(self._idea.chamber <= 1))
        yield Button("Cull",    classes="btn-gate btn-cull")

    def refresh_gate(self, idea: Idea) -> None:
        self._idea = idea
        result, label, css = self._evaluate()
        try:
            s = self.query_one(".gate-status", Static)
            s.update(label)
            s.set_classes(f"gate-status {css}")
            self.query_one(".btn-advance", Button).disabled = not result.passed
            self.query_one(".btn-return",  Button).disabled = idea.chamber <= 1
        except Exception:
            pass

    def _evaluate(self):
        if self._idea.chamber >= 4:
            return GateResult(passed=False, failures=[]), "◆  Codex Paratum — complete", "gate-passed"
        try:
            result = gate_for_advance(self._idea.chamber)(self._idea)
        except ValueError:
            result = GateResult(passed=False, failures=["Cannot advance further."])
        if result.passed:
            next_name = ["", "Cultivation House", "The Vestibule", "Codex Paratum"][self._idea.chamber]
            return result, f"◆  Gate clear — ready for {next_name}", "gate-passed"
        elif len(result.failures) < 3:
            return result, f"◇  {len(result.failures)} condition(s) remaining", "gate-partial"
        else:
            return result, f"✕  {len(result.failures)} conditions unmet", "gate-blocked"


# ── IdeaWorkspace ─────────────────────────────────────────────────────────────

class IdeaWorkspace(ScrollableContainer):
    """
    Middle pane. Rebuild strategy: mount new widgets first, then remove old
    ones. This prevents the DuplicateIds race from async remove_children().
    """

    FIELD_MAP = {
        "f-title":           "title",
        "f-tags":            "tags",
        "f-body":            "body",
        "f-motivation":      "motivation",
        "f-scope-in":        "scope_in",
        "f-scope-out":       "scope_out",
        "f-system-map":      "system_map",
        "f-dependencies":    "dependencies",
        "f-build-sequence":  "build_sequence",
        "f-open-questions":  "open_questions",
        "f-aesthetic-notes": "aesthetic_notes",
        "f-declaration":     "declaration",
    }

    def __init__(self) -> None:
        self._idea: Idea | None = None
        super().__init__(id="workspace")

    def compose(self) -> ComposeResult:
        yield Static(
            "Select or create an idea.  ctrl+n to begin.",
            classes="conv-empty",
            id="workspace-empty",
        )

    def load(self, idea: Idea) -> None:
        self._idea = idea
        self._rebuild()

    def clear(self) -> None:
        self._idea = None
        self.remove_children()
        self.mount(Static(
            "Select or create an idea.  ctrl+n to begin.",
            classes="conv-empty", id="workspace-empty",
        ))

    def refresh_gate(self) -> None:
        if self._idea is None:
            return
        try:
            self.query_one(GateBar).refresh_gate(self._idea)
        except Exception:
            pass

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._sync_field(event.text_area.id, event.text_area.text)

    def on_input_changed(self, event: Input.Changed) -> None:
        self._sync_field(event.input.id, event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        classes = event.button.classes
        if "btn-advance" in classes:
            self.app.screen.action_advance()
        elif "btn-return" in classes:
            self.app.screen.action_return_to()
        elif "btn-cull" in classes:
            self.app.screen.action_cull()

    def _sync_field(self, field_id, value):
        if self._idea is None or field_id is None:
            return
        attr = self.FIELD_MAP.get(field_id)
        if attr is None:
            return
        if attr == "tags":
            setattr(self._idea, attr, [t.strip() for t in value.split(",") if t.strip()])
        else:
            setattr(self._idea, attr, value)
        if attr == "declaration" and value.strip() and self._idea.declared_at is None:
            from models import _now
            self._idea.declared_at = _now()
        self.post_message(IdeaSaved(self._idea))
        self.refresh_gate()

    def _rebuild(self) -> None:
        if self._idea is None:
            return
        idea    = self._idea
        chamber = idea.chamber
        numeral = ["I", "II", "III", "IV"][chamber - 1]

        widgets = [
            Static(
                f"  {numeral}  {chamber_name(chamber)}  ·  {chamber_latin(chamber)}",
                classes=f"chamber-badge chamber-badge-{chamber}",
            ),
            WorkspaceField("Title",      "f-title",      idea.title,           multiline=False, required=True),
            WorkspaceField("Tags",       "f-tags",       ", ".join(idea.tags), multiline=False),
            WorkspaceField("Body",       "f-body",       idea.body,            required=True),
            WorkspaceField("Motivation", "f-motivation", idea.motivation,      required=True),
        ]

        if chamber >= 2:
            widgets += [
                WorkspaceField("Scope — Inside",  "f-scope-in",   idea.scope_in,   required=True),
                WorkspaceField("Scope — Outside", "f-scope-out",  idea.scope_out,  required=True),
                WorkspaceField("System Map",      "f-system-map", idea.system_map, required=True),
            ]
        if chamber >= 3:
            widgets += [
                WorkspaceField("Dependencies",    "f-dependencies",    idea.dependencies,    required=True),
                WorkspaceField("Build Sequence",  "f-build-sequence",  idea.build_sequence,  required=True),
                WorkspaceField("Open Questions",  "f-open-questions",  idea.open_questions),
                WorkspaceField("Aesthetic Notes", "f-aesthetic-notes", idea.aesthetic_notes),
            ]
        if chamber >= 4:
            widgets.append(WorkspaceField("Declaration", "f-declaration", idea.declaration, required=True))

        widgets.append(GateBar(idea))

        # Remove old children, then mount new ones cleanly.
        self.remove_children()
        self.mount(*widgets)
        self.scroll_home(animate=False)
