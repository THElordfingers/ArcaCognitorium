#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / ui/layout.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from models import Idea
from store import IdeaStore
from ui.conversation import ChainConversation, ConversationUpdated
from ui.modals import (
    AdvanceModal, CullModal, CullRegisterModal,
    DeclarationModal, ExportModal, NewIdeaModal, ReturnToModal,
)
from ui.pipeline import IdeaSelected, PipelineNav
from ui.workspace import IdeaSaved, IdeaWorkspace


class ChainScreen(Screen):
    """
    The main and only screen of The Dolium.
    Three panes: PipelineNav | IdeaWorkspace | ChainConversation.
    Owns the active_idea reference and all modal coordination.
    """

    BINDINGS = [
        ("ctrl+n", "new_idea",       "New"),
        ("ctrl+a", "advance",        "Advance"),
        ("ctrl+r", "return_to",      "Return"),
        ("ctrl+x", "cull",           "Cull"),
        ("ctrl+g", "cull_register",  "Register"),
        ("ctrl+e", "export",         "Export"),
        ("ctrl+q", "app.quit",       "Quit"),
        ("ctrl+m", "manual",         "Manual"),
        ("ctrl+c", "noop",           ""),
    ]

    # Ensure bindings fire from any focused widget by overriding
    # check_action to always permit these keys
    def check_action(self, action: str, parameters: tuple) -> bool | None:
        return True

    def action_noop(self) -> None:
        """Swallow ctrl+c to prevent Textual clipboard crash in 8.1.1."""
        pass

    def action_manual(self) -> None:
        """Open the manpage overlay."""
        from ui.modals import ManpageModal
        self.app.push_screen(ManpageModal())

    def __init__(self, store: IdeaStore, box: object, repo_path: str | None = None) -> None:
        self._store       = store
        self._box         = box
        self._repo_path   = repo_path
        self._active_idea: Idea | None = None
        super().__init__()

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("◆  The Dolium  —  Idea Fruition Chain", id="app-header")
        with Horizontal(id="main-layout"):
            yield PipelineNav(
                ideas     = self._store.all(),
                active_id = None,
            )
            yield IdeaWorkspace()
            yield ChainConversation()
        yield Static("  ^n new  ·  ^a advance  ·  ^r return  ·  ^x cull  ·  ^g register  ·  ^e export  ·  ^m manual  ·  ^q quit", id="status-bar")

    def on_mount(self) -> None:
        conv = self.query_one(ChainConversation)
        conv.set_box(self._box)
        conv.set_repo_path(self._repo_path)
        # Select the most recently updated idea on launch, if any
        # Use call_after_refresh to ensure DOM is fully mounted first
        ideas = self._store.all()
        if ideas:
            self.call_after_refresh(self._select_idea, ideas[0].id)

    # ── Message handlers ──────────────────────────────────────────────────────

    def on_idea_selected(self, message: IdeaSelected) -> None:
        self._select_idea(message.idea_id)

    def on_idea_saved(self, message: IdeaSaved) -> None:
        self._store.update(message.idea)
        self._refresh_pipeline()

    def on_conversation_updated(self, message: ConversationUpdated) -> None:
        idea = self._store.get(message.idea_id)
        if idea:
            idea.conversation = message.conversation
            self._store.update(idea)

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_new_idea(self) -> None:
        def handle(title: str | None) -> None:
            if not title:
                return
            idea = self._store.create(title)
            self._refresh_pipeline()
            self._select_idea(idea.id)

        self.app.push_screen(NewIdeaModal(), handle)

    def action_advance(self) -> None:
        if self._active_idea is None:
            self.app.notify("No idea selected.", severity="warning")
            return
        if self._active_idea.chamber >= 4:
            self.app.notify("This idea is already in the Codex Paratum.", severity="information")
            return

        # Chamber 3 → 4 uses the Declaration modal
        if self._active_idea.chamber == 3:
            self._push_declaration_modal()
            return

        def handle(confirmed: bool | None) -> None:
            if not confirmed:
                return
            try:
                self._store.advance(self._active_idea)
                self._refresh_all()
                self.app.notify(f"Advanced to {self._active_idea.chamber}.", severity="information")
            except ValueError as e:
                self.app.notify(str(e), severity="error")

        self.app.push_screen(AdvanceModal(self._active_idea), handle)

    def action_return_to(self) -> None:
        if self._active_idea is None:
            self.app.notify("No idea selected.", severity="warning")
            return
        if self._active_idea.chamber <= 1:
            self.app.notify("Already in the first chamber.", severity="information")
            return

        def handle(result: tuple | None) -> None:
            if result is None:
                return
            target, note = result
            try:
                self._store.return_to(self._active_idea, target, note)
                self._refresh_all()
            except ValueError as e:
                self.app.notify(str(e), severity="error")

        self.app.push_screen(ReturnToModal(self._active_idea), handle)

    def action_cull(self) -> None:
        if self._active_idea is None:
            self.app.notify("No idea selected.", severity="warning")
            return

        def handle(epitaph: str | None) -> None:
            if epitaph is None:
                return
            culled_id = self._active_idea.id
            try:
                self._store.cull(self._active_idea, epitaph)
                self._active_idea = None
                self.query_one(IdeaWorkspace).clear()
                self.query_one(ChainConversation).clear()
                self._refresh_pipeline()
                self.app.notify("Idea filed in the Cull Register.", severity="information")
            except ValueError as e:
                self.app.notify(str(e), severity="error")

        self.app.push_screen(CullModal(self._active_idea), handle)

    def action_cull_register(self) -> None:
        def handle(result: tuple | None) -> None:
            if result is None:
                return
            action, cull_id = result
            if action == "resurrect":
                try:
                    idea = self._store.resurrect(cull_id)
                    self._refresh_pipeline()
                    self._select_idea(idea.id)
                    self.app.notify(f'"{idea.title}" resurrected to the Fomentary.', severity="information")
                except ValueError as e:
                    self.app.notify(str(e), severity="error")

        self.app.push_screen(CullRegisterModal(self._store.culled()), handle)

    def action_export(self) -> None:
        if self._active_idea is None:
            self.app.notify("No idea selected.", severity="warning")
            return
        if self._active_idea.chamber < 4:
            self.app.notify("Only Codex Paratum ideas can be exported.", severity="warning")
            return

        def handle(formats: list | None) -> None:
            if not formats:
                return
            try:
                from export import ExportEngine
                engine  = ExportEngine(self._store.exports_dir)
                results = engine.generate(self._active_idea, formats)
                paths   = ", ".join(f".{k}" for k in results)
                self.app.notify(f"Exported: {paths}", severity="information")
            except Exception as e:
                self.app.notify(f"Export failed: {e}", severity="error")

        self.app.push_screen(ExportModal(self._active_idea), handle)

    # ── Private ───────────────────────────────────────────────────────────────

    def _select_idea(self, idea_id: str) -> None:
        idea = self._store.get(idea_id)
        if idea is None:
            return
        self._active_idea = idea
        self.query_one(IdeaWorkspace).load(idea)
        self.query_one(ChainConversation).load(idea)
        self.query_one(PipelineNav).set_active(idea_id)

    def _refresh_pipeline(self) -> None:
        active_id = self._active_idea.id if self._active_idea else None
        self.query_one(PipelineNav).refresh_ideas(self._store.all(), active_id)

    def _refresh_all(self) -> None:
        """Full refresh after chamber change."""
        if self._active_idea:
            # Re-fetch from store to get updated chamber
            self._active_idea = self._store.get(self._active_idea.id)
            if self._active_idea:
                self.query_one(IdeaWorkspace).load(self._active_idea)
                self.query_one(ChainConversation).load(self._active_idea)
        self._refresh_pipeline()

    def _push_declaration_modal(self) -> None:
        def handle(declaration: str | None) -> None:
            if declaration is None:
                return
            from models import _now
            self._active_idea.declaration  = declaration
            self._active_idea.declared_at  = _now()
            try:
                self._store.advance(self._active_idea)
                self._refresh_all()
                self.app.notify("Declared. Filed in the Codex Paratum.", severity="information")
                # Trigger export suite immediately
                self.action_export()
            except ValueError as e:
                self.app.notify(str(e), severity="error")

        self.app.push_screen(DeclarationModal(self._active_idea), handle)
