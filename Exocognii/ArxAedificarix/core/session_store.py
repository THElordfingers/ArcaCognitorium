#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          core/session_store.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from core.database import DatabaseManager

logger = logging.getLogger("arx.session_store")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Dataclasses — typed row representations
# ---------------------------------------------------------------------------

@dataclass
class Project:
    id: str
    name: str
    shared_instructions: str
    created_at: str


@dataclass
class Conversation:
    id: str
    project_id: str | None
    title: str
    builder_prompt: str
    created_at: str
    last_active_at: str


@dataclass
class Message:
    id: str
    conversation_id: str
    role: str
    content: str
    compressed: bool
    compression_group_id: str | None
    token_count: int
    created_at: str


@dataclass
class CompressionArchive:
    id: str
    compression_group_id: str
    original_messages: list[dict]
    summary: str
    compressed_at: str


@dataclass
class Attachment:
    id: str
    conversation_id: str | None
    project_id: str | None
    scope: str
    filename: str
    full_content: str
    summary_cache: str | None
    attached_at: str


@dataclass
class OutputFile:
    id: str
    conversation_id: str
    filename: str
    language: str
    content: str
    description: str
    export_status: str
    created_at: str


# ---------------------------------------------------------------------------
# SessionStore
# ---------------------------------------------------------------------------

class SessionStore:
    """
    Single point of database access. CRUD for all SQLite tables.
    Requires DatabaseManager.initialise() to have been called first.
    All write methods commit immediately.
    """

    def __init__(self) -> None:
        self._conn = DatabaseManager.connection()

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return DatabaseManager.execute_with_retry(sql, params)

    def _row_to_project(self, row: sqlite3.Row) -> Project:
        return Project(
            id=row["id"],
            name=row["name"],
            shared_instructions=row["shared_instructions"],
            created_at=row["created_at"],
        )

    def _row_to_conversation(self, row: sqlite3.Row) -> Conversation:
        return Conversation(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            builder_prompt=row["builder_prompt"],
            created_at=row["created_at"],
            last_active_at=row["last_active_at"],
        )

    def _row_to_message(self, row: sqlite3.Row) -> Message:
        return Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            compressed=bool(row["compressed"]),
            compression_group_id=row["compression_group_id"],
            token_count=row["token_count"],
            created_at=row["created_at"],
        )

    def _row_to_archive(self, row: sqlite3.Row) -> CompressionArchive:
        return CompressionArchive(
            id=row["id"],
            compression_group_id=row["compression_group_id"],
            original_messages=json.loads(row["original_messages"]),
            summary=row["summary"],
            compressed_at=row["compressed_at"],
        )

    def _row_to_attachment(self, row: sqlite3.Row) -> Attachment:
        return Attachment(
            id=row["id"],
            conversation_id=row["conversation_id"],
            project_id=row["project_id"],
            scope=row["scope"],
            filename=row["filename"],
            full_content=row["full_content"],
            summary_cache=row["summary_cache"],
            attached_at=row["attached_at"],
        )

    def _row_to_output_file(self, row: sqlite3.Row) -> OutputFile:
        return OutputFile(
            id=row["id"],
            conversation_id=row["conversation_id"],
            filename=row["filename"],
            language=row["language"],
            content=row["content"],
            description=row["description"],
            export_status=row["export_status"],
            created_at=row["created_at"],
        )

    # -----------------------------------------------------------------------
    # Projects
    # -----------------------------------------------------------------------

    def create_project(self, name: str, shared_instructions: str = "") -> str:
        """Insert new project row. Returns project id."""
        pid = _uuid()
        self._execute(
            """INSERT INTO projects (id, name, shared_instructions, created_at)
               VALUES (?, ?, ?, ?)""",
            (pid, name, shared_instructions, _now()),
        )
        self._conn.commit()
        logger.debug("Created project %s: %r", pid, name)
        return pid

    def get_project(self, project_id: str) -> Project | None:
        """Return Project dataclass or None if not found."""
        row = self._execute(
            "SELECT * FROM projects WHERE id=?", (project_id,)
        ).fetchone()
        return self._row_to_project(row) if row else None

    def get_all_projects(self) -> list[Project]:
        """Return all projects ordered by created_at."""
        rows = self._execute(
            "SELECT * FROM projects ORDER BY created_at"
        ).fetchall()
        return [self._row_to_project(r) for r in rows]

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        shared_instructions: str | None = None,
    ) -> None:
        """Update mutable project fields. Only provided fields are changed."""
        if name is not None:
            self._execute(
                "UPDATE projects SET name=? WHERE id=?", (name, project_id)
            )
        if shared_instructions is not None:
            self._execute(
                "UPDATE projects SET shared_instructions=? WHERE id=?",
                (shared_instructions, project_id),
            )
        self._conn.commit()

    def delete_project(self, project_id: str) -> None:
        """
        Delete project row. Conversations are SET NULL on project_id per schema.
        Attachments scoped to project are CASCADE deleted.
        """
        self._execute("DELETE FROM projects WHERE id=?", (project_id,))
        self._conn.commit()
        logger.debug("Deleted project %s", project_id)

    # -----------------------------------------------------------------------
    # Conversations
    # -----------------------------------------------------------------------

    def create_conversation(
        self,
        title: str,
        builder_prompt: str = "",
        project_id: str | None = None,
    ) -> str:
        """Insert new conversation row. Returns conversation id."""
        cid = _uuid()
        now = _now()
        self._execute(
            """INSERT INTO conversations
               (id, project_id, title, builder_prompt, created_at, last_active_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (cid, project_id, title, builder_prompt, now, now),
        )
        self._conn.commit()
        logger.debug("Created conversation %s: %r", cid, title)
        return cid

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Return Conversation dataclass or None."""
        row = self._execute(
            "SELECT * FROM conversations WHERE id=?", (conversation_id,)
        ).fetchone()
        return self._row_to_conversation(row) if row else None

    def get_all_conversations(self) -> list[Conversation]:
        """Return all conversations ordered by last_active_at descending."""
        rows = self._execute(
            "SELECT * FROM conversations ORDER BY last_active_at DESC"
        ).fetchall()
        return [self._row_to_conversation(r) for r in rows]

    def get_conversations_for_project(self, project_id: str) -> list[Conversation]:
        """Return conversations belonging to a project, newest first."""
        rows = self._execute(
            """SELECT * FROM conversations
               WHERE project_id=? ORDER BY last_active_at DESC""",
            (project_id,),
        ).fetchall()
        return [self._row_to_conversation(r) for r in rows]

    def get_ungrouped_conversations(self) -> list[Conversation]:
        """Return conversations with no project, newest first."""
        rows = self._execute(
            """SELECT * FROM conversations
               WHERE project_id IS NULL ORDER BY last_active_at DESC"""
        ).fetchall()
        return [self._row_to_conversation(r) for r in rows]

    def restore_last_active(self) -> str | None:
        """Return conversation_id with most recent last_active_at, or None."""
        row = self._execute(
            "SELECT id FROM conversations ORDER BY last_active_at DESC LIMIT 1"
        ).fetchone()
        return row["id"] if row else None

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        self._execute(
            "UPDATE conversations SET title=? WHERE id=?", (title, conversation_id)
        )
        self._conn.commit()

    def update_conversation_project(
        self, conversation_id: str, project_id: str | None
    ) -> None:
        """Reassign conversation to a different project (or ungrouped)."""
        self._execute(
            "UPDATE conversations SET project_id=? WHERE id=?",
            (project_id, conversation_id),
        )
        self._conn.commit()

    def touch_conversation(self, conversation_id: str) -> None:
        """Update last_active_at to now."""
        self._execute(
            "UPDATE conversations SET last_active_at=? WHERE id=?",
            (_now(), conversation_id),
        )
        self._conn.commit()

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete conversation and all cascading children."""
        self._execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
        self._conn.commit()
        logger.debug("Deleted conversation %s", conversation_id)

    # -----------------------------------------------------------------------
    # Messages
    # -----------------------------------------------------------------------

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        token_count: int = 0,
    ) -> str:
        """Insert message row; touch conversation. Returns message id."""
        mid = _uuid()
        now = _now()
        self._execute(
            """INSERT INTO messages
               (id, conversation_id, role, content, token_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (mid, conversation_id, role, content, token_count, now),
        )
        self._execute(
            "UPDATE conversations SET last_active_at=? WHERE id=?",
            (now, conversation_id),
        )
        self._conn.commit()
        return mid

    def get_messages(self, conversation_id: str) -> list[Message]:
        """Return all messages for conversation ordered by created_at."""
        rows = self._execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    def get_uncompressed_messages(
        self, conversation_id: str, limit: int | None = None
    ) -> list[Message]:
        """
        Return uncompressed messages in created_at order.
        If limit is provided, returns oldest N uncompressed messages.
        """
        sql = """SELECT * FROM messages
                 WHERE conversation_id=? AND compressed=0
                 ORDER BY created_at"""
        params: tuple[Any, ...] = (conversation_id,)
        if limit is not None:
            sql += " LIMIT ?"
            params = (conversation_id, limit)
        rows = self._execute(sql, params).fetchall()
        return [self._row_to_message(r) for r in rows]

    def update_message_token_count(self, msg_id: str, count: int) -> None:
        """Update token_count on a message row post-response."""
        self._execute(
            "UPDATE messages SET token_count=? WHERE id=?", (count, msg_id)
        )
        self._conn.commit()

    def mark_messages_compressed(
        self, message_ids: list[str], compression_group_id: str
    ) -> None:
        """Mark a batch of messages as compressed with a shared group id."""
        for mid in message_ids:
            self._execute(
                """UPDATE messages
                   SET compressed=1, compression_group_id=?
                   WHERE id=?""",
                (compression_group_id, mid),
            )
        self._conn.commit()

    # -----------------------------------------------------------------------
    # Compression Archive
    # -----------------------------------------------------------------------

    def write_compression_archive(
        self,
        compression_group_id: str,
        original_messages: list[dict],
        summary: str,
        compressed_at: str,
    ) -> str:
        """Insert compression_archive row. Returns archive id."""
        aid = _uuid()
        self._execute(
            """INSERT INTO compression_archive
               (id, compression_group_id, original_messages, summary, compressed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                aid,
                compression_group_id,
                json.dumps(original_messages),
                summary,
                compressed_at,
            ),
        )
        self._conn.commit()
        return aid

    def get_archive(self, compression_group_id: str) -> CompressionArchive | None:
        """Return CompressionArchive for a group id, or None."""
        row = self._execute(
            "SELECT * FROM compression_archive WHERE compression_group_id=?",
            (compression_group_id,),
        ).fetchone()
        return self._row_to_archive(row) if row else None

    # -----------------------------------------------------------------------
    # Attachments
    # -----------------------------------------------------------------------

    def save_attachment(
        self,
        attachment_id: str,
        filename: str,
        full_content: str,
        scope: str,
        summary_cache: str | None,
        conversation_id: str | None,
        project_id: str | None,
    ) -> None:
        """Insert attachment row."""
        self._execute(
            """INSERT INTO attachments
               (id, conversation_id, project_id, scope, filename,
                full_content, summary_cache, attached_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                attachment_id,
                conversation_id,
                project_id,
                scope,
                filename,
                full_content,
                summary_cache,
                _now(),
            ),
        )
        self._conn.commit()

    def get_attachments(
        self,
        conversation_id: str | None = None,
        project_id: str | None = None,
        scope: str | None = None,
    ) -> list[Attachment]:
        """
        Return attachments filtered by any combination of conversation_id,
        project_id, and scope. All provided filters are AND-combined.
        """
        conditions: list[str] = []
        params: list[Any] = []

        if conversation_id is not None:
            conditions.append("conversation_id=?")
            params.append(conversation_id)
        if project_id is not None:
            conditions.append("project_id=?")
            params.append(project_id)
        if scope is not None:
            conditions.append("scope=?")
            params.append(scope)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = self._execute(
            f"SELECT * FROM attachments {where} ORDER BY attached_at",
            tuple(params),
        ).fetchall()
        return [self._row_to_attachment(r) for r in rows]

    def update_attachment_summary(
        self, attachment_id: str, summary: str
    ) -> None:
        """Write summarisation result to summary_cache after async success."""
        self._execute(
            "UPDATE attachments SET summary_cache=? WHERE id=?",
            (summary, attachment_id),
        )
        self._conn.commit()

    def delete_attachment(self, attachment_id: str) -> None:
        self._execute("DELETE FROM attachments WHERE id=?", (attachment_id,))
        self._conn.commit()

    # -----------------------------------------------------------------------
    # Output Files
    # -----------------------------------------------------------------------

    def save_output_file(
        self,
        conversation_id: str,
        filename: str,
        language: str,
        content: str,
        description: str = "",
    ) -> str:
        """Insert output_files row. Returns file id."""
        fid = _uuid()
        self._execute(
            """INSERT INTO output_files
               (id, conversation_id, filename, language, content,
                description, export_status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (fid, conversation_id, filename, language, content, description, _now()),
        )
        self._conn.commit()
        return fid

    def get_output_files(self, conversation_id: str) -> list[OutputFile]:
        """Return all output files for a conversation ordered by created_at."""
        rows = self._execute(
            "SELECT * FROM output_files WHERE conversation_id=? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
        return [self._row_to_output_file(r) for r in rows]

    def mark_files_exported(self, file_ids: list[str]) -> None:
        """Set export_status='exported' for a batch of file ids."""
        for fid in file_ids:
            self._execute(
                "UPDATE output_files SET export_status='exported' WHERE id=?",
                (fid,),
            )
        self._conn.commit()
