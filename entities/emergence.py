#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨    ArcaCognitorium/entities/emergence.py
#╚══════════════════════════════════════════════════════════════════════════════
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from entities.council import Council


@dataclass
class EntitySignalState:
    entity_id: str
    signal_strength: float = 0.0
    has_emerged: bool = False


_DIAG_LOG_EMERGENCE = Path("storage/logs/emergence_diag.log")

def _diag(msg: str) -> None:
    try:
        _DIAG_LOG_EMERGENCE.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG_EMERGENCE, "a") as f:
            f.write(f"[EMERGENCE_DIAG] {msg}\n")
            f.flush()
    except Exception:
        pass

class EmergenceEngine:
    """
    Reads the Reflection log. Computes per-Entity signal scores.
    Returns newly emerged Entity IDs when thresholds are crossed.
    Emergence is silent --- no UI notification generated here.
    """

    EMERGENCE_THRESHOLD: float = 1.0
    SIGNAL_DECAY_PER_RECORD: float = 0.02
    MAX_SIGNAL: float = 3.0

    # Per-Entity domain keyword sets — fallback hardcoded for resilience
    ENTITY_DOMAINS: Dict[str, List[str]] = {
        "archivist": [
            "retrieve", "history", "past", "remember", "archive",
            "search", "chronicle",
        ],
        "contrarian": [
            "assume", "wrong", "challenge", "disagree", "but",
            "however", "alternative",
        ],
        "minimalist": [
            "simple", "brief", "short", "essential", "distill",
            "core", "just", "only",
        ],
        "speculator": [
            "imagine", "what if", "possible", "explore", "future",
            "potential", "could",
        ],
        "pessimist": [
            "risk", "problem", "fail", "wrong", "danger",
            "concern", "downside", "issue",
        ],
        "toolsmith": [
            "abstract", "pattern", "reuse", "tool", "build",
            "function", "class", "system",
        ],
        "systems_thinker": [
            "system", "constraint", "dependency", "flow",
            "architecture", "whole", "map",
        ],
        "socratic": [
            "why", "question", "purpose", "understand", "meaning",
            "what is", "how does",
        ],
    }

    def __init__(self, reflection_log_path: str | Path) -> None:
        self.reflection_log_path = Path(reflection_log_path)
        self._signals: Dict[str, EntitySignalState] = {
            eid: EntitySignalState(entity_id=eid)
            for eid in self.ENTITY_DOMAINS
        }

    def check_emergence(
        self,
        council: "Council",
        reflection_log_path: Optional[str | Path] = None,
    ) -> List[str]:
        """
        Read Reflection log. Update signal strengths. Return list of
        entity_ids that have just crossed the emergence threshold for the
        first time. Marks them as has_emerged=True in self._signals.

        Algorithm:
        1. Load all Reflection records from log.
        2. For each record, for each Entity:
           a. Check topic overlap with ENTITY_DOMAINS[entity_id]
           b. Accumulate signal += 0.15 per matching topic word
           c. Apply code/question bonuses for eligible Entities
           d. Apply decay: signal -= SIGNAL_DECAY_PER_RECORD if no match
        3. Cap signals at MAX_SIGNAL.
        4. For each Entity where signal >= EMERGENCE_THRESHOLD
           and has_emerged=False: mark emerged, add to newly_emerged.
        5. Return newly_emerged list.
        """
        log = Path(reflection_log_path) if reflection_log_path else self.reflection_log_path
        records = self._load_records(log)
        newly_emerged: List[str] = []

        for record in records:
            topics = {t.lower() for t in record.get("dominant_topics", [])}
            code_present = record.get("code_present", False)
            question_count = record.get("question_count", 0)

            for entity_id, state in self._signals.items():
                if state.has_emerged:
                    continue  # Already emerged — skip

                domain = set(self.ENTITY_DOMAINS.get(entity_id, []))
                matches = len(topics & domain)

                if matches > 0:
                    state.signal_strength += 0.15 * matches
                else:
                    state.signal_strength = max(
                        0.0,
                        state.signal_strength - self.SIGNAL_DECAY_PER_RECORD,
                    )

                # Bonuses for eligible Entities
                if entity_id in ("toolsmith", "systems_thinker") and code_present:
                    state.signal_strength += 0.05
                if entity_id == "socratic" and question_count >= 3:
                    state.signal_strength += 0.08

                # Cap
                state.signal_strength = min(self.MAX_SIGNAL, state.signal_strength)

        # Check thresholds after processing all records
        for entity_id, state in self._signals.items():
            if state.signal_strength >= self.EMERGENCE_THRESHOLD and not state.has_emerged:
                state.has_emerged = True
                newly_emerged.append(entity_id)

        return newly_emerged

    def get_signal_strengths(self) -> Dict[str, float]:
        """Return current signal_strength for all Entities. For /council debug command."""
        return {eid: s.signal_strength for eid, s in self._signals.items()}

    def reset(self) -> None:
        """Reset all signal states. For testing."""
        for state in self._signals.values():
            state.signal_strength = 0.0
            state.has_emerged = False

    def _load_records(self, path: Path) -> List[dict]:
        """Load Reflection records from jsonl. Skips malformed lines."""
        if not path.exists():
            return []
        records = []
        for line in path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records
