#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / chambers.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from models import Idea


# ── GateResult ────────────────────────────────────────────────────────────────

@dataclass
class GateResult:
    passed:   bool
    failures: list[str] = field(default_factory=list)


# ── Gate functions ────────────────────────────────────────────────────────────

def gate_1_to_2(idea: Idea) -> GateResult:
    """
    Fomentary → Cultivation House.
    Requires: title, body (min 20 chars), motivation.
    Title must not duplicate any idea already in chambers 2-4.
    NOTE: duplicate check is intentionally skipped here — the store
    would need to pass the full idea list. Duplication is a UI-layer
    concern; the gate enforces content requirements only.
    """
    failures = []

    if not idea.title.strip():
        failures.append("The idea has no title.")

    if len(idea.body.strip()) < 20:
        failures.append("The body is too sparse. Write at least a sentence.")

    if not idea.motivation.strip():
        failures.append("Motivation is empty. Why does this idea exist?")

    return GateResult(passed=len(failures) == 0, failures=failures)


def gate_2_to_3(idea: Idea) -> GateResult:
    """
    Cultivation House → Vestibule.
    Requires all gate_1_to_2 fields plus scope and system map.
    Body must be at least 100 chars — forces real cultivation.
    """
    failures = []

    if not idea.title.strip():
        failures.append("The idea has no title.")

    if len(idea.body.strip()) < 100:
        failures.append("The body is underdeveloped. Cultivate before advancing.")

    if not idea.motivation.strip():
        failures.append("Motivation is empty.")

    if not idea.scope_in.strip():
        failures.append("Scope (inside) is empty. What is this idea about?")

    if not idea.scope_out.strip():
        failures.append("Scope (outside) is empty. What is explicitly excluded?")

    if not idea.system_map.strip():
        failures.append("System map is empty. What systems does this touch or require?")

    return GateResult(passed=len(failures) == 0, failures=failures)


def gate_3_to_4(idea: Idea) -> GateResult:
    """
    Vestibule → Codex Paratum.
    Requires all prior fields plus dependencies, build sequence, and Declaration.
    """
    failures = []

    if not idea.title.strip():
        failures.append("The idea has no title.")

    if len(idea.body.strip()) < 100:
        failures.append("The body is underdeveloped.")

    if not idea.motivation.strip():
        failures.append("Motivation is empty.")

    if not idea.scope_in.strip():
        failures.append("Scope (inside) is empty.")

    if not idea.scope_out.strip():
        failures.append("Scope (outside) is empty.")

    if not idea.system_map.strip():
        failures.append("System map is empty.")

    if not idea.dependencies.strip():
        failures.append("Dependencies are empty. What must exist before this can be built?")

    if not idea.build_sequence.strip():
        failures.append("Build sequence is empty. In what order does this get built?")

    if not idea.declaration.strip():
        failures.append("The Declaration is absent. The Wizard must sign this idea forward.")

    if idea.declared_at is None:
        failures.append("No declaration timestamp. Save the Declaration field to set it.")

    return GateResult(passed=len(failures) == 0, failures=failures)


# ── Router ────────────────────────────────────────────────────────────────────

def gate_for_advance(current_chamber: int) -> Callable[[Idea], GateResult]:
    """
    Returns the appropriate gate function for advancing from current_chamber.
    Raises ValueError if the chamber is already at maximum or invalid.
    """
    gates = {
        1: gate_1_to_2,
        2: gate_2_to_3,
        3: gate_3_to_4,
    }
    if current_chamber not in gates:
        raise ValueError(
            f"Cannot advance from chamber {current_chamber}. "
            f"Chamber 4 is the final chamber."
        )
    return gates[current_chamber]


def can_return(current_chamber: int, target_chamber: int) -> GateResult:
    """
    Return is always permitted if target < current and target >= 1.
    """
    if target_chamber >= current_chamber:
        return GateResult(passed=False, failures=["Target must be a prior chamber."])
    if target_chamber < 1:
        return GateResult(passed=False, failures=["Target chamber must be at least 1."])
    return GateResult(passed=True)
