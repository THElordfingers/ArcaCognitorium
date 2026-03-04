#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/client/reflection.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from openai import OpenAI
from client.config import AppConfig
from memory.chronicle import Chronicle


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Reflection:
    cfg: AppConfig
    client: OpenAI
    vectors: Chronicle

    turns: int = 0

    def observe(
        self,
        *,
        conversation_id: str,
        summary: str,
        last_user: str,
        last_assistant: str,
    ) -> Optional[Dict[str, Any]]:
        if not self.cfg.reflection.enabled:
            return None

        self.turns += 1
        interval = int(self.cfg.reflection.reflection_interval_turns)
        if interval <= 0 or (self.turns % interval) != 0:
            return None

        model = self.cfg.analytics.model
        max_suggestions = int(self.cfg.analytics.max_suggestions)

        prompt = (
            "You are an internal quality reviewer for a terminal GPT client.\n"
            "Given the recent exchange and the conversation summary, suggest improvements to the client.\n"
            f"Return at most {max_suggestions} bullet points.\n\n"
            f"Conversation summary:\n{summary}\n\n"
            f"Last user:\n{last_user}\n\n"
            f"Last assistant:\n{last_assistant}\n"
        )

        resp = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": "Be concrete and actionable. No fluff."},
                {"role": "user", "content": prompt},
            ],
        )
        suggestions = resp.output_text.strip()

        self.vectors.add(
            suggestions,
            metadata={"type": "self_analytics", "conversation_id": conversation_id, "ts": _utc_now()},
        )

        path = self.cfg.storage.analytics_log_path
        event = {
            "ts": _utc_now(),
            "type": "self_analytics",
            "conversation_id": conversation_id,
            "model": model,
            "suggestions": suggestions,
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event
