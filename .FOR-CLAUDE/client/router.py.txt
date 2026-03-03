#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/client/router.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Tuple

from openai import OpenAI
from client.config import AppConfig


@dataclass
class ModelDecision:
    model: str
    reason: str


class ModelRouter:
    def __init__(self, cfg: AppConfig, api_key: str):
        self.cfg = cfg
        self.client = OpenAI(api_key=api_key)

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

    def stream_response_text(
        self,
        model: str,
        input_messages: List[Dict],
        *,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Tuple[Generator[str, None, None], Dict]:
        meta: Dict = {"usage": None}

        stream = self.client.responses.create(
            model=model,
            input=input_messages,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            stream=True,
        )

        def gen() -> Generator[str, None, None]:
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
                elif event.type == "response.completed":
                    # best effort; usage shapes vary by SDK version
                    try:
                        meta["usage"] = getattr(event, "response", None).usage
                    except Exception:
                        pass
                    break
                elif event.type == "response.error":
                    raise RuntimeError(getattr(event, "error", "Unknown streaming error"))

        return gen(), meta
