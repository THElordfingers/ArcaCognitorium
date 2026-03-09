#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨    ArcaCognitorium/entities/interruption.py
#╚══════════════════════════════════════════════════════════════════════════════
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from entities.council import Council
    from entities.emergence import EmergenceEngine
    from entities.dynamics import InterEntityDynamics


@dataclass
class InterruptionResult:
    """Result of an interruption check."""
    should_interrupt: bool
    entity_id: Optional[str]
    domain_score: float
    reason: str


class InterruptionEngine:
    """
    Evaluates whether any emerged Entity should interrupt after
    the primary response has been delivered.

    Interruption is ALWAYS post-response:
    1. Primary Entity (Luminarious or summoned) responds.
    2. app.py calls interruption_engine.check(message, response, council, emergence_engine)
    3. If interruption fires, app.py renders Entity bubble with ↯ glyph.
    4. Active Entity reverts to Luminarious after interruption.
    """

    DOMAIN_THRESHOLD: float = 0.65

    # Interruption domains — keyword sets per interruptible Entity
    INTERRUPTION_DOMAINS: Dict[str, List[str]] = {
        "archivist": [
            "remember", "recall", "what did", "last time", "we discussed",
            "previously", "history", "past", "earlier", "you said",
        ],
        "contrarian": [
            "definitely", "certainly", "obviously", "always", "never", "clearly",
            "must be", "is the best", "only way", "everyone knows", "proven",
        ],
        "speculator": [
            "only option", "the solution", "this will work", "decided to",
            "going with", "the answer is", "no alternative",
        ],
        "pessimist": [
            "ship", "deploy", "launch", "release", "push", "publish",
            "go live", "merge", "finalize", "done", "ready",
        ],
        "toolsmith": [
            "for this specific", "just this one", "only here", "case by case",
            "hardcoded", "this particular", "unique to",
        ],
        "systems_thinker": [
            "this part", "this component", "this module", "this layer",
            "just the", "isolated", "independent", "separate from",
        ],
        "socratic": [
            "what should i", "tell me the answer", "just tell me",
            "what do i do", "give me the solution", "solve this for me",
        ],
    }

    # Presence weights — probability of firing when domain matches
    PRESENCE_WEIGHTS: Dict[str, float] = {
        "archivist":      0.70,
        "contrarian":     0.65,
        "speculator":     0.45,
        "pessimist":      0.55,
        "toolsmith":      0.40,
        "systems_thinker": 0.50,
        "socratic":       0.35,
    }

    def check(
        self,
        message: str,
        response: str,
        council: "Council",
        emergence_engine: "EmergenceEngine",
        dynamics: Optional["InterEntityDynamics"] = None,
    ) -> InterruptionResult:
        """
        Check if any emerged Entity should interrupt.
        Evaluates all emerged, interruption-eligible Entities.
        Returns the first Entity that passes all three gates.
        Only one interruption fires per turn.

        Algorithm:
        1. Get list of emerged entity_ids from council.
        2. Shuffle list — prevents same Entity always winning.
        3. For each entity_id:
           a. Skip if entity_id not in INTERRUPTION_DOMAINS
           b. Gate 1: domain_score >= DOMAIN_THRESHOLD
           c. Gate 2: random.random() < PRESENCE_WEIGHTS[entity_id]
           d. Gate 3: emergence signal >= 0.3
           e. Check dynamics silence rules
           f. All gates pass → return InterruptionResult(True, ...)
        4. No entity passed → return InterruptionResult(False, None, ...)
        """
        emerged = list(council.get_emerged())
        random.shuffle(emerged)

        signals = emergence_engine.get_signal_strengths()
        combined = f"{message}\n{response}"

        for entity_id in emerged:
            if entity_id not in self.INTERRUPTION_DOMAINS:
                continue

            # Gate 1 — domain match
            score = self._domain_score(combined, entity_id)
            if score < self.DOMAIN_THRESHOLD:
                continue

            # Gate 2 — probability roll
            presence = self.PRESENCE_WEIGHTS.get(entity_id, 0.5)
            if random.random() >= presence:
                continue

            # Gate 3 — Reflection relevance
            if signals.get(entity_id, 0.0) < 0.3:
                continue

            # Silence rules via dynamics
            if dynamics and dynamics.is_silenced(entity_id):
                continue

            return InterruptionResult(
                should_interrupt=True,
                entity_id=entity_id,
                domain_score=score,
                reason=(
                    f"{entity_id} domain_score={score:.2f} "
                    f"signal={signals.get(entity_id, 0.0):.2f}"
                ),
            )

        return InterruptionResult(
            should_interrupt=False,
            entity_id=None,
            domain_score=0.0,
            reason="No Entity passed all three gates.",
        )

    def _domain_score(self, text: str, entity_id: str) -> float:
        """
        Keyword density scoring against INTERRUPTION_DOMAINS[entity_id].
        1 match → 0.33. 2 matches → 0.67. 3+ matches → 1.0.
        Normalized to 0.0–1.0.
        """
        text_lower = text.lower()
        keywords = self.INTERRUPTION_DOMAINS.get(entity_id, [])
        matches = sum(1 for kw in keywords if kw in text_lower)
        return min(1.0, matches / 3.0)
