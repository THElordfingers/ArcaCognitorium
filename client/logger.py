#╔══════════════════════════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    ArcaCognitorium/client/logger.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from client.config import AppConfig


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


@dataclass
class ImmutableLogger:
    cfg: AppConfig

    def log_event(self, event: Dict[str, Any]) -> None:
        if not self.cfg.logging.enabled:
            return
        path = self.cfg.storage.immutable_log_path
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def log_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        usage: Optional[dict] = None,
        extra: Optional[dict] = None,
    ) -> None:
        if not self.cfg.logging.enabled:
            return

        if role == "user" and not self.cfg.logging.log_user_messages:
            return
        if role == "assistant" and not self.cfg.logging.log_assistant_messages:
            return

        event = {
            "ts": _utc_now(),
            "type": "message",
            "conversation_id": conversation_id,
            "role": role,
            "model": model,
            "content_sha256": _sha256(content),
            "content": content,
            "usage": usage,
            "extra": extra or {},
        }
        self.log_event(event)
