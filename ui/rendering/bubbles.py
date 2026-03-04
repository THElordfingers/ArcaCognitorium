#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/rendering/bubbles.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════



from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Horizontal
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from dataclasses import dataclass
from ui.state import BubbleMessage


class WizardBubble(Widget):
    """Right-aligned bubble for Wizard input.
    Parchment background (#D4C8A8 tint). No header bar. Heavier visual weight.
    Width: 70% of pane. Aligned: right.
    """
    def __init__(self, message: BubbleMessage) -> None:
        super().__init__()
        self.message = message

    def render(self) -> Panel:
        content = Text(self.message.content, style="color(#D4C8A8)")
        return Panel(
            content,
            border_style="dim #B8860B",
            subtitle=Text(self.message.timestamp, style="#5A6070"),
            padding=(0, 1),
        )


class LuminariousBubble(Widget):
    """Left-aligned bubble for Luminarious and all Entity responses.
    Header bar in speaker color. Background tint at 10% opacity of speaker color.
    Supports streaming — content updates reactively as chunks arrive.
    """
    def __init__(self, message: BubbleMessage) -> None:
        super().__init__()
        self.message = message
        self._content = message.content

    def append_chunk(self, chunk: str) -> None:
        """Append streaming chunk to content. Triggers reactive re-render."""
        self._content += chunk
        self.refresh()

    def render(self) -> Panel:
        title = Text()
        title.append(self.message.display_name, style=f"bold #{self.message.color_hex}")
        title.append(f" ◆ {self.message.model_id} ◆ {self.message.timestamp}", style=f"#{self.message.color_hex}")
        if self.message.uninvited:
            title.append(" ↯", style=f"#{self.message.color_hex}")

        subtitle = None
        if self.message.chronicle_hit:
            subtitle = Text("✦", style=f"#{self.message.color_hex}")

        content = Text(self._content, style="#D4C8A8")
        return Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=f"#{self.message.color_hex}",
            padding=(0, 1),
        )


class BubbleFactory:
    """Creates the appropriate bubble widget for a given BubbleMessage."""

    @staticmethod
    def create(message: BubbleMessage) -> Widget:
        """
        Return WizardBubble if message.speaker_id == 'wizard'.
        Return LuminariousBubble for all other speakers.
        The LuminariousBubble handles both Luminarious and Entity responses —
        the speaker color in BubbleMessage determines the visual identity.
        """
        if message.speaker_id == 'wizard':
            return WizardBubble(message)
        return LuminariousBubble(message)
