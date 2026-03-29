"""
chambers.py — Dolium v2
GateEngine: pure gate evaluation functions. No UI, no I/O.
Returns GateResult(passed, failures) — UI renders the failures list.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from models import Idea


@dataclass
class GateResult:
    passed:   bool
    failures: list[str] = field(default_factory=list)


class GateEngine:
    """
    Pure static methods. Each gate_N_to_M(idea) checks the conditions
    required to leave chamber N and enter chamber M.
    """

    # ── Gate I → II ───────────────────────────────────────────────────────────

    @staticmethod
    def gate_1_to_2(idea: Idea) -> GateResult:
        """
        Fomentary → Cultivation House.
        Requires: title, body (≥100 chars), motivation (≥60 chars).
        """
        failures = []

        if not idea.title.strip():
            failures.append("Title is empty")

        if len(idea.body.strip()) < 100:
            remaining = 100 - len(idea.body.strip())
            failures.append(f"Body needs {remaining} more characters")

        if len(idea.motivation.strip()) < 60:
            remaining = 60 - len(idea.motivation.strip())
            failures.append(f"Motivation needs {remaining} more characters")

        return GateResult(passed=len(failures) == 0, failures=failures)

    # ── Gate II → III ─────────────────────────────────────────────────────────

    @staticmethod
    def gate_2_to_3(idea: Idea) -> GateResult:
        """
        Cultivation House → Vestibule.
        Requires: elaboration (≥150 chars), obstacles (≥60 chars), first_step (≥40 chars).
        """
        failures = []

        if len(idea.elaboration.strip()) < 150:
            remaining = 150 - len(idea.elaboration.strip())
            failures.append(f"Elaboration needs {remaining} more characters")

        if len(idea.obstacles.strip()) < 60:
            remaining = 60 - len(idea.obstacles.strip())
            failures.append(f"Obstacles needs {remaining} more characters")

        if len(idea.first_step.strip()) < 40:
            remaining = 40 - len(idea.first_step.strip())
            failures.append(f"First Step needs {remaining} more characters")

        return GateResult(passed=len(failures) == 0, failures=failures)

    # ── Gate III → IV ─────────────────────────────────────────────────────────

    @staticmethod
    def gate_3_to_4(idea: Idea) -> GateResult:
        """
        Vestibule → The Codex.
        Requires: refined_form (≥120 chars), open_problems (≥60 chars),
                  next_actions (≥60 chars).
        """
        failures = []

        if len(idea.refined_form.strip()) < 120:
            remaining = 120 - len(idea.refined_form.strip())
            failures.append(f"Refined Form needs {remaining} more characters")

        if len(idea.open_problems.strip()) < 60:
            remaining = 60 - len(idea.open_problems.strip())
            failures.append(f"Open Problems needs {remaining} more characters")

        if len(idea.next_actions.strip()) < 60:
            remaining = 60 - len(idea.next_actions.strip())
            failures.append(f"Next Actions needs {remaining} more characters")

        return GateResult(passed=len(failures) == 0, failures=failures)

    # ── Gate IV — Declaration ─────────────────────────────────────────────────

    @staticmethod
    def gate_declaration(idea: Idea) -> GateResult:
        """
        Gate for declaring an idea complete from the Codex.
        Requires: declaration (≥80 chars), summary (≥60 chars).
        """
        failures = []

        if len(idea.declaration.strip()) < 80:
            remaining = 80 - len(idea.declaration.strip())
            failures.append(f"Declaration needs {remaining} more characters")

        if len(idea.summary.strip()) < 60:
            remaining = 60 - len(idea.summary.strip())
            failures.append(f"Summary needs {remaining} more characters")

        return GateResult(passed=len(failures) == 0, failures=failures)

    # ── Dispatch helper ───────────────────────────────────────────────────────

    @staticmethod
    def gate_for_current_chamber(idea: Idea) -> GateResult:
        """Returns the gate result for the idea's current chamber exit."""
        gates = {
            1: GateEngine.gate_1_to_2,
            2: GateEngine.gate_2_to_3,
            3: GateEngine.gate_3_to_4,
            4: GateEngine.gate_declaration,
        }
        fn = gates.get(idea.chamber)
        if fn is None:
            return GateResult(passed=True)
        return fn(idea)

    @staticmethod
    def progress_fraction(idea: Idea) -> float:
        """Returns 0.0–1.0 completion fraction for the current chamber gate."""
        result = GateEngine.gate_for_current_chamber(idea)
        if result.passed:
            return 1.0
        total = len(result.failures) + 1  # +1 so passed=0 never divides to 1.0
        met   = total - len(result.failures) - 1
        return max(0.0, met / total)
