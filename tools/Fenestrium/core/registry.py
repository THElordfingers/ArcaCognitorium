"""
core/registry.py
Widget registry — self-describing definitions for every Textual and Rich widget
Fenestrium supports. Validated at import time.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Prop definition ────────────────────────────────────────────────────────────

@dataclass
class PropDef:
    label:   str
    type:    str                        # "str" | "int" | "bool" | "select"
    default: Any
    options: list[str] = field(default_factory=list)   # for type=="select"
    min:     int = 0
    max:     int = 100


# ── Widget definition ──────────────────────────────────────────────────────────

@dataclass
class WidgetDef:
    id:           str
    icon:         str
    desc:         str
    props:        dict[str, PropDef]
    is_container: bool = False
    rich_only:    bool = False

    # Positional constructor args (e.g. Button label, Label text)
    # fn(props) -> str  e.g. '"Click me"'
    code_args: Optional[Callable] = None

    # Full block override — used when the widget needs special structure
    # fn(props, child_code_strings, indent) -> str
    code_extra: Optional[Callable] = None

    # Rich import  e.g. {"from": "rich.panel", "names": ["Panel"]}
    rich_import: Optional[dict] = None

    # Extra textual widget imports needed (RadioButton, ListItem, Label…)
    extra_imports: list[str] = field(default_factory=list)

    # Extra rich imports for helper generation
    extra_rich_imports: list[dict] = field(default_factory=list)


# ── Registry ───────────────────────────────────────────────────────────────────

def _p(label, type_, default, **kwargs) -> PropDef:
    return PropDef(label=label, type=type_, default=default, **kwargs)


REGISTRY: dict[str, list[WidgetDef]] = {

    "Layout": [
        WidgetDef(
            id="Vertical", icon="⊟", desc="Stacks children top to bottom",
            is_container=True,
            props={
                "id": _p("id", "str", "vertical_1"),
            },
        ),
        WidgetDef(
            id="Horizontal", icon="⊞", desc="Arranges children side by side",
            is_container=True,
            props={
                "id": _p("id", "str", "horizontal_1"),
            },
        ),
        WidgetDef(
            id="Grid", icon="⊡", desc="CSS grid layout container",
            is_container=True,
            props={
                "id":      _p("id",      "str", "grid_1"),
                "columns": _p("columns", "int", 3, min=1, max=6),
                "rows":    _p("rows",    "int", 2, min=1, max=6),
                "gutter":  _p("gutter",  "int", 1, min=0, max=4),
            },
        ),
        WidgetDef(
            id="ScrollableContainer", icon="↕", desc="Overflow container with scroll",
            is_container=True,
            props={
                "id":         _p("id",         "str",  "scroll_1"),
                "horizontal": _p("horizontal", "bool", False),
                "vertical":   _p("vertical",   "bool", True),
            },
        ),
        WidgetDef(
            id="TabbedContent", icon="⬒", desc="Tabbed pane container",
            is_container=True,
            props={
                "id":   _p("id",   "str", "tabs_1"),
                "tabs": _p("tab names (csv)", "str", "Tab A,Tab B,Tab C"),
            },
            code_extra=lambda p, children, indent: _tabbed_content_code(p, children, indent),
        ),
    ],

    "Input": [
        WidgetDef(
            id="Input", icon="▐", desc="Single-line text field",
            props={
                "id":          _p("id",                   "str",  "my_input"),
                "placeholder": _p("placeholder",          "str",  "Enter text…"),
                "password":    _p("password mode",        "bool", False),
                "max_length":  _p("max_length (0=∞)",     "int",  0, min=0, max=256),
            },
        ),
        WidgetDef(
            id="Button", icon="◉", desc="Clickable action button",
            props={
                "id":      _p("id",      "str",    "my_btn"),
                "label":   _p("label",   "str",    "Click me"),
                "variant": _p("variant", "select", "default",
                              options=["default","primary","success","warning","error"]),
            },
            code_args=lambda p: f'"{p["label"] or "Click me"}"',
        ),
        WidgetDef(
            id="Select", icon="▾", desc="Dropdown selection widget",
            props={
                "id":      _p("id",            "str", "my_select"),
                "prompt":  _p("prompt",        "str", "Choose…"),
                "options": _p("options (csv)", "str", "Alpha,Beta,Gamma"),
            },
            code_extra=lambda p, ch, i: _select_code(p, i),
        ),
        WidgetDef(
            id="Checkbox", icon="☑", desc="Boolean toggle checkbox",
            props={
                "id":    _p("id",                "str",  "my_check"),
                "label": _p("label",             "str",  "Enable feature"),
                "value": _p("checked by default","bool", False),
            },
            code_args=lambda p: f'"{p["label"] or "Enable feature"}"',
        ),
        WidgetDef(
            id="RadioSet", icon="◎", desc="Exclusive radio button group",
            props={
                "id":      _p("id",            "str", "my_radio"),
                "options": _p("options (csv)", "str", "Option A,Option B,Option C"),
            },
            code_extra=lambda p, ch, i: _radioset_code(p, i),
            extra_imports=["RadioButton"],
        ),
        WidgetDef(
            id="Switch", icon="⏻", desc="On/off toggle switch",
            props={
                "id":    _p("id",         "str",  "my_switch"),
                "label": _p("label",      "str",  "Toggle"),
                "value": _p("default on", "bool", False),
            },
        ),
        WidgetDef(
            id="TextArea", icon="▤", desc="Multi-line syntax-highlighted editor",
            props={
                "id":       _p("id",       "str",    "my_textarea"),
                "language": _p("language", "select", "",
                               options=["","python","css","json","markdown","sql"]),
            },
        ),
    ],

    "Display": [
        WidgetDef(
            id="Label", icon="T", desc="Static text with rich markup",
            props={
                "id":     _p("id",           "str",  "my_label"),
                "text":   _p("text",         "str",  "Hello, World!"),
                "markup": _p("rich markup",  "bool", True),
            },
            code_args=lambda p: f'"{p["text"] or "Hello, World!"}"',
        ),
        WidgetDef(
            id="Static", icon="□", desc="Static content — string or Rich renderable",
            props={
                "id":      _p("id",      "str", "my_static"),
                "content": _p("content", "str", "Static content"),
            },
            code_args=lambda p: f'"{p["content"] or ""}"',
        ),
        WidgetDef(
            id="DataTable", icon="▦", desc="Sortable, scrollable data table",
            props={
                "id":      _p("id",            "str",    "my_table"),
                "columns": _p("columns (csv)", "str",    "Name,Score,Status"),
                "zebra":   _p("zebra stripes", "bool",   True),
                "cursor":  _p("cursor type",   "select", "row",
                              options=["row","column","cell","none"]),
            },
        ),
        WidgetDef(
            id="ProgressBar", icon="▰", desc="Visual progress indicator",
            props={
                "id":       _p("id",               "str",  "my_progress"),
                "total":    _p("total",            "int",  100, min=1, max=1000),
                "progress": _p("initial progress", "int",  40,  min=0, max=1000),
                "show_eta": _p("show ETA",         "bool", True),
            },
        ),
        WidgetDef(
            id="RichLog", icon="≣", desc="Rich-renderable auto-scrolling log",
            props={
                "id":        _p("id",               "str",  "my_log"),
                "highlight": _p("highlight",        "bool", True),
                "markup":    _p("markup",           "bool", True),
                "max_lines": _p("max_lines (0=∞)",  "int",  0, min=0, max=10000),
            },
        ),
        WidgetDef(
            id="Markdown", icon="M", desc="Rendered Markdown content block",
            props={
                "id":      _p("id",               "str", "my_md"),
                "content": _p("markdown content", "str", "# Heading\n\nBody text."),
            },
            code_args=lambda p: f'"""\n{p["content"] or "# Heading"}\n"""',
        ),
        WidgetDef(
            id="Sparkline", icon="∿", desc="Inline mini sparkline chart",
            props={
                "id":               _p("id",               "str",    "my_spark"),
                "summary_function": _p("summary_function", "select", "max",
                                       options=["max","min","mean"]),
            },
            code_extra=lambda p, ch, i: _sparkline_code(p, i),
        ),
    ],

    "Navigation": [
        WidgetDef(
            id="Header", icon="▔", desc="App header bar with title",
            props={
                "id":        _p("id",        "str", "my_header"),
                "title":     _p("title",     "str", "My App"),
                "sub_title": _p("sub_title", "str", ""),
            },
        ),
        WidgetDef(
            id="Footer", icon="▁", desc="App footer with key binding display",
            props={
                "id":       _p("id",               "str", "my_footer"),
                "bindings": _p("bindings (csv)",   "str", "q Quit,? Help,f Filter"),
            },
        ),
        WidgetDef(
            id="ListView", icon="☰", desc="Keyboard-navigable item list",
            props={
                "id":            _p("id",            "str", "my_list"),
                "items":         _p("items (csv)",   "str", "Item One,Item Two,Item Three"),
                "initial_index": _p("initial index", "int", 0, min=0, max=99),
            },
            code_extra=lambda p, ch, i: _listview_code(p, i),
            extra_imports=["ListItem", "Label"],
        ),
        WidgetDef(
            id="Tree", icon="⋮", desc="Expandable hierarchical tree widget",
            props={
                "id":    _p("id",          "str", "my_tree"),
                "label": _p("root label",  "str", "Root"),
            },
            code_args=lambda p: f'"{p["label"] or "Root"}"',
        ),
    ],

    "Rich": [
        WidgetDef(
            id="Panel", icon="▣", desc="Bordered panel with optional title",
            rich_only=True,
            rich_import={"from": "rich.panel", "names": ["Panel"]},
            props={
                "id":           _p("id (Static wrapper)", "str",    "my_panel"),
                "title":        _p("title",               "str",    "My Panel"),
                "subtitle":     _p("subtitle",            "str",    ""),
                "border_style": _p("border_style",        "select", "blue",
                                   options=["blue","green","red","yellow","magenta","cyan","bold blue","bold green"]),
            },
            code_extra=lambda p, ch, i: _panel_code(p, i),
        ),
        WidgetDef(
            id="Columns", icon="⫿", desc="Arrange renderables side by side",
            rich_only=True,
            rich_import={"from": "rich.columns", "names": ["Columns"]},
            extra_rich_imports=[{"from": "rich.text", "names": ["Text"]}],
            props={
                "id":     _p("id (Static wrapper)", "str",  "my_cols"),
                "equal":  _p("equal width",         "bool", False),
                "expand": _p("expand to fill",      "bool", False),
            },
            code_extra=lambda p, ch, i: _columns_code(p, i),
        ),
        WidgetDef(
            id="RichTable", icon="⊞", desc="Styled tabular data via Rich",
            rich_only=True,
            rich_import={"from": "rich.table", "names": ["Table"]},
            props={
                "id":        _p("id (Static wrapper)", "str",    "my_rtable"),
                "title":     _p("title",               "str",    ""),
                "columns":   _p("columns (csv)",       "str",    "Name,Value,Status"),
                "box_style": _p("box style",           "select", "ROUNDED",
                               options=["ROUNDED","SIMPLE","MINIMAL","HEAVY","DOUBLE","MARKDOWN"]),
            },
            code_extra=lambda p, ch, i: _richtable_code(p, i),
        ),
        WidgetDef(
            id="RichSyntax", icon="◈", desc="Syntax-highlighted code block",
            rich_only=True,
            rich_import={"from": "rich.syntax", "names": ["Syntax"]},
            props={
                "id":           _p("id (Static wrapper)", "str",    "my_syntax"),
                "language":     _p("language",            "select", "python",
                                   options=["python","javascript","typescript","bash","json","yaml","toml","sql","css","html","rust","go"]),
                "theme":        _p("theme",               "select", "monokai",
                                   options=["monokai","dracula","github-dark","solarized-dark","nord","one-dark"]),
                "line_numbers": _p("line numbers",        "bool",   False),
            },
            code_extra=lambda p, ch, i: _richsyntax_code(p, i),
        ),
        WidgetDef(
            id="Rule", icon="─", desc="Horizontal divider with optional title",
            rich_only=True,
            rich_import={"from": "rich.rule", "names": ["Rule"]},
            props={
                "id":    _p("id (Static wrapper)", "str",    "my_rule"),
                "title": _p("title",               "str",    ""),
                "style": _p("style",               "select", "bright_blue",
                            options=["bright_blue","green","red","yellow","white","dim","bold"]),
            },
            code_extra=lambda p, ch, i: _rule_code(p, i),
        ),
        WidgetDef(
            id="Align", icon="⟺", desc="Align a renderable within its container",
            rich_only=True,
            rich_import={"from": "rich.align", "names": ["Align"]},
            props={
                "id":         _p("id (Static wrapper)", "str",    "my_align"),
                "horizontal": _p("horizontal",          "select", "center",
                                 options=["left","center","right"]),
                "vertical":   _p("vertical",            "select", "middle",
                                 options=["top","middle","bottom"]),
            },
            code_extra=lambda p, ch, i: _align_code(p, i),
        ),
    ],
}

# Flat list for search / lookup
FLAT_REGISTRY: list[WidgetDef] = [w for cat in REGISTRY.values() for w in cat]

def get_widget_def(widget_id: str) -> Optional[WidgetDef]:
    return next((w for w in FLAT_REGISTRY if w.id == widget_id), None)

CONTAINER_IDS: frozenset[str] = frozenset(
    w.id for w in FLAT_REGISTRY if w.is_container
)


# ── code_extra helpers ─────────────────────────────────────────────────────────

def _tabbed_content_code(p: dict, children: list[str], indent: int) -> str:
    pad   = " " * indent
    inner = " " * (indent + 4)   # TabPane level
    deep  = " " * (indent + 8)   # content inside TabPane
    tabs  = [t.strip() for t in p.get("tabs", "Tab A,Tab B,Tab C").split(",") if t.strip()]
    id_arg = f'id="{p["id"]}"' if p.get("id") else ""
    panes = []
    for i, tab in enumerate(tabs):
        tab_id = tab.lower().replace(" ", "_")
        if i < len(children) and children[i].strip():
            # Re-indent the child body to deep level
            raw_body = children[i]
            # Strip existing leading whitespace and re-indent
            child_lines = raw_body.split("\n")
            # Find minimum indent of non-empty lines
            min_indent = min(
                (len(l) - len(l.lstrip()) for l in child_lines if l.strip()),
                default=0
            )
            reindented = "\n".join(
                deep + l[min_indent:] if l.strip() else ""
                for l in child_lines
            )
            body = reindented
        else:
            body = f"{deep}pass"
        panes.append(f'{inner}with TabbedContent.TabPane("{tab}", id="{tab_id}"):\n{body}')
    return f'{pad}with TabbedContent({id_arg}):\n' + "\n".join(panes)


def _select_code(p: dict, indent: int) -> str:
    pad  = " " * indent
    opts = [o.strip() for o in p.get("options", "Alpha,Beta,Gamma").split(",") if o.strip()]
    var  = f'{p.get("id", "my_select").upper()}_OPTIONS'
    opt_lines = "\n".join(f'    ("{o}", "{o.lower().replace(" ", "_")}"),' for o in opts)
    return (
        f"# Select options: (display_label, value)\n"
        f"{var} = [\n{opt_lines}\n]\n\n"
        f'{pad}yield Select(\n'
        f'{pad}    {var},\n'
        f'{pad}    prompt="{p.get("prompt", "Choose…")}",\n'
        f'{pad}    id="{p.get("id", "my_select")}",\n'
        f'{pad})'
    )


def _radioset_code(p: dict, indent: int) -> str:
    pad  = " " * indent
    opts = [o.strip() for o in p.get("options", "Option A,Option B,Option C").split(",") if o.strip()]
    btns = ",\n".join(f'{pad}    RadioButton("{o}")' for o in opts)
    return f'{pad}yield RadioSet(\n{btns},\n{pad}    id="{p.get("id", "my_radio")}",\n{pad})'


def _listview_code(p: dict, indent: int) -> str:
    pad   = " " * indent
    items = [i.strip() for i in p.get("items", "Item One,Item Two,Item Three").split(",") if i.strip()]
    lines = ",\n".join(f'{pad}    ListItem(Label("{item}"))' for item in items)
    return (
        f'{pad}yield ListView(\n{lines},\n'
        f'{pad}    id="{p.get("id", "my_list")}",\n'
        f'{pad}    initial_index={p.get("initial_index", 0)},\n'
        f'{pad})'
    )


def _sparkline_code(p: dict, indent: int) -> str:
    pad = " " * indent
    var = f'{p.get("id", "my_spark").upper()}_DATA'
    fn  = (p.get("summary_function") or "max").upper()
    return (
        f"{var} = [1, 4, 2, 7, 3, 9, 5, 8, 6, 4, 7, 3, 8, 5, 2]\n\n"
        f'{pad}yield Sparkline(\n'
        f'{pad}    {var},\n'
        f'{pad}    summary_function=Sparkline.{fn},\n'
        f'{pad}    id="{p.get("id", "my_spark")}",\n'
        f'{pad})'
    )


def _panel_code(p: dict, indent: int) -> str:
    pad = " " * indent
    sub = f', subtitle="{p["subtitle"]}"' if p.get("subtitle") else ""
    return (
        f'{pad}yield Static(\n'
        f'{pad}    Panel(\n'
        f'{pad}        "Your content here",\n'
        f'{pad}        title="{p.get("title", "My Panel")}"{sub},\n'
        f'{pad}        border_style="{p.get("border_style", "blue")}",\n'
        f'{pad}    ),\n'
        f'{pad}    id="{p.get("id", "my_panel")}",\n'
        f'{pad})'
    )


def _columns_code(p: dict, indent: int) -> str:
    pad = " " * indent
    var = f'{p.get("id", "my_cols").upper()}_ITEMS'
    return (
        f"# Columns items: list of Rich renderables\n"
        f"{var} = [\n    Text(\"item 1\"),\n    Text(\"item 2\"),\n    Text(\"item 3\"),\n]\n\n"
        f'{pad}yield Static(\n'
        f'{pad}    Columns({var}, equal={p.get("equal", False)}, expand={p.get("expand", False)}),\n'
        f'{pad}    id="{p.get("id", "my_cols")}",\n'
        f'{pad})'
    )


def _richtable_code(p: dict, indent: int) -> str:
    pad    = " " * indent
    fn     = f'build_table_{p.get("id", "my_rtable").replace("-", "_")}'
    return f'{pad}yield Static({fn}(), id="{p.get("id", "my_rtable")}")'


def _richsyntax_code(p: dict, indent: int) -> str:
    pad = " " * indent
    var = f'{p.get("id", "my_syntax").upper()}_CODE'
    return (
        f'{var} = """\n'
        f'def greet(name: str) -> str:\n'
        f'    return f"Hello, {{name}}!"\n'
        f'"""\n\n'
        f'{pad}yield Static(\n'
        f'{pad}    Syntax(\n'
        f'{pad}        {var}.strip(),\n'
        f'{pad}        "{p.get("language", "python")}",\n'
        f'{pad}        theme="{p.get("theme", "monokai")}",\n'
        f'{pad}        line_numbers={p.get("line_numbers", False)},\n'
        f'{pad}    ),\n'
        f'{pad}    id="{p.get("id", "my_syntax")}",\n'
        f'{pad})'
    )


def _rule_code(p: dict, indent: int) -> str:
    pad      = " " * indent
    title_arg = f'"{p["title"]}", ' if p.get("title") else ""
    return (
        f'{pad}yield Static(\n'
        f'{pad}    Rule({title_arg}style="{p.get("style", "bright_blue")}"),\n'
        f'{pad}    id="{p.get("id", "my_rule")}",\n'
        f'{pad})'
    )


def _align_code(p: dict, indent: int) -> str:
    pad = " " * indent
    return (
        f'{pad}yield Static(\n'
        f'{pad}    Align(\n'
        f'{pad}        "Your renderable here",\n'
        f'{pad}        horizontal="{p.get("horizontal", "center")}",\n'
        f'{pad}        vertical="{p.get("vertical", "middle")}",\n'
        f'{pad}    ),\n'
        f'{pad}    id="{p.get("id", "my_align")}",\n'
        f'{pad})'
    )


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_registry() -> None:
    """Called once at import. Warns loudly for any malformed widget definition."""
    import warnings
    required = ("id", "icon", "desc", "props")
    for cat, widgets in REGISTRY.items():
        for w in widgets:
            missing = [f for f in required if not getattr(w, f, None)]
            if missing:
                warnings.warn(
                    f"[Fenestrium] Widget '{w.id or 'UNKNOWN'}' in '{cat}' "
                    f"is missing: {', '.join(missing)}",
                    stacklevel=2,
                )


validate_registry()
