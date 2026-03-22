#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / ui/modals.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, TextArea

from chambers import gate_for_advance
from models import Idea, CullRecord, chamber_name, chamber_latin


# ── NewIdeaModal ──────────────────────────────────────────────────────────────

class NewIdeaModal(ModalScreen):
    """
    Single input: idea title.
    Returns the title string on confirm, None on cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("◆  New Idea", classes="modal-title")
            yield Static(
                "Name it. A working title is enough.",
                classes="modal-body",
            )
            yield Input(
                placeholder="Enter a title…",
                id="new-idea-input",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Create", id="btn-create", classes="btn-confirm")
                yield Button("Cancel", id="btn-cancel", classes="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#new-idea-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create":
            self._confirm()
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._confirm()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _confirm(self) -> None:
        title = self.query_one("#new-idea-input", Input).value.strip()
        if not title:
            self.query_one("#new-idea-input", Input).border_title = "Title required"
            return
        self.dismiss(title)


# ── AdvanceModal ──────────────────────────────────────────────────────────────

class AdvanceModal(ModalScreen):
    """
    Shows gate status for the active idea.
    Green checks for passed conditions, red ✕ for failures.
    Confirm button only appears if gate is fully passed.
    Returns True on confirm, None on cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, idea: Idea) -> None:
        self._idea = idea
        super().__init__()

    def compose(self) -> ComposeResult:
        gate_fn  = gate_for_advance(self._idea.chamber)
        result   = gate_fn(self._idea)
        next_name = chamber_name(self._idea.chamber + 1)
        next_lat  = chamber_latin(self._idea.chamber + 1)

        with Vertical(classes="modal-container"):
            yield Static(
                f"◆  Advance to {next_name}",
                classes="modal-title",
            )
            yield Static(
                f"{next_lat}",
                classes="modal-body",
            )

            # Gate conditions
            with Vertical(id="gate-conditions"):
                conditions = self._gate_conditions(self._idea.chamber)
                for label, field_check in conditions:
                    passed = field_check(self._idea)
                    icon   = "◆" if passed else "✕"
                    css    = "gate-success" if passed else "gate-failure"
                    yield Static(f"  {icon}  {label}", classes=css)

            with Horizontal(classes="modal-buttons"):
                if result.passed:
                    yield Button("Advance ›", id="btn-confirm", classes="btn-confirm")
                yield Button("Cancel", id="btn-cancel", classes="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _gate_conditions(self, chamber: int) -> list[tuple[str, callable]]:
        """Human-readable condition labels with their check functions."""
        base = [
            ("Title is present",           lambda i: bool(i.title.strip())),
            ("Body is developed",          lambda i: len(i.body.strip()) >= (20 if chamber == 1 else 100)),
            ("Motivation is stated",       lambda i: bool(i.motivation.strip())),
        ]
        if chamber >= 2:
            base += [
                ("Scope (inside) defined",     lambda i: bool(i.scope_in.strip())),
                ("Scope (outside) defined",    lambda i: bool(i.scope_out.strip())),
                ("System map present",         lambda i: bool(i.system_map.strip())),
            ]
        if chamber >= 3:
            base += [
                ("Dependencies named",         lambda i: bool(i.dependencies.strip())),
                ("Build sequence proposed",    lambda i: bool(i.build_sequence.strip())),
                ("Declaration written",        lambda i: bool(i.declaration.strip())),
                ("Declaration signed",         lambda i: i.declared_at is not None),
            ]
        return base


# ── ReturnToModal ─────────────────────────────────────────────────────────────

class ReturnToModal(ModalScreen):
    """
    Chamber selector — only prior chambers are selectable.
    Requires a note explaining the return.
    Returns (target_chamber, note) on confirm, None on cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, idea: Idea) -> None:
        self._idea   = idea
        self._target = idea.chamber - 1
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("◇  Return to Prior Chamber", classes="modal-title")
            yield Static(
                f"Current: {chamber_name(self._idea.chamber)}  —  select destination:",
                classes="modal-body",
            )

            with Vertical(id="chamber-options"):
                for c in range(1, self._idea.chamber):
                    active = "  ◆" if c == self._target else ""
                    yield Static(
                        f"  [{c}]  {chamber_name(c)}{active}",
                        id=f"chamber-opt-{c}",
                        classes=f"idea-entry idea-entry-{c}" + (" active" if c == self._target else ""),
                    )

            yield Static("Note (required):", classes="field-label required")
            yield TextArea(
                "",
                id="return-note",
                classes="field-textarea",
            )

            with Horizontal(classes="modal-buttons"):
                yield Button("Return ‹", id="btn-confirm", classes="btn-confirm")
                yield Button("Cancel",   id="btn-cancel",  classes="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#return-note", TextArea).focus()

    def on_static_click(self, event: Static.Click) -> None:
        wid = event.widget.id or ""
        if wid.startswith("chamber-opt-"):
            self._target = int(wid.split("-")[-1])
            self._refresh_options()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            note = self.query_one("#return-note", TextArea).text.strip()
            if not note:
                self.app.notify("A note is required when returning an idea.", severity="warning")
                return
            self.dismiss((self._target, note))
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _refresh_options(self) -> None:
        for c in range(1, self._idea.chamber):
            try:
                widget = self.query_one(f"#chamber-opt-{c}", Static)
                active = "  ◆" if c == self._target else ""
                widget.update(f"  [{c}]  {chamber_name(c)}{active}")
                base = f"idea-entry idea-entry-{c}"
                widget.set_classes(base + (" active" if c == self._target else ""))
            except Exception:
                pass


# ── CullModal ─────────────────────────────────────────────────────────────────

class CullModal(ModalScreen):
    """
    Requires an epitaph (min 10 chars).
    Returns the epitaph string on confirm, None on cancel.
    No undo — resurrection is via the Cull Register.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, idea: Idea) -> None:
        self._idea = idea
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("✕  Cull Idea", classes="modal-title")
            yield Static(
                f'"{self._idea.title}" will be removed from the pipeline '
                f"and filed in the Cull Register. This is not deletion — "
                f"resurrection is possible. But it requires intention.",
                classes="modal-body",
            )
            yield Static("Epitaph (required):", classes="field-label required")
            yield TextArea(
                "",
                id="epitaph-input",
                classes="field-textarea",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Cull",   id="btn-confirm", classes="btn-danger")
                yield Button("Cancel", id="btn-cancel",  classes="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#epitaph-input", TextArea).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            epitaph = self.query_one("#epitaph-input", TextArea).text.strip()
            if len(epitaph) < 10:
                self.app.notify("Epitaph must be at least 10 characters.", severity="warning")
                return
            self.dismiss(epitaph)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── DeclarationModal ──────────────────────────────────────────────────────────

class DeclarationModal(ModalScreen):
    """
    Shown when advancing from chamber 3 → 4.
    Wizard writes their Declaration. On confirm, declared_at is set
    and the idea advances to the Codex Paratum.
    Also triggers the export suite.
    Returns the declaration text on confirm, None on cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, idea: Idea) -> None:
        self._idea = idea
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("◆  The Declaration", classes="modal-title")
            yield Static(
                "Speak your intent. This is the Wizard's sign-off — "
                "a first-person statement confirming this idea is ready "
                "and expressing what it is for. It becomes part of the package.",
                classes="modal-body",
            )
            yield TextArea(
                self._idea.declaration,
                id="declaration-input",
                classes="field-textarea",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Declare & Advance ◆", id="btn-confirm", classes="btn-confirm")
                yield Button("Cancel",               id="btn-cancel",  classes="btn-cancel")

    def on_mount(self) -> None:
        ta = self.query_one("#declaration-input", TextArea)
        ta.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            text = self.query_one("#declaration-input", TextArea).text.strip()
            if len(text) < 10:
                self.app.notify("The Declaration must say something.", severity="warning")
                return
            self.dismiss(text)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── CullRegisterModal ─────────────────────────────────────────────────────────

class CullRegisterModal(ModalScreen):
    """
    Scrollable list of all CullRecords.
    Resurrect button on each row.
    Returns ("resurrect", cull_id) or None.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, records: list[CullRecord]) -> None:
        self._records = records
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("◆  Cull Register", classes="modal-title")

            with ScrollableContainer(id="cull-register-list"):
                if not self._records:
                    yield Static(
                        "The Register is empty. Nothing has been culled.",
                        classes="conv-empty",
                    )
                else:
                    for record in self._records:
                        yield self._build_record_row(record)

            with Horizontal(classes="modal-buttons"):
                yield Button("Close", id="btn-close", classes="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss(None)
        elif event.button.id.startswith("btn-resurrect-"):
            cull_id = event.button.id.replace("btn-resurrect-", "")
            self.dismiss(("resurrect", cull_id))

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _build_record_row(self, record: CullRecord) -> Vertical:
        row = Vertical(classes="cull-record")
        chamber_label = chamber_name(record.chamber_at_cull)
        date          = record.culled_at[:10] if record.culled_at else "unknown"

        row.compose = lambda: iter([
            Static(record.title,                           classes="cull-record-title"),
            Static(f"Culled from {chamber_label} · {date}", classes="cull-record-meta"),
            Static(f'"{record.epitaph}"',                    classes="cull-record-epitaph"),
            Button("Resurrect", id=f"btn-resurrect-{record.id}", classes="btn-confirm"),
        ])
        return row


# ── ExportModal ───────────────────────────────────────────────────────────────

class ExportModal(ModalScreen):
    """
    Format selector for Codex Paratum ideas.
    All formats checked by default.
    Returns list[str] of selected format keys, or None on cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    FORMATS = [
        ("wiz",  ".wiz  — Wizard-styled LibreOffice document"),
        ("docx", ".docx — Clean Word document for AI upload"),
        ("md",   ".md   — Markdown for terminal reference"),
        ("txt",  ".txt  — Plaintext, maximum portability"),
        ("json", ".json — Raw data export"),
    ]

    def __init__(self, idea: Idea) -> None:
        self._idea    = idea
        self._selected = {k for k, _ in self.FORMATS}
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Static("◆  Export Package", classes="modal-title")
            yield Static(
                f'Exporting: "{self._idea.title}"',
                classes="modal-body",
            )

            with Vertical(id="format-options"):
                for key, label in self.FORMATS:
                    yield Static(
                        f"  ◆  {label}",
                        id=f"fmt-{key}",
                        classes="gate-success",
                    )

            yield Static(
                "Click a format to toggle. All selected by default.",
                classes="field-label",
            )

            with Horizontal(classes="modal-buttons"):
                yield Button("Export ◆", id="btn-confirm", classes="btn-confirm")
                yield Button("Cancel",   id="btn-cancel",  classes="btn-cancel")

    def on_static_click(self, event: Static.Click) -> None:
        wid = event.widget.id or ""
        if wid.startswith("fmt-"):
            key = wid[4:]
            if key in self._selected:
                self._selected.discard(key)
                event.widget.set_classes("gate-failure")
                event.widget.update(f"  ✕  {self._label_for(key)}")
            else:
                self._selected.add(key)
                event.widget.set_classes("gate-success")
                event.widget.update(f"  ◆  {self._label_for(key)}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            if not self._selected:
                self.app.notify("Select at least one format.", severity="warning")
                return
            self.dismiss(list(self._selected))
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _label_for(self, key: str) -> str:
        return next((label for k, label in self.FORMATS if k == key), key)


# ── ManpageModal ──────────────────────────────────────────────────────────────

class ManpageModal(ModalScreen):
    """
    Displays a manpage in a scrollable overlay.
    Tab or click the chapter buttons to switch pages.
    """

    BINDINGS = [("escape", "cancel", "Close")]

    CHAPTERS = [
        ("overview",  "Overview"),
        ("chamber_1", "I  Fomentary"),
        ("chamber_2", "II  Cultivation"),
        ("chamber_3", "III  Vestibule"),
        ("chamber_4", "IV  Codex"),
    ]

    def __init__(self, page: str = "overview") -> None:
        self._page = page
        super().__init__()

    def compose(self) -> ComposeResult:
        from manpages import get_manpage, MANPAGE_TITLES
        with Vertical(classes="modal-container", id="manpage-container"):
            yield Static("◆  THE DOLIUM — MANUAL", classes="modal-title")
            with Horizontal(id="manpage-tabs"):
                for key, label in self.CHAPTERS:
                    active = " manpage-tab-active" if key == self._page else ""
                    yield Button(label, id=f"tab-{key}", classes=f"manpage-tab{active}")
            yield ScrollableContainer(
                Static(
                    get_manpage(self._page),
                    id="manpage-body",
                    classes="manpage-body",
                ),
                id="manpage-scroll",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Close [esc]", id="btn-close", classes="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss(None)
            return
        if event.button.id and event.button.id.startswith("tab-"):
            key = event.button.id[4:]
            self._page = key
            from manpages import get_manpage
            try:
                self.query_one("#manpage-body", Static).update(get_manpage(key))
                self.query_one("#manpage-scroll", ScrollableContainer).scroll_home(animate=False)
            except Exception:
                pass
            # Update tab highlight
            for k, _ in self.CHAPTERS:
                try:
                    tab = self.query_one(f"#tab-{k}", Button)
                    if k == key:
                        tab.add_class("manpage-tab-active")
                    else:
                        tab.remove_class("manpage-tab-active")
                except Exception:
                    pass

    def action_cancel(self) -> None:
        self.dismiss(None)
