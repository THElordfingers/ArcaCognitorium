# GNOSIUM EXANIMA — claudebox_manager/distiller.py
# v1.0.0
"""
Conversation distillation — compresses old message tails into dense summaries.

Triggered when a session's message count exceeds the configured
threshold (default 40). Runs on a separate, lightweight ClaudeBox
instance — never the conversation box. Writes one distillation row
per run.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from ..session.store import MessageRow, SessionStore
from ..prompt.tokens import estimate_tokens

logger = logging.getLogger("gnosium.distiller")

try:
    from claudebox import ClaudeBox
except ImportError:
    ClaudeBox = None  # type: ignore


DISTILL_SYSTEM_PROMPT = """\
You are a conversation distiller. Your job is to compress the
following exchange into a dense context summary that preserves every
decision made, every position taken, every unresolved question, and
each entity's current stance. Aim for maximum information density.

Hard ceiling: 800 tokens of output. Do not exceed it. Do not add
preamble. Do not add a sign-off. Output only the compressed summary.
"""


class Distiller:
    """Owns the lightweight distillation ClaudeBox."""

    def __init__(self, api_key_env: str = "CLAUDE_API_KEY"):
        self._api_key_env = api_key_env

    def distill_if_needed(
        self,
        store: SessionStore,
        session_id: str,
        threshold: int,
    ) -> Optional[str]:
        """
        Run one distillation pass if the session has exceeded threshold.
        Returns the summary text written to the store, or None if
        nothing was done.
        """
        if ClaudeBox is None:
            logger.warning("claudebox not importable — skipping distillation")
            return None

        messages = store.load_messages(session_id)
        if len(messages) <= threshold:
            return None

        # Distill the oldest (count - threshold) messages
        overflow = len(messages) - threshold
        to_distill = messages[:overflow]
        if not to_distill:
            return None

        prompt_body = _format_for_distillation(to_distill)

        api_key = os.environ.get(self._api_key_env)
        box = ClaudeBox(api_key=api_key, system_prompt=DISTILL_SYSTEM_PROMPT)
        try:
            response = box.send(prompt_body)
            summary = getattr(response, "text", "") or ""
        except Exception as exc:
            logger.error("distillation failed: %s", exc)
            return None

        if not summary.strip():
            return None

        store.write_distillation(
            session_id=session_id,
            summary=summary,
            from_message_id=to_distill[0].id,
            to_message_id=to_distill[-1].id,
            token_estimate=estimate_tokens(summary),
        )
        return summary


def _format_for_distillation(messages: list[MessageRow]) -> str:
    lines: list[str] = []
    for m in messages:
        if m.role == "wizard":
            lines.append(f"[Wizard] {m.content}")
        else:
            tag = m.entity_id or "entity"
            lines.append(f"[{tag}] {m.content}")
    return "\n\n".join(lines)
