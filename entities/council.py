
from __future__ import annotations
from dataclasses import dataclass, field
from entities.entity_compiler import EntityCompiler, CompiledEntity
from pathlib import Path


@dataclass
class CouncilState:
    """Snapshot of the Council at any moment."""
    active_entity_id: str
    compiled_entities: dict[str, CompiledEntity] = field(default_factory=dict)


class Council:
    """
    Manages the Entity Council for the session.
    Tracks compiled Entities, the active Entity, and summon/dismiss operations.

    Phase 6 scope:
      - Luminarious always compiled on init.
      - Assessor compiled on first summon.
      - Active Entity = Luminarious by default.
      - /summon switches active Entity.
      - /dismiss returns to Luminarious.
    """

    ANCHOR_ID = "luminarious"

    def __init__(self, compiler: EntityCompiler) -> None:
        """Init with compiler. Compile Luminarious immediately."""
        self.compiler = compiler
        self._compiled: dict[str, CompiledEntity] = {}
        self._active_id: str = self.ANCHOR_ID
        # Always compile the anchor Entity on startup
        self._compiled[self.ANCHOR_ID] = self.compiler.compile(self.ANCHOR_ID)
        self._emerged: set[str] = set()

    @property
    def active(self) -> CompiledEntity:
        """Return the currently active compiled Entity."""
        return self._compiled[self._active_id]

    @property
    def active_id(self) -> str:
        """Return the ID of the active Entity."""
        return self._active_id

    def summon(self, entity_id: str) -> CompiledEntity:
        """
        Summon an Entity by ID.
        Compiles on first summon if not already cached.
        Sets as active Entity.
        Returns the CompiledEntity.
        Raises EntityNotFoundError if entity_id has no role definition.
        """
        if entity_id not in self._compiled:
            self._compiled[entity_id] = self.compiler.compile(entity_id)
        self._active_id = entity_id
        return self._compiled[entity_id]

    def dismiss(self) -> CompiledEntity:
        """
        Dismiss the current Entity and return to Luminarious.
        Does nothing if Luminarious is already active.
        Returns the Luminarious CompiledEntity.
        """
        self._active_id = self.ANCHOR_ID
        return self._compiled[self.ANCHOR_ID]

    def get_compiled(self, entity_id: str) -> CompiledEntity | None:
        """Return compiled Entity by ID, or None if not yet compiled."""
        return self._compiled.get(entity_id)

    def get_all_compiled(self) -> dict[str, CompiledEntity]:
        """Return all currently compiled Entities."""
        return dict(self._compiled)

    def get_state(self) -> CouncilState:
        """Return a snapshot of current Council state."""
        return CouncilState(
            active_entity_id=self._active_id,
            compiled_entities=dict(self._compiled)
        )

    def emerge(self, entity_id: str) -> None:
        """
        Mark entity_id as emerged. Compiles and caches it if not already compiled.
        Silent — no UI notification generated here.
        """
        if entity_id not in self._emerged:
            if entity_id not in self._compiled:
                try:
                    self.summon(entity_id)
                except Exception:
                    pass  # EntityCompilationError — log handled by compiler
            self._emerged.add(entity_id)

    def get_emerged(self) -> set:
        """Return the set of currently emerged entity_ids."""
        return set(self._emerged)

    def has_emerged(self, entity_id: str) -> bool:
        """Return True if entity_id has emerged."""
        return entity_id in self._emerged

