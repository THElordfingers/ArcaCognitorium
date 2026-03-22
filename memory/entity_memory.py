#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨  ArcaCognitorium/memory/entity_memory.py
#╚══════════════════════════════════════════════════════════════════════════════
# VERSION: entity_memory.py v1.0
"""
EntityMemory — Private per-entity persistent memory.

Each Council entity accumulates a small bounded store of observations
from their own interactions with the Wizard. Separate from the Grimoire
(which is a portrait of the Wizard) and the Chronicle (which is a log
of what happened). This is the entity's own record of its relationship
with the Wizard — from its perspective, in its domain.

Storage:   storage/entities/{entity_id}/memory.json
Budget:    300 tokens per entity (configurable)
Write:     when entity speaks or interrupts — one observation extracted
Read:      injected into context after entity instruction string
Wizard:    /entity memory <id>  — read
           /entity purge <id>   — clear
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from client.router import ModelRouter

log = logging.getLogger(__name__)

_DIAG_LOG = Path("storage/logs/entity_memory_diag.log")

def _diag(msg: str) -> None:
    try:
        _DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG, "a") as f:
            f.write(f"[ENTITY_MEMORY] {msg}\n")
            f.flush()
    except Exception:
        pass


@dataclass
class MemoryEntry:
    content:    str
    context:    str        # brief snippet of what prompted this observation
    created_at: str
    entity_id:  str


class EntityMemory:
    """
    Manages private memory stores for all Council entities.

    One instance per session. Each entity's store is loaded lazily
    on first access and saved after every write.
    """

    DEFAULT_TOKEN_BUDGET = 300
    STORE_ROOT = Path("storage/entities")

    def __init__(
        self,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        router: Optional["ModelRouter"] = None,
    ) -> None:
        self._budget   = token_budget
        self._router   = router
        self._stores:  dict[str, list[MemoryEntry]] = {}

    def set_router(self, router: "ModelRouter") -> None:
        """Called after router is available (router not ready at init time)."""
        self._router = router

    # ── Public API ───────────────────────────────────────────────────────────

    def write(
        self,
        entity_id: str,
        entity_display_name: str,
        user_text: str,
        entity_response: str,
    ) -> bool:
        """
        Extract one observation from this interaction and store it.
        Returns True if something was written, False if nothing worth keeping.
        Called after entity speaks or interrupts.
        """
        observation = self._extract_observation(
            entity_id=entity_id,
            entity_display_name=entity_display_name,
            user_text=user_text,
            entity_response=entity_response,
        )
        if not observation:
            _diag(f"{entity_id}: no observation extracted")
            return False

        entries = self._load(entity_id)
        context_snippet = user_text[:120].strip()
        entry = MemoryEntry(
            content=observation,
            context=context_snippet,
            created_at=datetime.now(timezone.utc).isoformat(),
            entity_id=entity_id,
        )
        entries.append(entry)
        entries = self._trim_to_budget(entries)
        self._stores[entity_id] = entries
        self._save(entity_id, entries)
        _diag(f"{entity_id}: wrote — {observation[:80]}")
        return True

    def read(self, entity_id: str) -> str:
        """
        Build injection string for this entity's memory.
        Returns empty string if no entries.
        Injected into context after entity instruction string.
        """
        entries = self._load(entity_id)
        if not entries:
            return ""

        lines = [f"PRIVATE MEMORY — observations from past interactions:"]
        for e in entries:
            lines.append(f"- {e.content}")
        return "\n".join(lines)

    def purge(self, entity_id: str) -> None:
        """Clear all memory for this entity."""
        self._stores[entity_id] = []
        p = self._store_path(entity_id)
        if p.exists():
            p.unlink()
        _diag(f"{entity_id}: purged")

    def get_all_entries(self, entity_id: str) -> list[MemoryEntry]:
        """Return all entries for display via /entity memory command."""
        return self._load(entity_id)

    def token_usage(self, entity_id: str) -> dict:
        entries = self._load(entity_id)
        injection = self.read(entity_id)
        used = self._estimate_tokens(injection)
        return {
            "entity_id":    entity_id,
            "entry_count":  len(entries),
            "used_tokens":  used,
            "budget_tokens": self._budget,
            "pct":          round(used / self._budget * 100) if self._budget else 0,
        }

    # ── Private ──────────────────────────────────────────────────────────────

    def _extract_observation(
        self,
        entity_id: str,
        entity_display_name: str,
        user_text: str,
        entity_response: str,
    ) -> str:
        """
        Use a lightweight model call to extract one observation worth keeping.
        Falls back to a deterministic heuristic if no router available.
        """
        if not self._router:
            return self._heuristic_extract(entity_response)

        prompt = (
            f"You are {entity_display_name}. Review this interaction:\n\n"
            f"WIZARD: {user_text[:400]}\n\n"
            f"YOUR RESPONSE: {entity_response[:400]}\n\n"
            f"Extract exactly ONE observation worth remembering from your perspective. "
            f"This is your private memory — observations about the Wizard's patterns, "
            f"the nature of their questions, how they responded to your input, "
            f"what this exchange reveals about your relationship with them. "
            f"One sentence. Specific. No hedging. "
            f"If nothing is worth remembering, respond with exactly: NOTHING"
        )

        try:
            gen, _ = self._router.stream_response_text(
                self._router.cfg.models.nano if hasattr(self._router, 'cfg') else "claude-haiku-4-5-20251001",
                [{"role": "user", "content": prompt}],
                max_output_tokens=80,
            )
            result = "".join(gen).strip()
            if not result or result.upper() == "NOTHING" or len(result) < 10:
                return ""
            # Strip quotes if model wrapped the observation
            result = result.strip('"\'')
            return result[:300]
        except Exception as e:
            _diag(f"{entity_id}: extraction API failed ({e}), using heuristic")
            return self._heuristic_extract(entity_response)

    def _heuristic_extract(self, response: str) -> str:
        """
        Deterministic fallback: take the first substantial sentence
        from the entity response as a memory seed.
        """
        import re
        sentences = re.split(r"(?<=[.!?])\s+", response.strip())
        for s in sentences:
            s = s.strip()
            if len(s.split()) >= 8:
                return s[:200]
        return ""

    def _trim_to_budget(self, entries: list[MemoryEntry]) -> list[MemoryEntry]:
        """Drop oldest entries until within token budget."""
        while entries:
            injection = "\n".join(f"- {e.content}" for e in entries)
            if self._estimate_tokens(injection) <= self._budget:
                break
            entries = entries[1:]  # drop oldest
        return entries

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, int(len(text.split()) * 1.3))

    def _store_path(self, entity_id: str) -> Path:
        return self.STORE_ROOT / entity_id / "memory.json"

    def _load(self, entity_id: str) -> list[MemoryEntry]:
        if entity_id in self._stores:
            return self._stores[entity_id]
        p = self._store_path(entity_id)
        if not p.exists():
            self._stores[entity_id] = []
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            entries = [MemoryEntry(**e) for e in data.get("entries", [])]
            self._stores[entity_id] = entries
            return entries
        except Exception as e:
            log.warning(f"EntityMemory load failed for {entity_id}: {e}")
            self._stores[entity_id] = []
            return []

    def _save(self, entity_id: str, entries: list[MemoryEntry]) -> None:
        p = self._store_path(entity_id)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".json.tmp")
            payload = {
                "version": "1.0",
                "entity_id": entity_id,
                "entries": [asdict(e) for e in entries],
            }
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.rename(p)
        except Exception as e:
            log.warning(f"EntityMemory save failed for {entity_id}: {e}")
