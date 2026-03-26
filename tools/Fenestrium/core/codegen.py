"""
core/codegen.py
Generates correct, runnable Textual + Rich Python from a WidgetNode tree.

Architecture note — preamble/body split:
  Some widgets (Select, RadioSet, Sparkline, Rich widgets) need module-level
  constants or helper functions ABOVE the class definition. These are collected
  as "preambles" and hoisted out of compose() into the module scope.

  _emit_node() returns (preamble: str, body: str).
  generate() collects all preambles, deduplicates, and places them above
  the class.

Rules:
  - ComposeResult always imported
  - Positional args emitted before keyword args
  - id= never duplicated
  - Widgets with code_extra use that path exclusively
  - Empty containers emit `pass  # add children`
  - RichTable helpers named per node id (no collision)
  - Module-level constants never inside compose()
"""
from __future__ import annotations
from collections import defaultdict
from .registry import REGISTRY, FLAT_REGISTRY, get_widget_def, CONTAINER_IDS
from .tree import WidgetNode, tree_walk


# ── Import collection ──────────────────────────────────────────────────────────

def _collect_imports(root: WidgetNode, mode: str) -> str:
    widget_ids: set[str] = set()
    extra_tx:   set[str] = set()
    rich_groups: dict[str, set[str]] = defaultdict(set)
    has_rich = False

    def visit(n: WidgetNode) -> None:
        nonlocal has_rich
        widget_ids.add(n.widget_id)
        d = get_widget_def(n.widget_id)
        if not d:
            return
        if d.extra_imports:
            extra_tx.update(d.extra_imports)
        if d.rich_only:
            has_rich = True
            if d.rich_import:
                rich_groups[d.rich_import["from"]].update(d.rich_import["names"])
            for ri in d.extra_rich_imports:
                rich_groups[ri["from"]].update(ri["names"])

    tree_walk(root, visit)

    containers = sorted(wid for wid in widget_ids if wid in CONTAINER_IDS)
    tx_widgets = sorted(
        wid for wid in widget_ids
        if wid not in CONTAINER_IDS
        and not getattr(get_widget_def(wid), "rich_only", False)
    )
    all_tx = sorted(set(tx_widgets) | extra_tx)
    if has_rich and "Static" not in all_tx:
        all_tx = sorted(set(all_tx) | {"Static"})
    if "RichTable" in widget_ids:
        rich_groups["rich"].add("box")

    lines = []
    lines.append(
        "from textual.app import App, ComposeResult"
        if mode == "app" else
        "from textual.app import ComposeResult"
    )
    if containers:
        lines.append(f"from textual.containers import {', '.join(containers)}")
    if all_tx:
        lines.append(f"from textual.widgets import {', '.join(sorted(all_tx))}")
    for mod in sorted(rich_groups):
        lines.append(f"from {mod} import {', '.join(sorted(rich_groups[mod]))}")
    return "\n".join(lines)


# ── Rich table helpers ─────────────────────────────────────────────────────────

def _collect_richtable_helpers(root: WidgetNode) -> str:
    helpers = []

    def visit(n: WidgetNode) -> None:
        if n.widget_id != "RichTable":
            return
        p      = n.props
        fn     = f"build_table_{p.get('id', 'my_rtable').replace('-','_').replace(' ','_')}"
        cols   = [c.strip() for c in p.get("columns", "Name,Value,Status").split(",") if c.strip()]
        t_arg  = f'title="{p["title"]}", ' if p.get("title") else ""
        col_ln = "\n".join(f'    table.add_column("{c}")' for c in cols)
        rows   = ", ".join('"…"' for _ in cols)
        helpers.append(
            f"\ndef {fn}() -> Table:\n"
            f"    table = Table({t_arg}box=box.{p.get('box_style','ROUNDED')})\n"
            f"{col_ln}\n"
            f"    table.add_row({rows})\n"
            f"    return table"
        )

    tree_walk(root, visit)
    return "".join(helpers)


# ── Node emission — returns (preamble, body) ───────────────────────────────────
# preamble: module-level code (constants, helper vars) — goes ABOVE the class
# body:     the indented yield/with statement — goes inside compose()

def _emit_node(node: WidgetNode, indent: int) -> tuple[str, str]:
    """Returns (preamble, body)."""
    pad = " " * indent
    d   = get_widget_def(node.widget_id)
    p   = node.props

    if d and d.code_extra:
        # Collect child preambles + bodies
        child_preambles = []
        child_bodies    = []
        for c in node.children:
            cp, cb = _emit_node(c, indent + 4)
            if cp:
                child_preambles.append(cp)
            child_bodies.append(cb)

        result = d.code_extra(p, child_bodies, indent)

        # Split result: everything before the first `yield ` or `with ` at
        # the target indent level is preamble (module-level constants/helpers).
        # We scan for the first line that starts with exactly `indent` spaces
        # followed by "yield " or "with ".
        lines      = result.split("\n")
        split_idx  = len(lines)  # default: all preamble
        target_pad = " " * indent
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if (
                line.startswith(target_pad)
                and not line.startswith(target_pad + " ")
                and (stripped.startswith("yield ") or stripped.startswith("with "))
            ):
                split_idx = i
                break

        preamble_lines = lines[:split_idx]
        body_lines     = lines[split_idx:]

        combined_preamble = "\n".join(child_preambles)
        if any(l.strip() for l in preamble_lines):
            block = "\n".join(preamble_lines).strip()
            combined_preamble = (block + "\n" + combined_preamble).strip()

        body = "\n".join(body_lines)
        return combined_preamble, body

    # Standard path — positional args, then id, then non-default kwargs
    pos_args = d.code_args(p) if d and d.code_args else ""
    pos_keys: set[str] = set()
    if d and d.code_args:
        for k in ("label", "text", "content"):
            if k in (d.props or {}):
                pos_keys.add(k)

    def _fmt(v) -> str:
        if isinstance(v, bool): return "True" if v else "False"
        if isinstance(v, int):  return str(v)
        return f'"{v}"'

    kw_parts = []
    for k, v in p.items():
        if k == "id":       continue
        if k in pos_keys:   continue
        dflt = (d.props or {}).get(k)
        if dflt is not None and v == dflt.default: continue
        if v == "" or v is None: continue
        kw_parts.append(f"{k}={_fmt(v)}")

    id_arg   = f'id="{p["id"]}"' if p.get("id") else ""
    all_args = ", ".join(filter(None, [pos_args, id_arg, *kw_parts]))

    if d and d.is_container:
        if node.children:
            child_preambles = []
            child_bodies    = []
            for c in node.children:
                cp, cb = _emit_node(c, indent + 4)
                if cp: child_preambles.append(cp)
                child_bodies.append(cb)
            body = (
                f"{pad}with {node.widget_id}({all_args}):\n"
                + "\n".join(child_bodies)
            )
            return "\n".join(child_preambles), body
        else:
            return "", f"{pad}with {node.widget_id}({all_args}):\n{pad}    pass  # add children"

    return "", f"{pad}yield {node.widget_id}({all_args})"


# ── Public API ─────────────────────────────────────────────────────────────────

def generate(root: WidgetNode | None, mode: str = "class") -> str:
    """
    Generate a complete, runnable Python snippet from the composition tree.
    mode = "class"  → Widget subclass with compose()
    mode = "app"    → full App with __main__ guard
    """
    if root is None:
        return "\n".join([
            "# No widgets yet.",
            "# Press  n  to add a root container.",
            "#",
            "# Shortcuts:",
            "#   n       add root",
            "#   a       add child to selected container",
            "#   x       remove selected node",
            "#   c       copy snippet",
            "#   p       cycle preview mode",
            "#   ?       show all shortcuts",
        ])

    imports        = _collect_imports(root, mode)
    rich_helpers   = _collect_richtable_helpers(root)
    preamble, body = _emit_node(root, indent=8)

    # Preamble goes between imports and class definition
    pre_block = ""
    if preamble.strip():
        pre_block = "\n" + preamble.strip() + "\n"
    if rich_helpers:
        pre_block += rich_helpers + "\n"

    if mode == "class":
        base = root.widget_id if root.widget_id in CONTAINER_IDS else "Widget"
        return (
            f"{imports}\n"
            f"{pre_block}\n"
            f"class MyLayout({base}):\n"
            f'    DEFAULT_CSS = """\n'
            f"    MyLayout {{\n"
            f"        width: 100%;\n"
            f"        height: 100%;\n"
            f"    }}\n"
            f'    """\n\n'
            f"    def compose(self) -> ComposeResult:\n"
            f"{body}"
        )

    return (
        f"{imports}\n"
        f"{pre_block}\n"
        f"class FenestriumApp(App):\n"
        f'    CSS = """\n'
        f"    Screen {{\n"
        f"        align: center middle;\n"
        f"    }}\n"
        f'    """\n\n'
        f"    def compose(self) -> ComposeResult:\n"
        f"{body}\n\n"
        f'if __name__ == "__main__":\n'
        f"    app = FenestriumApp()\n"
        f"    app.run()"
    )
