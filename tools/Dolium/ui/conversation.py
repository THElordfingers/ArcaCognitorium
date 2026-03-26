#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / ui/conversation.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import asyncio
import threading

# token_logger — cross-app usage ledger
import sys as _sys
_sys.path.insert(0, str(__import__('pathlib').Path.home() / '.arca'))
try:
    from token_logger import log_usage as _log_usage
except ImportError:
    def _log_usage(*a, **kw): pass
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Static

from models import Idea, chamber_name
from prompts import prompt_for, build_user_message


# ── Messages ──────────────────────────────────────────────────────────────────

class ConversationUpdated(Message):
    """Fired after assistant responds — signals the store to persist conversation."""
    def __init__(self, idea_id: str, conversation: list[dict]) -> None:
        super().__init__()
        self.idea_id      = idea_id
        self.conversation = conversation


# ── Bubble widgets ────────────────────────────────────────────────────────────

class UserBubble(Vertical):
    def __init__(self, text: str) -> None:
        super().__init__(classes="conv-bubble-user")
        self._text = text

    def compose(self) -> ComposeResult:
        yield Static("Wizard", classes="conv-label-user")
        yield Static(self._text, classes="conv-bubble-body")


class AssistantBubble(Vertical):
    def __init__(self, text: str, chamber: int) -> None:
        super().__init__(classes="conv-bubble-assistant")
        self._text    = text
        self._chamber = chamber

    def compose(self) -> ComposeResult:
        yield Static(chamber_name(self._chamber), classes="conv-label-assistant")
        yield Static(self._text, classes="conv-bubble-body")


class ThinkingBubble(Static):
    def __init__(self) -> None:
        super().__init__("…", classes="conv-bubble-assistant", id="thinking-bubble")


# ── ChainConversation ─────────────────────────────────────────────────────────

class ChainConversation(Vertical):
    """
    Right pane. Conversation history + input field.

    ClaudeBox session management:
      - One session per idea, keyed by idea.id
      - Sessions are created on first message and reused across loads
      - System prompt is set per-session, updated when chamber changes
      - idea.conversation is display-only — ClaudeBox owns the API history
    """

    def __init__(self) -> None:
        self._idea:       Optional[Idea] = None
        self._box:        object         = None
        self._thinking:   bool           = False
        self._attached:   list[dict]     = []
        self._repo_path:  Optional[str]  = None
        self._sessions:   dict[str, str] = {}  # idea_id -> session_id
        super().__init__(id="conversation")

    def compose(self) -> ComposeResult:
        yield Static("◆  The Dolium", id="conv-header", classes="conv-header")
        yield ScrollableContainer(
            Static("No idea selected.", classes="conv-empty"),
            id="conv-history",
        )
        with Vertical(id="conv-input-row"):
            yield Input(
                placeholder="Speak to the chamber… (or /help for commands)",
                id="conv-input",
            )
            yield Button("Send", id="conv-send")
        with Horizontal(id="conv-cmd-bar"):
            yield Button("/attach",   id="cmd-attach",   classes="cmd-btn")
            yield Button("/attached", id="cmd-attached", classes="cmd-btn")
            yield Button("/clear",    id="cmd-clear",    classes="cmd-btn")
            yield Button("/man",      id="cmd-man",      classes="cmd-btn")
            yield Button("/save",     id="cmd-save",     classes="cmd-btn")
            yield Button("/files",    id="cmd-files",    classes="cmd-btn")
            yield Button("/help",     id="cmd-help",     classes="cmd-btn")

    # ── Public ────────────────────────────────────────────────────────────────

    def set_box(self, box: object) -> None:
        self._box = box

    def set_repo_path(self, path: Optional[str]) -> None:
        self._repo_path = path

    def load(self, idea: Idea) -> None:
        self._idea = idea
        self._update_header()
        self._render_history()
        # Update system prompt if session already exists for this idea
        if self._box and idea.id in self._sessions:
            try:
                self._box.set_session_system_prompt(
                    self._sessions[idea.id],
                    prompt_for(idea.chamber),
                )
            except Exception:
                pass

    def clear(self) -> None:
        self._idea = None
        self._update_header()
        history = self.query_one("#conv-history", ScrollableContainer)
        history.remove_children()
        history.mount(Static("No idea selected.", classes="conv-empty"))

    def append_turn(self, role: str, text: str) -> None:
        history = self.query_one("#conv-history", ScrollableContainer)
        if role == "user":
            history.mount(UserBubble(text))
        else:
            chamber = self._idea.chamber if self._idea else 1
            history.mount(AssistantBubble(text, chamber))
        history.scroll_end(animate=True)

    # ── Events ────────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "conv-send":
            self._submit()
            return
        cmd_map = {
            "cmd-attach":   "/attach ",
            "cmd-attached": "/attached",
            "cmd-clear":    "/clear",
            "cmd-man":      "/man",
            "cmd-save":     "/save ",
            "cmd-files":    "/files",
            "cmd-help":     "/help",
        }
        if event.button.id in cmd_map:
            cmd = cmd_map[event.button.id]
            inp = self.query_one("#conv-input", Input)
            if cmd.endswith(" "):
                inp.value = cmd
                inp.focus()
            else:
                inp.value = ""
                self._handle_slash(cmd)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "conv-input":
            self._submit()

    # ── Private — submission ──────────────────────────────────────────────────

    def _submit(self) -> None:
        if self._idea is None:
            self.app.notify("Select an idea first.", severity="warning")
            return
        if self._thinking:
            return
        inp  = self.query_one("#conv-input", Input)
        text = inp.value.strip()
        if not text:
            return
        if text.startswith("/"):
            inp.value = ""
            self._handle_slash(text)
            return
        if self._box is None:
            self.app.notify("ClaudeBox not initialised.", severity="error")
            return
        inp.value = ""
        self._idea.conversation.append({"role": "user", "content": text})
        self.append_turn("user", text)
        self._start_thinking()
        asyncio.create_task(self._call_api(text))

    async def _call_api(self, user_text: str) -> None:
        if self._idea is None or self._box is None:
            self._stop_thinking()
            return

        # Build context-enriched message — passes full idea so entity
        # sees all populated fields, not just title and body preview
        full_message = build_user_message(self._idea, user_text)

        # Prepend any attached files
        if self._attached:
            blocks = [f"[ATTACHED FILE: {f['filename']}]\n```\n{f['content']}\n```"
                      for f in self._attached]
            full_message = "\n\n".join(blocks) + "\n\n" + full_message
            self._attached.clear()

        # Get or create session for this idea
        session_id = self._get_or_create_session(self._idea)

        try:
            response = await asyncio.to_thread(
                self._threaded_send,
                full_message,
                session_id,
            )
        except Exception as e:
            self._stop_thinking()
            self.app.notify(f"API error: {e}", severity="error")
            return

        self._stop_thinking()
        self._idea.conversation.append({"role": "assistant", "content": response})
        self.append_turn("assistant", response)
        self.post_message(ConversationUpdated(self._idea.id, self._idea.conversation))

    def _threaded_send(self, content: str, session_id: str) -> str:
        """
        Synchronous. Runs via asyncio.to_thread.
        Uses send_threaded with on_complete to get the full response.
        on_token only delivers one token in this version of ClaudeBox,
        so we ignore it and rely entirely on response.text from on_complete.
        """
        done   = threading.Event()
        result = []
        errors = []

        def on_complete(response) -> None:
            text = response.text if hasattr(response, 'text') else str(response)
            result.append(text or "")
            try:
                u = response.usage
                _log_usage(
                    app="dolium",
                    model=getattr(response, "model", "unknown"),
                    input_tokens=getattr(u, "input_tokens", 0),
                    output_tokens=getattr(u, "output_tokens", 0),
                    session_id=session_id,
                )
            except Exception:
                pass
            done.set()

        def on_error(e: Exception) -> None:
            errors.append(e)
            done.set()

        self._box.send_threaded(
            content     = content,
            session_id  = session_id,
            on_complete = on_complete,
            on_error    = on_error,
        )

        done.wait(timeout=120)

        if errors:
            raise errors[0]

        return result[0] if result else ""

    def _get_or_create_session(self, idea: Idea) -> str:
        """
        Return the existing session ID for this idea, or create a new one.
        System prompt is set to the chamber's prompt on creation.
        """
        if idea.id in self._sessions:
            return self._sessions[idea.id]

        system = prompt_for(idea.chamber)
        try:
            session = self._box.create_session(
                session_id=idea.id,
                system_prompt=system,
            )
            sid = session.id if hasattr(session, 'id') else idea.id
        except Exception as e:
            import sys
            print(f"[dolium] create_session failed: {type(e).__name__}: {e}", file=sys.stderr)
            sid = idea.id

        self._sessions[idea.id] = sid
        return sid

    # ── Private — slash commands ──────────────────────────────────────────────

    def _handle_slash(self, text: str) -> None:
        parts   = text.split(None, 1)
        command = parts[0].lower()
        arg     = parts[1].strip() if len(parts) > 1 else ""

        if command == "/attach":
            if not arg:
                self._system_bubble("Usage: /attach <filename>  e.g. /attach router.py")
                return
            self._cmd_attach(arg)
        elif command == "/attached":
            if not self._attached:
                self._system_bubble("No files attached.")
            else:
                names = ", ".join(f["filename"] for f in self._attached)
                self._system_bubble(f"Attached: {names}")
        elif command == "/clear":
            self._attached.clear()
            self._system_bubble("Attachments cleared.")
        elif command == "/files":
            self._cmd_list_files()
        elif command == "/man":
            self._cmd_man(arg)
        elif command == "/save":
            self._cmd_save(arg)
        elif command == "/help":
            self._system_bubble(
                "/attach <filename>  — attach a file from the AC repo\n"
                "/attached           — list attached files\n"
                "/clear              — clear attachments\n"
                "/files              — list available files in AC repo\n"
                "/save <field>       — append last response to a field\n"
                "/man [chamber]      — open the manual  (e.g. /man 1)\n"
                "/help               — this message"
            )
        else:
            self._system_bubble(f"Unknown command: {command}  —  type /help")

    def _cmd_man(self, arg: str) -> None:
        """Open the manpage overlay."""
        page_map = {
            "":  "overview", "0": "overview",
            "1": "chamber_1", "2": "chamber_2",
            "3": "chamber_3", "4": "chamber_4",
            "fomentary": "chamber_1", "cultivation": "chamber_2",
            "vestibule": "chamber_3", "codex": "chamber_4",
        }
        key = page_map.get(arg.strip().lower(), "overview")
        from ui.modals import ManpageModal
        self.app.push_screen(ManpageModal(page=key))

    def _cmd_save(self, field: str) -> None:
        """Append the last assistant response to a workspace field."""
        if self._idea is None:
            self._system_bubble("No idea selected.")
            return
        valid = {
            "body", "motivation", "scope_in", "scope_out", "system_map",
            "dependencies", "build_sequence", "open_questions", "aesthetic_notes",
        }
        field = field.strip().lower()
        if not field:
            self._system_bubble("Usage: /save <field>  e.g. /save body")
            return
        if field not in valid:
            self._system_bubble(f"Unknown field: {field}\nValid: {', '.join(sorted(valid))}")
            return
        last_response = None
        for turn in reversed(self._idea.conversation):
            if turn.get("role") == "assistant":
                last_response = turn.get("content", "").strip()
                break
        if not last_response:
            self._system_bubble("No assistant response found to save.")
            return
        existing = getattr(self._idea, field, "").strip()
        separator = "\n\n" if existing else ""
        setattr(self._idea, field, existing + separator + last_response)
        from ui.workspace import IdeaSaved, IdeaWorkspace
        self.post_message(IdeaSaved(self._idea))
        try:
            self.app.screen.query_one(IdeaWorkspace).load(self._idea)
        except Exception:
            pass
        self._system_bubble(f"Saved to {field}.")

    def _cmd_attach(self, filename: str) -> None:
        if not self._repo_path:
            self._system_bubble(
                "DOLIUM_REPO_PATH is not set.\n"
                "Add to your shell config:\n"
                "  export DOLIUM_REPO_PATH=/home/lordfingers/ArcaCognitorium"
            )
            return
        from pathlib import Path as _Path
        repo = _Path(self._repo_path).expanduser().resolve()
        if not repo.exists():
            self._system_bubble(f"Repo path not found: {repo}")
            return
        candidates = [
            c for c in repo.glob(f"**/{filename}")
            if "__pycache__" not in str(c) and ".git" not in str(c)
        ]
        if not candidates:
            self._system_bubble(f"File not found in repo: {filename}")
            return
        candidates.sort(key=lambda p: len(p.parts))
        path = candidates[0]
        try:
            source = path.read_text(encoding="utf-8")
        except Exception as e:
            self._system_bubble(f"Could not read {path.name}: {e}")
            return
        self._attached = [a for a in self._attached if a["filename"] != path.name]
        self._attached.append({"filename": path.name, "content": source, "path": str(path)})
        lines = source.count("\n") + 1
        self._system_bubble(f"Attached: {path.relative_to(repo)}  ({lines} lines)")

    def _cmd_list_files(self) -> None:
        if not self._repo_path:
            self._system_bubble("DOLIUM_REPO_PATH is not set.")
            return
        from pathlib import Path as _Path
        repo = _Path(self._repo_path).expanduser().resolve()
        if not repo.exists():
            self._system_bubble(f"Repo path not found: {repo}")
            return
        all_files = sorted([
            str(p.relative_to(repo))
            for p in list(repo.glob("**/*.py")) + list(repo.glob("**/*.yaml"))
            if "__pycache__" not in str(p) and ".git" not in str(p)
        ])
        if not all_files:
            self._system_bubble("No files found.")
            return
        self._system_bubble("Available files:\n" + "\n".join(f"  {f}" for f in all_files[:40]))

    def _system_bubble(self, text: str) -> None:
        history = self.query_one("#conv-history", ScrollableContainer)
        history.mount(Static(text, classes="conv-bubble-system"))
        history.scroll_end(animate=True)

    def _start_thinking(self) -> None:
        self._thinking = True
        history = self.query_one("#conv-history", ScrollableContainer)
        history.mount(ThinkingBubble())
        history.scroll_end(animate=True)
        self.query_one("#conv-send", Button).disabled = True

    def _stop_thinking(self) -> None:
        self._thinking = False
        try:
            self.query_one("#thinking-bubble").remove()
        except Exception:
            pass
        self.query_one("#conv-send", Button).disabled = False

    def _update_header(self) -> None:
        header = self.query_one("#conv-header", Static)
        if self._idea is None:
            header.update("◆  The Dolium")
            return
        numeral = ["I", "II", "III", "IV"][self._idea.chamber - 1]
        header.update(f"◆  {numeral} — {chamber_name(self._idea.chamber)}")

    def _render_history(self) -> None:
        history = self.query_one("#conv-history", ScrollableContainer)
        history.remove_children()
        if not self._idea or not self._idea.conversation:
            history.mount(Static(
                "The chamber is quiet. Begin when ready.",
                classes="conv-empty",
            ))
            return
        for turn in self._idea.conversation:
            role    = turn.get("role", "")
            content = turn.get("content", "").strip()
            if not content:
                continue
            if role == "user":
                history.mount(UserBubble(content))
            elif role == "assistant":
                history.mount(AssistantBubble(content, self._idea.chamber))
        history.scroll_end(animate=False)
