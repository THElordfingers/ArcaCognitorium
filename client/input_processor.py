#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/input_processor.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedInput:
    kind: str               # "command" | "text"
    text: str
    command: Optional[str] = None
    args: Optional[str] = None


class InputProcessor:
    def parse(self, raw: str) -> ParsedInput:
        s = (raw or "").replace("\x00", "").strip()
        if not s:
            return ParsedInput(kind="text", text="")

        if s.startswith("/"):
            parts = s.split(" ", 1)
            cmd = parts[0].strip()
            args = parts[1].strip() if len(parts) > 1 else ""
            return ParsedInput(kind="command", text=s, command=cmd, args=args)

        return ParsedInput(kind="text", text=s)

