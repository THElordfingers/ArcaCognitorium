#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / store.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from models import Idea, ChamberLog, CullRecord
from chambers import gate_for_advance


# ── IdeaStore ─────────────────────────────────────────────────────────────────

class IdeaStore:
    """
    The only object that touches the filesystem.
    Holds the full idea list in memory after load.
    Writes the entire JSON on every mutation — acceptable at any realistic idea count.
    All methods are synchronous.
    """

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir  = Path(storage_dir)
        self.exports_dir  = self.storage_dir / "exports"
        self._ideas_path  = self.storage_dir / "ideas.json"
        self._culled_path = self.storage_dir / "culled.json"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        self._ideas:  list[Idea]       = []
        self._culled: list[CullRecord] = []

        self._load()

    # ── Public API ────────────────────────────────────────────────────────────

    def all(self) -> list[Idea]:
        """All ideas, newest first."""
        return sorted(self._ideas, key=lambda i: i.updated_at, reverse=True)

    def by_chamber(self, n: int) -> list[Idea]:
        """Ideas in chamber n, newest first."""
        return sorted(
            [i for i in self._ideas if i.chamber == n],
            key=lambda i: i.updated_at,
            reverse=True,
        )

    def get(self, idea_id: str) -> Optional[Idea]:
        """Single idea by UUID, or None."""
        for idea in self._ideas:
            if idea.id == idea_id:
                return idea
        return None

    def create(self, title: str) -> Idea:
        """Create a new Idea in chamber 1. Write to disk. Return the new Idea."""
        idea = Idea(title=title.strip())
        self._ideas.append(idea)
        self._write_ideas()
        return idea

    def update(self, idea: Idea) -> None:
        """
        Persist a mutated Idea.
        Caller mutates the Idea object first, then calls update().
        """
        idea.touch()
        # Replace in list if present, append if somehow missing
        for i, existing in enumerate(self._ideas):
            if existing.id == idea.id:
                self._ideas[i] = idea
                self._write_ideas()
                return
        self._ideas.append(idea)
        self._write_ideas()

    def advance(self, idea: Idea, note: str = "") -> Idea:
        """
        Advance idea to the next chamber.
        Runs the appropriate gate — raises ValueError with failure list if blocked.
        Appends ChamberLog entry. Calls update().
        """
        gate_fn = gate_for_advance(idea.chamber)
        result  = gate_fn(idea)

        if not result.passed:
            raise ValueError("\n".join(result.failures))

        from_chamber  = idea.chamber
        idea.chamber += 1
        idea.log.append(ChamberLog(
            from_chamber=from_chamber,
            to_chamber=idea.chamber,
            note=note,
        ))
        self.update(idea)
        return idea

    def return_to(self, idea: Idea, target_chamber: int, note: str = "") -> Idea:
        """
        Return idea to any prior chamber.
        Never blocked — return is always permitted.
        Raises ValueError only if target >= current or target < 1.
        """
        if target_chamber >= idea.chamber:
            raise ValueError("Target chamber must be less than current chamber.")
        if target_chamber < 1:
            raise ValueError("Target chamber must be at least 1.")

        from_chamber  = idea.chamber
        idea.chamber  = target_chamber
        idea.log.append(ChamberLog(
            from_chamber=from_chamber,
            to_chamber=target_chamber,
            note=note,
        ))
        self.update(idea)
        return idea

    def cull(self, idea: Idea, epitaph: str) -> CullRecord:
        """
        Remove idea from active store. Write CullRecord to culled.json.
        Epitaph is required — raises ValueError if empty.
        """
        epitaph = epitaph.strip()
        if not epitaph:
            raise ValueError("An epitaph is required to cull an idea.")

        record = CullRecord(
            id              = idea.id,
            title           = idea.title,
            chamber_at_cull = idea.chamber,
            epitaph         = epitaph,
            body_snapshot   = idea.body,
        )

        self._ideas  = [i for i in self._ideas if i.id != idea.id]
        self._culled.append(record)

        self._write_ideas()
        self._write_culled()
        return record

    def culled(self) -> list[CullRecord]:
        """All CullRecords, most recently culled first."""
        return sorted(self._culled, key=lambda r: r.culled_at, reverse=True)

    def resurrect(self, cull_id: str) -> Idea:
        """
        Create a new Idea from a CullRecord's body snapshot.
        Returns to chamber 1. Removes record from culled.json.
        Raises ValueError if cull_id not found.
        """
        record = next((r for r in self._culled if r.id == cull_id), None)
        if record is None:
            raise ValueError(f"No culled idea with id {cull_id!r}")

        idea = Idea(
            title = record.title,
            body  = record.body_snapshot,
        )
        idea.log.append(ChamberLog(
            from_chamber=0,
            to_chamber=1,
            note=f"Resurrected from cull. Original epitaph: {record.epitaph}",
        ))

        self._culled = [r for r in self._culled if r.id != cull_id]
        self._ideas.append(idea)

        self._write_ideas()
        self._write_culled()
        return idea

    # ── Private ───────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if self._ideas_path.exists():
            try:
                data = json.loads(self._ideas_path.read_text(encoding="utf-8"))
                self._ideas = [Idea.from_dict(d) for d in data.get("ideas", [])]
            except Exception:
                self._ideas = []
        else:
            self._ideas = []

        if self._culled_path.exists():
            try:
                data = json.loads(self._culled_path.read_text(encoding="utf-8"))
                self._culled = [CullRecord.from_dict(d) for d in data.get("culled", [])]
            except Exception:
                self._culled = []
        else:
            self._culled = []

    def _write_ideas(self) -> None:
        payload = {"ideas": [i.to_dict() for i in self._ideas]}
        self._ideas_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _write_culled(self) -> None:
        payload = {"culled": [r.to_dict() for r in self._culled]}
        self._culled_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
