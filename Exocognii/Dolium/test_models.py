"""
test_models.py — Dolium v2
Round-trip serialization tests for all dataclasses.
Run: python test_models.py
"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from models import (
    Idea, ChamberLog, CullRecord, ConversationTurn,
    CHAMBER_FOMENTARY, CHAMBER_CULTIVATION, CHAMBER_VESTIBULE, CHAMBER_CODEX,
    CHAMBER_NAMES,
)


class TestChamberLog(unittest.TestCase):

    def test_round_trip(self):
        log = ChamberLog(from_chamber=1, to_chamber=2, note="test note")
        d   = log.to_dict()
        log2 = ChamberLog.from_dict(d)
        self.assertEqual(log2.from_chamber, 1)
        self.assertEqual(log2.to_chamber, 2)
        self.assertEqual(log2.note, "test note")
        self.assertEqual(log2.timestamp, log.timestamp)

    def test_defaults(self):
        log = ChamberLog(from_chamber=2, to_chamber=3)
        self.assertEqual(log.note, "")
        self.assertTrue(log.timestamp)  # auto-populated

    def test_from_dict_missing_optional(self):
        log = ChamberLog.from_dict({"from_chamber": 1, "to_chamber": 2})
        self.assertEqual(log.note, "")


class TestCullRecord(unittest.TestCase):

    def test_round_trip(self):
        rec  = CullRecord(idea_id="abc-123", reason="not viable", chamber=2)
        d    = rec.to_dict()
        rec2 = CullRecord.from_dict(d)
        self.assertEqual(rec2.idea_id, "abc-123")
        self.assertEqual(rec2.reason, "not viable")
        self.assertEqual(rec2.chamber, 2)

    def test_defaults(self):
        rec = CullRecord(idea_id="x", reason="reason")
        self.assertEqual(rec.chamber, 1)
        self.assertTrue(rec.timestamp)


class TestConversationTurn(unittest.TestCase):

    def test_round_trip_user(self):
        turn  = ConversationTurn(role="user", content="what is this?")
        d     = turn.to_dict()
        turn2 = ConversationTurn.from_dict(d)
        self.assertEqual(turn2.role, "user")
        self.assertEqual(turn2.content, "what is this?")
        self.assertFalse(turn2.is_whisper)

    def test_round_trip_whisper(self):
        turn  = ConversationTurn(role="assistant", content="a marginal observation", is_whisper=True)
        d     = turn.to_dict()
        turn2 = ConversationTurn.from_dict(d)
        self.assertTrue(turn2.is_whisper)
        self.assertEqual(turn2.content, "a marginal observation")

    def test_is_whisper_defaults_false(self):
        turn = ConversationTurn.from_dict({"role": "assistant", "content": "hello"})
        self.assertFalse(turn.is_whisper)


class TestIdea(unittest.TestCase):

    def _make_idea(self) -> Idea:
        idea = Idea(title="Test Idea")
        idea.body       = "This is the body of the idea, quite detailed."
        idea.motivation = "Because it matters."
        idea.tags       = ["one", "two"]
        idea.chamber_log.append(ChamberLog(from_chamber=1, to_chamber=2))
        idea.conversation.append(ConversationTurn(role="user", content="hello"))
        idea.conversation.append(ConversationTurn(role="assistant", content="noted", is_whisper=True))
        return idea

    def test_round_trip_full(self):
        idea  = self._make_idea()
        d     = idea.to_dict()
        idea2 = Idea.from_dict(d)

        self.assertEqual(idea2.id,    idea.id)
        self.assertEqual(idea2.title, "Test Idea")
        self.assertEqual(idea2.body,  idea.body)
        self.assertEqual(idea2.tags,  ["one", "two"])
        self.assertFalse(idea2.culled)

        self.assertEqual(len(idea2.chamber_log), 1)
        self.assertEqual(idea2.chamber_log[0].to_chamber, 2)

        self.assertEqual(len(idea2.conversation), 2)
        self.assertEqual(idea2.conversation[0].role, "user")
        self.assertTrue(idea2.conversation[1].is_whisper)

    def test_empty_idea_round_trip(self):
        idea  = Idea()
        d     = idea.to_dict()
        idea2 = Idea.from_dict(d)
        self.assertEqual(idea2.chamber, CHAMBER_FOMENTARY)
        self.assertEqual(idea2.tags, [])
        self.assertEqual(idea2.conversation, [])
        self.assertFalse(idea2.culled)

    def test_from_dict_missing_fields(self):
        """from_dict must not raise on a partial dict (forward-compat)."""
        idea = Idea.from_dict({"id": "x", "title": "Sparse"})
        self.assertEqual(idea.title, "Sparse")
        self.assertEqual(idea.body, "")
        self.assertEqual(idea.chamber, CHAMBER_FOMENTARY)

    def test_touch_updates_timestamp(self):
        idea = Idea(title="Touch Test")
        before = idea.updated
        import time; time.sleep(0.01)
        idea.touch()
        self.assertGreater(idea.updated, before)

    def test_chamber_name(self):
        idea = Idea()
        roman = {1: "I", 2: "II", 3: "III", 4: "IV"}
        for n in (1, 2, 3, 4):
            idea.chamber = n
            self.assertIn(roman[n], idea.chamber_name())

    def test_char_count(self):
        idea = Idea()
        self.assertEqual(idea.char_count("  hello  "), 5)
        self.assertEqual(idea.char_count(""), 0)

    def test_culled_flag_survives_round_trip(self):
        idea = Idea(title="Doomed")
        idea.culled = True
        idea2 = Idea.from_dict(idea.to_dict())
        self.assertTrue(idea2.culled)

    def test_chamber_constants(self):
        self.assertEqual(CHAMBER_FOMENTARY,   1)
        self.assertEqual(CHAMBER_CULTIVATION, 2)
        self.assertEqual(CHAMBER_VESTIBULE,   3)
        self.assertEqual(CHAMBER_CODEX,       4)
        self.assertEqual(len(CHAMBER_NAMES),  4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
