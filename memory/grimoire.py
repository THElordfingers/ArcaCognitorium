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
import json, uuid
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
    source:     str
    tags:       list[str]
    active:     bool = True

    @classmethod
    def create(cls, content: str, category: str,
               source: str = "manual",
               tags: list[str] | None = None) -> "GrimoireEntry":
        """Factory method. Generates entry_id and created_at automatically.
        entry_id format: grim_{YYYYMMDD}_{4-char uuid fragment}
        """
        now = datetime.now(timezone.utc)
        entry_id = f"grim_{now.strftime('%Y%m%d')}_{uuid.uuid4().hex[:4]}"
        return cls(
            entry_id=entry_id,
            content=content,
            category=category,
            created_at=now.isoformat(),
            source=source,
            tags=tags or [],
            active=True
        )


class Grimoire:
    """
    Personal permanent memory layer.
    Never compressed. Never summarized. Never automatically modified.
    Injected into every conversation context within the token budget.
    The Wizard's indelible self, present in every exchange.
    """

    DEFAULT_MAX_TOKENS = 800
    DEFAULT_STORE_PATH = Path("data/grimoire/grimoire.json")

    def __init__(self,
                 store_path: Path | None = None,
                 max_injection_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        """
        Load Grimoire from disk on init.
        Create empty store if file absent — not an error, expected on first run.
        """
        self.store_path = store_path or self.DEFAULT_STORE_PATH
        self.max_injection_tokens = max_injection_tokens
        self._entries: list[GrimoireEntry] = []
        self._load()

    # ── Public API ──────────────────────────────────────────────────────

    def add(self, content: str, category: str,
            source: str = "manual",
            tags: list[str] | None = None) -> GrimoireEntry:
        """
        Create and persist a new Grimoire entry.
        Returns the created GrimoireEntry.

        Implementation:
          entry = GrimoireEntry.create(content, category, source, tags)
          self._entries.append(entry)
          self._save()
          return entry
        """
        entry = GrimoireEntry.create(content, category, source, tags)
        self._entries.append(entry)
        self._save()
        return entry

    def remove(self, entry_id: str) -> bool:
        """
        Soft-delete: set entry.active = False.
        Returns True if entry found and deactivated.
        Returns False if entry_id not found.
        Does NOT physically delete — preserves history, allows undo.

        Implementation:
          for entry in self._entries:
              if entry.entry_id == entry_id:
                  entry.active = False
                  self._save()
                  return True
          return False
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.active = False
                self._save()
                return True
        return False

    def restore(self, entry_id: str) -> bool:
        """
        Reverse a soft-delete: set entry.active = True.
        Returns True if found and restored, False otherwise.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.active = True
                self._save()
                return True
        return False

    def edit(self, entry_id: str, new_content: str) -> bool:
        """
        Update the content of an existing entry.
        Does NOT change created_at or entry_id.
        Returns True if found and updated, False otherwise.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.content = new_content
                self._save()
                return True
        return False

    def get_active(self) -> list[GrimoireEntry]:
        """Return all entries where active=True, sorted by created_at ascending.
        Oldest entries first — they get priority in token budget.
        """
        return sorted(
            [e for e in self._entries if e.active],
            key=lambda e: e.created_at
        )

    def get_all(self) -> list[GrimoireEntry]:
        """Return all entries including inactive. For management page display."""
        return sorted(self._entries, key=lambda e: e.created_at)

    def build_injection_string(self) -> str:
        """
        Assemble active entries into a context injection string.
        Respects max_injection_tokens budget.
        Oldest entries included first — if budget exceeded, newest dropped.

        Format:
          GRIMOIRE — The Wizard's Permanent Memory:
          [communication_style] I prefer terse explanations unless I ask for depth.
          [work_patterns] I work in focused blocks of 2-3 hours.
          ...

        Returns empty string if no active entries.
        Returns empty string if token budget is 0.

        Implementation:
          active = self.get_active()
          if not active:
              return ""

          header = "GRIMOIRE — The Wizard's Permanent Memory:\n"
          lines = []
          budget = self.max_injection_tokens - self._estimate_tokens(header)

          for entry in active:
              line = f"[{entry.category}] {entry.content}"
              cost = self._estimate_tokens(line)
              if cost > budget:
                  break  # No more room — stop here
              lines.append(line)
              budget -= cost

          if not lines:
              return ""
          return header + "\n".join(lines)
        """
        active = self.get_active()
        if not active:
            return ""
        header = "GRIMOIRE — The Wizard's Permanent Memory:\n"
        lines = []
        budget = self.max_injection_tokens - self._estimate_tokens(header) - 2
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
        """
        Return token usage summary for status display.
        {"used": int, "budget": int, "pct": int, "entry_count": int}
        """
        injection = self.build_injection_string()
        used = self._estimate_tokens(injection)
        return {
            "used": used,
            "budget": self.max_injection_tokens,
            "pct": round(used / self.max_injection_tokens * 100),
            "entry_count": len(self.get_active())
        }

    # ── Private Methods ─────────────────────────────────────────────────

    def _estimate_tokens(self, text: str) -> int:
        """
        Conservative token estimate: word count * 1.3.
        Intentionally over-estimates to prevent budget overflow.
        Not a precise tokenizer — sufficient for budget management.
        """
        if not text:
            return 0
        return max(1, int(len(text.split()) * 1.3))

    def _save(self) -> None:
        """
        Persist Grimoire to disk atomically.
        Atomic write pattern: write to .tmp → rename to target.
        Prevents corruption on crash mid-write.

        Implementation:
          self.store_path.parent.mkdir(parents=True, exist_ok=True)
          tmp = self.store_path.with_suffix(".tmp")
          payload = {
              "version": "1.0",
              "wizard_id": "lordfingears",
              "max_injection_tokens": self.max_injection_tokens,
              "last_updated": datetime.now(timezone.utc).isoformat(),
              "entries": [asdict(e) for e in self._entries]
          }
          tmp.write_text(json.dumps(payload, indent=2))
          tmp.rename(self.store_path)
        """
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.store_path.with_suffix(".tmp")
        payload = {
            "version": "1.0",
            "wizard_id": "lordfingears",
            "max_injection_tokens": self.max_injection_tokens,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "entries": [asdict(e) for e in self._entries]
        }
        tmp.write_text(json.dumps(payload, indent=2))
        tmp.rename(self.store_path)

    def _load(self) -> None:
        """
        Load Grimoire from disk.
        If file absent: initialize empty — not an error.
        If file present but malformed JSON: log warning, initialize empty,
          rename corrupt file to grimoire.json.bak.

        Implementation:
          if not self.store_path.exists():
              return  # Fresh install — empty Grimoire is correct
          try:
              data = json.loads(self.store_path.read_text())
              self._entries = [GrimoireEntry(**e) for e in data.get("entries", [])]
              loaded_max = data.get("max_injection_tokens")
              if loaded_max:
                  self.max_injection_tokens = loaded_max
          except (json.JSONDecodeError, TypeError) as e:
              bak = self.store_path.with_suffix(".json.bak")
              self.store_path.rename(bak)
              # logger.warning(f"Corrupt Grimoire — backed up to {bak}")
              self._entries = []
        """
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
