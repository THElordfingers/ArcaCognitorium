#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨    ArcaCognitorium/entities/dynamics.py
#╚══════════════════════════════════════════════════════════════════════════════
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EntityRelationship:
    entity_a: str
    entity_b: str
    relationship_type: str  # "friction" | "trust" | "tension" | "silence_rule"
    effect: str             # Human-readable description of the behavioral effect


class InterEntityDynamics:
    """
    Tracks inter-Entity relationship state and enforces dynamic rules.
    Called by InterruptionEngine before firing to check silence rules.
    Called by app.py when mounting bubbles to check post-speak multipliers.

    Relationship graph:
    - Contrarian → after speaking: Speculator and Minimalist silenced same turn
    - Pessimist ↔ Speculator: productive friction, weighted to alternate
    - Archivist + Toolsmith: trust — Toolsmith may append without full gate
    - Socratic → Contrarian: after Socratic interrupts, Contrarian presence_weight x2 next turn
    - Assessor → all: write priority
    - Minimalist → all: response length watchdog
    """

    # After entity_a speaks this turn, silence these entity_ids the same turn
    SILENCE_RULES: Dict[str, Set[str]] = {
        "contrarian": {"speculator", "minimalist"},
        "socratic":   set(),  # Socratic silences no one, but boosts Contrarian
    }

    # After entity_a speaks, multiply presence_weight of entity_b for next turn
    POST_SPEAK_MULTIPLIERS: Dict[str, Dict[str, float]] = {
        "socratic":    {"contrarian": 2.0},
        "contrarian":  {"socratic":   1.5},
        "archivist":   {"toolsmith":  1.3},
    }

    # Pessimist/Speculator alternation tracking
    ALTERNATION_PAIRS: List[tuple] = [("pessimist", "speculator")]

    def __init__(self) -> None:
        self._spoke_this_turn: List[str] = []
        self._next_turn_multipliers: Dict[str, float] = {}
        self._alternation_last: Dict[tuple, str] = {}

    # ── Turn lifecycle ────────────────────────────────────────────────────────

    def reset_turn(self) -> None:
        """Call at the start of each new conversation turn."""
        # Apply pending multipliers to next-turn tracking, then clear
        self._spoke_this_turn = []
        self._next_turn_multipliers = {}

    def record_speaker(self, entity_id: str) -> None:
        """Record that an Entity has spoken this turn. Updates multiplier queue."""
        self._spoke_this_turn.append(entity_id)

        # Queue next-turn multipliers
        for target, multiplier in self.POST_SPEAK_MULTIPLIERS.get(entity_id, {}).items():
            current = self._next_turn_multipliers.get(target, 1.0)
            self._next_turn_multipliers[target] = min(current * multiplier, 2.0)

        # Track alternation pairs
        for pair in self.ALTERNATION_PAIRS:
            if entity_id in pair:
                self._alternation_last[pair] = entity_id

    # ── Silence & weight queries ──────────────────────────────────────────────

    def is_silenced(self, entity_id: str) -> bool:
        """Return True if entity_id is silenced this turn by another Entity's silence rule."""
        for speaker in self._spoke_this_turn:
            if entity_id in self.SILENCE_RULES.get(speaker, set()):
                return True
        return False

    def get_presence_multiplier(self, entity_id: str) -> float:
        """
        Return the presence_weight multiplier for entity_id this turn.
        1.0 = unmodified. 2.0 = doubled. Applied by InterruptionEngine.
        """
        # Check alternation pairs — if partner just spoke, suppress this entity
        for pair in self.ALTERNATION_PAIRS:
            if entity_id in pair:
                last = self._alternation_last.get(tuple(sorted(pair)))
                if last and last != entity_id:
                    # Partner spoke most recently — give this one a boost
                    return 1.5
                elif last == entity_id:
                    # This entity spoke most recently — suppress slightly
                    return 0.7

        return self._next_turn_multipliers.get(entity_id, 1.0)

    def speakers_this_turn(self) -> List[str]:
        """Return list of entity_ids that have spoken this turn."""
        return list(self._spoke_this_turn)

    def get_relationships(self) -> List[EntityRelationship]:
        """Return human-readable relationship graph. For /council debug command."""
        return [
            EntityRelationship("contrarian", "speculator", "silence_rule",
                "After Contrarian speaks, Speculator silenced same turn."),
            EntityRelationship("contrarian", "minimalist", "silence_rule",
                "After Contrarian speaks, Minimalist silenced same turn."),
            EntityRelationship("pessimist", "speculator", "friction",
                "When both emerged, interruptions weighted to alternate."),
            EntityRelationship("archivist", "toolsmith", "trust",
                "Toolsmith presence_weight boosted after Archivist retrieval."),
            EntityRelationship("socratic", "contrarian", "tension",
                "After Socratic interrupts, Contrarian presence_weight doubled next turn."),
            EntityRelationship("assessor", "all", "write_priority",
                "Assessor Grimoire writes take precedence over any in-session write conflict."),
            EntityRelationship("minimalist", "all", "length_watchdog",
                "When Minimalist emerges, flags responses over 500 words with one-sentence alternative."),
        ]
