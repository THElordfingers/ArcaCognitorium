"""
widgets/specularium.py
Specularium — live preview pane with three modes:

  subprocess  — headless ANSI/SVG capture (isolated, ~500ms)
  inline      — dynamic widget mounting in-process (instant)
  svg         — SVG export + xdg-open (external viewer)

Mode is toggled with  p  or the mode buttons in the header.
"""
from __future__ import annotations
import asyncio
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static, LoadingIndicator, ContentSwitcher
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual import work

from core.tree import WidgetNode
from core.codegen import generate


PreviewMode = str  # "subprocess" | "inline" | "svg"
MODES: list[PreviewMode] = ["inline", "subprocess", "svg"]
MODE_LABELS = {
    "inline":     "inline (i)",
    "subprocess": "process (p)",
    "svg":        "svg (s)",
}


class SpeculariumPane(Vertical):
    """
    Pane 3: live preview.
    """

    DEFAULT_CSS = """
    SpeculariumPane {
        width: 1fr;
        border-right: solid $border;
        background: $background;
    }
    SpeculariumPane #specularium-header {
        background: $surface-darken-2;
        height: 1;
        padding: 0 2;
    }
    SpeculariumPane #header-title {
        color: $accent;
        text-style: bold;
        width: 1fr;
    }
    SpeculariumPane #mode-bar {
        width: auto;
    }
    SpeculariumPane .mode-btn {
        min-width: 12;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
    }
    SpeculariumPane .mode-btn.active {
        color: $accent;
        text-style: bold;
    }
    SpeculariumPane #preview-area {
        height: 1fr;
        padding: 1 2;
    }
    SpeculariumPane #preview-label {
        color: $text-muted;
        margin-bottom: 1;
    }
    SpeculariumPane #preview-content {
        height: 1fr;
        border: round $border;
        background: $surface-darken-2;
        padding: 1;
        overflow: auto auto;
    }
    SpeculariumPane #preview-empty {
        color: $text-muted;
        text-align: center;
        padding: 4 4;
    }
    SpeculariumPane #loading {
        display: none;
    }
    SpeculariumPane #loading.visible {
        display: block;
    }
    SpeculariumPane #status-bar {
        height: 1;
        background: $surface-darken-2;
        color: $text-muted;
        padding: 0 2;
    }
    """

    mode: reactive[PreviewMode] = reactive("inline")

    def __init__(self) -> None:
        super().__init__()
        self._root:          WidgetNode | None = None
        self._selected_uid:  str | None        = None
        self._preview_full:  bool              = True  # full tree vs selected node
        self._last_code:     str               = ""

    def compose(self) -> ComposeResult:
        with Horizontal(id="specularium-header"):
            yield Static("SPECULARIUM  live preview", id="header-title")
            with Horizontal(id="mode-bar"):
                for m in MODES:
                    cls = "mode-btn active" if m == "inline" else "mode-btn"
                    yield Static(MODE_LABELS[m], id=f"mode-{m}", classes=cls)

        with Vertical(id="preview-area"):
            yield Static("", id="preview-label")
            yield LoadingIndicator(id="loading")
            yield ScrollableContainer(id="preview-content")
            yield Static(
                "Add a root container in Arbor to begin.",
                id="preview-empty",
            )

        yield Static("", id="status-bar")

    def on_static_click(self, event) -> None:
        sid = (event.widget.id or "")
        if sid.startswith("mode-"):
            mode = sid[5:]
            if mode in MODES:
                self.set_mode(mode)

    def set_mode(self, mode: PreviewMode) -> None:
        self.mode = mode
        for m in MODES:
            btn = self.query_one(f"#mode-{m}", Static)
            if m == mode:
                btn.add_class("active")
            else:
                btn.remove_class("active")
        self.refresh_preview()

    def cycle_mode(self) -> None:
        idx = MODES.index(self.mode)
        self.set_mode(MODES[(idx + 1) % len(MODES)])

    def update_tree(self, root: WidgetNode | None, selected_uid: str | None) -> None:
        self._root         = root
        self._selected_uid = selected_uid
        self.refresh_preview()

    def toggle_scope(self) -> None:
        """Toggle between full-tree and selected-node preview."""
        self._preview_full = not self._preview_full
        self.refresh_preview()

    def refresh_preview(self) -> None:
        empty = self.query_one("#preview-empty", Static)
        if self._root is None:
            empty.display = True
            self.query_one("#preview-content", ScrollableContainer).display = False
            self._set_status("No tree")
            return
        empty.display = False
        self.query_one("#preview-content", ScrollableContainer).display = True

        # Generate code for the target (full tree or selected node)
        target = self._root
        if not self._preview_full and self._selected_uid:
            from core.tree import tree_find
            found = tree_find(self._root, self._selected_uid)
            if found:
                target = found

        code = generate(target, mode="class")
        self._last_code = code

        scope = "COMPOSITUS" if self._preview_full else "ISOLATUS"
        self.query_one("#preview-label", Static).update(
            f"[dim]{scope}[/]  ·  mode: [bold]{self.mode}[/]"
        )

        if self.mode == "inline":
            self._render_inline(code)
        elif self.mode == "subprocess":
            self._render_subprocess(code)
        elif self.mode == "svg":
            self._render_svg_mode(code)

    def _render_inline(self, code: str) -> None:
        """Mount the widget directly inside the preview content area."""
        from preview.inline_preview import build_widget
        content = self.query_one("#preview-content", ScrollableContainer)
        content.remove_children()
        try:
            widget = build_widget(code)
            content.mount(widget)
            self._set_status("inline · live")
        except Exception as e:
            content.mount(Label(f"[red]Mount error:[/] {e}", markup=True))
            self._set_status(f"inline · error: {e}")

    @work(exclusive=True, thread=True)
    def _render_subprocess(self, code: str) -> None:
        """Run subprocess preview in a background thread."""
        self.call_from_thread(self._set_loading, True)
        from preview.subprocess_preview import render_svg
        success, result = render_svg(code)
        self.call_from_thread(self._set_loading, False)
        self.call_from_thread(self._apply_subprocess_result, success, result)

    def _apply_subprocess_result(self, success: bool, result: str) -> None:
        content = self.query_one("#preview-content", ScrollableContainer)
        content.remove_children()
        if success:
            # Display SVG inline as markup (Textual renders SVG in Static)
            content.mount(Static(result, markup=False))
            self._set_status("subprocess · ok")
        else:
            content.mount(Label(f"[red]{result}[/]", markup=True))
            self._set_status("subprocess · failed")

    @work(exclusive=True, thread=True)
    def _render_svg_mode(self, code: str) -> None:
        """Export SVG and open in system viewer."""
        self.call_from_thread(self._set_loading, True)
        from preview.svg_preview import export_svg
        success, msg = export_svg(code)
        self.call_from_thread(self._set_loading, False)
        content = self.query_one("#preview-content", ScrollableContainer)
        self.call_from_thread(content.remove_children)
        if success:
            self.call_from_thread(
                content.mount,
                Label(f"[green]SVG exported:[/]\n{msg}\n\n[dim](opened in system viewer)[/]",
                      markup=True)
            )
            self.call_from_thread(self._set_status, f"svg · {msg}")
        else:
            self.call_from_thread(
                content.mount,
                Label(f"[red]SVG export failed:[/]\n{msg}", markup=True)
            )
            self.call_from_thread(self._set_status, f"svg · failed")

    def _set_loading(self, visible: bool) -> None:
        loader = self.query_one("#loading", LoadingIndicator)
        loader.display = visible

    def _set_status(self, msg: str) -> None:
        self.query_one("#status-bar", Static).update(msg)
