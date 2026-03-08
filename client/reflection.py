#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/reflection.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING

from client.config import AppConfig
from memory.chronicle import Chronicle

if TYPE_CHECKING:
    from claudebox import ClaudeBox


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Reflection:
    cfg: AppConfig
    box: "ClaudeBox"
    chronicle: Chronicle
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

        model = self.cfg.reflection.model
        max_suggestions = int(self.cfg.reflection.max_suggestions)

        prompt = (
            "You are an internal quality reviewer for a terminal AI client.\n"
            "Given the recent exchange and the conversation summary, suggest improvements to the client.\n"
            f"Return at most {max_suggestions} bullet points.\n\n"
            f"Conversation summary:\n{summary}\n\n"
            f"Last user:\n{last_user}\n\n"
            f"Last assistant:\n{last_assistant}\n"
        )

        response = self.box.send(
            prompt,
            model=model,
            system="Be concrete and actionable. No fluff.",
            stream=False,
        )

        suggestions = response.text.strip()

        self.chronicle.add(
            suggestions,
            metadata={
                "type": "self_analytics",
                "conversation_id": conversation_id,
                "ts": _utc_now(),
            },
        )

        path = self.cfg.storage.reflection_log_path
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

    def extract_routing_signals(self, messages: list[dict]) -> dict:
        user_messages = [m for m in messages if m.get("role") == "user"]
        all_content = " ".join(m.get("content", "") for m in user_messages)

        stopwords = {
            "the", "a", "an", "is", "it", "i", "to", "of", "in", "for",
            "that", "this", "and", "or", "but", "with", "be", "was", "are",
        }
        words = [
            w.lower() for w in re.findall(r"\b\w{4,}\b", all_content)
            if w.lower() not in stopwords
        ]
        top_topics = [w for w, _ in Counter(words).most_common(3)]

        signals = {
            "timestamp": _utc_now(),
            "dominant_topics": top_topics,
            "message_length_avg": (
                sum(len(m.get("content", "").split()) for m in user_messages)
                / max(len(user_messages), 1)
            ),
            "code_present": bool(re.search(r"```|def |class |import ", all_content)),
            "question_count": sum(
                1 for m in user_messages if m.get("content", "").rstrip().endswith("?")
            ),
            "turn_count": len(messages),
        }

        from pathlib import Path
        log_path = Path(self.cfg.storage.reflection_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(json.dumps(signals) + "\n")

        return signals
