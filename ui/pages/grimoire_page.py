#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/pages/grimoire_page.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (DataTable, Label, Button,
                             Input, Select, Footer)
from textual.containers import Horizontal, Vertical, ScrollableContainer
from memory.grimoire import Grimoire, GrimoireEntry


class GrimoirePage(Screen):
    """
    Grimoire management TUI.
    Shows all entries (active + inactive) in a DataTable.
    Provides add, remove, restore, edit controls.
    Token budget bar shows current Grimoire fill.
    """

    BINDINGS = [
        ("a", "add_entry", "Add"),
        ("d", "remove_entry", "Remove"),
        ("r", "restore_entry", "Restore"),
        ("e", "edit_entry", "Edit"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """
        Layout:
          Top: Title label + token budget bar
          Middle: DataTable (entry_id | active | category | content | source | created)
          Bottom: Action buttons (Add / Remove / Restore / Edit) + Back
        """
        usage = self.app.grimoire.token_usage()
        yield Label(
            f"◆  GRIMOIRE  —  {usage['used']}/{usage['budget']} tokens  ({usage['pct']}%)",
            id="grimoire-title"
        )
        yield self._build_token_bar(usage["pct"])
        yield DataTable(id="grimoire-table")
        with Horizontal(id="grimoire-actions"):
            yield Button("Add [a]",     id="btn-add",     variant="primary")
            yield Button("Remove [d]",  id="btn-remove",  variant="warning")
            yield Button("Restore [r]", id="btn-restore", variant="default")
            yield Button("Edit [e]",    id="btn-edit",    variant="default")
            yield Button("Back [esc]",  id="btn-back",    variant="default")

    def on_mount(self) -> None:
        """Populate DataTable with all Grimoire entries on page load."""
        table = self.query_one("#grimoire-table", DataTable)
        table.add_columns("ID", "●", "Category", "Content", "Source", "Created")
        for entry in self.app.grimoire.get_all():
            table.add_row(
                entry.entry_id,
                "✓" if entry.active else "✗",
                entry.category,
                entry.content[:60] + "..." if len(entry.content) > 60 else entry.content,
                entry.source,
                entry.created_at[:10]
            )

    def action_add_entry(self) -> None:
        self.app.push_screen(AddEntryModal(), self._on_entry_added)

    def _on_entry_added(self, result: tuple[str, str] | None) -> None:
        if not result:
            return
        content, category = result
        self.app.grimoire.add(content, category)
        self._refresh_table()

    def action_remove_entry(self) -> None:
        table = self.query_one("#grimoire-table", DataTable)
        if table.cursor_row is None:
            return
        row = table.get_row_at(table.cursor_row)
        entry_id = str(row[0])
        self.app.grimoire.remove(entry_id)
        self._refresh_table()

    def action_restore_entry(self) -> None:
        table = self.query_one("#grimoire-table", DataTable)
        if table.cursor_row is None:
            return
        row = table.get_row_at(table.cursor_row)
        entry_id = str(row[0])
        self.app.grimoire.restore(entry_id)
        self._refresh_table()

    def action_edit_entry(self) -> None:
        table = self.query_one("#grimoire-table", DataTable)
        if table.cursor_row is None:
            return
        row = table.get_row_at(table.cursor_row)
        entry_id = str(row[0])
        entry = next((e for e in self.app.grimoire.get_all() if e.entry_id == entry_id), None)
        if not entry:
            return
        self.app.push_screen(EditEntryModal(entry_id, entry.content), self._on_entry_edited)

    def _on_entry_edited(self, result: tuple[str, str] | None) -> None:
        if not result:
            return
        entry_id, new_content = result
        self.app.grimoire.edit(entry_id, new_content)
        self._refresh_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add":
            self.action_add_entry()
        elif event.button.id == "btn-remove":
            self.action_remove_entry()
        elif event.button.id == "btn-restore":
            self.action_restore_entry()
        elif event.button.id == "btn-edit":
            self.action_edit_entry()
        elif event.button.id == "btn-back":
            self.app.pop_screen()

    def _refresh_table(self) -> None:
        table = self.query_one("#grimoire-table", DataTable)
        table.clear()
        for entry in self.app.grimoire.get_all():
            table.add_row(
                entry.entry_id,
                "✓" if entry.active else "✗",
                entry.category,
                entry.content[:60] + "..." if len(entry.content) > 60 else entry.content,
                entry.source,
                entry.created_at[:10]
            )
        usage = self.app.grimoire.token_usage()
        self.query_one("#grimoire-title", Label).update(
            f"◆ GRIMOIRE — {usage['used']}/{usage['budget']} tokens ({usage['pct']}%)"
        )
        filled = round(usage['pct'] / 100 * 16)
        bar = "▓" * filled + "░" * (16 - filled)
        self.query_one("#grimoire-token-bar", Label).update(bar)


class AddEntryModal(Screen):
    def compose(self) -> ComposeResult:
        yield Label("◆ ADD GRIMOIRE ENTRY", id="modal-title")
        yield Input(placeholder="Category (e.g. communication_style)", id="modal-category")
        yield Input(placeholder="Content", id="modal-content")
        with Horizontal():
            yield Button("Add", id="modal-confirm", variant="primary")
            yield Button("Cancel", id="modal-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "modal-confirm":
            content = self.query_one("#modal-content", Input).value.strip()
            category = self.query_one("#modal-category", Input).value.strip() or "general"
            if content:
                self.dismiss((content, category))
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)


class EditEntryModal(Screen):
    def __init__(self, entry_id: str, current_content: str) -> None:
        super().__init__()
        self.entry_id = entry_id
        self.current_content = current_content

    def compose(self) -> ComposeResult:
        yield Label(f"◆ EDIT ENTRY — {self.entry_id}", id="modal-title")
        yield Input(value=self.current_content, id="modal-content")
        with Horizontal():
            yield Button("Save", id="modal-confirm", variant="primary")
            yield Button("Cancel", id="modal-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "modal-confirm":
            new_content = self.query_one("#modal-content", Input).value.strip()
            if new_content:
                self.dismiss((self.entry_id, new_content))
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)
