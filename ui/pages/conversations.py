#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/pages/conversations.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════



from __future__ import annotations
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Vertical
from memory.conversation_store import ConversationStore





class ConversationsPage(Screen):
    """Conversation browser. Lists all past Threads with metadata."""

    def __init__(self, store: ConversationStore) -> None:
        super().__init__()
        self.store = store

    def compose(self) -> ComposeResult:
        yield Label('◆  CONVERSATIONS  ◆', id='convpage-title')
        convos = self.store.list()
        if not convos:
            yield Static('(no conversations yet)', classes='convpage-empty')
            return
        with ListView(id='convpage-list'):
            for c in convos:
                title = c.get('title') or '(untitled)'
                updated = c.get('updated_at', '')[:16] or '—'
                cid = c.get('id', '')
                yield ListItem(
                    Label(f'{title}  [{updated}]'),
                    id=f'conv__{cid}'
                )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ''
        if not item_id.startswith('conv__'):
            return
        cid = item_id[6:]
        self.dismiss(cid)
