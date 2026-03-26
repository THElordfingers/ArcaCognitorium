"""
app.py — Fenestrium
A Textual TUI for composing Textual + Rich widget layouts,
with live rendered preview and Python snippet export.

Usage:
    python -m fenestrium
    # or:
    python app.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Label, Input
from textual.containers import Horizontal, Vertical
from textual import on, work

from .core.registry import REGISTRY, get_widget_def, CONTAINER_IDS
from .core.tree import (
    WidgetNode, make_node,
    tree_add, tree_delete, tree_patch, tree_find, tree_find_parent,
    count_nodes, tree_depth,
)
from .core.codegen import generate
from .core import session

from .widgets.classis  import ClassisPane, WidgetSelected, PropChanged
from .widgets.arbor    import ArborPane, NodeSelected, AddChildRequested, RemoveRequested
from .widgets.specularium import SpeculariumPane
from .widgets.codex    import CodexPane


class PickerModal(Vertical):
    """
    Inline modal for choosing a widget to add.
    Shown over the Arbor/Classis area; dismissed with Esc.
    """

    DEFAULT_CSS = """
    PickerModal {
        width: 40;
        height: 30;
        background: #131720;
        border: round #3d5080;
        layer: above;
        offset: 22 2;
        display: none;
    }
    PickerModal.visible {
        display: block;
    }
    PickerModal #picker-header {
        height: 1;
        background: #1a2030;
        color: #c9a84c;
        padding: 0 2;
        text-style: bold;
    }
    PickerModal #picker-search {
        margin: 0 1;
    }
    PickerModal #picker-list {
        height: 1fr;
    }
    PickerModal .picker-item {
        padding: 0 2;
        color: #c8d0e8;
        height: 2;
    }
    PickerModal .picker-item:hover {
        background: #222840;
        color: #e8eeff;
    }
    PickerModal .picker-item.container-item {
        color: #3fc6c6;
    }
    PickerModal .picker-item.rich-item {
        color: #a07de8;
    }
    PickerModal #picker-footer {
        height: 1;
        background: #1a2030;
        color: #4a5570;
        padding: 0 2;
    }
    """

    def __init__(self, containers_only: bool = False) -> None:
        super().__init__()
        self.containers_only = containers_only

    def compose(self) -> ComposeResult:
        title = "SELECT ROOT CONTAINER" if self.containers_only else "ADD CHILD WIDGET"
        yield Static(title, id="picker-header")
        yield Input(placeholder="⌕  filter…", id="picker-search")
        yield Vertical(id="picker-list")
        yield Static("↑↓ navigate  ·  Enter select  ·  Esc close", id="picker-footer")

    def on_mount(self) -> None:
        self._populate("")
        self.query_one("#picker-search", Input).focus()

    def _populate(self, query: str) -> None:
        from ..core.registry import FLAT_REGISTRY
        lst = self.query_one("#picker-list", Vertical)
        # Synchronously detach all children before remounting.
        # remove_children() is async and causes DuplicateIds when _populate
        # is called rapidly (e.g. on every keystroke in the search field).
        for child in list(lst.children):
            child.remove()
        self._pick_map: dict[str, str] = {}   # name -> widget_id
        q = query.lower()
        for w in FLAT_REGISTRY:
            if self.containers_only and not w.is_container:
                continue
            if q and q not in w.id.lower() and q not in w.desc.lower():
                continue
            cls = "picker-item"
            if w.is_container: cls += " container-item"
            elif w.rich_only:  cls += " rich-item"
            # No id= on items — avoids DuplicateIds on repopulate.
            # Carry widget_id via name= instead.
            item = Static(
                f"{w.icon}  {w.id}  [dim]{w.desc[:30]}[/]",
                classes=cls, name=w.id, markup=True,
            )
            self._pick_map[w.id] = w.id
            lst.mount(item)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-search":
            self._populate(event.value)

    def on_static_click(self, event) -> None:
        widget_id = event.widget.name or ""
        if widget_id and widget_id in getattr(self, "_pick_map", {}):
            self.app.on_picker_selection(widget_id)
            self.dismiss()

    def dismiss(self) -> None:
        self.remove_class("visible")


class ConfirmClearModal(Static):
    """Tiny confirmation widget for clearing the tree."""

    DEFAULT_CSS = """
    ConfirmClearModal {
        width: 40;
        height: 7;
        background: #131720;
        border: round #e05555;
        layer: above;
        offset: 22 8;
        display: none;
        padding: 1 2;
        color: #c8d0e8;
    }
    ConfirmClearModal.visible {
        display: block;
    }
    """

    def __init__(self) -> None:
        super().__init__(
            "Clear the entire tree?\n\n"
            "[bold red]y[/]  confirm    [dim]Esc[/]  cancel",
            markup=True,
        )


class FenestriumApp(App):
    """Fenestrium — Textual Widget Fabricator"""

    CSS_PATH  = Path(__file__).parent / "fenestrium.tcss"
    TITLE     = "FENESTRIUM"
    SUB_TITLE = "Textual + Rich Widget Fabricator"

    BINDINGS = [
        Binding("n",          "add_root",           "Add root",        show=True),
        Binding("a",          "add_child",          "Add child",       show=True),
        Binding("x",          "remove_node",        "Remove",          show=True),
        Binding("c",          "copy_snippet",       "Copy",            show=True),
        Binding("p",          "cycle_preview",      "Preview mode",    show=True),
        Binding("f",          "preview_full",       "Full tree",       show=False),
        Binding("t",          "preview_node",       "Node only",       show=False),
        Binding("1",          "cat_1",              "Layout",          show=False),
        Binding("2",          "cat_2",              "Input",           show=False),
        Binding("3",          "cat_3",              "Display",         show=False),
        Binding("4",          "cat_4",              "Navigation",      show=False),
        Binding("5",          "cat_5",              "Rich",            show=False),
        Binding("question_mark", "show_help",       "Help",            show=True),
        Binding("ctrl+c",     "quit",               "Quit",            show=True),
        Binding("escape",     "dismiss_modal",      "Close",           show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._tree:          WidgetNode | None = None
        self._selected_uid:  str | None        = None
        self._picker_target: str | None        = None  # parent uid for new child
        self._picker_containers_only = False

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Horizontal(id="title-bar"):
            yield Static(
                "⬡ FENESTRIUM  [dim]·  Textual + Rich Widget Fabricator[/]",
                id="title-left", markup=True,
            )
            yield Static(
                f"[dim]{count_nodes(self._tree)} nodes  ·  press [bold]?[/] for help[/]",
                id="title-right", markup=True,
            )
        with Horizontal(id="main-area"):
            yield ClassisPane()
            yield ArborPane()
            yield SpeculariumPane()
            yield CodexPane()
        yield Static("", id="status-bar-global")

        # Modals (hidden by default, shown via add_class("visible"))
        yield PickerModal(containers_only=False)
        yield ConfirmClearModal()

    def on_mount(self) -> None:
        # Restore last session
        root, uid = session.load()
        if root:
            self._tree         = root
            self._selected_uid = uid
            self._sync_all()
            self._notify("Session restored.")

    # ── Session save on exit ──────────────────────────────────────────────────

    def on_unmount(self) -> None:
        session.save(self._tree, self._selected_uid)

    # ── Message handlers ──────────────────────────────────────────────────────

    @on(WidgetSelected)
    def on_widget_selected(self, event: WidgetSelected) -> None:
        """User clicked a widget in Classis — add it to the tree."""
        d = event.widget_def
        if self._tree is None:
            # First widget becomes root
            node = make_node(d.id, {k: v.default for k, v in d.props.items()})
            self._tree = node
            self._selected_uid = node.uid
        else:
            sel_def = get_widget_def(
                tree_find(self._tree, self._selected_uid).widget_id
            ) if self._selected_uid else None
            if not sel_def or not sel_def.is_container:
                self._notify("Select a container node to add children.", severity="warning")
                return
            node = make_node(d.id, {k: v.default for k, v in d.props.items()})
            self._tree = tree_add(self._tree, self._selected_uid, node)
            self._selected_uid = node.uid
        self._sync_all()

    @on(PropChanged)
    def on_prop_changed(self, event: PropChanged) -> None:
        if not self._tree or not self._selected_uid:
            return
        self._tree = tree_patch(self._tree, self._selected_uid, {event.key: event.value})
        self._sync_preview()
        self._sync_codex()

    @on(NodeSelected)
    def on_node_selected(self, event: NodeSelected) -> None:
        self._selected_uid = event.uid
        self._sync_classis()
        self._sync_preview()

    @on(RemoveRequested)
    def on_remove_requested(self, event: RemoveRequested) -> None:
        if event.uid == (self._tree.uid if self._tree else None):
            self.query_one(ConfirmClearModal).add_class("visible")
        else:
            self._do_remove(event.uid)

    def on_picker_selection(self, widget_id: str) -> None:
        """Called from PickerModal when user selects a widget."""
        d = get_widget_def(widget_id)
        if not d:
            return
        node = make_node(d.id, {k: v.default for k, v in d.props.items()})
        if self._tree is None:
            self._tree = node
        else:
            target = self._picker_target or self._selected_uid
            if target:
                self._tree = tree_add(self._tree, target, node)
        self._selected_uid = node.uid
        self._picker_target = None
        self._sync_all()

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_add_root(self) -> None:
        if self._tree is not None:
            self._notify("Tree already has a root. Clear it first.", severity="warning")
            return
        self._show_picker(containers_only=True)

    def action_add_child(self) -> None:
        if not self._tree:
            self.action_add_root()
            return
        sel = self._get_selected_node()
        if not sel:
            self._notify("Select a container node first.", severity="warning")
            return
        d = get_widget_def(sel.widget_id)
        if not d or not d.is_container:
            self._notify(f"{sel.widget_id} is a leaf — select a container.", severity="warning")
            return
        self._picker_target = sel.uid
        self._show_picker(containers_only=False)

    def action_remove_node(self) -> None:
        if not self._tree or not self._selected_uid:
            return
        if self._selected_uid == self._tree.uid:
            self.query_one(ConfirmClearModal).add_class("visible")
        else:
            self._do_remove(self._selected_uid)

    def action_copy_snippet(self) -> None:
        self.query_one(CodexPane).copy_to_clipboard()

    def action_cycle_preview(self) -> None:
        self.query_one(SpeculariumPane).cycle_mode()

    def action_preview_full(self) -> None:
        s = self.query_one(SpeculariumPane)
        s._preview_full = True
        s.refresh_preview()

    def action_preview_node(self) -> None:
        s = self.query_one(SpeculariumPane)
        s._preview_full = False
        s.refresh_preview()

    def action_cat_1(self) -> None: self.query_one(ClassisPane).set_category(0)
    def action_cat_2(self) -> None: self.query_one(ClassisPane).set_category(1)
    def action_cat_3(self) -> None: self.query_one(ClassisPane).set_category(2)
    def action_cat_4(self) -> None: self.query_one(ClassisPane).set_category(3)
    def action_cat_5(self) -> None: self.query_one(ClassisPane).set_category(4)

    def action_dismiss_modal(self) -> None:
        for m in self.query(PickerModal):
            m.remove_class("visible")
        for m in self.query(ConfirmClearModal):
            m.remove_class("visible")

    def action_show_help(self) -> None:
        self._notify(
            "n=root  a=add child  x=remove  c=copy  "
            "p=cycle preview  f=full  t=node  1-5=category  ?=help",
        )

    def action_quit(self) -> None:
        session.save(self._tree, self._selected_uid)
        self.exit()

    # ── Keyboard handler for confirm-clear ────────────────────────────────────

    def on_key(self, event) -> None:
        confirm = self.query_one(ConfirmClearModal)
        if "visible" in confirm.classes:
            if event.key == "y":
                self._do_clear()
                confirm.remove_class("visible")
                event.stop()
            elif event.key == "escape":
                confirm.remove_class("visible")
                event.stop()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_selected_node(self) -> WidgetNode | None:
        if not self._tree or not self._selected_uid:
            return None
        return tree_find(self._tree, self._selected_uid)

    def _do_remove(self, uid: str) -> None:
        if not self._tree:
            return
        parent = tree_find_parent(self._tree, uid)
        self._tree = tree_delete(self._tree, uid)
        self._selected_uid = parent.uid if parent else (self._tree.uid if self._tree else None)
        self._sync_all()

    def _do_clear(self) -> None:
        self._tree         = None
        self._selected_uid = None
        self._sync_all()
        self._notify("Tree cleared.")

    def _show_picker(self, containers_only: bool) -> None:
        modal = self.query_one(PickerModal)
        modal.containers_only = containers_only
        modal.add_class("visible")
        modal.on_mount()

    def _sync_all(self) -> None:
        self._sync_arbor()
        self._sync_classis()
        self._sync_preview()
        self._sync_codex()
        self._sync_title()

    def _sync_arbor(self) -> None:
        self.query_one(ArborPane).load_tree(self._tree, self._selected_uid)

    def _sync_classis(self) -> None:
        sel = self._get_selected_node()
        can_add = bool(sel and get_widget_def(sel.widget_id) and
                       get_widget_def(sel.widget_id).is_container)
        self.query_one(ClassisPane).update_selection(sel, can_add)

    def _sync_preview(self) -> None:
        self.query_one(SpeculariumPane).update_tree(self._tree, self._selected_uid)

    def _sync_codex(self) -> None:
        codex = self.query_one(CodexPane)
        codex.update_code(
            code_class=generate(self._tree, mode="class"),
            code_app=generate(self._tree, mode="app"),
        )

    def _sync_title(self) -> None:
        n = count_nodes(self._tree)
        self.query_one("#title-right", Static).update(
            f"[dim]{n} node{'s' if n != 1 else ''}  ·  press [bold]?[/] for help[/]"
        )

    def _notify(self, msg: str, severity: str = "information") -> None:
        self.notify(msg, severity=severity)  # type: ignore


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    app = FenestriumApp()
    app.run()


if __name__ == "__main__":
    main()
