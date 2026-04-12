#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      core/attachment_manager.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import uuid
from pathlib import Path

from core.session_store import Attachment, SessionStore

logger = logging.getLogger("arx.attachment_manager")

_SUMMARISE_PROMPT = (
    "Summarise the following file for use as reference context in a build session. "
    "Be concise. Preserve all key definitions, structures, class names, function "
    "signatures, and architectural decisions. Omit boilerplate."
)

# Files larger than this will not be sent for summarisation — stored raw only.
# A summary attempt on a 500KB file wastes tokens and likely truncates anyway.
_MAX_SUMMARISE_BYTES = 200_000


class AttachmentError(Exception):
    """Raised when a file cannot be read. Distinct from summarisation failure."""


class AttachmentManager:
    """
    Attaches files to a conversation or project scope.

    Summarisation via ClaudeBox is attempted synchronously — callers that
    want non-blocking attachment should run attach_file() in a QRunnable.

    Failure modes:
        - File unreadable     → raises AttachmentError; nothing stored.
        - Summarisation fails → attachment stored with summary_cache=None;
                                caller checks and may offer retry.
        - File too large      → attachment stored without summarisation;
                                summary_cache set to a size-warning string
                                so the caller knows why.
    """

    def __init__(self, store: SessionStore, box) -> None:
        """
        Parameters
        ----------
        store : SessionStore
        box   : ClaudeBox instance — synchronous send() only.
        """
        self._store = store
        self._box = box

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def attach_file(
        self,
        path: Path,
        scope: str,
        conversation_id: str | None = None,
        project_id: str | None = None,
    ) -> Attachment:
        """
        Read file, attempt summarisation, store in SQLite.

        Parameters
        ----------
        path            : Absolute path to the file.
        scope           : 'conversation' or 'project'.
        conversation_id : Required when scope='conversation'.
        project_id      : Required when scope='project'.

        Returns
        -------
        Attachment dataclass. Check .summary_cache is None to detect
        summarisation failure and offer retry to the Wizard.

        Raises
        ------
        AttachmentError : File could not be read (permissions, missing, etc.)
        ValueError      : Invalid scope or missing id for scope.
        """
        self._validate_scope(scope, conversation_id, project_id)

        try:
            full_content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AttachmentError(
                f"Cannot read file {path}: {exc}"
            ) from exc

        summary = self._summarise(path.name, full_content)

        att_id = str(uuid.uuid4())
        self._store.save_attachment(
            attachment_id=att_id,
            filename=path.name,
            full_content=full_content,
            scope=scope,
            summary_cache=summary,
            conversation_id=conversation_id,
            project_id=project_id,
        )

        # Build and return the full Attachment dataclass.
        attachments = self._store.get_attachments(
            conversation_id=conversation_id,
            project_id=project_id,
        )
        match = next((a for a in attachments if a.id == att_id), None)
        if match:
            return match

        # Fallback construct if get_attachments filtering misses it.
        from datetime import datetime, timezone
        return Attachment(
            id=att_id,
            conversation_id=conversation_id,
            project_id=project_id,
            scope=scope,
            filename=path.name,
            full_content=full_content,
            summary_cache=summary,
            attached_at=datetime.now(timezone.utc).isoformat(),
        )

    def retry_summarise(self, attachment_id: str) -> bool:
        """
        Attempt to summarise a previously unsummarised attachment.
        Returns True if successful, False if it fails again.
        Used by the retry button in ChatPane.
        """
        # Find the attachment — search all scopes.
        att = self._find_by_id(attachment_id)
        if att is None:
            logger.warning(
                "retry_summarise: attachment %r not found.", attachment_id
            )
            return False

        if att.summary_cache:
            logger.debug(
                "retry_summarise: attachment %r already has a summary.",
                attachment_id,
            )
            return True

        summary = self._summarise(att.filename, att.full_content)
        if summary is None:
            return False

        self._store.update_attachment_summary(attachment_id, summary)
        return True

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _summarise(self, filename: str, content: str) -> str | None:
        """
        Attempt summarisation. Returns summary string on success, None on
        any failure. Never raises — failure is caller's problem to surface.
        """
        byte_size = len(content.encode("utf-8"))
        if byte_size > _MAX_SUMMARISE_BYTES:
            logger.warning(
                "AttachmentManager: %s is %d bytes — skipping summarisation.",
                filename, byte_size,
            )
            # Return a canned notice rather than None so the system block
            # at least communicates why the summary is absent.
            return (
                f"(File too large for summarisation: {byte_size:,} bytes. "
                f"Content available but not injected into context.)"
            )

        try:
            prompt = f"{_SUMMARISE_PROMPT}\n\nFilename: {filename}\n\n{content}"
            response = self._box.send(prompt)
            summary = self._extract_text(response).strip()
            if not summary:
                raise ValueError("Empty summary returned.")
            logger.debug(
                "AttachmentManager: summarised %s (%d chars → %d chars)",
                filename, len(content), len(summary),
            )
            return summary
        except Exception as exc:
            logger.warning(
                "AttachmentManager: summarisation failed for %s: %s",
                filename, exc,
            )
            return None

    def _find_by_id(self, attachment_id: str) -> Attachment | None:
        """Retrieve an attachment by id regardless of scope/conversation."""
        # Fetch all — SessionStore has no get_by_id; this is acceptable
        # since attachment counts per session are small.
        all_atts = self._store.get_attachments()
        return next((a for a in all_atts if a.id == attachment_id), None)

    @staticmethod
    def _validate_scope(
        scope: str,
        conversation_id: str | None,
        project_id: str | None,
    ) -> None:
        if scope not in ("conversation", "project"):
            raise ValueError(
                f"Invalid scope {scope!r}. Must be 'conversation' or 'project'."
            )
        if scope == "conversation" and not conversation_id:
            raise ValueError(
                "conversation_id is required for scope='conversation'."
            )
        if scope == "project" and not project_id:
            raise ValueError(
                "project_id is required for scope='project'."
            )

    @staticmethod
    def _extract_text(response) -> str:
        if hasattr(response, "text"):
            return response.text or ""
        if hasattr(response, "content") and isinstance(response.content, list):
            return "".join(
                block.text for block in response.content
                if hasattr(block, "text")
            )
        return str(response)
