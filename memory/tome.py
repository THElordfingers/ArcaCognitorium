from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from storage.project_store import ProjectStore


@dataclass
class TomeEntry:
    """Single inarguable truth in the active project's Tome."""
    entry_id:   str
    content:    str
    category:   str
    created_at: str
    source:     str
    tags:       list[str]
    active:     bool = True

    @classmethod
    def create(cls, content: str, category: str,
               source: str = "manual",
               tags: list[str] | None = None) -> "TomeEntry":
        """Factory method. Generates entry_id and created_at."""
        now = datetime.now(timezone.utc)
        entry_id = f"tome_{now.strftime('%Y%m%d')}_{uuid.uuid4().hex[:4]}"
        return cls(
            entry_id=entry_id, content=content, category=category,
            created_at=now.isoformat(), source=source,
            tags=tags or [], active=True
        )


class Tome:
    """
    Per-project knowledge layer.
    Silent when no project is active.
    Activates when a project is loaded — injects project truths into every context.
    Never compressed. Never automatic. Always under Wizard control.
    Delegates persistence to ProjectStore — Tome entries live in project JSON.
    """

    DEFAULT_MAX_TOKENS = 600

    def __init__(self,
                 project_store: "ProjectStore",
                 max_injection_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        """
        Initialize with a ProjectStore reference.
        Tome has no state of its own — all data lives in the active project.
        active_project_id: str | None — set by app when project is switched.
        """
        self.project_store = project_store
        self.max_injection_tokens = max_injection_tokens
        self._active_project_id: str | None = None

    # ── Project Activation ──────────────────────────────────────────────

    def activate_project(self, project_id: str) -> None:
        """Set the active project. Called by app when project is switched."""
        self._active_project_id = project_id

    def deactivate(self) -> None:
        """Clear active project. Tome goes silent. Called when project closed."""
        self._active_project_id = None

    @property
    def is_active(self) -> bool:
        """True if a project is currently active."""
        return self._active_project_id is not None

    # ── Public API ──────────────────────────────────────────────────────

    def add(self, content: str, category: str,
            source: str = "manual",
            tags: list[str] | None = None) -> TomeEntry | None:
        """
        Create and persist a new Tome entry in the active project.
        Returns None if no project is active — cannot add to nowhere.

        Implementation:
          if not self._active_project_id:
              return None
          entry = TomeEntry.create(content, category, source, tags)
          entries = self._load_entries()
          entries.append(entry)
          self._save_entries(entries)
          return entry
        """
        if not self._active_project_id:
            return None
        entry = TomeEntry.create(content, category, source, tags)
        entries = self._load_entries()
        entries.append(entry)
        self._save_entries(entries)
        return entry

    def remove(self, entry_id: str) -> bool:
        """
        Soft-delete: set entry.active = False.
        Returns True if found, False otherwise.
        Identical pattern to Grimoire.remove().
        """
        entries = self._load_entries()
        for entry in entries:
            if entry.entry_id == entry_id:
                entry.active = False
                self._save_entries(entries)
                return True
        return False

    def restore(self, entry_id: str) -> bool:
        """Reverse soft-delete. Returns True if found and restored."""
        entries = self._load_entries()
        for entry in entries:
            if entry.entry_id == entry_id:
                entry.active = True
                self._save_entries(entries)
                return True
        return False

    def edit(self, entry_id: str, new_content: str) -> bool:
        """Update content of existing entry. Returns True if found."""
        entries = self._load_entries()
        for entry in entries:
            if entry.entry_id == entry_id:
                entry.content = new_content
                self._save_entries(entries)
                return True
        return False

    def get_active(self) -> list[TomeEntry]:
        """Return active entries for current project, sorted by created_at asc."""
        if not self._active_project_id:
            return []
        return sorted(
            [e for e in self._load_entries() if e.active],
            key=lambda e: e.created_at
        )

    def get_all(self) -> list[TomeEntry]:
        """Return all entries including inactive. For management page."""
        if not self._active_project_id:
            return []
        return sorted(self._load_entries(), key=lambda e: e.created_at)

    def build_injection_string(self) -> str:
        """
        Assemble active entries into context injection string.
        Returns empty string if no project active or no active entries.
        Respects max_injection_tokens budget (oldest first).

        Format:
          TOME — [Project Name] Project Truths:
          [architecture] All async workers use Textual run_worker(fn, thread=True).
          [convention] snake_case throughout. No exceptions.
          ...

        Implementation mirrors Grimoire.build_injection_string() exactly,
        with project name in the header and TomeEntry objects.
        """
        if not self._active_project_id:
            return ""
        active = self.get_active()
        if not active:
            return ""
        project_name = self.project_store.get_project_name(
            self._active_project_id
        )
        header = f"TOME — {project_name} Project Truths:\n"
        lines = []
        budget = self.max_injection_tokens - self._estimate_tokens(header)
        for entry in active:
            line = f"[{entry.category}] {entry.content}"
            cost = self._estimate_tokens(line)
            if cost > budget:
                break
            lines.append(line)
            budget -= cost
        if not lines:
            return ""
        return header + "\n".join(lines)

    def token_usage(self) -> dict:
        """Token usage summary. {"used", "budget", "pct", "entry_count"}"""
        injection = self.build_injection_string()
        used = self._estimate_tokens(injection)
        return {
            "used": used,
            "budget": self.max_injection_tokens,
            "pct": round(used / self.max_injection_tokens * 100),
            "entry_count": len(self.get_active())
        }

    # ── Private Methods ─────────────────────────────────────────────────

    def _load_entries(self) -> list[TomeEntry]:
        """
        Load TomeEntry list from active project via project_store.
        Returns [] if no project active or project has no tome_entries key.
        """
        raw = self.project_store.get_tome_entries(self._active_project_id)
        return [TomeEntry(**e) for e in raw]

    def _save_entries(self, entries: list[TomeEntry]) -> None:
        """Persist TomeEntry list to active project via project_store."""
        from dataclasses import asdict
        self.project_store.save_tome_entries(
            self._active_project_id,
            [asdict(e) for e in entries]
        )

    def _estimate_tokens(self, text: str) -> int:
        """Conservative token estimate: word count * 1.3."""
        return max(1, int(len(text.split()) * 1.3))
