#╔══════════════════════════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/memory/summarizer.py
#║ ⛨
#╚═════════════════════════════════════════════════════════


from __future__ import annotations

from dataclasses import dataclass
from openai import OpenAI
from client.config import AppConfig


@dataclass
class Summarizer:
    cfg: AppConfig
    client: OpenAI

    def rollup(self, *, existing_summary: str, transcript: str) -> str:
        model = self.cfg.models.summary
        sys = (
            "You compress conversations into durable memory.\n"
            "Preserve: goals, decisions, constraints, technical details, names.\n"
            "Prefer bullet points. Avoid fluff."
        )
        user = (
            "Existing summary (may be empty):\n"
            f"{existing_summary}\n\n"
            "New transcript to merge:\n"
            f"{transcript}\n\n"
            "Return an updated concise summary."
        )
        resp = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user},
            ],
        )
        return resp.output_text.strip()
