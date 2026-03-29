"""
test_store.py — Dolium v2
IdeaStore CRUD, advance, return_to, cull, resurrect tests.
Uses a temporary directory — no side effects.
Run: python test_store.py
"""

import sys
import os
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
from models import Idea, CHAMBER_FOMENTARY, CHAMBER_CULTIVATION, CHAMBER_VESTIBULE, CHAMBER_CODEX
from store import IdeaStore


class TestIdeaStore(unittest.TestCase):

    def setUp(self):
        self._tmpdir = Path(tempfile.mkdtemp())
        self._store  = IdeaStore(self._tmpdir)

    def tearDown(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    # ── Create ────────────────────────────────────────────────────────────────

    def test_create_returns_idea(self):
        idea = self._store.create("Test Idea")
        self.assertEqual(idea.title, "Test Idea")
        self.assertEqual(idea.chamber, CHAMBER_FOMENTARY)
        self.assertFalse(idea.culled)

    def test_create_persists(self):
        idea = self._store.create("Persisted")
        store2 = IdeaStore(self._tmpdir)
        loaded = store2.get(idea.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Persisted")

    def test_create_multiple(self):
        self._store.create("Alpha")
        self._store.create("Beta")
        self._store.create("Gamma")
        self.assertEqual(len(self._store.all_active()), 3)

    # ── Get / Read ────────────────────────────────────────────────────────────

    def test_get_nonexistent_returns_none(self):
        self.assertIsNone(self._store.get("no-such-id"))

    def test_all_active_excludes_culled(self):
        a = self._store.create("Active")
        c = self._store.create("Culled")
        self._store.cull(c, "test")
        active = self._store.all_active()
        ids = [i.id for i in active]
        self.assertIn(a.id, ids)
        self.assertNotIn(c.id, ids)

    def test_by_chamber(self):
        a = self._store.create("In Fomentary")
        b = self._store.create("To Advance")
        b.body       = "x" * 100
        b.motivation = "x" * 60
        self._store.advance(b)
        fomentary = self._store.by_chamber(CHAMBER_FOMENTARY)
        cultivation = self._store.by_chamber(CHAMBER_CULTIVATION)
        self.assertIn(a.id, [i.id for i in fomentary])
        self.assertIn(b.id, [i.id for i in cultivation])

    # ── Update ────────────────────────────────────────────────────────────────

    def test_update_persists_field_change(self):
        idea = self._store.create("Update Test")
        idea.body = "A new body text."
        self._store.update(idea)

        store2  = IdeaStore(self._tmpdir)
        loaded  = store2.get(idea.id)
        self.assertEqual(loaded.body, "A new body text.")

    def test_update_touches_timestamp(self):
        import time
        idea   = self._store.create("Touch")
        before = idea.updated
        time.sleep(0.01)
        idea.body = "changed"
        self._store.update(idea)
        self.assertGreater(idea.updated, before)

    # ── Advance ───────────────────────────────────────────────────────────────

    def test_advance_increments_chamber(self):
        idea = self._store.create("Advancer")
        self.assertEqual(idea.chamber, CHAMBER_FOMENTARY)
        self._store.advance(idea)
        self.assertEqual(idea.chamber, CHAMBER_CULTIVATION)

    def test_advance_logs_transition(self):
        idea = self._store.create("Logger")
        self._store.advance(idea)
        self.assertEqual(len(idea.chamber_log), 1)
        self.assertEqual(idea.chamber_log[0].from_chamber, CHAMBER_FOMENTARY)
        self.assertEqual(idea.chamber_log[0].to_chamber,   CHAMBER_CULTIVATION)

    def test_advance_clamps_at_codex(self):
        idea = self._store.create("Ceiling")
        idea.chamber = CHAMBER_CODEX
        self._store.advance(idea)
        self.assertEqual(idea.chamber, CHAMBER_CODEX)

    def test_advance_persists(self):
        idea = self._store.create("Persist Advance")
        self._store.advance(idea)
        store2  = IdeaStore(self._tmpdir)
        loaded  = store2.get(idea.id)
        self.assertEqual(loaded.chamber, CHAMBER_CULTIVATION)

    # ── Return to ─────────────────────────────────────────────────────────────

    def test_return_to_earlier_chamber(self):
        idea = self._store.create("Returner")
        idea.chamber = CHAMBER_VESTIBULE
        self._store.update(idea)
        self._store.return_to(idea, CHAMBER_FOMENTARY)
        self.assertEqual(idea.chamber, CHAMBER_FOMENTARY)

    def test_return_to_logs_regression(self):
        idea = self._store.create("Regression")
        idea.chamber = CHAMBER_CULTIVATION
        self._store.update(idea)
        self._store.return_to(idea, CHAMBER_FOMENTARY)
        self.assertTrue(any(e.note == "returned" for e in idea.chamber_log))

    def test_return_to_same_chamber_no_op(self):
        idea = self._store.create("Same")
        idea.chamber = CHAMBER_CULTIVATION
        self._store.update(idea)
        prev_log_len = len(idea.chamber_log)
        self._store.return_to(idea, CHAMBER_CULTIVATION)
        self.assertEqual(idea.chamber, CHAMBER_CULTIVATION)
        self.assertEqual(len(idea.chamber_log), prev_log_len)

    def test_return_to_invalid_target_no_op(self):
        idea = self._store.create("Invalid")
        self._store.return_to(idea, 0)
        self.assertEqual(idea.chamber, CHAMBER_FOMENTARY)

    # ── Cull ──────────────────────────────────────────────────────────────────

    def test_cull_marks_idea(self):
        idea = self._store.create("Doomed")
        self._store.cull(idea, "not viable")
        self.assertTrue(idea.culled)

    def test_cull_creates_record(self):
        idea   = self._store.create("Culled One")
        record = self._store.cull(idea, "no good")
        self.assertEqual(record.idea_id, idea.id)
        self.assertEqual(record.reason, "no good")

    def test_cull_record_persists(self):
        idea = self._store.create("Cull Persist")
        self._store.cull(idea, "stale")
        store2   = IdeaStore(self._tmpdir)
        records  = store2.cull_records()
        self.assertTrue(any(r.idea_id == idea.id for r in records))

    def test_cull_excluded_from_active(self):
        idea = self._store.create("Gone")
        self._store.cull(idea, "bye")
        active = [i.id for i in self._store.all_active()]
        self.assertNotIn(idea.id, active)

    def test_all_culled(self):
        a = self._store.create("A")
        b = self._store.create("B")
        self._store.cull(a, "r")
        self._store.cull(b, "r")
        culled_ids = [i.id for i in self._store.all_culled()]
        self.assertIn(a.id, culled_ids)
        self.assertIn(b.id, culled_ids)

    # ── Resurrect ─────────────────────────────────────────────────────────────

    def test_resurrect_unculls(self):
        idea = self._store.create("Phoenix")
        self._store.cull(idea, "test")
        self.assertTrue(idea.culled)
        resurrected = self._store.resurrect(idea.id)
        self.assertIsNotNone(resurrected)
        self.assertFalse(resurrected.culled)

    def test_resurrect_removes_cull_record(self):
        idea = self._store.create("Record Gone")
        self._store.cull(idea, "test")
        self._store.resurrect(idea.id)
        records = self._store.cull_records()
        self.assertFalse(any(r.idea_id == idea.id for r in records))

    def test_resurrect_nonexistent_returns_none(self):
        result = self._store.resurrect("no-such-id")
        self.assertIsNone(result)

    def test_resurrect_appears_in_active(self):
        idea = self._store.create("Back")
        self._store.cull(idea, "gone")
        self._store.resurrect(idea.id)
        active_ids = [i.id for i in self._store.all_active()]
        self.assertIn(idea.id, active_ids)

    # ── Corruption recovery ───────────────────────────────────────────────────

    def test_corrupt_ideas_json_creates_backup(self):
        ideas_path = self._tmpdir / "ideas.json"
        ideas_path.write_text("{ not valid json !!!", encoding="utf-8")
        store2 = IdeaStore(self._tmpdir)
        self.assertIsNotNone(store2.load_error)
        self.assertTrue((self._tmpdir / "ideas.json.bak").exists())
        self.assertEqual(store2.all_active(), [])

    # ── Delete ────────────────────────────────────────────────────────────────

    def test_delete_permanently(self):
        idea = self._store.create("Permanent Delete")
        result = self._store.delete_permanently(idea.id)
        self.assertTrue(result)
        self.assertIsNone(self._store.get(idea.id))

    def test_delete_nonexistent_returns_false(self):
        result = self._store.delete_permanently("ghost")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
