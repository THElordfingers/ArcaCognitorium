"""
widgets/arbor.py
Arbor — the composition tree pane.
Displays the current WidgetNode tree and handles selection, add, remove.
"""
from __future__ import annotations
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static, Tree as TextualTree
from textual.widgets.tree import TreeNode
from textual.containers import Vertical
from textual.message import Message
from textual import on

from core.registry import get_widget_def, CONTAINER_IDS
from core.tree import WidgetNode, tree_walk, count_nodes, tree_depth


class NodeSelected(Message):
    def __init__(self, uid: str) -> None:
        super().__init__()
        self.uid = uid


class AddChildRequested(Message):
    def __init__(self, parent_uid: str) -> None:
        super().__init__()
        self.parent_uid = parent_uid


class RemoveRequested(Message):
    def __init__(self, uid: str) -> None:
        super().__init__()
        self.uid = uid


class ArborPane(Vertical):
    """
    Pane 2: shows the current composition tree using Textual's Tree widget.
    """

    DEFAULT_CSS = """
    ArborPane {
        width: 22;
        border-right: solid $border;
        background: $surface-darken-1;
    }
    ArborPane #arbor-header {
        background: $surface-darken-2;
        color: $success;
        padding: 0 2;
        height: 1;
        text-style: bold;
    }
    ArborPane #arbor-tree {
        height: 1fr;
        background: $surface-darken-1;
        border: none;
        padding: 0;
    }
    ArborPane #arbor-footer {
        height: 1;
        background: $surface-darken-2;
        color: $text-muted;
        padding: 0 2;
    }
    ArborPane #arbor-empty {
        color: $text-muted;
        padding: 1 2;
        text-align: center;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._root:         WidgetNode | None = None
        self._selected_uid: str | None        = None
        # Map uid → TreeNode for selection sync
        self._uid_to_tnode: dict[str, TreeNode] = {}

    def compose(self) -> ComposeResult:
        yield Static("ARBOR  composition tree", id="arbor-header")
        yield Static(
            "No tree yet.\nPress [bold cyan]n[/] to add a root container.",
            id="arbor-empty", markup=True,
        )
        tree = TextualTree("", id="arbor-tree")
        tree.show_root = False
        tree.display = False
        yield tree
        yield Static("", id="arbor-footer")

    def load_tree(self, root: WidgetNode | None, selected_uid: str | None) -> None:
        self._root         = root
        self._selected_uid = selected_uid
        self._uid_to_tnode = {}
        tx_tree = self.query_one("#arbor-tree", TextualTree)
        empty   = self.query_one("#arbor-empty", Static)

        if root is None:
            tx_tree.display = False
            empty.display   = True
            self._update_footer()
            return

        empty.display   = False
        tx_tree.display = True
        tx_tree.clear()
        self._build_tree_nodes(tx_tree.root, root)
        tx_tree.root.expand()
        self._update_footer()

        # Re-select
        if selected_uid and selected_uid in self._uid_to_tnode:
            self._uid_to_tnode[selected_uid].select()

    def _build_tree_nodes(self, parent_tnode: TreeNode, node: WidgetNode) -> None:
        d        = get_widget_def(node.widget_id)
        icon     = d.icon if d else "□"
        label    = f"{icon} {node.widget_id}"
        if node.props.get("id"):
            label += f"  [dim]#{node.props['id']}[/]"
        if d and d.rich_only:
            label += "  [magenta]rich[/]"

        tnode = parent_tnode.add(label, data=node.uid, expand=True)
        self._uid_to_tnode[node.uid] = tnode
        for child in node.children:
            self._build_tree_nodes(tnode, child)

    def _update_footer(self) -> None:
        if self._root:
            n = count_nodes(self._root)
            d = tree_depth(self._root)
            self.query_one("#arbor-footer", Static).update(
                f"{n} node{'s' if n != 1 else ''}  ·  depth {d}  "
                f" [red]c[/]lear"
            )
        else:
            self.query_one("#arbor-footer", Static).update("")

    @on(TextualTree.NodeSelected)
    def on_tree_node_selected(self, event: TextualTree.NodeSelected) -> None:
        uid = event.node.data
        if uid:
            self._selected_uid = uid
            self.post_message(NodeSelected(uid))

    @on(TextualTree.NodeHighlighted)
    def on_tree_node_highlighted(self, event: TextualTree.NodeHighlighted) -> None:
        uid = event.node.data
        if uid:
            self._selected_uid = uid
