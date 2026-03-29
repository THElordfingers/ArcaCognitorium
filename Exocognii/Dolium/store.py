"""
store.py — Dolium v2
IdeaStore: JSON persistence with in-memory cache.
Single source of truth. Synchronous reads/writes.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import (
    Idea,
    ChamberLog,
    CullRecord,
    CHAMBER_FOMENTARY,
    CHAMBER_CODEX,
)


class IdeaStore:
    """
    Manages all Idea persistence.

    Storage layout:
        storage/
            ideas.json    — active ideas (including culled)
            culled.json   — cull records
            exports/      — export output directory
    """

    def __init__(self, storage_dir: Path):
        self._dir        = Path(storage_dir)
        self._ideas_path = self._dir / "ideas.json"
        self._culled_path = self._dir / "culled.json"
        self._exports_dir = self._dir / "exports"

        self._dir.mkdir(parents=True, exist_ok=True)
        self._exports_dir.mkdir(exist_ok=True)

        self._ideas: dict[str, Idea] = {}
        self._cull_records: list[CullRecord] = []

        self._load()

    # ── Load / Save ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load ideas.json and culled.json into memory. Backs up on corruption."""
        self._ideas = {}
        self._cull_records = []

        if self._ideas_path.exists():
            try:
                data = json.loads(self._ideas_path.read_text(encoding="utf-8"))
                for d in data:
                    idea = Idea.from_dict(d)
                    self._ideas[idea.id] = idea
            except (json.JSONDecodeError, KeyError, TypeError):
                bak = self._ideas_path.with_suffix(".json.bak")
                shutil.copy2(self._ideas_path, bak)
                self._ideas = {}
                # Caller is notified via the return — UI checks via load_error property
                self._load_error = f"ideas.json was corrupt — backed up to {bak.name}, starting empty."

        if self._culled_path.exists():
            try:
                data = json.loads(self._culled_path.read_text(encoding="utf-8"))
                self._cull_records = [CullRecord.from_dict(d) for d in data]
            except (json.JSONDecodeError, KeyError, TypeError):
                self._cull_records = []

    def _save_ideas(self) -> None:
        data = [idea.to_dict() for idea in self._ideas.values()]
        self._ideas_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _save_culled(self) -> None:
        data = [r.to_dict() for r in self._cull_records]
        self._culled_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @property
    def load_error(self) -> Optional[str]:
        return getattr(self, "_load_error", None)

    @property
    def exports_dir(self) -> Path:
        return self._exports_dir

    # ── Read ──────────────────────────────────────────────────────────────────

    def all_active(self) -> list[Idea]:
        """Return all non-culled ideas, sorted by chamber then created."""
        return sorted(
            [i for i in self._ideas.values() if not i.culled],
            key=lambda i: (i.chamber, i.created),
        )

    def all_culled(self) -> list[Idea]:
        return [i for i in self._ideas.values() if i.culled]

    def by_chamber(self, chamber: int) -> list[Idea]:
        return [i for i in self.all_active() if i.chamber == chamber]

    def get(self, idea_id: str) -> Optional[Idea]:
        return self._ideas.get(idea_id)

    def cull_records(self) -> list[CullRecord]:
        return list(self._cull_records)

    # ── Write ─────────────────────────────────────────────────────────────────

    def create(self, title: str) -> Idea:
        """Create a new Idea in the Fomentary."""
        idea = Idea(title=title, chamber=CHAMBER_FOMENTARY)
        self._ideas[idea.id] = idea
        self._save_ideas()
        return idea

    def update(self, idea: Idea) -> None:
        """Persist an already-modified Idea object."""
        idea.touch()
        self._ideas[idea.id] = idea
        self._save_ideas()

    def advance(self, idea: Idea) -> Idea:
        """
        Advance idea to the next chamber. Caller must check gate before calling.
        Records a ChamberLog entry.
        """
        if idea.chamber >= CHAMBER_CODEX:
            return idea

        prev = idea.chamber
        idea.chamber += 1
        idea.chamber_log.append(ChamberLog(from_chamber=prev, to_chamber=idea.chamber))
        self.update(idea)
        return idea

    def return_to(self, idea: Idea, target_chamber: int) -> Idea:
        """Return idea to an earlier chamber. Logs the regression."""
        if target_chamber >= idea.chamber or target_chamber < CHAMBER_FOMENTARY:
            return idea

        prev = idea.chamber
        idea.chamber = target_chamber
        idea.chamber_log.append(
            ChamberLog(from_chamber=prev, to_chamber=target_chamber, note="returned")
        )
        self.update(idea)
        return idea

    def cull(self, idea: Idea, reason: str) -> CullRecord:
        """Mark idea as culled. Creates a CullRecord."""
        record = CullRecord(idea_id=idea.id, reason=reason, chamber=idea.chamber)
        idea.culled = True
        self._cull_records.append(record)
        self.update(idea)
        self._save_culled()
        return record

    def resurrect(self, idea_id: str) -> Optional[Idea]:
        """Un-cull an idea. Removes its most recent CullRecord."""
        idea = self._ideas.get(idea_id)
        if not idea:
            return None
        idea.culled = False
        self._cull_records = [r for r in self._cull_records if r.idea_id != idea_id]
        self.update(idea)
        self._save_culled()
        return idea

    def delete_permanently(self, idea_id: str) -> bool:
        """Remove idea entirely from the store. No recovery."""
        if idea_id in self._ideas:
            del self._ideas[idea_id]
            self._save_ideas()
            return True
        return False
