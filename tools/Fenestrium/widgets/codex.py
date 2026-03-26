"""
widgets/codex.py
Codex — generated Python output pane.
Shows syntax-tinted code and handles clipboard copy.
"""
from __future__ import annotations
import pyperclip
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static, RichLog
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.message import Message

from rich.syntax import Syntax


class CodexPane(Vertical):
    """
    Pane 4: displays generated Python with Rich syntax highlighting.
    Copy to clipboard via button or  c  keybinding.
    """

    DEFAULT_CSS = """
    CodexPane {
        width: 40;
        background: $surface-darken-1;
    }
    CodexPane #codex-header {
        background: $surface-darken-2;
        height: 1;
        padding: 0 2;
    }
    CodexPane #codex-title {
        color: $accent;
        text-style: bold;
        width: 1fr;
    }
    CodexPane #mode-class {
        min-width: 7;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
    }
    CodexPane #mode-app {
        min-width: 5;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
    }
    CodexPane .codex-mode-active {
        color: $accent;
        text-style: bold;
    }
    CodexPane #code-scroll {
        height: 1fr;
        padding: 0;
    }
    CodexPane #copy-bar {
        height: 1;
        background: $surface-darken-2;
        align: center middle;
    }
    CodexPane #copy-btn {
        min-width: 20;
        height: 1;
        border: none;
        background: $accent 20%;
        color: $accent;
        text-align: center;
    }
    CodexPane #copy-btn.copied {
        background: $success 20%;
        color: $success;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._code:       str  = ""
        self._export_mode: str = "class"   # "class" | "app"
        self._copied:     bool = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="codex-header"):
            yield Static("CODEX  output", id="codex-title")
            yield Static("class", id="mode-class", classes="codex-mode-active")
            yield Static("app",   id="mode-app")
        yield ScrollableContainer(id="code-scroll")
        with Horizontal(id="copy-bar"):
            yield Static("⎘  COPY SNIPPET", id="copy-btn")

    def on_mount(self) -> None:
        self._render_placeholder()

    def on_static_click(self, event) -> None:
        sid = event.widget.id or ""
        if sid == "mode-class":
            self._set_mode("class")
        elif sid == "mode-app":
            self._set_mode("app")
        elif sid == "copy-btn":
            self.copy_to_clipboard()

    def _set_mode(self, mode: str) -> None:
        self._export_mode = mode
        self.query_one("#mode-class", Static).set_classes(
            "codex-mode-active" if mode == "class" else ""
        )
        self.query_one("#mode-app", Static).set_classes(
            "codex-mode-active" if mode == "app" else ""
        )
        self._rerender()

    def update_code(self, code_class: str, code_app: str) -> None:
        """Called by the app when the tree changes."""
        self._code_class = code_class
        self._code_app   = code_app
        self._rerender()

    def _rerender(self) -> None:
        code = getattr(self, f"_code_{self._export_mode}", "")
        scroll = self.query_one("#code-scroll", ScrollableContainer)
        scroll.remove_children()
        if not code:
            self._render_placeholder()
            return
        scroll.mount(
            Static(
                Syntax(code, "python", theme="monokai", line_numbers=True),
                markup=False,
            )
        )

    def _render_placeholder(self) -> None:
        from core.codegen import generate
        placeholder = generate(None)
        scroll = self.query_one("#code-scroll", ScrollableContainer)
        scroll.remove_children()
        scroll.mount(
            Static(
                Syntax(placeholder, "python", theme="monokai", line_numbers=False),
                markup=False,
            )
        )

    def copy_to_clipboard(self) -> None:
        code = getattr(self, f"_code_{self._export_mode}", "")
        if not code:
            return
        try:
            pyperclip.copy(code)
            self._flash_copied()
        except Exception:
            # pyperclip may not be available in all envs
            pass

    def _flash_copied(self) -> None:
        btn = self.query_one("#copy-btn", Static)
        btn.update("✓  COPIED")
        btn.add_class("copied")
        self.set_timer(1.8, self._reset_copy_btn)

    def _reset_copy_btn(self) -> None:
        btn = self.query_one("#copy-btn", Static)
        btn.update("⎘  COPY SNIPPET")
        btn.remove_class("copied")
