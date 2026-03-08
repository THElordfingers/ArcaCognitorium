#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/router.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Tuple

from claudebox import ClaudeBox
from client.config import AppConfig


@dataclass
class ModelDecision:
    model: str
    reason: str


class ModelRouter:

    def __init__(self, cfg: AppConfig, api_key: str):
        self.cfg = cfg
        self._api_key = api_key
        # One ClaudeBox instance per router — multi_session handles concurrency
        self._box = ClaudeBox(api_key=api_key, stream=True)

    # ------------------------------------------------------------------
    # Routing logic — unchanged from OpenAI version
    # ------------------------------------------------------------------

    def decide(self, user_text: str, *, forced: Optional[str] = None) -> ModelDecision:
        models = self.cfg.models
        if forced == "smart":
            return ModelDecision(model=models.smart, reason="forced smart")
        lowered = user_text.lower()
        for kw in self.cfg.routing.reasoning_keywords:
            if kw in lowered:
                return ModelDecision(model=models.smart, reason=f"keyword '{kw}'")
        if len(user_text) >= int(self.cfg.routing.long_input_threshold_chars):
            return ModelDecision(model=models.smart, reason="long input")
        default_bucket = self.cfg.routing.default
        chosen = getattr(models, default_bucket, models.fast)
        return ModelDecision(model=chosen, reason=f"default={default_bucket}")

    # ------------------------------------------------------------------
    # Streaming — same public signature as OpenAI version
    # Returns: (generator_of_str, meta_dict)
    # ------------------------------------------------------------------

    def stream_response_text(
        self,
        model: str,
        input_messages: List[Dict],
        *,
        max_output_tokens: Optional[int] = None,
        instructions: Optional[str] = None,
    ) -> Tuple[Generator[str, None, None], Dict]:

        meta: Dict = {"usage": None}

        # Collect system messages into instructions if not provided
        if instructions is None:
            system_parts = [m["content"] for m in input_messages if m.get("role") == "system"]
            if system_parts:
                instructions = "\n\n".join(system_parts)

        # ClaudeBox only accepts user/assistant roles
        filtered = [m for m in input_messages if m.get("role") in ("user", "assistant")]

        # Build a unique session for this call
        session_id = f"stream_{threading.get_ident()}_{id(meta)}"
        self._box.create_session(session_id)

        # Inject history (all messages except the final user turn)
        history = filtered[:-1]
        for msg in history:
            if msg["role"] == "user":
                self._box.conversation.add_user_message(msg["content"], session_id)
            elif msg["role"] == "assistant":
                self._box.conversation.add_assistant_message(msg["content"], session_id)

        # The final user message is the live prompt
        last_user = next(
            (m["content"] for m in reversed(filtered) if m["role"] == "user"),
            ""
        )

        # Build send kwargs
        send_kwargs: Dict = {"model": model, "session_id": session_id}
        if instructions:
            send_kwargs["system"] = instructions
        if max_output_tokens:
            send_kwargs["max_tokens"] = max_output_tokens

        def gen() -> Generator[str, None, None]:
            try:
                for token in self._box.stream(last_user, **send_kwargs):
                    yield token
                # Capture usage after stream completes
                try:
                    usage = self._box.get_token_usage(session_id)
                    meta["usage"] = usage
                except Exception:
                    pass
            finally:
                # Always clean up the session
                try:
                    self._box.delete_session(session_id)
                except Exception:
                    pass

        return gen(), meta
