#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    ArcaCognitorium/memory/grimoire.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════




from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class GrimoireEntry:
    """Single permanent fact in the Wizard's Grimoire."""
    entry_id:   str
    content:    str
    category:   str
    created_at: str
    source:     str          # "manual" | "assessor" | "archivist"
    tags:       list[str]
    active:     bool = True

    @property
    def is_assessor_entry(self) -> bool:
        """Assessor entries are write-protected — cannot be edited or removed by Wizard."""
        return self.source in ("assessor", "archivist")

    @classmethod
    def create(
        cls,
        content: str,
        category: str,
        source: str = "manual",
        tags: list[str] | None = None,
    ) -> "GrimoireEntry":
        now = datetime.now(timezone.utc)
        entry_id = f"grim_{now.strftime('%Y%m%d')}_{uuid.uuid4().hex[:4]}"
        return cls(
            entry_id=entry_id,
            content=content,
            category=category,
            created_at=now.isoformat(),
            source=source,
            tags=tags or [],
            active=True,
        )


class Grimoire:
    """
    Personal permanent memory layer.
    Never compressed. Never summarised. Never automatically modified.
    Injected into every conversation context within the token budget.

    Sources:
      manual   — Wizard-authored entries. Fully mutable.
      assessor — Written by the Background Assessor. Read-only for the Wizard.
      archivist — Written by the Archivist. Read-only for the Wizard.

    The Wizard can see all entries but cannot edit or remove assessor/archivist
    entries. This preserves the integrity of the machine's portrait of the Wizard.
    """

    DEFAULT_MAX_TOKENS = 800
    DEFAULT_STORE_PATH = Path("storage/grimoire/grimoire.json")

    def __init__(
        self,
        store_path: Path | None = None,
        max_injection_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        self.store_path = store_path or self.DEFAULT_STORE_PATH
        self.max_injection_tokens = max_injection_tokens
        self._entries: list[GrimoireEntry] = []
        self._load()

    # ── Public API ──────────────────────────────────────────────────────

    def add(
        self,
        content: str,
        category: str,
        source: str = "manual",
        tags: list[str] | None = None,
    ) -> GrimoireEntry:
        entry = GrimoireEntry.create(content, category, source, tags)
        self._entries.append(entry)
        self._save()
        return entry

    def remove(self, entry_id: str, force: bool = False) -> tuple[bool, str]:
        """
        Soft-delete an entry.
        Returns (success, message).
        Assessor/archivist entries are protected — force=True required to remove them.
        force=True is only passed by internal systems, never by Wizard commands.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                if entry.is_assessor_entry and not force:
                    return False, f"Entry {entry_id} is an Assessor observation and cannot be removed."
                entry.active = False
                self._save()
                return True, f"Removed {entry_id}."
        return False, f"Entry not found: {entry_id}"

    def restore(self, entry_id: str) -> bool:
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.active = True
                self._save()
                return True
        return False

    def edit(self, entry_id: str, new_content: str) -> tuple[bool, str]:
        """
        Update content of an entry.
        Assessor/archivist entries are protected — Wizard cannot edit them.
        Returns (success, message).
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                if entry.is_assessor_entry:
                    return False, f"Entry {entry_id} is an Assessor observation and cannot be edited."
                entry.content = new_content
                self._save()
                return True, f"Updated {entry_id}."
        return False, f"Entry not found: {entry_id}"

    def get_active(self) -> list[GrimoireEntry]:
        return sorted(
            [e for e in self._entries if e.active],
            key=lambda e: e.created_at
        )

    def get_all(self) -> list[GrimoireEntry]:
        return sorted(self._entries, key=lambda e: e.created_at)

    def get_by_source(self, source: str) -> list[GrimoireEntry]:
        """Return all active entries from a specific source."""
        return [e for e in self.get_active() if e.source == source]

    def build_injection_string(self) -> str:
        """
        Assemble active entries into a context injection string.
        Groups entries by source for clarity in the context window.
        """
        active = self.get_active()
        if not active:
            return ""

        header = "GRIMOIRE — The Wizard's Permanent Memory:\n"
        lines = []
        budget = self.max_injection_tokens - self._estimate_tokens(header) - 2

        for entry in active:
            # Source prefix for context clarity
            if entry.source == "assessor":
                prefix = "[assessor_observation]"
            elif entry.source == "archivist":
                prefix = "[archivist_observation]"
            else:
                prefix = f"[{entry.category}]"

            line = f"{prefix} {entry.content}"
            cost = self._estimate_tokens(line)
            if cost > budget:
                break
            lines.append(line)
            budget -= cost

        if not lines:
            return ""
        return header + "\n".join(lines)

    def token_usage(self) -> dict:
        injection = self.build_injection_string()
        used = self._estimate_tokens(injection)
        return {
            "used": used,
            "budget": self.max_injection_tokens,
            "pct": round(used / self.max_injection_tokens * 100) if self.max_injection_tokens else 0,
            "entry_count": len(self.get_active()),
            "manual_count": len(self.get_by_source("manual")),
            "assessor_count": len(self.get_by_source("assessor")),
        }

    # ── Private ─────────────────────────────────────────────────────────

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, int(len(text.split()) * 1.3))

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.store_path.with_suffix(".tmp")
        payload = {
            "version": "1.1",
            "max_injection_tokens": self.max_injection_tokens,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "entries": [asdict(e) for e in self._entries],
        }
        tmp.write_text(json.dumps(payload, indent=2))
        tmp.rename(self.store_path)

    def _load(self) -> None:
        if not self.store_path.exists():
            return
        try:
            data = json.loads(self.store_path.read_text())
            self._entries = [GrimoireEntry(**e) for e in data.get("entries", [])]
            loaded_max = data.get("max_injection_tokens")
            if loaded_max:
                self.max_injection_tokens = loaded_max
        except (json.JSONDecodeError, TypeError):
            bak = self.store_path.with_suffix(".json.bak")
            self.store_path.rename(bak)
            self._entries = []
