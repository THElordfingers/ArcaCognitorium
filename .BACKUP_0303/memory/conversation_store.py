#╔═══════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/memory/conversation_store.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import copy
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from client.config import AppConfig
from client.migrations import ConversationMigrator
from memory.summarizer import Summarizer


def _now_local() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _conv_path(cfg: AppConfig, conv_id: str) -> str:
    return os.path.join(cfg.storage.conversations_dir, f"{conv_id}.json")


@dataclass
class Thread:
    id: str
    name: str
    created_at: str
    updated_at: str
    summary: str
    messages: List[Dict[str, Any]]  # {role, content, ts, model?, routing_reason?}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "summary": self.summary,
            "messages": self.messages,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Thread":
        return Thread(
            id=str(d.get("id", "main")),
            name=str(d.get("name", d.get("id", "main"))),
            created_at=str(d.get("created_at", "")),
            updated_at=str(d.get("updated_at", "")),
            summary=str(d.get("summary", "")),
            messages=list(d.get("messages", []) or []),
        )


@dataclass
class Conversation:
    id: str
    title: str
    created_at: str
    updated_at: str
    active_thread_id: str
    threads: List[Thread]
    schema_version: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active_thread_id": self.active_thread_id,
            "threads": [t.to_dict() for t in self.threads],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Conversation":
        # Accept already-migrated
        if isinstance(d.get("threads"), list):
            threads = [Thread.from_dict(x) for x in (d.get("threads") or [])]
            active = str(d.get("active_thread_id") or "main")

            if not threads:
                now = _now_local()
                threads = [
                    Thread(
                        id="main",
                        name="main",
                        created_at=str(d.get("created_at", now)),
                        updated_at=str(d.get("updated_at", now)),
                        summary="",
                        messages=[],
                    )
                ]
                active = "main"

            if not any(t.id == active for t in threads):
                active = "main" if any(t.id == "main" for t in threads) else threads[0].id

            return Conversation(
                id=str(d.get("id", "")),
                title=str(d.get("title", "")),
                created_at=str(d.get("created_at", "")),
                updated_at=str(d.get("updated_at", "")),
                active_thread_id=active,
                threads=threads,
                schema_version=int(d.get("schema_version", 2) or 2),
            )

        # Accept legacy in-memory mapping (should be migrated on disk on startup)
        summary = str(d.get("summary", "") or "")
        messages = list(d.get("messages", []) or [])
        now = _now_local()
        return Conversation(
            id=str(d.get("id", "")),
            title=str(d.get("title", "")),
            created_at=str(d.get("created_at", now)),
            updated_at=str(d.get("updated_at", now)),
            active_thread_id="main",
            threads=[
                Thread(
                    id="main",
                    name="main",
                    created_at=str(d.get("created_at", now)),
                    updated_at=str(d.get("updated_at", now)),
                    summary=summary,
                    messages=messages,
                )
            ],
            schema_version=2,
        )


class ConversationStore:
    """
    Phase 3:
      - Conversations contain multiple threads (tabs).
      - Only one thread is active at a time.
      - Append/write goes to active thread (or specified thread_id).

    LF rules preserved:
      - Do not auto-create a conversation on startup.
      - active may be None until user /new or /load.
    """

    def __init__(self, cfg: AppConfig, summarizer: Summarizer):
        self.cfg = cfg
        self.summarizer = summarizer
        self.active: Optional[Conversation] = None

    # -------------------------
    # Migration
    # -------------------------
    def migrate_all_if_needed(self) -> Tuple[int, Optional[str]]:
        migrator = ConversationMigrator(self.cfg.storage.conversations_dir)
        res = migrator.migrate_all_if_needed()
        return res.migrated_count, res.backup_dir

    # -------------------------
    # Active / threads
    # -------------------------
    def has_active(self) -> bool:
        return self.active is not None

    def active_thread_id(self) -> Optional[str]:
        return self.active.active_thread_id if self.active else None

    def threads(self) -> List[Thread]:
        return list(self.active.threads) if self.active else []

    def get_thread(self, thread_id: Optional[str] = None) -> Thread:
        if self.active is None:
            raise RuntimeError("No active conversation loaded.")
        tid = (thread_id or self.active.active_thread_id or "main").strip() or "main"
        for t in self.active.threads:
            if t.id == tid:
                return t
        # Ensure main exists as a fallback
        if tid != "main":
            return self.get_thread("main")
        main = Thread(id="main", name="main", created_at=_now_local(), updated_at=_now_local(), summary="", messages=[])
        self.active.threads.insert(0, main)
        self.active.active_thread_id = "main"
        self.save()
        return main

    def set_active_thread(self, thread_id: str) -> None:
        if self.active is None:
            raise RuntimeError("No active conversation loaded.")
        tid = (thread_id or "").strip()
        if not tid:
            return
        if not any(t.id == tid for t in self.active.threads):
            raise ValueError("No such thread.")
        self.active.active_thread_id = tid
        self.save()

    def rename_thread(self, thread_id: str, new_name: str) -> None:
        if self.active is None:
            raise RuntimeError("No active conversation loaded.")
        tid = (thread_id or "").strip()
        name = (new_name or "").strip()
        if not tid or not name:
            raise ValueError("Thread id and name required.")
        for t in self.active.threads:
            if t.id == tid:
                t.name = name
                t.updated_at = _now_local()
                self.save()
                return
        raise ValueError("No such thread.")

    def delete_thread(self, thread_id: str) -> None:
        """
        Delete a non-main thread.

        LF rule:
          - When deleting a branch, ALWAYS switch to main.

        Safety:
          - Cannot delete main.
          - After deletion, active_thread_id == "main".
        """
        if self.active is None:
            raise RuntimeError("No active conversation loaded.")

        tid = (thread_id or "").strip()
        if not tid:
            raise ValueError("Thread id required.")
        if tid == "main":
            raise ValueError("Cannot delete 'main' thread.")

        # Ensure main exists
        _ = self.get_thread("main")

        if not any(t.id == tid for t in self.active.threads):
            raise ValueError("No such thread.")

        # Always switch to main (even if deleting an inactive thread)
        self.active.active_thread_id = "main"

        # Remove thread
        self.active.threads = [t for t in self.active.threads if t.id != tid]

        # Touch timestamps
        now = _now_local()
        self.active.updated_at = now
        main = self.get_thread("main")
        main.updated_at = now

        self.save()

    def _next_branch_display_name(self) -> str:
        if self.active is None:
            stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            return f"branch-1-{stamp}"

        n = 0
        for t in self.active.threads:
            if t.id == "main":
                continue
            if (t.name or "").strip().lower().startswith("branch-"):
                n += 1
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return f"branch-{n+1}-{stamp}"

    def branch_from_assistant_turn(self, turn_index: Optional[int] = None, *, last: bool = False) -> Thread:
        """
        Branch from the Nth assistant message in the active thread (1-based), or last assistant message.

        Copies messages from start through that assistant message (inclusive) into a new thread.
        """
        src = self.get_thread()
        assistant_positions = [i for i, m in enumerate(src.messages) if (m.get("role") == "assistant")]

        if not assistant_positions:
            raise ValueError("No assistant turns available to branch from.")

        if last:
            cut_i = assistant_positions[-1]
        else:
            if turn_index is None or turn_index < 1 or turn_index > len(assistant_positions):
                raise ValueError(f"Turn index out of range. Available assistant turns: 1..{len(assistant_positions)}")
            cut_i = assistant_positions[turn_index - 1]

        copied_messages = copy.deepcopy(src.messages[: cut_i + 1])

        now = _now_local()
        tid = uuid.uuid4().hex[:12]
        name = self._next_branch_display_name()

        t = Thread(
            id=tid,
            name=name,
            created_at=now,
            updated_at=now,
            summary=src.summary,
            messages=copied_messages,
        )

        if self.active is None:
            raise RuntimeError("No active conversation loaded.")
        self.active.threads.append(t)
        self.active.active_thread_id = tid
        self.save()
        return t

    # -------------------------
    # CRUD
    # -------------------------
    def _create_new(self) -> Conversation:
        conv_id = uuid.uuid4().hex[:12]
        now = _now_local()
        conv = Conversation(
            id=conv_id,
            title="",
            created_at=now,
            updated_at=now,
            active_thread_id="main",
            threads=[
                Thread(
                    id="main",
                    name="main",
                    created_at=now,
                    updated_at=now,
                    summary="",
                    messages=[],
                )
            ],
            schema_version=2,
        )
        self.save(conv)
        return conv

    def new(self) -> Conversation:
        self.active = self._create_new()
        return self.active

    def clear_active(self) -> None:
        self.active = None

    def save(self, conv: Optional[Conversation] = None) -> None:
        conv = conv or self.active
        if conv is None:
            raise RuntimeError("No active conversation to save.")
        conv.updated_at = _now_local()
        path = _conv_path(self.cfg, conv.id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(conv.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self, conv_id: str) -> Conversation:
        path = _conv_path(self.cfg, conv_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No such conversation: {conv_id}")
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.active = Conversation.from_dict(d)
        _ = self.get_thread(self.active.active_thread_id)
        return self.active

    def delete(self, conv_id: str) -> bool:
        path = _conv_path(self.cfg, conv_id)
        if not os.path.exists(path):
            return False
        os.remove(path)
        return True

    def list(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        d = self.cfg.storage.conversations_dir
        if not os.path.exists(d):
            return out
        for name in os.listdir(d):
            if not name.endswith(".json"):
                continue
            path = os.path.join(d, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    c = json.load(f)
                out.append(
                    {
                        "id": c.get("id", name[:-5]),
                        "title": c.get("title", ""),
                        "updated_at": c.get("updated_at", ""),
                        "created_at": c.get("created_at", ""),
                    }
                )
            except Exception:
                continue
        out.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return out

    def find_by_title(self, title: str) -> List[Dict[str, Any]]:
        want = (title or "").strip().lower()
        if not want:
            return []
        matches: List[Dict[str, Any]] = []
        for c in self.list():
            have = (c.get("title") or "").strip().lower()
            if have == want:
                matches.append(c)
        return matches

    def _title_exists(self, title: str, *, exclude_id: Optional[str] = None) -> bool:
        want = (title or "").strip().lower()
        if not want:
            return False
        for c in self.list():
            if exclude_id and c.get("id") == exclude_id:
                continue
            if (c.get("title") or "").strip().lower() == want:
                return True
        return False

    def make_unique_title(self, base: str, *, exclude_id: Optional[str] = None) -> str:
        base = (base or "").strip()
        if not base:
            return ""
        if not self._title_exists(base, exclude_id=exclude_id):
            return base
        i = 2
        while True:
            candidate = f"{base} ({i})"
            if not self._title_exists(candidate, exclude_id=exclude_id):
                return candidate
            i += 1

    # -------------------------
    # Append + summarization (thread-scoped)
    # -------------------------
    def append(
        self,
        role: str,
        content: str,
        *,
        thread_id: Optional[str] = None,
        model: Optional[str] = None,
        routing_reason: Optional[str] = None,
    ) -> None:
        if self.active is None:
            raise RuntimeError("No active conversation loaded. Use /new or /load.")

        t = self.get_thread(thread_id)

        msg: Dict[str, Any] = {"role": role, "content": content, "ts": _now_local()}
        if role == "assistant":
            if model:
                msg["model"] = model
            if routing_reason:
                msg["routing_reason"] = routing_reason

        t.messages.append(msg)
        t.updated_at = _now_local()

        if role == "user" and not (self.active.title or "").strip():
            base = (content.strip().splitlines()[0][:60] or "Conversation").strip()
            self.active.title = self.make_unique_title(base, exclude_id=self.active.id)

        self._maybe_summarize(t)
        self.save()

    def _maybe_summarize(self, thread: Thread) -> None:
        mem_cfg = self.cfg.memory
        if not mem_cfg.summarize.enabled:
            return

        msgs = thread.messages
        trigger = int(mem_cfg.summarize.trigger_after_messages)
        keep_last = int(mem_cfg.summarize.keep_last_messages)
        short_max = int(mem_cfg.short_term_max_messages)

        if len(msgs) <= max(trigger, short_max):
            return

        older = msgs[:-keep_last]
        recent = msgs[-keep_last:]

        transcript = [f"{m.get('role','').upper()}: {m.get('content','')}" for m in older]
        transcript_text = "\n".join(transcript)

        thread.summary = self.summarizer.rollup(
            existing_summary=thread.summary,
            transcript=transcript_text,
        )
        thread.messages = recent

    # -------------------------
    # Peek helper (for project-scoped retrieval)
    # -------------------------
    def peek_active_thread_id(self, conv_id: str) -> str:
        """
        Best-effort: read conversation file and return its active_thread_id.
        Returns "main" if missing/unreadable.
        """
        conv_id = (conv_id or "").strip()
        if not conv_id:
            return "main"
        path = _conv_path(self.cfg, conv_id)
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            tid = d.get("active_thread_id", "main")
            return str(tid or "main")
        except Exception:
            return "main"
