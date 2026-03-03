#╔══════════════════════════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/client/renderer.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.table import Table

from client.config import AppConfig


@dataclass
class RenderContext:
    model: Optional[str] = None


class Renderer:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.console = Console()

    def _ts(self) -> str:
        if not self.cfg.ui.show_timestamps:
            return ""
        if self.cfg.app.timezone == "utc":
            return datetime.utcnow().strftime("%H:%M:%S UTC")
        return datetime.now().strftime("%H:%M:%S")

    def banner(self):
        name = self.cfg.app.name
        version = self.cfg.app.version
        help_line = "Commands: /help  /menu  /new  /load <id>  /remember <txt>  /vquery <txt>  /vdump  /exit"
        title = f"{name} v{version}"

        self.console.print(Panel.fit(
            Text(f"{title}\n{help_line}", style=self.cfg.ui.text.system_style),
            border_style=self.cfg.ui.panel.border_style_system,
            title="System",
            title_align="left",
        ))

    def help(self):
                lines = [
                    "/help                   Show help",
                    "/menu                   List & select conversations",
                    "/new                    Start a new conversation",
                    "/load <id>              Load a conversation by id",
                    "/remember <text>        Add a note to long-term memory (vector store)",
                    "/vaddfile <path>        Ingest a local text file into vector memory",
                    "/vadddir <path>         Ingest a directory of text files into vector memory",
                    "/vquery <text>          Query long-term memory (vector store)",
                    "/vdump                  Dump vector store stats",
                    "/smart                  Force next turn to use smart model",
                    "/exit                   Quit",
                ]
                self.console.print(Panel(
                    Text("\n".join(lines), style=self.cfg.ui.text.system_style),
                    border_style=self.cfg.ui.panel.border_style_system,
                    title="Help",
                    title_align="left",

        ))

    def system(self, message: str):
        self.console.print(Panel(
            Text(message, style=self.cfg.ui.text.system_style),
            border_style=self.cfg.ui.panel.border_style_system,
            title=f"System {self._ts()}".strip(),
            title_align="left",
        ))

    def error(self, message: str):
        self.console.print(Panel(
            Text(message, style=self.cfg.ui.text.system_style),
            border_style=self.cfg.ui.panel.border_style_error,
            title=f"Error {self._ts()}".strip(),
            title_align="left",
        ))

    def user(self, message: str):
        self.console.print(Panel(
            Text(message, style=self.cfg.ui.text.user_style),
            border_style=self.cfg.ui.panel.border_style_user,
            title=f"You {self._ts()}".strip(),
            title_align="left",
        ))

    def assistant_stream(self, title: str = "Assistant"):
        """
        Returns a (update_fn, close_fn) pair.
        update_fn(delta_text) appends to the panel.
        close_fn() stops Live and returns full text.
        """
        style = self.cfg.ui.text.assistant_style
        border = self.cfg.ui.panel.border_style_assistant

        full = Text("", style=style)

        panel = Panel(
            full,
            border_style=border,
            title=title,
            title_align="left",
        )

        live = Live(panel, console=self.console, refresh_per_second=24, transient=False)
        live.start()

        def update(delta: str):
            full.append(delta)
            live.update(Panel(full, border_style=border, title=title, title_align="left"))

        def close() -> str:
            live.stop()
            return full.plain

        return update, close

    def menu(self, conversations: list[dict], active_id: str):
        """
        Renders a two-column menu: left list, right instructions.
        """
        max_items = int(self.cfg.ui.menu.max_items)

        table = Table(show_header=True, header_style=self.cfg.ui.text.system_style, expand=True)
        table.add_column("ID", style=self.cfg.ui.text.dim_style, width=14, overflow="fold")
        table.add_column("Title", overflow="fold")
        table.add_column("Updated", style=self.cfg.ui.text.dim_style, width=20)

        for c in conversations[:max_items]:
            is_active = (c["id"] == active_id)
            title = c.get("title") or "(untitled)"
            updated = c.get("updated_at", "")
            if is_active:
                title = f"[{self.cfg.ui.text.user_style}]* {title}[/]"
            table.add_row(c["id"], title, updated)

        right = Text(
            "Type an ID to load it, or press Enter to cancel.\n"
            "Tip: use /new to start a fresh conversation.",
            style=self.cfg.ui.text.system_style,
        )

        layout = Layout()
        layout.split_row(
            Layout(Panel(table, border_style=self.cfg.ui.panel.border_style_system, title="Conversations"), ratio=2),
            Layout(Panel(right, border_style=self.cfg.ui.panel.border_style_system, title="Instructions"), ratio=1),
        )
        self.console.print(layout)
