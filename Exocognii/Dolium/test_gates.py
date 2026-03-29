"""
test_gates.py — Dolium v2
Gate function tests — passing and failing conditions for all four chambers.
Run: python test_gates.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from models import Idea, CHAMBER_FOMENTARY, CHAMBER_CULTIVATION, CHAMBER_VESTIBULE, CHAMBER_CODEX
from chambers import GateEngine, GateResult


def _idea_with(**kwargs) -> Idea:
    """Helper: make an Idea with specific field values."""
    idea = Idea(title="Test")
    for k, v in kwargs.items():
        setattr(idea, k, v)
    return idea


class TestGate1To2(unittest.TestCase):
    """Fomentary → Cultivation House."""

    def test_passes_with_all_fields(self):
        idea = _idea_with(
            title      = "Valid Title",
            body       = "x" * 100,
            motivation = "y" * 60,
        )
        result = GateEngine.gate_1_to_2(idea)
        self.assertTrue(result.passed)
        self.assertEqual(result.failures, [])

    def test_fails_empty_title(self):
        idea = _idea_with(title="", body="x" * 100, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Title" in f for f in result.failures))

    def test_fails_whitespace_title(self):
        idea = _idea_with(title="   ", body="x" * 100, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Title" in f for f in result.failures))

    def test_fails_body_too_short(self):
        idea = _idea_with(title="T", body="x" * 50, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Body" in f for f in result.failures))

    def test_body_exactly_100_passes(self):
        idea = _idea_with(title="T", body="x" * 100, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertTrue(result.passed)

    def test_body_99_fails(self):
        idea = _idea_with(title="T", body="x" * 99, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)

    def test_fails_motivation_too_short(self):
        idea = _idea_with(title="T", body="x" * 100, motivation="y" * 30)
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Motivation" in f for f in result.failures))

    def test_motivation_exactly_60_passes(self):
        idea = _idea_with(title="T", body="x" * 100, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        self.assertTrue(result.passed)

    def test_multiple_failures_reported(self):
        idea = _idea_with(title="", body="", motivation="")
        result = GateEngine.gate_1_to_2(idea)
        self.assertFalse(result.passed)
        self.assertEqual(len(result.failures), 3)

    def test_failure_message_includes_remaining_chars(self):
        idea = _idea_with(title="T", body="x" * 50, motivation="y" * 60)
        result = GateEngine.gate_1_to_2(idea)
        body_failure = next(f for f in result.failures if "Body" in f)
        self.assertIn("50", body_failure)  # 100 - 50 = 50 remaining


class TestGate2To3(unittest.TestCase):
    """Cultivation House → Vestibule."""

    def test_passes_with_all_fields(self):
        idea = _idea_with(
            elaboration = "e" * 150,
            obstacles   = "o" * 60,
            first_step  = "f" * 40,
        )
        result = GateEngine.gate_2_to_3(idea)
        self.assertTrue(result.passed)

    def test_fails_elaboration_short(self):
        idea = _idea_with(elaboration="e" * 100, obstacles="o" * 60, first_step="f" * 40)
        result = GateEngine.gate_2_to_3(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Elaboration" in f for f in result.failures))

    def test_fails_obstacles_short(self):
        idea = _idea_with(elaboration="e" * 150, obstacles="o" * 30, first_step="f" * 40)
        result = GateEngine.gate_2_to_3(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Obstacles" in f for f in result.failures))

    def test_fails_first_step_short(self):
        idea = _idea_with(elaboration="e" * 150, obstacles="o" * 60, first_step="f" * 10)
        result = GateEngine.gate_2_to_3(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("First Step" in f for f in result.failures))

    def test_elaboration_exactly_150_passes(self):
        idea = _idea_with(elaboration="e" * 150, obstacles="o" * 60, first_step="f" * 40)
        result = GateEngine.gate_2_to_3(idea)
        self.assertTrue(result.passed)

    def test_first_step_exactly_40_passes(self):
        idea = _idea_with(elaboration="e" * 150, obstacles="o" * 60, first_step="f" * 40)
        result = GateEngine.gate_2_to_3(idea)
        self.assertTrue(result.passed)


class TestGate3To4(unittest.TestCase):
    """Vestibule → The Codex."""

    def test_passes_with_all_fields(self):
        idea = _idea_with(
            refined_form  = "r" * 120,
            open_problems = "p" * 60,
            next_actions  = "n" * 60,
        )
        result = GateEngine.gate_3_to_4(idea)
        self.assertTrue(result.passed)

    def test_fails_refined_form_short(self):
        idea = _idea_with(refined_form="r" * 50, open_problems="p" * 60, next_actions="n" * 60)
        result = GateEngine.gate_3_to_4(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Refined Form" in f for f in result.failures))

    def test_fails_open_problems_short(self):
        idea = _idea_with(refined_form="r" * 120, open_problems="p" * 10, next_actions="n" * 60)
        result = GateEngine.gate_3_to_4(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Open Problems" in f for f in result.failures))

    def test_fails_next_actions_short(self):
        idea = _idea_with(refined_form="r" * 120, open_problems="p" * 60, next_actions="n" * 5)
        result = GateEngine.gate_3_to_4(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Next Actions" in f for f in result.failures))

    def test_all_fail_empty(self):
        idea = _idea_with(refined_form="", open_problems="", next_actions="")
        result = GateEngine.gate_3_to_4(idea)
        self.assertFalse(result.passed)
        self.assertEqual(len(result.failures), 3)


class TestGateDeclaration(unittest.TestCase):
    """The Codex — Declaration gate."""

    def test_passes_with_all_fields(self):
        idea = _idea_with(declaration="d" * 80, summary="s" * 60)
        result = GateEngine.gate_declaration(idea)
        self.assertTrue(result.passed)

    def test_fails_declaration_short(self):
        idea = _idea_with(declaration="d" * 20, summary="s" * 60)
        result = GateEngine.gate_declaration(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Declaration" in f for f in result.failures))

    def test_fails_summary_short(self):
        idea = _idea_with(declaration="d" * 80, summary="s" * 10)
        result = GateEngine.gate_declaration(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Summary" in f for f in result.failures))

    def test_exactly_at_thresholds_passes(self):
        idea = _idea_with(declaration="d" * 80, summary="s" * 60)
        result = GateEngine.gate_declaration(idea)
        self.assertTrue(result.passed)


class TestGateDispatch(unittest.TestCase):
    """gate_for_current_chamber dispatch."""

    def test_dispatches_chamber_1(self):
        idea = Idea(title="T", chamber=1)
        result = GateEngine.gate_for_current_chamber(idea)
        self.assertIsInstance(result, GateResult)

    def test_dispatches_chamber_4(self):
        idea = Idea(title="T", chamber=4)
        result = GateEngine.gate_for_current_chamber(idea)
        self.assertIsInstance(result, GateResult)

    def test_whitespace_body_does_not_pass(self):
        """Whitespace-only fields should not satisfy char requirements."""
        idea = _idea_with(
            title      = "T",
            body       = " " * 200,  # lots of whitespace but strip() → 0 chars
            motivation = "m" * 60,
        )
        idea.chamber = 1
        result = GateEngine.gate_for_current_chamber(idea)
        self.assertFalse(result.passed)
        self.assertTrue(any("Body" in f for f in result.failures))

    def test_progress_fraction_zero_when_all_fail(self):
        idea = Idea(title="", chamber=1)
        frac = GateEngine.progress_fraction(idea)
        self.assertGreaterEqual(frac, 0.0)
        self.assertLessEqual(frac, 1.0)

    def test_progress_fraction_one_when_passed(self):
        idea = _idea_with(
            title="T", body="x" * 100, motivation="y" * 60, chamber=1
        )
        idea.chamber = 1
        frac = GateEngine.progress_fraction(idea)
        self.assertEqual(frac, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
