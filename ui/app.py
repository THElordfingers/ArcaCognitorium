#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/app.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations
from dataclasses import dataclass
from ui.panes.status_layer import StatusLayer


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
from textual.widgets import Static, Input, Button

from client.config import AppConfig
from client.router import ModelRouter
from client.input_processor import InputProcessor
from client.clipboard import copy_to_clipboard
from client.reflection import Reflection

from memory.chronicle import Chronicle
from memory.distillation import Distillation
from memory.conversation_store import ConversationStore
from memory.project_store import ProjectStore

from ui.panes.left_menu import LeftMenuPane
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
    """Two attached bubbles: header + body (Textual 2.1.2-safe)."""

    def __init__(self, header: str, body: str = "", *, classes: str = "", render_mode: RenderMode = "plain") -> None:
        super().__init__(classes=classes)
        self._header_text = header or ""
        self._body_text = body or ""
        self._render_mode: RenderMode = render_mode
        self.header_widget: Optional[Static] = None
        self.body_widget: Optional[Static] = None
        

    def _renderable(self, text: str):
        text = text or ""
        return RichMarkdown(text) if self._render_mode == "markdown" else text

    def compose(self) -> ComposeResult:
        self.header_widget = Static(self._renderable(self._header_text.rstrip()), classes="bubble_head", markup=False)
        self.body_widget = Static(self._renderable(self._body_text.rstrip()), classes="bubble_tail", markup=False)
        yield self.header_widget
        yield self.body_widget

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
    Screen { layout: horizontal; }

    #left, #middle, #right { height: 100%; }
    #left   { width: 32%; border: round yellow; }
    #middle { width: 38%; border: round magenta; }
    #right  { width: 30%; border: round green; }

    #legend    { height: auto; padding: 1 1; border: round yellow; }
    #menu_page { height: 1fr;  border: round yellow; }
    #menu_cmd  { height: 3; }

    #current_turn { height: 1fr; padding: 1 1; border: round magenta; }
    #chat_input   { height: 9;  border: round cyan; }

    #history_tabs  { height: auto; padding: 0 1; }
    #history_view  { height: 1fr; padding: 1 1; border: round green; }
    #history_input { height: 3; }

    .spacer { width: 1fr; }
    .bubble_row { height: auto; width: 1fr; }

    .bubble_combo {
        width: 88%;
        height: auto;
        margin: 0 0 1 0;
    }
    .bubble_combo.system { width: 1fr; }

    .bubble_head {
        padding: 0 1;
        text-style: bold;
        background: rgb(40,40,40);
        height: auto;
        width: 1fr;
        border: round white;
        border-bottom: none;
    }

    .bubble_tail {
        padding: 0 1 1 1;
        height: auto;
        width: 1fr;
        border: round white;
        border-top: none;

    .boot_sigil { opacity: 8%; color: #C9A84C; height: auto; }
    .boot_banner { color: #C9A84C; height: auto; }
    .boot_line { color: #5A6070; height: auto; }
    }

    .user .bubble_head { border: round cyan; border-bottom: none; }
    .user .bubble_tail { border: round cyan; border-top: none; }

    .assistant .bubble_head { border: round magenta; border-bottom: none; }
    .assistant .bubble_tail { border: round magenta; border-top: none; }

    .system .bubble_head { border: round yellow; border-bottom: none; }
    .system .bubble_tail { border: round yellow; border-top: none; }

    #status_layer { height: 3; border: round white; }

    #conjure-title { color: #C9A84C; text-style: bold; padding: 1 2; }
    .conjure-section { height: auto; margin: 1 0; }
    .conjure-section-header { color: #B87333; text-style: bold; padding: 0 1; }
    .conjure-row { height: auto; padding: 0 1; }
    .conjure-key { color: #D4C8A8; width: 30; }
    .conjure-empty { color: #5A6070; padding: 0 2; }

    #convpage-title { color: #C9A84C; text-style: bold; padding: 1 2; }
    .convpage-empty { color: #5A6070; padding: 1 2; }



    /* app.css additions for Phase 2 */
    
    /* Outer frame — double border on the app itself */
    ArcaCognitorium {
        border: double #C9A84C;
        background: #0D0B0E;
    }
    
    /* Title banner strip */
    #title-banner {
        height: 3;
        background: #0D0B0E;
        border-bottom: solid #2A2535;
        content-align: left middle;
        padding: 0 1;
        color: #B8860B;
    }
    
    /* Center pane */
    #chat-pane {
        background: #0D0B0E;
        border-right: solid #2A2535;
        border-left: solid #2A2535;
    }
    
    /* Invocation Field */
    #invocation-field {
        height: auto;
        max-height: 10;
        background: #161218;
        border: solid #2A2535;
        padding: 0 1;
        color: #D4C8A8;
    }
    #invocation-field:focus {
        border: solid #C68B2A;
    }
    
    /* Entity interrupt pulse — added/removed by AnimationController */
    .entity-pulse {
        border: solid #C9A84C;  /* Overridden per entity color in Python */
    }
    
    /* Distillation ripple on history pane */
    .distillation-ripple {
        border: solid #C68B2A;
        transition: border 1200ms;
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

        self.oa_client = self.router.client
        self.vectors = Chronicle(cfg, client=self.oa_client)
        self.distillation = Distillation(cfg, client=self.oa_client)
        self.conversations = ConversationStore(cfg, summarizer=self.distillation)
        self.reflection = Reflection(cfg, client=self.oa_client, vectors=self.vectors)

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
            max_injection_tokens=self.cfg.raw.get("memory", {}).get("grimoire_max_tokens", 800)
        )
        

    def _on_conversation_selected(self, cid: str | None) -> None:
        if cid:
            self.conversations.load(cid)
            self._render_full_history_from_store(clear_first=True)
            self._render_legend()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                self.left = LeftMenuPane(id="left")
                self.middle = ActiveChatPane(id="middle")
                self.right = HistoryPane(id="right")
                yield self.left
                yield self.middle
                yield self.right
            self.status_layer = StatusLayer(id="status_layer")
            yield self.status_layer

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
        streaming = "yes" if self._streaming else "no"
        conv = self.conversations.active

        if conv is None:
            conv_line = "Conversation: (none loaded)"
            scope_line = "Scope: (none)"
            thread_line = "Thread: (none)"
        else:
            # LF: show id for bugfixing for now
            conv_line = f"Conversation: {conv.title or '(untitled)'}  (id={conv.id})"
            pid = self.projects.project_for_conversation(conv.id)
            if pid:
                p = self.projects.get_by_id(pid)
                scope_line = f"Scope: Project — {p.name if p else '(project)'}"
            else:
                scope_line = "Scope: Main"
            t = self.conversations.get_thread(conv.active_thread_id)
            thread_line = f"Thread: {t.name} (id={t.id})"

        if not self.current.user_text and not self.current.assistant_text:
            turn_state = "empty"
        else:
            turn_state = "complete" if self.current.assistant_complete else "in-progress"

        model_info = ""
        if self.cfg.ui.show_model_badge and self.current.model:
            model_info = f"\nModel: {self.current.model} ({self.current.routing_reason})"

        hist = f"\nHistory filter: {self._history_query}" if self._history_query else ""
        status = f"\nStatus: {self._status}" if self._status else ""

        self.left.set_legend(
            f"{self.cfg.app.name} v{self.cfg.app.version}\n"
            f"{conv_line}\n"
            f"{scope_line}\n"
            f"{thread_line}\n"
            f"Left page: {self._left_page}\n"
            f"Streaming: {streaming}\n"
            f"Current turn: {turn_state}{model_info}{hist}{status}"
        )

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
            self.left.set_page(self._home_page_text())

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
    ) -> BubbleCombo:
        combo = BubbleCombo(header, body, classes=f"bubble_combo {combo_classes}", render_mode=render_mode)
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

            head = ["**Assistant**"]
            if self.cfg.ui.show_model_badge and self.current.model:
                head.append(f"`{self.current.model}` ({self.current.routing_reason})")
            ts2 = _ts_now(self.cfg)
            if ts2:
                head.append(ts2)

            self._mount_combo(
                self.right.history_view,
                header=" • ".join(head),
                body=self._pending.assistant_text,
                render_mode="markdown",
                align="left",
                combo_classes="assistant",
            )

        self._pending = None

    async def _assistant_task(self, *, user_text: str, thread_id: str) -> None:
        if not self.conversations.active:
            return

        self._streaming = True
        try:
            await asyncio.to_thread(self.conversations.append, "user", user_text, thread_id=thread_id)
            context = await asyncio.to_thread(self._build_context, user_text, thread_id)
            decision = self.router.decide(user_text)

            self.current.model = decision.model
            self.current.routing_reason = decision.reason
            self._render_legend()

            parts = ["**Assistant**"]
            if self.cfg.ui.show_model_badge:
                parts.append(f"`{decision.model}` ({decision.reason})")
            ts = _ts_now(self.cfg)
            if ts:
                parts.append(ts)
            header = " • ".join(parts)

            self._assistant_combo = self._mount_combo(
                self.middle.current_turn,
                header=header,
                body="",
                render_mode="markdown",
                align="left",
                combo_classes="assistant",
            )
            await asyncio.to_thread(self._stream_in_thread, decision.model, context)

            self.current.assistant_complete = True
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
                self.vectors.add,
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

        except Exception as e:
            self._set_status(f"Assistant error: {e}")
        finally:
            self._streaming = False
            self._render_legend()

    def _stream_in_thread(self, model: str, context: List[Dict]) -> None:
        gen, _meta = self.router.stream_response_text(
            model,
            context,
            temperature=self.cfg.raw.get("temperature", None),
            max_output_tokens=self.cfg.raw.get("max_output_tokens", None),
        )
        delay = float(self.cfg.ui.typing_delay_seconds)
        for delta in gen:
            if delay > 0:
                time.sleep(delay)
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

        retrieved = self.vectors.query(
            user_text,
            top_k=int(mem_cfg.retrieve_top_k),
            conversation_ids=allowed_ids,
            thread_by_conversation=thread_by_conv,
        )
        if retrieved:
            blob = "\n\n".join(f"[score={r['score']:.3f}] {r['text']}" for r in retrieved)
            messages.append({"role": "system", "content": "Relevant long-term memory:\n" + blob})

        short_max = int(mem_cfg.short_term_max_messages)
        for m in thread.messages[-short_max:]:
            messages.append({"role": m.get("role", ""), "content": m.get("content", "")})

        if not messages or messages[-1]["role"] != "user" or messages[-1]["content"] != user_text:
            messages.append({"role": "user", "content": user_text})
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
                model = m.get("model", None)
                rr = m.get("routing_reason", None)

                head_parts = ["**Assistant**"]
                if self.cfg.ui.show_model_badge and model:
                    head_parts.append(f"`{model}` ({rr})" if rr else f"`{model}`")
                if ts:
                    head_parts.append(ts)

                self._mount_combo(
                    self.right.history_view,
                    header=" • ".join(head_parts),
                    body=content,
                    render_mode="markdown",
                    align="left",
                    combo_classes="assistant",
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
            self._set_status("Threads: " + " | ".join(lines))
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


#        self.push_screen(ConversationsPage(self.conversations), self._on_conversation_selected)
#        
#        def _on_conversation_selected(self, cid: str | None) -> None:
#            if cid:
#                self.conversations.load(cid)
#                self._render_full_history_from_store(clear_first=True)
#                self._render_legend()
