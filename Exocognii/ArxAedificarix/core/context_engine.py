#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                         core/context_engine.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
from dataclasses import dataclass, field

from core.config_loader import ConfigLoader
from core.session_store import Attachment, Conversation, SessionStore

logger = logging.getLogger("arx.context_engine")


@dataclass
class PayloadEstimate:
    system_block: str
    messages_array: list[dict]
    estimated_tokens: int
    # Convenience: flat text of all message content for external token math.
    _full_text: str = field(default="", repr=False)


class ContextEngine:
    """
    Assembles the API payload (system_block, messages_array) for each send.

    Owns no persistent state beyond references to the store and the loaded
    builder prompt. The payload is assembled fresh on every call to
    assemble_payload() — no caching, no stale mirrors.

    Compression detection is advisory: threshold_exceeded() tells the caller
    whether to trigger CompressionEngine before proceeding with the send.
    The ContextEngine itself never triggers compression.
    """

    def __init__(
        self,
        session_store: SessionStore,
        builder_prompt: str,
    ) -> None:
        self._store = session_store
        self._builder_prompt = builder_prompt

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def assemble_payload(
        self,
        conversation_id: str,
        draft_text: str = "",
    ) -> PayloadEstimate:
        """
        Produce system_block and messages_array for one API call.

        system_block composition (in order):
            1. Builder prompt (always present)
            2. Project shared_instructions (if conversation belongs to project)
            3. Project-scoped attachment summaries
            4. Conversation-scoped attachment summaries

        messages_array composition:
            - First call bootstrap: synthetic user turn seeded from
              conversation.builder_prompt + attachment references.
            - Subsequent calls: all stored messages, with compressed turns
              replaced by their archive summary (one per compression group).

        draft_text is included in token estimation only — not in the payload.
        """
        conversation = self._store.get_conversation(conversation_id)
        if conversation is None:
            raise ValueError(
                f"ContextEngine: conversation {conversation_id!r} not found."
            )

        project = None
        if conversation.project_id:
            project = self._store.get_project(conversation.project_id)

        # --- attachment collection ---
        project_attachments: list[Attachment] = []
        if project:
            project_attachments = self._store.get_attachments(
                project_id=project.id, scope="project"
            )
        conv_attachments = self._store.get_attachments(
            conversation_id=conversation_id, scope="conversation"
        )
        all_attachments = project_attachments + conv_attachments

        # --- system_block ---
        system_block = self._build_system_block(
            project_shared=project.shared_instructions if project else "",
            attachments=all_attachments,
        )

        # --- messages_array ---
        messages = self._store.get_messages(conversation_id)

        if not messages:
            bootstrap = self._build_bootstrap(conversation, all_attachments)
            messages_array = [{"role": "user", "content": bootstrap}]
        else:
            messages_array = self._build_messages_array(messages)

        # --- token estimation ---
        full_text = (
            system_block
            + " ".join(m["content"] for m in messages_array)
            + draft_text
        )
        estimated_tokens = self._estimate(full_text)

        return PayloadEstimate(
            system_block=system_block,
            messages_array=messages_array,
            estimated_tokens=estimated_tokens,
            _full_text=full_text,
        )

    def estimate_tokens(self, text: str) -> int:
        """Heuristic token estimate: word count × 1.3."""
        return self._estimate(text)

    def threshold_exceeded(self, estimated_tokens: int) -> bool:
        """
        Return True if the estimate crosses the compression trigger threshold.
        Reads live from ConfigLoader — reflects config changes at runtime.
        """
        limit = ConfigLoader.model_context_limit()
        threshold = ConfigLoader.compression_threshold()
        trigger = int(limit * threshold)
        exceeded = estimated_tokens > trigger
        if exceeded:
            logger.debug(
                "Threshold exceeded: %d tokens > %d (%.0f%% of %d)",
                estimated_tokens, trigger,
                ConfigLoader.compression_threshold() * 100,
                limit,
            )
        return exceeded

    def update_builder_prompt(self, new_prompt: str) -> None:
        """
        Hot-swap the builder prompt. Used by persona selector.
        Takes effect on the next assemble_payload() call.
        """
        self._builder_prompt = new_prompt
        logger.info("ContextEngine: builder prompt updated.")

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _build_system_block(
        self,
        project_shared: str,
        attachments: list[Attachment],
    ) -> str:
        parts: list[str] = [self._builder_prompt]

        if project_shared:
            parts.append(project_shared)

        for att in attachments:
            if att.summary_cache:
                parts.append(f"[FILE: {att.filename}]\n{att.summary_cache}")
            else:
                # Unsummarised — include filename only; do not inject raw
                # content into system block (could be arbitrarily large).
                parts.append(
                    f"[FILE: {att.filename}] (summary unavailable — "
                    f"summarisation pending or failed)"
                )

        return "\n\n".join(parts)

    def _build_messages_array(self, messages: list) -> list[dict]:
        """
        Flatten stored messages into API message dicts.
        Compressed groups are collapsed to a single assistant turn
        containing the archive summary. Each group appears exactly once,
        in the position of the first message in that group.
        """
        result: list[dict] = []
        seen_groups: set[str] = set()

        for msg in messages:
            if msg.compressed:
                gid = msg.compression_group_id
                if gid in seen_groups:
                    continue  # subsequent messages in same group — skip
                archive = self._store.get_archive(gid)
                if archive:
                    result.append({
                        "role": "assistant",
                        "content": archive.summary,
                    })
                else:
                    # Archive row missing — degrade gracefully by including
                    # the compressed message content with a marker.
                    logger.warning(
                        "No archive found for compression_group_id %r — "
                        "falling back to raw content.", gid
                    )
                    result.append({
                        "role": msg.role,
                        "content": f"[archived] {msg.content}",
                    })
                seen_groups.add(gid)
            else:
                result.append({"role": msg.role, "content": msg.content})

        return result

    def _build_bootstrap(
        self,
        conversation: Conversation,
        attachments: list[Attachment],
    ) -> str:
        """
        Synthetic first user turn for a fresh conversation.
        Injects conversation.builder_prompt and attachment references
        so The Builder has immediate context on session open.
        """
        parts: list[str] = []

        if conversation.builder_prompt:
            parts.append(conversation.builder_prompt)

        for att in attachments:
            if att.summary_cache:
                parts.append(
                    f"Reference document: {att.filename}\n{att.summary_cache}"
                )
            else:
                parts.append(
                    f"Reference document attached: {att.filename} "
                    f"(summary pending)"
                )

        return "\n\n".join(parts) if parts else "Begin."

    @staticmethod
    def _estimate(text: str) -> int:
        """Heuristic: split on whitespace, multiply by 1.3."""
        return int(len(text.split()) * 1.3)
