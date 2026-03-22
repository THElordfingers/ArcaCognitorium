#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/entities/interruption.py
#║ ⛨
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

from pathlib import Path

_DIAG_LOG_INTERRUPTION = Path("storage/logs/interruption_diag.log")

def _diag(msg: str) -> None:
    try:
        _DIAG_LOG_INTERRUPTION.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG_INTERRUPTION, "a") as f:
            f.write(f"[INTERRUPTION_DIAG] {msg}\n")
            f.flush()
    except Exception:
        pass

@dataclass
class InterruptionResult:
    should_interrupt: bool
    entity_id: Optional[str]
    domain_score: float
    reason: str


class InterruptionEngine:
    """
    Evaluates whether any emerged Entity should interrupt after
    the primary response has been delivered.

    Gate 3 (signal strength) is bypassed when Council is in dev_emerge_all
    mode — force-emerged entities have no organic signal but should still
    be able to speak.
    """

    DOMAIN_THRESHOLD: float = 0.65

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
        "minimalist": [
            "complicated", "complex", "too much", "overwhelming", "verbose",
            "simplify", "all these", "elaborate", "lengthy",
        ],
    }

    PRESENCE_WEIGHTS: Dict[str, float] = {
        "archivist":       0.70,
        "contrarian":      0.65,
        "speculator":      0.45,
        "pessimist":       0.55,
        "toolsmith":       0.40,
        "systems_thinker": 0.50,
        "socratic":        0.35,
        "minimalist":      0.50,
    }

    def check(
        self,
        message: str,
        response: str,
        council: "Council",
        emergence_engine: "EmergenceEngine",
        dynamics: Optional["InterEntityDynamics"] = None,
    ) -> InterruptionResult:
        emerged = list(council.get_emerged())
        random.shuffle(emerged)

        signals = emergence_engine.get_signal_strengths()
        combined = f"{message}\n{response}"
        dev_mode = council.is_dev_mode() if hasattr(council, 'is_dev_mode') else False

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

            # Gate 3 — Reflection signal strength
            # Bypassed in dev mode since force-emerged entities have no organic signal
            if not dev_mode:
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
                    + (" [dev]" if dev_mode else "")
                ),
            )

        return InterruptionResult(
            should_interrupt=False,
            entity_id=None,
            domain_score=0.0,
            reason="No Entity passed all gates.",
        )

    def _domain_score(self, text: str, entity_id: str) -> float:
        text_lower = text.lower()
        keywords = self.INTERRUPTION_DOMAINS.get(entity_id, [])
        matches = sum(1 for kw in keywords if kw in text_lower)
        return min(1.0, matches / 3.0)
