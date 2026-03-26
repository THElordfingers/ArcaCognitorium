"""
widgets/classis.py
Classis — widget registry browser pane.
Shows categories, search, and Propria (prop editor) for the selected node.
"""
from __future__ import annotations
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import (
    Label, Input, Button, ListView, ListItem,
    Static, ContentSwitcher,
)
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message

from core.registry import REGISTRY, FLAT_REGISTRY, get_widget_def, WidgetDef
from core.tree import WidgetNode


class WidgetSelected(Message):
    """Emitted when user clicks a widget in the browser."""
    def __init__(self, widget_def: WidgetDef) -> None:
        super().__init__()
        self.widget_def = widget_def


class PropChanged(Message):
    """Emitted when a prop value is edited."""
    def __init__(self, key: str, value) -> None:
        super().__init__()
        self.key   = key
        self.value = value


class PropRow(Horizontal):
    """A single prop label + input row."""

    DEFAULT_CSS = """
    PropRow {
        height: auto;
        margin-bottom: 1;
    }
    PropRow Label {
        width: 14;
        color: $text-muted;
        padding-top: 1;
    }
    PropRow Input {
        width: 1fr;
    }
    PropRow .prop-bool {
        width: 1fr;
        height: 3;
        border: tall $border;
        background: $surface;
        content-align: center middle;
        color: $text-muted;
    }
    PropRow .prop-bool.on {
        background: $accent 20%;
        color: $accent;
        border: tall $accent;
    }
    """

    def __init__(self, prop_key: str, prop_def, current_value) -> None:
        super().__init__()
        self.prop_key     = prop_key
        self.prop_def     = prop_def
        self.current_value = current_value

    def compose(self) -> ComposeResult:
        yield Label(self.prop_def.label[:13])
        ptype = self.prop_def.type
        val   = self.current_value

        if ptype == "str":
            yield Input(value=str(val), id=f"prop_{self.prop_key}")
        elif ptype == "int":
            yield Input(value=str(val), id=f"prop_{self.prop_key}",
                        type="integer")
        elif ptype == "bool":
            cls = "prop-bool on" if val else "prop-bool"
            yield Static(f"{'☑ true' if val else '☐ false'}",
                         id=f"prop_{self.prop_key}", classes=cls)
        elif ptype == "select":
            # Use a Label + cycle-on-click pattern
            yield Static(str(val), id=f"prop_{self.prop_key}",
                         classes="prop-select")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == f"prop_{self.prop_key}":
            ptype = self.prop_def.type
            try:
                val = int(event.value) if ptype == "int" else event.value
            except ValueError:
                return
            self.post_message(PropChanged(self.prop_key, val))

    def on_static_click(self, event) -> None:
        ptype = self.prop_def.type
        if ptype == "bool":
            new_val = not self.current_value
            self.current_value = new_val
            widget = self.query_one(f"#prop_{self.prop_key}", Static)
            widget.update(f"{'☑ true' if new_val else '☐ false'}")
            widget.set_classes("prop-bool on" if new_val else "prop-bool")
            self.post_message(PropChanged(self.prop_key, new_val))
        elif ptype == "select":
            opts = self.prop_def.options
            cur  = self.current_value
            idx  = opts.index(cur) if cur in opts else 0
            new_val = opts[(idx + 1) % len(opts)]
            self.current_value = new_val
            self.query_one(f"#prop_{self.prop_key}", Static).update(new_val)
            self.post_message(PropChanged(self.prop_key, new_val))


class Propria(ScrollableContainer):
    """Prop editor section shown below the widget list when a node is selected."""

    DEFAULT_CSS = """
    Propria {
        height: auto;
        max-height: 50%;
        border-top: solid $border;
        background: $surface-darken-1;
    }
    Propria #propria-header {
        background: $surface-darken-2;
        color: $accent-lighten-1;
        padding: 0 2;
        height: 1;
        text-style: bold;
    }
    Propria #propria-empty {
        color: $text-muted;
        padding: 1 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._node: WidgetNode | None = None

    def compose(self) -> ComposeResult:
        yield Static("PROPRIA", id="propria-header")
        yield Static("No selection", id="propria-empty")

    def load_node(self, node: WidgetNode | None) -> None:
        self._node = node
        self.query("#propria-empty").first().display = node is None
        # Remove old prop rows
        for row in self.query(PropRow):
            row.remove()
        if node is None:
            return
        d = get_widget_def(node.widget_id)
        if not d:
            return
        for key, prop_def in d.props.items():
            row = PropRow(key, prop_def, node.props.get(key, prop_def.default))
            self.mount(row)


class ClassisPane(Vertical):
    """
    Left pane: widget browser (search + categories) + Propria.
    """

    DEFAULT_CSS = """
    ClassisPane {
        width: 22;
        border-right: solid $border;
        background: $surface-darken-1;
    }
    ClassisPane #classis-header {
        background: $surface-darken-2;
        color: $warning;
        padding: 0 2;
        height: 1;
        text-style: bold;
    }
    ClassisPane #search-input {
        margin: 0 1;
    }
    ClassisPane #category-bar {
        height: 1;
        background: $surface-darken-2;
    }
    ClassisPane #category-bar Button {
        min-width: 4;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
    }
    ClassisPane #category-bar Button.active {
        color: $warning;
        text-style: bold;
    }
    ClassisPane #widget-list {
        height: 1fr;
    }
    ClassisPane .widget-item {
        height: auto;
        padding: 0 1;
        border-left: tall transparent;
    }
    ClassisPane .widget-item:hover {
        background: $surface;
    }
    ClassisPane .widget-item.disabled {
        opacity: 35%;
    }
    ClassisPane .widget-item.selected {
        border-left: tall $accent;
        background: $accent 15%;
    }
    ClassisPane .widget-item .wname {
        color: $text;
    }
    ClassisPane .widget-item .wdesc {
        color: $text-muted;
        text-style: italic;
    }
    ClassisPane .rich-badge {
        color: $secondary;
        background: $secondary 20%;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._active_cat     = "Layout"
        self._search         = ""
        self._can_add        = False
        self._selected_node: WidgetNode | None = None

    def compose(self) -> ComposeResult:
        yield Static("CLASSIS  widget registry", id="classis-header")
        yield Input(placeholder="⌕  Search…", id="search-input")
        with Horizontal(id="category-bar"):
            for i, cat in enumerate(REGISTRY.keys()):
                classes = "active" if cat == self._active_cat else ""
                yield Button(f"{cat[:4]} {i+1}", id=f"cat-{cat}", classes=classes)
        yield ScrollableContainer(id="widget-list")
        yield Propria()

    def on_mount(self) -> None:
        self._refresh_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._search = event.value.strip().lower()
            self._refresh_list()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid.startswith("cat-"):
            cat = bid[4:]
            self._active_cat = cat
            for btn in self.query("#category-bar Button"):
                btn.remove_class("active")
            event.button.add_class("active")
            self._refresh_list()

    def _refresh_list(self) -> None:
        container = self.query_one("#widget-list", ScrollableContainer)
        container.remove_children()
        if self._search:
            widgets = [w for w in FLAT_REGISTRY
                       if self._search in w.id.lower() or self._search in w.desc.lower()]
        else:
            widgets = REGISTRY.get(self._active_cat, [])

        for w in widgets:
            disabled = self._can_add is False and self._selected_node is not None
            classes  = "widget-item"
            if disabled:
                classes += " disabled"
            item = Vertical(classes=classes, id=f"wi-{w.id}")
            item.border_subtitle = w.id
            container.mount(item)

    def on_vertical_click(self, event) -> None:
        # Identify which widget-item was clicked
        node = event.widget
        while node and not (node.id or "").startswith("wi-"):
            node = node.parent
        if not node:
            return
        widget_id = (node.id or "")[3:]
        d = get_widget_def(widget_id)
        if d:
            self.post_message(WidgetSelected(d))

    def update_selection(self, node: WidgetNode | None, can_add: bool) -> None:
        """Called by the app when tree selection changes."""
        self._selected_node = node
        self._can_add       = can_add
        self._refresh_list()
        self.query_one(Propria).load_node(node)

    def set_category(self, index: int) -> None:
        cats = list(REGISTRY.keys())
        if 0 <= index < len(cats):
            self._active_cat = cats[index]
            for btn in self.query("#category-bar Button"):
                btn.remove_class("active")
            target = self.query_one(f"#cat-{cats[index]}", Button)
            target.add_class("active")
            self._refresh_list()
