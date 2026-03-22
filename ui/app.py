#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/ui/app.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════




from __future__ import annotations
from dataclasses import dataclass
from ui.panes.status_layer import StatusLayer
from pathlib import Path


import asyncio
import shlex
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Literal

from rich.markdown import Markdown as RichMarkdown
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import MouseDown, MouseMove, MouseUp
from textual.widgets import Static, Input, Button

from client.config import AppConfig
from client.router import ModelRouter
from client.input_processor import InputProcessor
from client.clipboard import copy_to_clipboard
from client.reflection import Reflection

from memory.chronicle import Chronicle
from memory.entity_memory import EntityMemory
from memory.distillation import Distillation
from memory.conversation_store import ConversationStore
from memory.project_store import ProjectStore

from ui.panes.left_menu import LeftMenuPane, _build_home_nav
from ui.panes.active_chat import ActiveChatPane
from ui.panes.history import HistoryPane
from ui.pages.conversations import ConversationsPage
from ui.rendering.animations import AnimationController, AnimationConfig




def _ci_contains(haystack: str, needle: str) -> bool:
    return (needle or "").strip().lower() in (haystack or "").lower()


def _ts_now(cfg: AppConfig) -> str:
    if not cfg.ui.show_timestamps:
        return ""
    if cfg.app.timezone == "utc":
        return datetime.utcnow().strftime("%H:%M:%S UTC")
    return datetime.now().strftime("%H:%M:%S")


def _ts_from_store(cfg: AppConfig, ts: str) -> str:
    return ts if cfg.ui.show_timestamps else ""


RenderMode = Literal["plain", "markdown"]
AlignMode = Literal["left", "right", "full"]

LeftPage = Literal[
    "home",
    "help_index",
    "help_home",
    "help_conversations",
    "help_menu",
    "help_chat",
    "help_history",
    "conversations",
    "project",
    "config",
]


class BubbleCombo(Vertical):
    """
    Chat bubble — header + colour bar + body.

    Header:     NAME  [glyph]  [title right-justified]
    Colour bar: solid strip in entity jewel tone, full width
    Body:       response text

    Both entity and user bubbles get a colour bar.
    User colour defaults to steel blue #4A7A9B if no color_hex given.
    """

    USER_COLOR = "4A7A9B"

    def __init__(
        self,
        header: str,
        body: str = "",
        *,
        classes: str = "",
        render_mode: RenderMode = "plain",
        color_hex: Optional[str] = None,
        glyph: str = "",
        title: str = "",
    ) -> None:
        super().__init__(classes=classes)
        self._header_text = header or ""
        self._body_text = body or ""
        self._render_mode: RenderMode = render_mode
        self._color_hex = color_hex
        self._glyph = glyph or ""
        self._title = title or ""
        self.header_widget: Optional[Static] = None
        self.bar_widget: Optional[Static] = None
        self.body_widget: Optional[Static] = None

    def _renderable(self, text: str):
        text = text or ""
        return RichMarkdown(text) if self._render_mode == "markdown" else text

    def _build_header_markup(self, hex_val: str) -> str:
        name_part = self._header_text.rstrip()
        glyph_part = f"  {self._glyph}" if self._glyph else ""
        left = f"{name_part}{glyph_part}"
        if self._title:
            return (
                f"[bold #{hex_val}]{left}[/]"
                f"[#{hex_val}]{self._title:>40}[/]"
            )
        return f"[bold #{hex_val}]{left}[/]"

    def compose(self) -> ComposeResult:
        hex_val = (self._color_hex or self.USER_COLOR).lstrip("#")
        self.header_widget = Static(
            self._build_header_markup(hex_val),
            classes="bubble_head",
            markup=True,
        )
        self.bar_widget = Static(
            f"[#{hex_val}]{'▒' * 120}[/]",
            classes="bubble_bar",
            markup=True,
        )
        self.body_widget = Static(
            self._renderable(self._body_text.rstrip()),
            classes="bubble_tail",
            markup=False,
        )
        yield self.header_widget
        yield self.bar_widget
        yield self.body_widget

    def on_mount(self) -> None:
        hex_val = f"#{(self._color_hex or self.USER_COLOR).lstrip('#')}"
        if self.header_widget:
            self.header_widget.styles.border = ("solid", hex_val)
            self.header_widget.styles.border_bottom = ("none", hex_val)
        if self.bar_widget:
            self.bar_widget.styles.border_left = ("solid", hex_val)
            self.bar_widget.styles.border_right = ("solid", hex_val)
            self.bar_widget.styles.border_top = ("none", hex_val)
            self.bar_widget.styles.border_bottom = ("none", hex_val)
        if self.body_widget:
            self.body_widget.styles.border = ("solid", hex_val)
            self.body_widget.styles.border_top = ("none", hex_val)

    def append(self, delta: str) -> None:
        self._body_text += delta
        if self.body_widget is not None:
            self.body_widget.update(self._renderable(self._body_text.rstrip()))


class BubbleRow(Horizontal):
    """Row wrapper for left/right/full alignment using spacers."""

    def __init__(self, combo: BubbleCombo, *, align: AlignMode) -> None:
        super().__init__(classes="bubble_row")
        self._combo = combo
        self._align = align

    def compose(self) -> ComposeResult:
        if self._align == "full":
            yield self._combo
            return

        spacer_left = Static("", classes="spacer", markup=False)
        spacer_right = Static("", classes="spacer", markup=False)

        if self._align == "right":
            yield spacer_left
            yield self._combo
        else:
            yield self._combo
            yield spacer_right


class PaneDragHandle(Static):
    """
    A thin vertical drag handle between the middle and right panes.
    Dragging horizontally adjusts the width of #right.

    Width range: 15% – 55% of screen width.
    """

    _HANDLE_CHAR = "▕"
    _WIDTH_MIN_PCT = 15
    _WIDTH_MAX_PCT = 55
    _WIDTH_DEFAULT_PCT = 28

    def __init__(self) -> None:
        super().__init__(self._HANDLE_CHAR, classes="pane_drag_handle", markup=False)
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_width = 0

    def on_mouse_down(self, event: MouseDown) -> None:
        self._dragging = True
        self._drag_start_x = event.screen_x
        right = self.app.query_one("#right")
        # Store current width in percent if possible, else cells
        try:
            self._drag_start_width = right.styles.width.value  # type: ignore[union-attr]
        except Exception:
            self._drag_start_width = self._WIDTH_DEFAULT_PCT
        self.capture_mouse()
        event.stop()

    def on_mouse_move(self, event: MouseMove) -> None:
        if not self._dragging:
            return
        delta_x = event.screen_x - self._drag_start_x
        screen_w = self.app.size.width or 80
        # Convert pixel delta to percent of screen width
        delta_pct = (delta_x / screen_w) * 100
        new_pct = self._drag_start_width - delta_pct  # drag left = wider right pane
        new_pct = max(self._WIDTH_MIN_PCT, min(self._WIDTH_MAX_PCT, new_pct))
        try:
            right = self.app.query_one("#right")
            right.styles.width = f"{new_pct:.1f}%"
        except Exception:
            pass
        event.stop()

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
        event.stop()



from ui.state import StatusState



@dataclass
class PendingArchive:
    """
    Tracks the most recent completed turn *displayed in middle* but not yet shown in history.
    LF invariant: "current turn bundle moves to history only on next submit".
    """
    conversation_id: str
    thread_id: str
    user_text: str
    assistant_text: str


@dataclass
class CurrentTurn:
    user_text: str = ""
    assistant_text: str = ""
    assistant_complete: bool = False
    model: Optional[str] = None
    routing_reason: Optional[str] = None
    thread_id: Optional[str] = None


class ChatTUIApp(App):
    CSS = """
    /* ── Arca Cognitorium — Dark Field Aesthetic ─────────────────────────── */

    Screen {
        background: #0D0B0E;
    }

    /* ── Three-pane horizontal strip ──────────────────────────────────────── */
    #app_root {
        layout: vertical;
        height: 100%;
    }
    #pane_row {
        layout: horizontal;
        height: 1fr;
    }

    #left {
        width: 26%;
        height: 100%;
        background: #0D0B0E;
        border-right: solid #2A2535;
        layout: vertical;
    }

    #middle {
        width: 1fr;
        height: 100%;
        background: #0D0B0E;
        layout: vertical;
    }

    #right {
        width: 28%;
        height: 100%;
        background: #0D0B0E;
        border-left: solid #2A2535;
        layout: vertical;
    }

    /* ── Left pane internals ───────────────────────────────────────────────── */
    #legend {
        height: auto;
        padding: 1 2;
        color: #5A6070;
        border-bottom: solid #2A2535;
    }

    #menu_page {
        height: 1fr;
        padding: 1 2;
        color: #D4C8A8;
        background: #0D0B0E;
    }

    #menu_cmd {
        height: 3;
        border-top: solid #2A2535;
        background: #161218;
        color: #D4C8A8;
        padding: 0 1;
    }

    #menu_cmd:focus {
        border-top: solid #C9A84C;
    }

    /* ── Middle pane internals ─────────────────────────────────────────────── */
    #current_turn {
        height: 1fr;
        padding: 1 2;
        background: #0D0B0E;
    }

    #chat_input {
        height: 6;
        max-height: 20;
        border-top: solid #C9A84C;
        background: #161218;
        color: #D4C8A8;
        padding: 0 2;
    }

    #chat_input:focus {
        border-top: solid #C68B2A;
    }

    /* ── Right pane internals ──────────────────────────────────────────────── */
    #history_tabs {
        height: auto;
        padding: 0 1;
        border-bottom: solid #2A2535;
    }

    #history_view {
        height: 1fr;
        padding: 1 2;
        background: #0D0B0E;
    }

    #history_input {
        height: 3;
        border-top: solid #2A2535;
        background: #161218;
        color: #D4C8A8;
        padding: 0 1;
    }

    #history_input:focus {
        border-top: solid #C9A84C;
    }

    /* ── Status layer ──────────────────────────────────────────────────────── */
    #status_layer {
        height: 2;
        min-height: 2;
        background: #0D0B0E;
        border-top: solid #2A2535;
        padding: 0 1;
    }

    /* ── Thread tab buttons ────────────────────────────────────────────────── */
    Button {
        background: #161218;
        color: #5A6070;
        border: solid #C9A84C;
        height: 1;
        min-width: 6;
        padding: 0 1;
    }
    Button:focus {
        background: #1A1628;
        color: #C9A84C;
        border: solid #C9A84C;
    }
    Button:hover {
        background: #1A1628;
        color: #D4C8A8;
    }
    Button.-active {
        background: #1A1628;
        color: #C9A84C;
        border: solid #C9A84C;
    }

    /* ── Bubble system ─────────────────────────────────────────────────────── */
    .spacer { width: 1fr; }
    .bubble_row { height: auto; width: 1fr; }

    /* In the history pane, bubbles stack full-width — no offset */
    #history_view .bubble_combo {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
    }
    #history_view .spacer { display: none; }

    .bubble_combo {
        width: 82%;
        height: auto;
        margin: 0 0 1 0;
    }
    .bubble_combo.system { width: 1fr; }

    .bubble_head {
        padding: 0 2;
        text-style: bold;
        background: #1A1628;
        height: auto;
        width: 1fr;
        border: solid #C9A84C;
        border-bottom: none;
        color: #C9A84C;
    }

    .bubble_tail {
        padding: 1 2;
        height: auto;
        width: 1fr;
        background: #161218;
        border: solid #2A2535;
        border-top: none;
        color: #D4C8A8;
    }

    /* User bubbles — parchment/cyan treatment */
    .user .bubble_head {
        background: #141820;
        border: solid #4A7A9B;
        border-bottom: none;
        color: #7AAEC8;
    }
    .user .bubble_tail {
        background: #0F1318;
        border: solid #2A3A4A;
        border-top: none;
        color: #D4C8A8;
    }

    /* Assistant/Entity bubbles — gold/amber treatment */
    .assistant .bubble_head {
        background: #1A1628;
        border: solid #C9A84C;
        border-bottom: none;
        color: #C9A84C;
    }
    .assistant .bubble_tail {
        background: #131020;
        border: solid #2A2535;
        border-top: none;
        color: #D4C8A8;
    }

    /* Entity interrupt — jewel tone, slightly narrower */
    .entity-interrupt.bubble_combo { width: 70%; }
    .entity-interrupt .bubble_head {
        background: #1A1A28;
        border: solid #7A6A9A;
        border-bottom: none;
        color: #A898C8;
    }
    .entity-interrupt .bubble_tail {
        background: #0F0F1C;
        border: solid #2A2540;
        border-top: none;
        color: #D4C8A8;
    }

    /* System messages — mist treatment */
    .system .bubble_head {
        background: #0F0F14;
        border: solid #2A2535;
        border-bottom: none;
        color: #5A6070;
        text-style: italic;
    }
    .system .bubble_tail {
        background: #0D0B0E;
        border: solid #1E1C28;
        border-top: none;
        color: #5A6070;
        text-style: italic;
    }

    /* ── Boot sequence ─────────────────────────────────────────────────────── */
    .boot_sigil {
        color: #C9A84C;
        height: auto;
        content-align: center middle;
        opacity: 8%;
    }
    .boot_banner { color: #C9A84C; height: auto; }
    .boot_line   { color: #5A6070; height: auto; text-style: italic; }

    /* ── Animation targets ─────────────────────────────────────────────────── */
    .entity-pulse       { border: solid #C9A84C; }
    .distillation-ripple { border: solid #C68B2A; }

    /* ── Conjuration Chamber ───────────────────────────────────────────────── */
    #conjure-title          { color: #C9A84C; text-style: bold; padding: 1 2; }
    .conjure-section        { height: auto; margin: 1 0; }
    .conjure-section-header { color: #AD6F3B; text-style: bold; padding: 0 1; }
    .conjure-row            { height: auto; padding: 0 1; }
    .conjure-key            { color: #D4C8A8; width: 30; }
    .conjure-empty          { color: #5A6070; padding: 0 2; }

    #convpage-title  { color: #C9A84C; text-style: bold; padding: 1 2; }
    .convpage-empty  { color: #5A6070; padding: 1 2; }

    /* ── Council nav entries ───────────────────────────────────────────────── */
    .council-member { color: #C9A84C; padding: 0 2; height: auto; }
    .council-active { text-style: bold; }
    .council-empty  { color: #2A2535; padding: 0 2; height: auto; text-style: italic; }

    /* ── Pane drag handle ──────────────────────────────────────────────────── */
    .pane_drag_handle {
        width: 1;
        height: 100%;
        background: #0D0B0E;
        color: #2A2535;
        content-align: center middle;
    }
    .pane_drag_handle:hover {
        background: #1A1628;
        color: #C9A84C;
    }

    """



    BINDINGS = [Binding("ctrl+q", "quit", "Quit", show=False)]
    SEED_GREETING = "Conversation started. Send your first message when ready."

    THREADTAB_PREFIX = "threadtab-"  # must match ui/panes/history.py

    def __init__(self, cfg: AppConfig, *, api_key: str) -> None:
        super().__init__()
        self.cfg = cfg

        self.router = ModelRouter(cfg, api_key=api_key)
        self.input = InputProcessor()

        self.chronicle = Chronicle(cfg)
        self.distillation = Distillation(box=self.router._box, cfg=cfg)
        self.conversations = ConversationStore(cfg, summarizer=self.distillation)
        self.reflection = Reflection(cfg, box=self.router._box, chronicle=self.chronicle)
        


        self.projects = ProjectStore()

        self.current = CurrentTurn()
        self._assistant_combo: Optional[BubbleCombo] = None
        self._streaming = False

        self._left_page: LeftPage = "home"
        self._nav_stack: List[LeftPage] = []
        self._history_query: str = ""
        self._status: str = ""

        self._project_page_id: Optional[str] = None

        # Pending archive state (LF invariant)
        self._pending: Optional[PendingArchive] = None

        self.animation_controller = AnimationController(
            app=self,
            config=AnimationConfig(**self.cfg.raw.get('animations', {}))
        )

        from memory.grimoire import Grimoire
        # Phase 3 addition — instantiate Grimoire
        self.grimoire = Grimoire(
            store_path=Path("storage/grimoire/grimoire.json"),
            max_injection_tokens=self.cfg.raw.get("memory", {}).get("grimoire_max_tokens", 800)
        )
        

        from memory.tome import Tome
        self.tome = Tome(
            project_store=self.projects,
            max_injection_tokens=self.cfg.raw.get("memory", {}).get("tome_max_tokens", 600)
        )

        self.entity_memory = EntityMemory(
            token_budget=self.cfg.raw.get("memory", {}).get("entity_memory_budget", 300),
        )

        from entities.entity_compiler import EntityCompiler
        from entities.council import Council
        from entities.emergence import EmergenceEngine
        from entities.interruption import InterruptionEngine
        from entities.dynamics import InterEntityDynamics
        self.compiler = EntityCompiler("entities")
        dev_emerge_all = bool(self.cfg.raw.get("dev", {}).get("emerge_all", False))
        self.council = Council(self.compiler, dev_emerge_all=dev_emerge_all)
        reflection_log = self.cfg.raw.get("storage", {}).get(
            "reflection_log_path", "storage/logs/reflections.jsonl"
        )
        self.emergence_engine = EmergenceEngine(reflection_log)
        self.interruption_engine = InterruptionEngine()
        self.dynamics = InterEntityDynamics()

        from client.assessor import BackgroundAssessor
        from client.archivist_chronicler import BackgroundArchivist
        self.background_assessor = BackgroundAssessor(
            config=self.cfg,
            grimoire=self.grimoire,
            chronicle=self.chronicle,
            compiler=self.compiler,   # EntityCompiler instance
        )
        self.background_archivist = BackgroundArchivist(
            config=self.cfg,
            chronicle=self.chronicle,
            compiler=self.compiler,
        )


    def _on_conversation_selected(self, cid: str | None) -> None:
        if cid:
            self.conversations.load(cid)
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()

    def compose(self) -> ComposeResult:
        with Vertical(id="app_root"):
            with Horizontal(id="pane_row"):
                self.left        = LeftMenuPane(id="left")
                self.middle      = ActiveChatPane(id="middle")
                self._drag_handle = PaneDragHandle()
                self.right       = HistoryPane(id="right")
                yield self.left
                yield self.middle
                yield self._drag_handle
                yield self.right
            yield StatusLayer(id="status_layer")

    def _app_bind(self, key: str, action: str) -> None:
        try:
            self.bind(key, action, show=False, priority=True)  # type: ignore[call-arg]
        except TypeError:
            self.bind(key, action, show=False)

    async def on_mount(self) -> None:
        self._app_bind(str(self.cfg.keys.focus_left), "focus_left")
        self._app_bind(str(self.cfg.keys.focus_middle), "focus_middle")
        self._app_bind(str(self.cfg.keys.focus_right), "focus_right")
        self._app_bind(str(self.cfg.keys.submit_message), "submit_message")
        # Seed status bar with initial entity state
        self.status_layer = self.query_one("#status_layer", StatusLayer)
        entity = self.council.active
        self.status_layer.update_status(
            entity_name=entity.display_name,
            entity_color=entity.color_hex,
            model_id=self.cfg.raw.get("default_model", "—"),
        )
        await self._run_boot_sequence()
        self.animation_controller.start_idle()

    async def _run_boot_sequence(self) -> None:
        """
        Boot sequence procedure:
        1. Render dark screen with single sigil from sigils/ directory
           - Load random .txt file from sigils/ directory
           - If sigils/ empty, use fallback: single '◆' centered
           - Display at low opacity in center of chat pane
        2. Render ASCII title via pyfiglet
           - Select random font from config.boot.banner_fonts list
           - Call: pyfiglet.figlet_format('ARCA COGNITORIUM', font=font)
           - Display in title banner region in gold color
        3. Display opening line
           - Select random line from config.boot.boot_lines list
           - Render in center pane in mist italic
           - Await asyncio.sleep(1.5)  # Let Wizard read it
        4. Resolve interface
           - Remove boot overlay
           - Mount StatusLayer, left menu, history pane (already composed)
           - StatusLayer initial state populated from config
        5. Focus Invocation Field
        """
        if not self.cfg.raw.get('boot', {}).get('boot_enabled', True):
            return

        from pathlib import Path
        import random
        import pyfiglet
        from textual.widgets import Static

        # 1. Sigil
        sigil_text = '◆'
        sigil_files = list(Path('sigils').glob('*.txt'))
        if sigil_files:
            sigil_text = random.choice(sigil_files).read_text()

        sigil = Static(sigil_text, classes='boot_sigil', markup=False)
        await self.middle.current_turn.mount(sigil)
        await asyncio.sleep(0.8)

        # 2. ASCII title banner
        banner_fonts = self.cfg.raw.get('boot', {}).get('banner_fonts', ['slant'])
        font = random.choice(banner_fonts)
        try:
            banner_text = pyfiglet.figlet_format('ARCA COGNITORIUM', font=font)
        except Exception:
            banner_text = 'ARCA COGNITORIUM'

        banner = Static(f'[bold #C9A84C]{banner_text}[/]', classes='boot_banner')
        await self.middle.current_turn.mount(banner)
        await asyncio.sleep(0.6)

        # 3. Opening line
        boot_lines = self.cfg.raw.get('boot', {}).get('boot_lines', ['The fire is lit.'])
        line = random.choice(boot_lines)
        opening = Static(f'[italic #5A6070]{line}[/]', classes='boot_line')
        await self.middle.current_turn.mount(opening)
        await asyncio.sleep(1.5)

        # 4. Remove boot overlay
        sigil.remove()
        banner.remove()
        opening.remove()

        # 5. Focus
        self.middle.focus_input()
        
        copy_key = str(self.cfg.keys.get("copy_last", "") or "")
        if copy_key:
            self._app_bind(copy_key, "copy_last")

        # Widget-level keymaps (Textual 2.1.2 compatibility)
        self.middle.chat_input.set_keymap(
            submit=str(self.cfg.keys.submit_message),
            focus_left=str(self.cfg.keys.focus_left),
            focus_middle=str(self.cfg.keys.focus_middle),
            focus_right=str(self.cfg.keys.focus_right),
            copy_last=copy_key or None,
        )
        self.left.cmd.set_keymap(
            focus_left=str(self.cfg.keys.focus_left),
            focus_middle=str(self.cfg.keys.focus_middle),
            focus_right=str(self.cfg.keys.focus_right),
        )
        if hasattr(self.left, "page") and hasattr(self.left.page, "set_keymap"):
            self.left.page.set_keymap(
                focus_left=str(self.cfg.keys.focus_left),
                focus_middle=str(self.cfg.keys.focus_middle),
                focus_right=str(self.cfg.keys.focus_right),
            )
        self.right.history_input.set_keymap(
            focus_left=str(self.cfg.keys.focus_left),
            focus_middle=str(self.cfg.keys.focus_middle),
            focus_right=str(self.cfg.keys.focus_right),
        )


        # Phase 3 migration + backups (one-time as needed)
        try:
            migrated, backup_dir = await asyncio.to_thread(self.conversations.migrate_all_if_needed)
            if migrated > 0:
                self._set_status(f"Migrated {migrated} conversation(s) to Phase 3 schema. Backup: {backup_dir}")
        except Exception as e:
            self._set_status(f"Migration check failed: {e}")

        # Startup behavior (Option A): auto-load most recent conversation if any exist (no creation).
        convos = self.conversations.list()
        if convos:
            try:
                self.conversations.load(convos[0]["id"])
            except Exception:
                self.conversations.clear_active()

        self._refresh_thread_tabs()
        self._render_full_history_from_store(clear_first=True)
        self._refresh_council_nav()
        self._go_left_page("home", push=False)
        self._render_legend()
        self.middle.focus_input()


    # -------------------------
    # Status / legend
    # -------------------------
    def _set_status(self, msg: str) -> None:
        self._status = (msg or "").strip()
        self._render_legend()

    def _render_legend(self) -> None:
        conv = self.conversations.active
        entity = self.council.active if hasattr(self, "council") else None

        # Line 1: app name + active entity
        entity_label = entity.display_name if entity else "LUMINARIOUS"
        line1 = f"◆ {self.cfg.app.name}  ·  {entity_label}"

        # Line 2: active conversation title
        if conv:
            title = conv.title or "(untitled)"
            pid = self.projects.project_for_conversation(conv.id)
            if pid:
                p = self.projects.get_by_id(pid)
                scope = f"  [{p.name if p else 'project'}]"
            else:
                scope = ""
            line2 = f"Thread: {title}{scope}"
        else:
            line2 = "No conversation loaded"

        # Line 3: status message (cleared after display on next render if empty)
        line3 = self._status if self._status else ""

        legend = line1 + "\n" + line2
        if line3:
            legend += "\n" + line3

        self.left.set_legend(legend)

    # -------------------------
    # Thread tabs
    # -------------------------
    def _refresh_thread_tabs(self) -> None:
        conv = self.conversations.active
        if conv is None:
            self.right.set_tabs([])
            return
        tabs = []
        for t in conv.threads:
            tabs.append((t.id, t.name, (t.id == conv.active_thread_id)))
        self.right.set_tabs(tabs)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = (event.button.id or "").strip()
        if not bid.startswith(self.THREADTAB_PREFIX):
            return

        if self._streaming:
            self._set_status("Cannot switch threads while streaming.")
            return

        tid = bid[len(self.THREADTAB_PREFIX) :].strip()
        if not tid:
            return
        try:
            self.conversations.set_active_thread(tid)
        except Exception as e:
            self._set_status(f"Thread switch failed: {e}")
            return

        # Keep LF pending invariant: do NOT force-append pending to history on switch.
        self._refresh_thread_tabs()
        self._render_full_history_from_store(clear_first=True)
        self._render_legend()

    # -------------------------
    # Actions
    # -------------------------
    def action_focus_left(self) -> None:
        self.left.focus_input()

    def action_focus_middle(self) -> None:
        self.middle.focus_input()

    def action_focus_right(self) -> None:
        self.right.focus_input()

    def action_submit_message(self) -> None:
        if not self.middle.chat_input.has_focus:
            return
        self._submit_middle_message()

    def action_copy_last(self) -> None:
        text = self._get_last_assistant_text()
        if not text.strip():
            self._set_status("Nothing to copy yet.")
            return
        ok, method = copy_to_clipboard(text)
        self._set_status(f"Copied last assistant message ({method})." if ok else f"Copy failed: {method}")

    # -------------------------
    # Left router
    # -------------------------
    def _go_left_page(self, page: LeftPage, *, push: bool = True) -> None:
        if push and self._left_page != page:
            self._nav_stack.append(self._left_page)
        self._left_page = page
        self._render_left_page()

    def _back_left_page(self) -> None:
        # LF: /back from a project page returns to /conversations
        if self._left_page == "project":
            self._project_page_id = None
            self._go_left_page("conversations", push=False)
            return

        if not self._nav_stack:
            self._render_left_page()
            return
        self._left_page = self._nav_stack.pop()
        self._render_left_page()

    def _render_left_page(self) -> None:
        if self._left_page == "home":
            # LeftMenuPane owns the home nav — reset it to display the lore nav structure
            self.left.set_page(_build_home_nav(self.left._council_lines))

        elif self._left_page == "help_index":
            self.left.set_page(self._help_index_text())
        elif self._left_page == "help_home":
            self.left.set_page(self._help_home_text())
        elif self._left_page == "help_conversations":
            self.left.set_page(self._help_conversations_text())
        elif self._left_page == "help_menu":
            self.left.set_page(self._help_menu_text())
        elif self._left_page == "help_chat":
            self.left.set_page(self._help_chat_text())
        elif self._left_page == "help_history":
            self.left.set_page(self._help_history_text())

        elif self._left_page == "conversations":
            self.left.set_page(self._conversations_page_text())
        elif self._left_page == "project":
            self.left.set_page(self._project_page_text())
        elif self._left_page == "config":
            self.left.set_page(self._config_page_text())
        else:
            self.left.set_page("Unknown page.")

    def _home_page_text(self) -> str:
        # LF: Home shows no commands.
        return "\n".join(["Home", "====", "", "Pages", "-----", "Home", "Help", "Conversations", "Config"])

    # -------------------------
    # Help pages (Phase 3: /help <topic>)
    # -------------------------
    def _help_index_text(self) -> str:
        return "\n".join(
            [
                "Help",
                "====",
                "",
                "Help topics (use /help <topic>)",
                "-------------------------------",
                "  /help home",
                "  /help conversations",
                "  /help menu",
                "  /help chat",
                "  /help history",
                "",
                "Navigation (NOT help)",
                "---------------------",
                "  /home        (alias: /menu)",
                "  /conversations",
                "  /config",
                "  /back",
                "",
                "Phase 3 threads/branching (commands)",
                "-----------------------------------",
                "  /threads",
                "  /thread <n|name|id>",
                "  /thread rename <n|name|id> \"New Name\"",
                "  /thread delete <n|name|id>",
                "  /branch <n|last>",
            ]
        )

    def _help_home_text(self) -> str:
        return "\n".join(
            [
                "Help — Home",
                "===========",
                "",
                "Home is a landing page.",
                "",
                "Go there with:",
                "  /home",
                "  /menu   (alias)",
            ]
        )

    def _help_conversations_text(self) -> str:
        return "\n".join(
            [
                "Help — Conversations",
                "====================",
                "",
                "Open the conversations hub:",
                "  /conversations",
                "",
                "Common commands (menu pane):",
                "  /new [\"Title\"]",
                "  /load <n>",
                "  /load name \"Title\"",
                "  /rename \"New Title\"",
                "  /delete <n>",
                "  /delete name \"Title\"",
                "",
                "Projects:",
                "  /project new \"Project\"",
                "  /project <n>   (from projects list)",
                "  /project \"Name\"",
                "  /move <n|\"Title\"> \"Project\"",
                "  /delete project <n|\"Project\">",
            ]
        )

    def _help_menu_text(self) -> str:
        return "\n".join(
            [
                "Help — Menu (Left Pane Command Prompt)",
                "======================================",
                "",
                "The left pane input expects slash-commands:",
                "  /help ...",
                "  /home  /menu",
                "  /conversations",
                "  /config",
                "  /back",
                "  /quit",
                "",
                "Note:",
                "  Chat messages are written in the middle pane.",
            ]
        )

    def _help_chat_text(self) -> str:
        submit = str(self.cfg.keys.submit_message)
        copy_key = str(self.cfg.keys.get("copy_last", "") or "")
        return "\n".join(
            [
                "Help — Chat (Middle Pane)",
                "------------------------",
                "",
                "Authoring",
                "---------",
                "Enter: newline",
                f"{submit}: submit",
                "",
                "Fallback submit",
                "---------------",
                "/send   (from menu pane)",
                "",
                "Copy",
                "----",
                f"{copy_key}: copy last assistant",
                "/copy",
            ]
        )

    def _help_history_text(self) -> str:
        return "\n".join(
            [
                "Help — History (Right Pane)",
                "--------------------------",
                "",
                "Threads (tabs)",
                "-------------",
                "Click a thread tab to switch (blocked while streaming).",
                "Or use:",
                "  /threads",
                "  /thread <n|name|id>",
                "",
                "Thread lifecycle",
                "---------------",
                "  /thread rename <n|name|id> \"New Name\"",
                "  /thread delete <n|name|id>  (cannot delete main; switches to main)",
                "",
                "Branching",
                "--------",
                "  /branch last",
                "  /branch <n>   (n = assistant turn index in current thread)",
                "",
                "Search (filter)",
                "--------------",
                "Type query in right input and press Enter to filter.",
                "Submit empty query to clear.",
            ]
        )

    def _config_page_text(self) -> str:
        return "\n".join(["Config", "======", "", "(unchanged in this step)"])

    # -------------------------
    # Hub + Project pages
    # -------------------------
    def _main_conversations(self) -> List[Dict[str, str]]:
        # Main list = conversations not in any project.
        return [c for c in self.conversations.list() if not self.projects.is_projected(c["id"])]

    def _project_conversations(self, project_id: str) -> List[Dict[str, str]]:
        p = self.projects.get_by_id(project_id)
        if not p:
            return []
        allow = set(p.conversation_ids)
        return [c for c in self.conversations.list() if c.get("id") in allow]

    def _conversations_page_text(self) -> str:
        convos = self._main_conversations()
        projects = self.projects.list_projects()

        def trunc(s: str, n: int) -> str:
            s = s or ""
            return s if len(s) <= n else (s[: n - 1] + "…")

        title_w = 36
        lines: List[str] = []
        lines.append("Conversations (Main)")
        lines.append("===================")
        lines.append("")
        if not convos:
            lines.append("(none)")
        else:
            for idx, c in enumerate(convos, start=1):
                active_marker = "*" if (self.conversations.active and c["id"] == self.conversations.active.id) else " "
                title = c.get("title") or "(untitled)"
                updated = c.get("updated_at") or ""
                lines.append(f"{active_marker} {idx:>3}. {trunc(title, title_w):<{title_w}}  [{updated}]")

        lines.append("")
        lines.append("Projects")
        lines.append("========")
        lines.append("")
        if not projects:
            lines.append("(none)")
        else:
            for i, p in enumerate(projects, start=1):
                lines.append(f"  {i:>3}. {trunc(p.name, 44):<44}  ({len(p.conversation_ids)} convos)")

        lines.append("")
        lines.append("Commands are contextual to this page (Main + Projects).")
        return "\n".join(lines)

    def _project_page_text(self) -> str:
        if not self._project_page_id:
            return 'No project selected. Use: /project <n>  or  /project "Title"'

        p = self.projects.get_by_id(self._project_page_id)
        if not p:
            return "Project not found."

        convos = self._project_conversations(p.id)

        def trunc(s: str, n: int) -> str:
            s = s or ""
            return s if len(s) <= n else (s[: n - 1] + "…")

        title_w = 36
        lines: List[str] = []
        lines.append(f"Project: {p.name}")
        lines.append("=" * (9 + len(p.name)))
        lines.append("")
        if not convos:
            lines.append("(none)")
        else:
            for idx, c in enumerate(convos, start=1):
                active_marker = "*" if (self.conversations.active and c["id"] == self.conversations.active.id) else " "
                title = c.get("title") or "(untitled)"
                updated = c.get("updated_at") or ""
                lines.append(f"{active_marker} {idx:>3}. {trunc(title, title_w):<{title_w}}  [{updated}]")

        lines.append("")
        lines.append("All commands are contextual to this project. Use /back to return to /conversations.")
        return "\n".join(lines)

    def _refresh_lists_if_visible(self) -> None:
        if self._left_page in ("conversations", "project"):
            self._render_left_page()

    # -------------------------
    # History search
    # -------------------------
    def _apply_history_search(self, query: str) -> None:
        q = (query or "").strip()
        self._history_query = q
        self._render_full_history_from_store(clear_first=True)
        self._set_status("History filter cleared." if not q else f"History filtered by: {q}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "menu_cmd":
            await self._handle_menu_command(event.value)
            event.input.value = ""
            return
        if event.input.id == "history_input":
            self._apply_history_search(event.value)
            event.input.value = ""
            return

    # -------------------------
    # Helpers
    # -------------------------
    def _parse_argv(self, args: str) -> List[str]:
        try:
            return shlex.split(args or "")
        except Exception:
            return (args or "").strip().split()

    def _title_exists(self, title: str, *, exclude_id: Optional[str] = None) -> bool:
        want = (title or "").strip().lower()
        if not want:
            return False
        for c in self.conversations.list():
            if exclude_id and c.get("id") == exclude_id:
                continue
            if (c.get("title") or "").strip().lower() == want:
                return True
        return False

    def _find_conversation_id_by_title(self, title: str) -> Optional[str]:
        matches = self.conversations.find_by_title(title)
        if not matches:
            return None
        return matches[0].get("id")

    def _resolve_project_id_by_index(self, idx: int) -> Optional[str]:
        projects = self.projects.list_projects()
        if idx < 1 or idx > len(projects):
            return None
        return projects[idx - 1].id

    def _resolve_project_id_by_name(self, name: str) -> Optional[str]:
        p = self.projects.get_by_name_ci(name)
        return p.id if p else None

    def _current_conversation_index_list(self) -> List[Dict[str, str]]:
        if self._left_page == "project" and self._project_page_id:
            return self._project_conversations(self._project_page_id)
        return self._main_conversations()

    def _resolve_conversation_id_by_index(self, idx: int) -> Optional[str]:
        subset = self._current_conversation_index_list()
        if idx < 1 or idx > len(subset):
            return None
        return subset[idx - 1]["id"]

    def _seed_new_conversation(self) -> None:
        if not self.conversations.active:
            return
        t = self.conversations.get_thread()
        if t.messages:
            return
        self.conversations.append("assistant", self.SEED_GREETING)

    def _mount_combo(
        self,
        container,
        *,
        header: str,
        body: str,
        render_mode: RenderMode,
        align: AlignMode,
        combo_classes: str,
        color_hex: Optional[str] = None,
    ) -> BubbleCombo:
        combo = BubbleCombo(header, body, classes=f"bubble_combo {combo_classes}", render_mode=render_mode, color_hex=color_hex)
        container.mount(BubbleRow(combo, align=align))
        return combo

    def _should_exclude_pending_for_render(self, conv_id: str, thread_id: str, messages: List[Dict]) -> int:
        """
        Returns how many trailing messages to exclude from history rendering for LF invariant.
        Excludes 2 messages (user+assistant) iff they match pending and are the last two messages.
        """
        if not self._pending:
            return 0
        p = self._pending
        if p.conversation_id != conv_id or p.thread_id != thread_id:
            return 0
        if len(messages) < 2:
            return 0
        m2 = messages[-1]
        m1 = messages[-2]
        if (
            m1.get("role") == "user"
            and (m1.get("content") or "") == p.user_text
            and m2.get("role") == "assistant"
            and (m2.get("content") or "") == p.assistant_text
        ):
            return 2
        return 0

    # -------------------------
    # Chat submit / assistant
    # -------------------------
    def _submit_middle_message(self) -> None:
        if self._streaming:
            self._set_status("Assistant is streaming; please wait.")
            return
        if not self.conversations.active:
            self._set_status("No conversation loaded. Use /new or /load.")
            return

        text = self.middle.get_chat_text().replace("\x00", "").rstrip()
        if not text.strip():
            return

        # If there is a pending completed turn, archive it now (LF invariant: on next submit).
        if self._pending is not None:
            self._archive_pending_if_visible()
            self.middle.clear_current_turn()

        # Start new current turn
        self.middle.set_chat_text("")
        self.current = CurrentTurn(user_text=text, thread_id=self.conversations.active.active_thread_id)

        you_header = "You"
        ts = _ts_now(self.cfg)
        if ts:
            you_header = f"{you_header} {ts}"

        self._mount_combo(
            self.middle.current_turn,
            header=you_header,
            body=text,
            render_mode="plain",
            align="right",
            combo_classes="user",
        )

        self._render_legend()
        asyncio.create_task(self._assistant_task(user_text=text, thread_id=self.current.thread_id or "main"))

    def _archive_pending_if_visible(self) -> None:
        """
        If pending belongs to the currently active thread, show it in history view.
        Always clears pending afterwards (because "next submit" has occurred).
        """
        if not self._pending:
            return

        conv = self.conversations.active
        if conv and self._pending.conversation_id == conv.id and self._pending.thread_id == conv.active_thread_id:
            you_header = "You"
            ts = _ts_now(self.cfg)
            if ts:
                you_header = f"{you_header} {ts}"

            self._mount_combo(
                self.right.history_view,
                header=you_header,
                body=self._pending.user_text,
                render_mode="plain",
                align="right",
                combo_classes="user",
            )

            active_entity = self.council.active
            entity_name = active_entity.display_name if active_entity else "LUMINARIOUS"
            entity_color = active_entity.color_hex if active_entity else "C9A84C"

            self._mount_combo(
                self.right.history_view,
                header=entity_name,
                body=self._pending.assistant_text,
                render_mode="markdown",
                align="left",
                combo_classes="assistant",
                color_hex=entity_color,
            )
            self.call_after_refresh(self.right.scroll_to_bottom)

        self._pending = None

    async def _assistant_task(self, *, user_text: str, thread_id: str) -> None:
        if not self.conversations.active:
            return

        self._streaming = True
        self.dynamics.reset_turn()  # Phase 8: reset inter-entity dynamics each turn
        self.status_layer.update_status(chronicle_retrieved=False, streaming=True)
        try:
            await asyncio.to_thread(self.conversations.append, "user", user_text, thread_id=thread_id)
            context = await asyncio.to_thread(self._build_context, user_text, thread_id)

            # Update context fill estimate (4 chars ≈ 1 token, 100k window)
            total_chars = sum(len(m.get("content") or "") for m in context)
            context_pct = min(int(total_chars / 400_000 * 100), 100)
            self.status_layer.update_status(context_pct=context_pct)

            decision = self.router.decide(user_text)

            self.current.model = decision.model
            self.current.routing_reason = decision.reason
            self.status_layer.update_status(
                model_id=decision.model,
                streaming=True,
            )
            self._render_legend()

            # Push model + streaming state to status bar
            self.status_layer.update_status(
                model_id=decision.model,
                streaming=True,
            )

            # Header: entity display name only, coloured in entity's jewel tone
            active_entity = self.council.active
            entity_name = active_entity.display_name if active_entity else "LUMINARIOUS"
            entity_color = active_entity.color_hex if active_entity else "C9A84C"
            header = entity_name

            self._assistant_combo = self._mount_combo(
                self.middle.current_turn,
                header=header,
                body="",
                render_mode="markdown",
                align="left",
                combo_classes="assistant",
                color_hex=entity_color,
            )
            await asyncio.to_thread(self._stream_in_thread, decision.model, context)

            self.current.assistant_complete = True
            self.status_layer.update_status(streaming=False)
            self._render_legend()

            assistant_text = self.current.assistant_text
            await asyncio.to_thread(
                self.conversations.append,
                "assistant",
                assistant_text,
                thread_id=thread_id,
                model=decision.model,
                routing_reason=decision.reason,
            )

            conv = self.conversations.active
            if conv:
                self._pending = PendingArchive(
                    conversation_id=conv.id,
                    thread_id=thread_id,
                    user_text=user_text,
                    assistant_text=assistant_text,
                )

            await asyncio.to_thread(
                self.chronicle.add,
                f"USER: {user_text}\nASSISTANT: {assistant_text}",
                {"type": "turn", "conversation_id": self.conversations.active.id, "thread_id": thread_id},
            )

            # thread-scoped summary for analytics
            t = self.conversations.get_thread(thread_id)
            await asyncio.to_thread(
                self.reflection.observe,
                conversation_id=self.conversations.active.id,
                summary=t.summary,
                last_user=user_text,
                last_assistant=assistant_text,
            )

            # Background Assessor — silent observation cycle
            thread_for_assess = self.conversations.get_thread(thread_id)
            result = await asyncio.to_thread(
                self.background_assessor.tick,
                thread_messages=thread_for_assess.messages,
                conversation_id=self.conversations.active.id,
                router=self.router,
            )
            if result.fired and result.written > 0:
                self.status_layer.update_status(grimoire_active=True)
                self.animation_controller.fire_event("grimoire_inject")

            # Entity private memory — write after primary response
            _em_entity = self.council.active
            await asyncio.to_thread(
                self.entity_memory.write,
                _em_entity.entity_id,
                _em_entity.display_name,
                user_text,
                assistant_text,
            )

            # Background Archivist — chronicle preservation cycle
            archivist_result = await asyncio.to_thread(
                self.background_archivist.tick,
                thread_messages=thread_for_assess.messages,
                conversation_id=self.conversations.active.id,
                thread_id=thread_id,
                router=self.router,
            )


            # Phase 8: emergence check + interruption
            await asyncio.to_thread(self._check_emergence)
            await self._check_interruption(user_text, assistant_text)

        except Exception as e:
            self._set_status(f"Assistant error: {e}")
        finally:
            self._streaming = False
            self.status_layer.update_status(streaming=False)
            self._render_legend()

    def _stream_in_thread(self, model: str, context: List[Dict]) -> None:
        import json, sys, random as _rng
        for i, m in enumerate(context):
            _cc = m.get("content") or ""
            if not _cc.strip():
                print(f"DEBUG EMPTY MSG idx={i} role={m.get('role')} content={repr(m.get('content'))}", file=sys.stderr)
        gen, _meta = self.router.stream_response_text(
            model,
            context,
            max_output_tokens=self.cfg.raw.get("max_output_tokens", None),
        )
        base = float(self.cfg.ui.typing_delay_seconds)
        for delta in gen:
            if base > 0:
                if delta in ".!?":
                    time.sleep(base * _rng.uniform(3.0, 5.0))
                elif delta in ",;:":
                    time.sleep(base * _rng.uniform(1.5, 2.5))
                elif delta == "\n":
                    time.sleep(base * _rng.uniform(1.0, 2.0))
                elif delta == " ":
                    time.sleep(base * _rng.uniform(0.5, 1.2))
                else:
                    time.sleep(base * _rng.uniform(0.3, 1.0))
            self.call_from_thread(self._append_assistant_delta, delta)

    def _append_assistant_delta(self, delta: str) -> None:
        self.current.assistant_text += delta
        if self._assistant_combo:
            self._assistant_combo.append(delta)

    # -------------------------
    # Context / history rendering
    # -------------------------
    def _build_context(self, user_text: str, thread_id: str) -> List[Dict]:
        conv = self.conversations.active
        if conv is None:
            return [{"role": "user", "content": user_text}]

        mem_cfg = self.cfg.memory
        messages: List[Dict] = []

        # Phase 6: Entity instruction string — always first in context.
        # Prefixed with lore self-knowledge so Entities understand their habitat.
        active_entity = self.council.active
        if active_entity:
            lore_prefix = (
                "You exist within the Arca Cognitorium — a living oracle and instrument of thought "
                "built by the Wizard. You are one voice among the Council, a body of distinct Entities "
                "each with their own domain, temperament, and purpose. The Wizard consults you "
                "through the Invocation Field. You do not explain the interface or break its atmosphere. "
                "You speak from within the machine, not about it.\n\n"
            )
            entity_mem = self.entity_memory.read(active_entity.entity_id)
            instruction_with_memory = active_entity.instruction_str
            if entity_mem:
                instruction_with_memory += "\n\n" + entity_mem
            messages.append({
                "role": "system",
                "content": lore_prefix + instruction_with_memory
            })



        thread = self.conversations.get_thread(thread_id)
        if thread.summary:
            messages.append({"role": "system", "content": f"Conversation summary:\n{thread.summary}"})

        
        # Phase 3 addition — Grimoire injection
        grimoire_injection = self.grimoire.build_injection_string()
        if grimoire_injection:
            messages.insert(1, {
                "role": "system",
                "content": grimoire_injection
            })
            # Update status layer — Grimoire is present in this context
            self.status_layer.update_status(grimoire_active=True)
            # Fire visual event
            self.animation_controller.fire_event("grimoire_inject")
        else:
            self.status_layer.update_status(grimoire_active=False)
        
        # Phase 4 — Tome injection (project-scoped knowledge)
        tome_injection = self.tome.build_injection_string()
        if tome_injection:
            messages.append({
                "role": "system",
                "content": tome_injection
            })

        # Phase 3 decision:
        # retrieval is project-scoped on conversation_ids BUT thread-restricted per conversation
        proj_id = self.projects.project_for_conversation(conv.id)
        allowed_ids = self.projects.conversation_ids_for_project(proj_id) if proj_id else [conv.id]

        # Build per-conversation active thread mapping for retrieval filtering
        thread_by_conv: Dict[str, str] = {}
        for cid in allowed_ids:
            if cid == conv.id:
                thread_by_conv[cid] = conv.active_thread_id
            else:
                thread_by_conv[cid] = self.conversations.peek_active_thread_id(cid)

        retrieved = self.chronicle.query(
            user_text,
            top_k=int(mem_cfg.retrieve_top_k),
            conversation_ids=allowed_ids,
            thread_by_conversation=thread_by_conv,
        )
        if retrieved:
            blob = "\n\n".join(f"[score={r['score']:.3f}] {r['text']}" for r in retrieved)
            messages.append({"role": "system", "content": "Relevant long-term memory:\n" + blob})
            self.status_layer.update_status(chronicle_retrieved=True)
        else:
            self.status_layer.update_status(chronicle_retrieved=False)

        # Phase 5: distillation trigger
        if self.distillation.should_distill(thread.messages, getattr(self.cfg.memory, 'distillation_threshold', 6000)):
            result = self.distillation.distill(
                thread.messages,
                extract_to_chronicle=True,
                chronicle=self.chronicle,
                reflection=self.reflection
            )
            messages.append(result.compressed_message)
            self.animation_controller.fire_event('distillation')
            self.status_layer.update_status(
                distillation_count=self.status_layer.state.distillation_count + 1
            )
            self.router.router.refresh_reflection_baseline()  # Phase 7/8
            return messages

        short_max = int(mem_cfg.short_term_max_messages)
        for m in thread.messages[-short_max:]:
            messages.append({"role": m.get("role", ""), "content": m.get("content") or ""})

        if not messages or messages[-1]["role"] != "user" or messages[-1]["content"] != user_text:
            messages.append({"role": "user", "content": user_text})

        # Estimate context fill % and push to status bar
        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_tokens = total_chars // 4
        context_limit = self.cfg.raw.get("context_token_limit", 8000)
        context_pct = min(100, int(estimated_tokens / max(context_limit, 1) * 100))
        self.status_layer.update_status(context_pct=context_pct)

        return messages

    def _render_full_history_from_store(self, *, clear_first: bool) -> None:
        if clear_first:
            self.right.clear_history()

        conv = self.conversations.active
        if conv is None:
            self.right.history_view.mount(Static("No conversation loaded.", markup=False))
            return

        self._refresh_thread_tabs()

        t = self.conversations.get_thread(conv.active_thread_id)
        q = (self._history_query or "").strip()

        exclude_tail = self._should_exclude_pending_for_render(conv.id, t.id, t.messages)
        msgs = t.messages[:-exclude_tail] if exclude_tail else t.messages

        for m in msgs:
            role = m.get("role", "")
            content = m.get("content", "")
            ts = _ts_from_store(self.cfg, m.get("ts", ""))

            if q and not (_ci_contains(content, q) or _ci_contains(role, q) or _ci_contains(ts, q)):
                continue

            if role == "user":
                header = "You" if not ts else f"You {ts}"
                self._mount_combo(
                    self.right.history_view,
                    header=header,
                    body=content,
                    render_mode="plain",
                    align="right",
                    combo_classes="user",
                )
            elif role == "assistant":
                entity_name = m.get("entity_name", "LUMINARIOUS")
                entity_id = m.get("entity_id", "luminarious")
                compiled = self.council.get_compiled(entity_id)
                entity_color = compiled.color_hex if compiled else "C9A84C"

                self._mount_combo(
                    self.right.history_view,
                    header=entity_name,
                    body=content,
                    render_mode="markdown",
                    align="left",
                    combo_classes="assistant",
                    color_hex=entity_color,
                )
            else:
                header = role if not ts else f"{role} {ts}"
                self._mount_combo(
                    self.right.history_view,
                    header=header,
                    body=content,
                    render_mode="markdown",
                    align="full",
                    combo_classes="system",
                )

        # Always land at the bottom after a full render
        self.call_after_refresh(self.right.scroll_to_bottom)

    def _get_last_assistant_text(self) -> str:
        if (self.current.assistant_text or "").strip():
            return self.current.assistant_text
        conv = self.conversations.active
        if not conv:
            return ""
        t = self.conversations.get_thread(conv.active_thread_id)
        for m in reversed(t.messages):
            if m.get("role") == "assistant":
                return m.get("content", "") or ""
        return ""



    # ── Phase 8: Emergence, Interruption, Council Nav ────────────────────────

    def _check_emergence(self) -> None:
        """
        Read Reflection log. Check for newly emerged Entities.
        Silent — no system bubble. Called via asyncio.to_thread after distillation.
        """
        newly_emerged = self.emergence_engine.check_emergence(self.council)
        if newly_emerged:
            for entity_id in newly_emerged:
                try:
                    self.council.emerge(entity_id)
                except Exception:
                    pass
            self._refresh_council_nav()
            self.router.router.refresh_reflection_baseline()

    async def _check_interruption(self, message: str, response: str) -> None:
        """
        Post-response interruption check. If an Entity passes all three gates,
        renders an interruption bubble with ↯ in the header.
        Active Entity reverts to Luminarious after. Only one interruption per turn.
        """
        result = self.interruption_engine.check(
            message, response,
            council=self.council,
            emergence_engine=self.emergence_engine,
            dynamics=self.dynamics,
        )
        if not result.should_interrupt:
            return

        entity_id = result.entity_id
        compiled = self.council.get_compiled(entity_id)
        if not compiled:
            try:
                compiled = self.council.summon(entity_id)
            except Exception:
                return

        context = [
            {"role": "system", "content": compiled.instruction_str},
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
            {"role": "user", "content": (
                "You are interrupting this conversation. Speak briefly — one to three "
                "sentences only. Do not summarize what was said. Offer your specific "
                "perspective from your domain. Begin immediately."
            )},
        ]

        try:
            interruption_text = await asyncio.to_thread(
                self._interruption_api_call, context, compiled.sampling_profile
            )
        except Exception as e:
            self._set_status(f"Interruption error ({entity_id}): {e}")
            return

        self._mount_combo(
            self.middle.current_turn,
            header=f"↯ {compiled.display_name}",
            body=interruption_text,
            render_mode="markdown",
            align="left",
            combo_classes="assistant entity-interrupt",
        )
        self.animation_controller.fire_event(
            "entity_interrupt",
            entity_color=compiled.color_hex,
        )
        self.dynamics.record_speaker(entity_id)

        # Entity private memory — write after interruption
        await asyncio.to_thread(
            self.entity_memory.write,
            entity_id,
            compiled.display_name,
            message,
            interruption_text,
        )

        self.council.dismiss()  # revert to Luminarious

    def _interruption_api_call(self, context: list, profile: dict) -> str:
        """Synchronous. Run via asyncio.to_thread."""
        gen, _meta = self.router.stream_response_text(
            self.cfg.models.nano,
            context,
            max_output_tokens=profile.get("max_output_tokens", 300),
        )
        return "".join(gen)

    def _refresh_council_nav(self) -> None:
        """Update left nav COUNCIL section after emergence. Silent."""
        emerged = self.council.get_emerged()
        council_lines: list = []
        for entity_id in sorted(emerged):
            compiled = self.council.get_compiled(entity_id)
            name = compiled.display_name if compiled else entity_id.upper()
            council_lines.append(f"◆ {name}")
        if hasattr(self.left, "set_council"):
            self.left.set_council(council_lines)


    async def _handle_entity_command(self, argv: list) -> None:
        """
        /entity memory <id>   — show entity private memory
        /entity purge <id>    — clear entity private memory
        /entity memory all    — show all entity memory stores
        """
        if not argv:
            self._set_status("Usage: /entity memory <id> | /entity purge <id>")
            return

        sub = argv[0].lower()

        if sub == "memory":
            if len(argv) < 2:
                self._set_status("Usage: /entity memory <entity_id>  OR  /entity memory all")
                return
            target = argv[1].lower()
            if target == "all":
                lines = []
                for eid in ["luminarious"] + self.council.ALL_ENTITY_IDS:
                    entries = self.entity_memory.get_all_entries(eid)
                    if entries:
                        compiled = self.council.get_compiled(eid)
                        name = compiled.display_name if compiled else eid.upper()
                        lines.append(f"{name} ({len(entries)} entries):")
                        for e in entries:
                            lines.append(f"  - {e.content}")
                if not lines:
                    self._set_status("No entity memories recorded yet.")
                else:
                    self._set_status("\n".join(lines))
                return
            entries = self.entity_memory.get_all_entries(target)
            if not entries:
                self._set_status(f"No memory for {target}.")
                return
            compiled = self.council.get_compiled(target)
            name = compiled.display_name if compiled else target.upper()
            lines = [f"{name} — private memory ({len(entries)} entries):"]
            for e in entries:
                lines.append(f"  [{e.created_at[:10]}] {e.content}")
                if e.context:
                    lines.append(f"    context: {e.context[:80]}")
            usage = self.entity_memory.token_usage(target)
            lines.append(f"  tokens: {usage['used_tokens']}/{usage['budget_tokens']} ({usage['pct']}%)")
            self._set_status("\n".join(lines))

        elif sub == "purge":
            if len(argv) < 2:
                self._set_status("Usage: /entity purge <entity_id>")
                return
            target = argv[1].lower()
            self.entity_memory.purge(target)
            self._set_status(f"Memory purged: {target}")

        else:
            self._set_status("Usage: /entity memory <id> | /entity purge <id>")

    async def _handle_model_command(self, argv: list) -> None:
        """
        /model              — list all models
        /model smart|fast   — pin tier
        /model [id]         — pin specific model
        /model auto         — unpin, resume routing
        """
        router = self.router.router
        if not argv:
            models = router.list_models()
            if models is None:
                self._set_status("Model registry not found at entities/models.yaml.")
                return
            lines = [
                f"[{m.get('tier','')}] {m.get('display_name','')} — {m.get('id','')}"
                for m in models
            ]
            self._set_status("Models:\n" + "\n".join(lines))
            return
        sub = argv[0].lower().strip()
        if sub == "auto":
            router.unpin_model()
            self._set_status("◆ Auto-routing restored.")
            return
        if sub == "smart":
            model_id = self.cfg.models.smart
        elif sub == "fast":
            model_id = self.cfg.models.fast
        else:
            model_id = argv[0].strip()
            models = router.list_models() or []
            known_ids = {m.get("id") for m in models}
            if known_ids and model_id not in known_ids:
                self._set_status(f"Unknown model: {model_id!r}. Use /model to list available.")
                return
        router.pin_model(model_id)
        self._set_status(
            f"◆ Model pinned: {model_id}. /model auto to resume routing."
        )

    async def _handle_route_command(self, argv: list) -> None:
        """
        /route              — show last routing decision breakdown
        /route [message]    — score hypothetical without sending
        """
        router = self.router.router
        if argv:
            result = router.route_full(" ".join(argv).strip())
            self._set_status(f"[HYPOTHETICAL]\n{router.format_route_display(result)}")
        else:
            self._set_status(router.format_route_display())

    async def _handle_council_command(self, argv: list) -> None:
        """
        /council            — show emerged entities
        /council signals    — all entity signal strengths
        /council dynamics   — relationship graph
        """
        if not argv:
            emerged = self.council.get_emerged()
            signals = self.emergence_engine.get_signal_strengths()
            if not emerged:
                self._set_status("No Entities have emerged yet. The Council stirs...")
                return
            lines = ["COUNCIL"]
            for eid in sorted(emerged):
                sig = signals.get(eid, 0.0)
                compiled = self.council.get_compiled(eid)
                name = compiled.display_name if compiled else eid.upper()
                lines.append(f"  ◆ {name}  (signal: {sig:.2f})")
            self._set_status("\n".join(lines))
            return
        sub = argv[0].lower()
        if sub == "signals":
            signals = self.emergence_engine.get_signal_strengths()
            lines = ["Signal strengths:"]
            for eid, sig in sorted(signals.items(), key=lambda x: -x[1]):
                mark = "◆" if self.council.has_emerged(eid) else "·"
                lines.append(f"  {mark} {eid:<20} {sig:.3f}")
            self._set_status("\n".join(lines))
            return
        if sub == "dynamics":
            rels = self.dynamics.get_relationships()
            lines = ["Relationship graph:"]
            for r in rels:
                lines.append(f"  [{r.relationship_type}] {r.entity_a} → {r.entity_b}: {r.effect}")
            self._set_status("\n".join(lines))
            return
        self._set_status("Council commands: /council · /council signals · /council dynamics")

    async def _handle_grimoire_command(self, args: list[str]) -> None:
        if not args:
            # push GrimoirePage — placeholder until GrimoirePage is built
            self._set_status("Grimoire page not yet implemented. Use /grimoire list.")
            return

        sub = args[0].lower()

        if sub == "add":
            if len(args) < 2:
                self._set_status("Usage: /grimoire add [category:] content")
                return
            rest = " ".join(args[1:])
            if ":" in args[1]:
                category, content = rest.split(":", 1)
                category = category.strip()
                content = content.strip()
            else:
                category = "general"
                content = rest.strip()
            if not content:
                self._set_status("Grimoire entry content cannot be empty.")
                return
            entry = self.grimoire.add(content, category)
            self._set_status(f"Grimoire entry added: [{entry.category}] {entry.entry_id}")

        elif sub == "list":
            active = self.grimoire.get_active()
            if not active:
                self._set_status("Grimoire is empty.")
                return
            lines = [f"[{e.entry_id}] [{e.category}] {e.content}" for e in active]
            self._set_status("Grimoire:\n" + "\n".join(lines))

        elif sub == "remove":
            if len(args) < 2:
                self._set_status("Usage: /grimoire remove <entry_id>")
                return
            ok = self.grimoire.remove(args[1])
            self._set_status(f"Removed {args[1]}." if ok else f"Entry not found: {args[1]}")

        elif sub == "restore":
            if len(args) < 2:
                self._set_status("Usage: /grimoire restore <entry_id>")
                return
            ok = self.grimoire.restore(args[1])
            self._set_status(f"Restored {args[1]}." if ok else f"Entry not found: {args[1]}")

        elif sub == "edit":
            if len(args) < 3:
                self._set_status("Usage: /grimoire edit <entry_id> <new content>")
                return
            new_content = " ".join(args[2:]).strip()
            ok = self.grimoire.edit(args[1], new_content)
            self._set_status(f"Updated {args[1]}." if ok else f"Entry not found: {args[1]}")

        elif sub == "status":
            usage = self.grimoire.token_usage()
            self._set_status(
                f"Grimoire: {usage['entry_count']} entries · "
                f"{usage['used']}/{usage['budget']} tokens ({usage['pct']}%)"
            )   

        else:
            self._set_status(
                "Grimoire commands: add [cat:] content · list · remove <id> · "
                "restore <id> · edit <id> <content> · status"
            )


    # -------------------------
    # Commands (LF spec + Phase 3 additions + /help <topic>)
    # -------------------------

    async def _handle_tome_command(self, args: list[str]) -> None:
        if not self.tome.is_active:
            self._set_status("No project is active. Open a project to use the Tome.")
            return
        if not args:
            self._set_status("Tome page not yet implemented. Use /tome list.")
            return
        sub = args[0].lower()
        if sub == "add":
            if len(args) < 2:
                self._set_status("Usage: /tome add [category:] content")
                return
            rest = " ".join(args[1:])
            if ":" in args[1]:
                category, content = rest.split(":", 1)
                category = category.strip()
                content = content.strip()
            else:
                category = "general"
                content = rest.strip()
            if not content:
                self._set_status("Tome entry content cannot be empty.")
                return
            entry = self.tome.add(content, category)
            if entry:
                self._set_status(f"Tome entry added: [{entry.category}] {entry.entry_id}")
            else:
                self._set_status("Failed to add Tome entry.")
        elif sub == "list":
            active = self.tome.get_active()
            if not active:
                self._set_status("Tome is empty.")
                return
            lines = [f"[{e.entry_id}] [{e.category}] {e.content}" for e in active]
            self._set_status("Tome:\n" + "\n".join(lines))
        elif sub == "remove":
            if len(args) < 2:
                self._set_status("Usage: /tome remove <entry_id>")
                return
            ok = self.tome.remove(args[1])
            self._set_status(f"Removed {args[1]}." if ok else f"Entry not found: {args[1]}")
        elif sub == "restore":
            if len(args) < 2:
                self._set_status("Usage: /tome restore <entry_id>")
                return
            ok = self.tome.restore(args[1])
            self._set_status(f"Restored {args[1]}." if ok else f"Entry not found: {args[1]}")
        elif sub == "edit":
            if len(args) < 3:
                self._set_status("Usage: /tome edit <entry_id> <new content>")
                return
            new_content = " ".join(args[2:]).strip()
            ok = self.tome.edit(args[1], new_content)
            self._set_status(f"Updated {args[1]}." if ok else f"Entry not found: {args[1]}")
        elif sub == "status":
            usage = self.tome.token_usage()
            self._set_status(
                f"Tome: {usage['entry_count']} entries · "
                f"{usage['used']}/{usage['budget']} tokens ({usage['pct']}%)"
            )
        else:
            self._set_status(
                "Tome commands: add [cat:] content · list · remove <id> · "
                "restore <id> · edit <id> <content> · status"
            )

    async def _handle_summon_command(self, args: list[str]) -> None:
        if not args:
            try:
                import yaml
                with open("entities/canon/entity_canon.yaml") as f:
                    canon = yaml.safe_load(f)
                lines = [
                    f"[{e['entity_id']}] {e['display_name']} #{e['color_hex']}"
                    for e in canon.get("entities", [])
                ]
                self._set_status("Entities:\n" + "\n".join(lines))
            except Exception as e:
                self._set_status(f"Could not load entity canon: {e}")
            return
        entity_id = args[0].lower().strip()
        if entity_id == "luminarious":
            self._set_status("Luminarious is already the anchor. Nothing to summon.")
            return
        if entity_id == "assessor":
            await self._run_assessor()
            return
        try:
            self.council.summon(entity_id)
            entity = self.council.active
            self.status_layer.update_status(
                entity_name=entity.display_name,
                entity_color=entity.color_hex
            )
            self._set_status(f"Summoned: {entity.display_name}")
        except Exception as e:
            self._set_status(f"Summon failed: {e}")

    async def _run_assessor(self) -> None:
        if not self.conversations.active:
            self._set_status("No conversation loaded. Assessor requires an active Thread.")
            return
        try:
            self.council.summon("assessor")
        except Exception as e:
            self._set_status(f"Assessor compilation failed: {e}")
            return
        assessor = self.council.active
        self.status_layer.update_status(
            entity_name=assessor.display_name,
            entity_color=assessor.color_hex
        )
        thread = self.conversations.get_thread(
            self.conversations.active.active_thread_id
        )
        # Assessor instruction string — passed as instructions param, not in messages
        assessor_instructions = assessor.instruction_str

        # Build context as user/assistant messages only
        messages = []

        # Grimoire context as user message
        grimoire_injection = self.grimoire.build_injection_string()
        if grimoire_injection:
            messages.append({"role": "user", "content": "GRIMOIRE (existing long-term memory):\n" + grimoire_injection})
            messages.append({"role": "assistant", "content": "Grimoire context received."})

        # Chronicle fragments as user message
        retrieved = self.chronicle.query(
            "wizard profile patterns preferences communication style",
            top_k=3,
            conversation_ids=[self.conversations.active.id],
            thread_by_conversation={
                self.conversations.active.id: self.conversations.active.active_thread_id
            }
        )
        if retrieved:
            blob = "\n\n".join(f"[score={r['score']:.3f}] {r['text']}" for r in retrieved)
            messages.append({"role": "user", "content": "CHRONICLE FRAGMENTS:\n" + blob})
            messages.append({"role": "assistant", "content": "Chronicle context received."})

        # Thread history
        for m in thread.messages[-10:]:
            role = m.get("role", "")
            content_text = m.get("content", "").strip()
            if role in ("user", "assistant") and content_text:
                messages.append({"role": role, "content": content_text})

        # Task prompt
        messages.append({
            "role": "user",
            "content": (
                "Analyze this Thread. Produce a structured profile observation "
                "of the Wizard using EXACTLY the section headers specified. "
                "Skip observations already present in the Grimoire."
            )
        })
        try:
            profile = assessor.sampling_profile
            response_text = await asyncio.to_thread(
                self._assessor_api_call,
                messages,
                profile,
                assessor_instructions,
            )
        except Exception as e:
            self._set_status(f"Assessor API call failed: {e}")
            self.council.dismiss()
            return
        self._mount_combo(
            self.middle.current_turn,
            header="THE ASSESSOR",
            body=response_text,
            render_mode="markdown",
            align="full",
            combo_classes="system assessor",
        )
        written, skipped = self._assessor_write_grimoire(response_text)
        self.council.dismiss()
        entity = self.council.active
        self.status_layer.update_status(
            entity_name=entity.display_name,
            entity_color=entity.color_hex
        )
        self._set_status(
            f"Assessor complete. {written} observations written · {skipped} skipped. "
            f"Returned to {entity.display_name}."
        )

    def _assessor_api_call(self, messages: list, profile: dict, instructions: str | None = None) -> str:
        gen, _meta = self.router.stream_response_text(
            self.router.decide("assessor profile observation").model,
            messages,
            max_output_tokens=profile.get("max_output_tokens", 1500),
            instructions=instructions,
        )
        return "".join(gen)

    def _assessor_write_grimoire(self, response_text: str) -> tuple[int, int]:
        import re
        sections = {
            "COMMUNICATION_STYLE": "communication_style",
            "WORK_PATTERNS": "work_patterns",
            "FRICTION_POINTS": "friction_points",
            "PREFERENCES": "preferences",
        }
        written = 0
        skipped = 0
        active_entries = [e.content.lower() for e in self.grimoire.get_active()]
        for section_header, category in sections.items():
            pattern = rf"{section_header}:\s*\n((?:\s*-[^\n]+\n?)+)"
            match = re.search(pattern, response_text)
            if not match:
                continue
            block = match.group(1)
            observations = re.findall(r"-\s*(.+?)(?:\s*\[.*?\])?$", block, re.MULTILINE)
            for obs in observations:
                obs = obs.strip()
                if not obs:
                    continue
                obs_lower = obs.lower()
                if any(
                    len(set(obs_lower.split()) & set(e.split())) / max(len(obs_lower.split()), 1) > 0.6
                    for e in active_entries
                ):
                    skipped += 1
                    continue
                self.grimoire.add(obs, category, source="assessor")
                written += 1
        return written, skipped

    async def _handle_menu_command(self, raw: str) -> None:
        parsed = self.input.parse(raw)
        if parsed.kind != "command":
            self._set_status("Menu prompt expects commands. Try /help.")
            return

        cmd = (parsed.command or "").lower().strip()
        argv = self._parse_argv((parsed.args or "").strip())

        if cmd == "/grimoire":
            await self._handle_grimoire_command(argv)
            return

        if cmd == "/tome":
            await self._handle_tome_command(argv)
            return

        if cmd == "/entity":
            await self._handle_entity_command(argv)
            return

        if cmd == "/summon":
            await self._handle_summon_command(argv)
            return

        if cmd == "/dismiss":
            self.council.dismiss()
            entity = self.council.active
            self.status_layer.update_status(
                entity_name=entity.display_name,
                entity_color=entity.color_hex
            )
            self._set_status(f"Returned to: {entity.display_name}")
            return

        if cmd == "/model":
            await self._handle_model_command(argv)
            return

        if cmd == "/route":
            await self._handle_route_command(argv)
            return

        if cmd == "/council":
            await self._handle_council_command(argv)
            return


        # -------------------------
        # Help routing: /help <topic>
        # -------------------------
        if cmd == "/help":
            topic = " ".join(argv).strip().lower()
            if not topic:
                self._go_left_page("help_index")
                return

            if topic in ("home",):
                self._go_left_page("help_home")
                return
            if topic in ("conversations", "conversation"):
                self._go_left_page("help_conversations")
                return
            if topic in ("menu", "system"):
                self._go_left_page("help_menu")
                return
            if topic in ("chat",):
                self._go_left_page("help_chat")
                return
            if topic in ("history",):
                self._go_left_page("help_history")
                return

            self._set_status(f"Unknown help topic: {topic!r} (try: /help)")
            self._go_left_page("help_index")
            return

        # Pages (navigation)
        if cmd in ("/home", "/menu"):
            self._go_left_page("home")
            return
        if cmd == "/conversations":
            self._project_page_id = None
            self._go_left_page("conversations")
            return
        if cmd == "/config":
            self._go_left_page("config")
            return
        if cmd == "/back":
            self._back_left_page()
            return

        # Utilities
        if cmd in ("/exit", "/quit"):
            self.exit()
            return
        if cmd == "/send":
            self._submit_middle_message()
            return
        if cmd == "/copy":
            self.action_copy_last()
            return
        if cmd == "/debug":
            visible = self.left.toggle_debug()
            self._set_status(f"Debug legend {'ON' if visible else 'OFF'}")
            return


        # -------------------------
        # Phase 3: threads / branching
        # -------------------------
        if cmd == "/threads":
            if not self.conversations.active:
                self._set_status("No conversation loaded.")
                return
            conv = self.conversations.active
            lines = []
            for i, t in enumerate(conv.threads, start=1):
                mark = "*" if t.id == conv.active_thread_id else " "
                lines.append(f"{mark} {i}. {t.name} (id={t.id})")
            self._set_status(": " + " | ".join(lines))
            return

        if cmd == "/thread":
            if not self.conversations.active:
                self._set_status("No conversation loaded.")
                return
            if self._streaming:
                self._set_status("Cannot modify/switch threads while streaming.")
                return
            if not argv:
                self._set_status(
                    'Usage: /thread <n|name|id>  OR  /thread rename <n|name|id> "New Name"  OR  /thread delete <n|name|id>'
                )
                return

            conv = self.conversations.active

            def resolve_thread_id(token: str) -> Optional[str]:
                token = (token or "").strip()
                if not token:
                    return None
                if token.isdigit():
                    idx = int(token)
                    if idx < 1 or idx > len(conv.threads):
                        return None
                    return conv.threads[idx - 1].id
                want = token.lower()
                for th in conv.threads:
                    if (th.name or "").strip().lower() == want or th.id == token:
                        return th.id
                return None

            sub = argv[0].lower().strip()

            # /thread rename <target> "New Name"
            if sub == "rename":
                if len(argv) < 3:
                    self._set_status('Usage: /thread rename <n|name|id> "New Name"')
                    return
                tid = resolve_thread_id(argv[1])
                if not tid:
                    self._set_status("Thread not found.")
                    return
                new_name = " ".join(argv[2:]).strip()
                try:
                    self.conversations.rename_thread(tid, new_name)
                except Exception as e:
                    self._set_status(f"Rename failed: {e}")
                    return

                self._refresh_thread_tabs()
                self._render_full_history_from_store(clear_first=True)
                self._render_legend()
                return

            # /thread delete <target>
            if sub == "delete":
                if len(argv) < 2:
                    self._set_status("Usage: /thread delete <n|name|id>")
                    return

                tid = resolve_thread_id(argv[1])
                if not tid:
                    self._set_status("Thread not found.")
                    return

                # capture display name before deletion
                tname = None
                for th in conv.threads:
                    if th.id == tid:
                        tname = th.name
                        break

                # Pending safety: if pending belongs to the deleted thread, drop it (do NOT archive).
                if self._pending and self._pending.conversation_id == conv.id and self._pending.thread_id == tid:
                    self._pending = None

                # If the middle bundle belongs to the deleted thread, clear it (prevents orphan UI).
                if (self.current.thread_id or "") == tid:
                    self.current = CurrentTurn()
                    self.middle.clear_current_turn()

                try:
                    self.conversations.delete_thread(tid)  # store enforces: cannot delete main; always switch to main
                except Exception as e:
                    self._set_status(f"Thread delete failed: {e}")
                    return

                self._set_status(f"Thread deleted: {tname or tid}. Switched to main.")
                self._refresh_thread_tabs()
                self._render_full_history_from_store(clear_first=True)
                self._render_legend()
                return

            # /thread <target>  (switch thread)
            token = " ".join(argv).strip()
            tid2: Optional[str] = resolve_thread_id(token)
            if not tid2:
                self._set_status("Thread not found.")
                return

            try:
                self.conversations.set_active_thread(tid2)
            except Exception as e:
                self._set_status(f"Thread switch failed: {e}")
                return

            self._refresh_thread_tabs()
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()
            return

        if cmd == "/branch":
            if not self.conversations.active:
                self._set_status("No conversation loaded.")
                return
            if self._streaming:
                self._set_status("Cannot /branch while streaming.")
                return
            if not argv:
                self._set_status("Usage: /branch <n|last>")
                return

            token = argv[0].strip().lower()
            try:
                if token == "last":
                    t = self.conversations.branch_from_assistant_turn(last=True)
                elif token.isdigit():
                    t = self.conversations.branch_from_assistant_turn(int(token), last=False)
                else:
                    self._set_status("Usage: /branch <n|last>")
                    return
            except Exception as e:
                self._set_status(f"Branch failed: {e}")
                return

            # Switching thread shouldn't force-archive pending (LF invariant)
            self._set_status(f"Branched to: {t.name}")
            self._refresh_thread_tabs()
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()
            return

        # -------------------------
        # Existing commands preserved (new/load/rename/delete/move/project)
        # -------------------------

        # /new ["Title"] (contextual: project page => creates inside project)
        if cmd == "/new":
            if self._streaming:
                self._set_status("Cannot /new while streaming.")
                return

            title = " ".join(argv).strip() if argv else ""
            if title and self._title_exists(title):
                self._set_status(f"Title already exists: {title!r}")
                return

            conv = self.conversations.new()
            if title:
                self.conversations.active.title = title
                self.conversations.save()

            if self._left_page == "project" and self._project_page_id:
                self.projects.assign_conversation(conv.id, self._project_page_id)

            self._pending = None
            self.middle.clear_current_turn()
            self.current = CurrentTurn()
            self._seed_new_conversation()
            self._refresh_thread_tabs()
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()
            self._refresh_lists_if_visible()
            return

        # /rename "New Title"   OR   /rename <title> "New Title"
        if cmd == "/rename":
            if not argv:
                self._set_status('Usage: /rename "New Title"  OR  /rename <title> "New Title"')
                return

            if len(argv) == 1:
                if not self.conversations.active:
                    self._set_status("No conversation loaded.")
                    return
                new_title = argv[0].strip()
                if self._title_exists(new_title, exclude_id=self.conversations.active.id):
                    self._set_status(f"Title already exists: {new_title!r}")
                    return
                self.conversations.active.title = new_title
                self.conversations.save()
                self._render_legend()
                self._refresh_lists_if_visible()
                return

            old_title = argv[0].strip()
            new_title = " ".join(argv[1:]).strip()

            if self._title_exists(new_title):
                self._set_status(f"Title already exists: {new_title!r}")
                return

            target_id = self._find_conversation_id_by_title(old_title)
            if not target_id:
                self._set_status(f"No conversation found with title: {old_title!r}")
                return

            prev_id = self.conversations.active.id if self.conversations.active else None
            try:
                self.conversations.load(target_id)
                self.conversations.active.title = new_title
                self.conversations.save()
            finally:
                if prev_id and prev_id != target_id:
                    self.conversations.load(prev_id)
                elif prev_id is None:
                    self.conversations.clear_active()

            self._render_legend()
            self._refresh_lists_if_visible()
            return

        # /load <n>  OR  /load name "Title"
        if cmd == "/load":
            if not argv:
                self._set_status('Usage: /load <n>  OR  /load name "Title"')
                return
            if self._streaming:
                self._set_status("Cannot /load while streaming.")
                return

            token = argv[0].strip()
            conv_id: Optional[str] = None

            if token.lower() == "name":
                title = " ".join(argv[1:]).strip()
                conv_id = self._find_conversation_id_by_title(title)
                if not conv_id:
                    self._set_status(f"No conversation found with title: {title!r}")
                    return
            elif token.isdigit():
                conv_id = self._resolve_conversation_id_by_index(int(token))
                if not conv_id:
                    self._set_status("Index out of range.")
                    return
            else:
                conv_id = token  # id still works (not advertised)

            try:
                conv = self.conversations.load(conv_id)
            except Exception as e:
                self._set_status(f"Load failed: {e}")
                return

            # If loaded convo is inside a project, go to that project page automatically
            pid = self.projects.project_for_conversation(conv.id)
            if pid:
                self._project_page_id = pid
                self._left_page = "project"
            else:
                self._project_page_id = None

            self._pending = None
            self.middle.clear_current_turn()
            self.current = CurrentTurn()
            self._refresh_thread_tabs()
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()
            self._refresh_lists_if_visible()
            return

        # /delete <n> OR /delete name "Title" OR /delete project ...
        if cmd == "/delete":
            if len(argv) >= 1 and argv[0].lower() == "project":
                # /delete project "Project"  OR  /delete project <n>
                if len(argv) < 2:
                    self._set_status('Usage: /delete project "Project"  OR  /delete project <n>')
                    return

                target = " ".join(argv[1:]).strip()
                proj_id: Optional[str] = None

                if target.isdigit():
                    proj_id = self._resolve_project_id_by_index(int(target))
                else:
                    proj_id = self._resolve_project_id_by_name(target)

                if not proj_id:
                    self._set_status("Project not found.")
                    return

                proj = self.projects.get_by_id(proj_id)
                conv_ids = list(proj.conversation_ids) if proj else []

                # If we're viewing it, go back to hub
                if self._project_page_id == proj_id:
                    self._project_page_id = None
                    self._left_page = "conversations"

                # Delete conversations in the project (LF decision)
                active_deleted = False
                for cid in conv_ids:
                    if self.conversations.active and self.conversations.active.id == cid:
                        active_deleted = True
                    self.conversations.delete(cid)
                    self.projects.drop_conversation_everywhere(cid)

                # Delete the project record
                if not self.projects.delete_by_id(proj_id):
                    self._set_status("Delete project failed.")
                    return

                # If active convo was deleted, Option A: auto-load most recent remaining, else none loaded
                if active_deleted:
                    remaining = self.conversations.list()
                    if remaining:
                        try:
                            self.conversations.load(remaining[0]["id"])
                        except Exception:
                            self.conversations.clear_active()
                    else:
                        self.conversations.clear_active()

                    self._pending = None
                    self.middle.clear_current_turn()
                    self.current = CurrentTurn()
                    self._refresh_thread_tabs()
                    self._render_full_history_from_store(clear_first=True)

                self._render_legend()
                self._refresh_lists_if_visible()
                return

            # /delete <n>  OR  /delete name "Title"
            if not argv:
                self._set_status('Usage: /delete <n>  OR  /delete name "Title"')
                return
            if self._streaming:
                self._set_status("Cannot /delete while streaming.")
                return

            token = argv[0].strip()
            conv_id: Optional[str] = None

            if token.lower() == "name":
                title = " ".join(argv[1:]).strip()
                conv_id = self._find_conversation_id_by_title(title)
                if not conv_id:
                    self._set_status(f"No conversation found with title: {title!r}")
                    return
            elif token.isdigit():
                conv_id = self._resolve_conversation_id_by_index(int(token))
                if not conv_id:
                    self._set_status("Index out of range.")
                    return
            else:
                conv_id = token

            was_active = bool(self.conversations.active and self.conversations.active.id == conv_id)

            if not self.conversations.delete(conv_id):
                self._set_status("Delete failed: conversation not found.")
                return

            self.projects.drop_conversation_everywhere(conv_id)

            if was_active:
                remaining = self.conversations.list()
                if remaining:
                    try:
                        self.conversations.load(remaining[0]["id"])
                    except Exception:
                        self.conversations.clear_active()
                else:
                    self.conversations.clear_active()

                self._pending = None
                self.middle.clear_current_turn()
                self.current = CurrentTurn()
                self._refresh_thread_tabs()
                self._render_full_history_from_store(clear_first=True)

            self._render_legend()
            self._refresh_lists_if_visible()
            return

        # /move "Title" "Project"   OR   /move <n> "Project"
        if cmd == "/move":
            if len(argv) < 2:
                self._set_status('Usage: /move "Title" "Project"  OR  /move <n> "Project"')
                return

            src = argv[0].strip()
            project_name = " ".join(argv[1:]).strip()
            proj_id = self._resolve_project_id_by_name(project_name)
            if not proj_id:
                self._set_status(f"Project not found: {project_name!r}")
                return

            if src.isdigit():
                conv_id = self._resolve_conversation_id_by_index(int(src))
            else:
                conv_id = self._find_conversation_id_by_title(src)

            if not conv_id:
                self._set_status("Conversation not found.")
                return

            self.projects.assign_conversation(conv_id, proj_id)
            self._render_legend()
            self._refresh_lists_if_visible()
            return

        # /project new "Title"  OR  /project <n>  OR  /project "Title"
        if cmd == "/project":
            if not argv:
                self._set_status('Usage: /project new "Title"  OR  /project <n>  OR  /project "Title"')
                return

            first = argv[0].strip()

            if first.lower() == "new":
                name = " ".join(argv[1:]).strip()
                if not name:
                    self._set_status('Usage: /project new "Title"')
                    return
                try:
                    self.projects.create(name)
                except Exception as e:
                    self._set_status(f"Project create failed: {e}")
                    return
                self._refresh_lists_if_visible()
                return

            if first.isdigit():
                proj_id = self._resolve_project_id_by_index(int(first))
                if not proj_id:
                    self._set_status("Project index out of range.")
                    return
                self._project_page_id = proj_id
                self._go_left_page("project")
                return

            name = " ".join(argv).strip()
            proj_id = self._resolve_project_id_by_name(name)
            if not proj_id:
                self._set_status(f"Project not found: {name!r}")
                return
            self._project_page_id = proj_id
            self._go_left_page("project")
            return

        self._set_status(f"Unknown command: {cmd} (try /help)")
