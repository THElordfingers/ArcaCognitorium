"""
core/tree.py
Immutable tree of WidgetNode objects.
All operations return new trees — no mutation anywhere.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class WidgetNode:
    uid:       str
    widget_id: str
    props:     dict
    children:  list["WidgetNode"] = field(default_factory=list)

    def __post_init__(self):
        # Ensure children is always a list (not shared reference)
        self.children = list(self.children)

    def to_dict(self) -> dict:
        return {
            "uid":       self.uid,
            "widget_id": self.widget_id,
            "props":     self.props,
            "children":  [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WidgetNode":
        return cls(
            uid       = d["uid"],
            widget_id = d["widget_id"],
            props     = d["props"],
            children  = [cls.from_dict(c) for c in d.get("children", [])],
        )


def make_node(widget_id: str, props: dict) -> WidgetNode:
    """Create a new leaf node with a UUID uid."""
    return WidgetNode(uid=str(uuid.uuid4()), widget_id=widget_id, props=dict(props))


# ── Pure tree transformations ──────────────────────────────────────────────────
# Every function returns a new tree. The original is never modified.

def tree_map(node: WidgetNode, fn: Callable[[WidgetNode], WidgetNode]) -> WidgetNode:
    """Apply fn to every node bottom-up, returning a new tree."""
    mapped_children = [tree_map(c, fn) for c in node.children]
    return fn(WidgetNode(
        uid=node.uid, widget_id=node.widget_id,
        props=node.props, children=mapped_children,
    ))


def tree_find(node: WidgetNode, uid: str) -> Optional[WidgetNode]:
    """Return the node with the given uid, or None."""
    if node.uid == uid:
        return node
    for child in node.children:
        result = tree_find(child, uid)
        if result:
            return result
    return None


def tree_find_parent(node: WidgetNode, uid: str) -> Optional[WidgetNode]:
    """Return the parent of the node with the given uid, or None."""
    for child in node.children:
        if child.uid == uid:
            return node
        result = tree_find_parent(child, uid)
        if result:
            return result
    return None


def tree_add(root: WidgetNode, parent_uid: str, child: WidgetNode) -> WidgetNode:
    """Append child to the children of the node with parent_uid."""
    def fn(n: WidgetNode) -> WidgetNode:
        if n.uid == parent_uid:
            return WidgetNode(
                uid=n.uid, widget_id=n.widget_id,
                props=n.props, children=[*n.children, child],
            )
        return n
    return tree_map(root, fn)


def tree_delete(root: WidgetNode, uid: str) -> WidgetNode:
    """Remove the node with the given uid (and all its descendants)."""
    def fn(n: WidgetNode) -> WidgetNode:
        return WidgetNode(
            uid=n.uid, widget_id=n.widget_id, props=n.props,
            children=[c for c in n.children if c.uid != uid],
        )
    return tree_map(root, fn)


def tree_patch(root: WidgetNode, uid: str, props: dict) -> WidgetNode:
    """Merge props into the node with the given uid."""
    def fn(n: WidgetNode) -> WidgetNode:
        if n.uid == uid:
            return WidgetNode(
                uid=n.uid, widget_id=n.widget_id,
                props={**n.props, **props}, children=n.children,
            )
        return n
    return tree_map(root, fn)


def tree_walk(node: WidgetNode, fn: Callable[[WidgetNode], None]) -> None:
    """Call fn on every node in pre-order (no return value)."""
    fn(node)
    for child in node.children:
        tree_walk(child, fn)


def count_nodes(node: Optional[WidgetNode]) -> int:
    if not node:
        return 0
    return 1 + sum(count_nodes(c) for c in node.children)


def tree_depth(node: Optional[WidgetNode]) -> int:
    if not node or not node.children:
        return 0
    return 1 + max(tree_depth(c) for c in node.children)
