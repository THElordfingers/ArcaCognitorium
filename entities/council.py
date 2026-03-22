#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/entities/council.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from entities.entity_compiler import EntityCompiler, CompiledEntity

log = logging.getLogger(__name__)


@dataclass
class CouncilState:
    active_entity_id: str
    compiled_entities: dict[str, CompiledEntity] = field(default_factory=dict)


class Council:
    """
    Manages the Entity Council for the session.

    Emerged entity state is persisted to disk so the Council accumulates
    across sessions rather than resetting on every restart.

    Persistence: storage/council/emerged.json
    Format: {"emerged": ["entity_id_1", "entity_id_2"]}

    Dev flag: pass dev_emerge_all=True to force all known entities emerged
    immediately. Used during development. Remove before release.
    """

    ANCHOR_ID = "luminarious"
    EMERGED_PATH = Path("storage/council/emerged.json")

    ALL_ENTITY_IDS: List[str] = [
        "archivist",
        "contrarian",
        "minimalist",
        "speculator",
        "pessimist",
        "toolsmith",
        "systems_thinker",
        "socratic",
    ]

    def __init__(
        self,
        compiler: EntityCompiler,
        dev_emerge_all: bool = False,
    ) -> None:
        self.compiler = compiler
        self._compiled: dict[str, CompiledEntity] = {}
        self._active_id: str = self.ANCHOR_ID
        self._emerged: set[str] = set()
        self._dev_mode: bool = dev_emerge_all

        self._compiled[self.ANCHOR_ID] = self.compiler.compile(self.ANCHOR_ID)

        if dev_emerge_all:
            self._force_emerge_all()
        else:
            self._load_emerged()
            for entity_id in list(self._emerged):
                if entity_id not in self._compiled:
                    try:
                        self._compiled[entity_id] = self.compiler.compile(entity_id)
                    except Exception:
                        self._emerged.discard(entity_id)

    @property
    def active(self) -> CompiledEntity:
        return self._compiled[self._active_id]

    @property
    def active_id(self) -> str:
        return self._active_id

    def summon(self, entity_id: str) -> CompiledEntity:
        if entity_id not in self._compiled:
            self._compiled[entity_id] = self.compiler.compile(entity_id)
        self._active_id = entity_id
        return self._compiled[entity_id]

    def dismiss(self) -> CompiledEntity:
        self._active_id = self.ANCHOR_ID
        return self._compiled[self.ANCHOR_ID]

    def get_compiled(self, entity_id: str) -> CompiledEntity | None:
        return self._compiled.get(entity_id)

    def get_all_compiled(self) -> dict[str, CompiledEntity]:
        return dict(self._compiled)

    def get_state(self) -> CouncilState:
        return CouncilState(
            active_entity_id=self._active_id,
            compiled_entities=dict(self._compiled)
        )

    def emerge(self, entity_id: str) -> None:
        if entity_id not in self._emerged:
            if entity_id not in self._compiled:
                try:
                    self._compiled[entity_id] = self.compiler.compile(entity_id)
                except Exception:
                    return
            self._emerged.add(entity_id)
            if not self._dev_mode:
                self._save_emerged()

    def get_emerged(self) -> set:
        return set(self._emerged)

    def has_emerged(self, entity_id: str) -> bool:
        return entity_id in self._emerged

    def is_dev_mode(self) -> bool:
        return self._dev_mode

    def _save_emerged(self) -> None:
        try:
            self.EMERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.EMERGED_PATH.with_suffix(".json.tmp")
            payload = {"emerged": sorted(self._emerged)}
            tmp.write_text(json.dumps(payload, indent=2))
            tmp.rename(self.EMERGED_PATH)
        except Exception as e:
            log.warning(f"Council emerged save failed: {e}")

    def _load_emerged(self) -> None:
        if not self.EMERGED_PATH.exists():
            return
        try:
            data = json.loads(self.EMERGED_PATH.read_text())
            emerged = data.get("emerged", [])
            if isinstance(emerged, list):
                self._emerged = set(str(e) for e in emerged)
        except Exception as e:
            log.warning(f"Council emerged load failed: {e}")
            self._emerged = set()

    def _force_emerge_all(self) -> None:
        for entity_id in self.ALL_ENTITY_IDS:
            if entity_id not in self._compiled:
                try:
                    self._compiled[entity_id] = self.compiler.compile(entity_id)
                except Exception:
                    continue
            self._emerged.add(entity_id)
        log.warning("DEV MODE: All entities force-emerged. Remove dev_emerge_all before release.")
