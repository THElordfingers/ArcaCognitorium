#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      core/compression_engine.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from core.config_loader import ConfigLoader
from core.session_store import SessionStore

logger = logging.getLogger("arx.compression_engine")

_COMPRESSION_PROMPT = (
    "Summarise the following conversation turns into a compact context block. "
    "Preserve all decisions made, files referenced, code structures agreed upon, "
    "and current build state. Do not editorialize. Be dense and complete.\n"
    "Output format: SUMMARY BLOCK — [date range] — [content]"
)


class CompressionError(RuntimeError):
    """Raised when compression cannot proceed. Caller skips and logs."""


@dataclass
class CompressionRecord:
    compression_group_id: str
    summary: str
    archived_message_ids: list[str]
    archived_count: int


class CompressionEngine:
    """
    Summarises the oldest N uncompressed conversation turns via a
    synchronous ClaudeBox call, then archives the originals in SQLite.

    MUST only be called from a background thread (QRunnable / worker).
    The synchronous box.send() will block — calling from the main thread
    will freeze the UI.

    The ClaudeBox instance passed in should be a dedicated compression
    box, not the primary streaming box, to avoid session contamination.
    It is constructed with no session_id — each compression call is
    stateless from ClaudeBox's perspective.
    """

    def __init__(self, store: SessionStore, box) -> None:
        """
        Parameters
        ----------
        store : SessionStore
        box   : ClaudeBox instance — synchronous send() only; no streaming.
        """
        self._store = store
        self._box = box

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def trigger(self, conversation_id: str) -> CompressionRecord:
        """
        Compress the oldest N uncompressed turns for the conversation.

        Steps:
            1. Fetch oldest N uncompressed messages from SQLite.
            2. Build compression prompt with turn content.
            3. Call box.send() synchronously (caller is on worker thread).
            4. Write compression_archive row.
            5. Mark source messages as compressed.
            6. Return CompressionRecord with summary and archived ids.

        Raises CompressionError if:
            - No uncompressed messages exist (nothing to do).
            - box.send() raises (API/network failure).
            - SQLite write fails after successful API call (critical — logged).
        """
        batch_size = ConfigLoader.compression_batch_size()

        messages = self._store.get_uncompressed_messages(
            conversation_id, limit=batch_size
        )
        if not messages:
            raise CompressionError(
                f"No uncompressed messages to compress in conversation "
                f"{conversation_id!r}."
            )

        logger.info(
            "CompressionEngine: compressing %d messages in conversation %s",
            len(messages), conversation_id,
        )

        turns_text = "\n".join(
            f"[{m.role.upper()}]: {m.content}" for m in messages
        )
        prompt_content = f"{_COMPRESSION_PROMPT}\n\n{turns_text}"

        # Synchronous call — already on worker thread.
        try:
            response = self._box.send(prompt_content)
            summary = self._extract_text(response).strip()
            if not summary:
                raise CompressionError(
                    "CompressionEngine: API returned empty summary."
                )
        except CompressionError:
            raise
        except Exception as exc:
            raise CompressionError(
                f"CompressionEngine: box.send() failed: {exc}"
            ) from exc

        group_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Write archive and mark messages — both must succeed.
        try:
            self._store.write_compression_archive(
                compression_group_id=group_id,
                original_messages=[
                    {"role": m.role, "content": m.content} for m in messages
                ],
                summary=summary,
                compressed_at=now,
            )
            self._store.mark_messages_compressed(
                message_ids=[m.id for m in messages],
                compression_group_id=group_id,
            )
        except Exception as exc:
            # Archive write failed after successful API call — this is bad.
            # Log critical. The messages remain uncompressed, so the next
            # trigger attempt will re-compress the same turns. Non-fatal
            # to the session, but the summary is lost.
            logger.critical(
                "CompressionEngine: SQLite write failed after successful "
                "API call. group_id=%s error=%s — summary lost.", group_id, exc
            )
            raise CompressionError(
                f"CompressionEngine: archive write failed: {exc}"
            ) from exc

        logger.info(
            "CompressionEngine: %d messages archived under group %s",
            len(messages), group_id,
        )

        return CompressionRecord(
            compression_group_id=group_id,
            summary=summary,
            archived_message_ids=[m.id for m in messages],
            archived_count=len(messages),
        )

    def summary_preview(self, record: CompressionRecord, max_chars: int = 120) -> str:
        """
        Return a truncated preview of the compression summary for the
        ChatPane compression notice. Strips the SUMMARY BLOCK header if present.
        """
        text = record.summary
        # Strip leading "SUMMARY BLOCK — [date range] — " if present
        if text.startswith("SUMMARY BLOCK"):
            parts = text.split("—", 2)
            text = parts[-1].strip() if len(parts) == 3 else text
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "…"
        return text

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_text(response) -> str:
        """
        Extract text from a ClaudeBox response object.
        Handles both .text attribute and content block list patterns.
        """
        if hasattr(response, "text"):
            return response.text or ""
        # Fallback: content block list (raw API response shape)
        if hasattr(response, "content") and isinstance(response.content, list):
            return "".join(
                block.text
                for block in response.content
                if hasattr(block, "text")
            )
        return str(response)
