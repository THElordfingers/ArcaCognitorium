"""
Phase 3 — Grimoire Test Suite
Run: pytest tests/test_phase3_grimoire.py -v
"""
import pytest
from pathlib import Path
import json


# ── GrimoireEntry Tests ───────────────────────────────────────────────────

def test_grimoire_entry_create_generates_id():
    """GrimoireEntry.create() produces a valid entry_id."""
    from memory.grimoire import GrimoireEntry
    e = GrimoireEntry.create("I prefer terse answers", "style")
    assert e.entry_id.startswith("grim_")
    assert len(e.entry_id) > 10
    assert e.active == True
    assert e.source == "manual"

def test_grimoire_entry_create_with_tags():
    """GrimoireEntry.create() preserves tags."""
    from memory.grimoire import GrimoireEntry
    e = GrimoireEntry.create("step-by-step", "style", tags=["preference"])
    assert "preference" in e.tags


# ── Grimoire CRUD Tests ───────────────────────────────────────────────────

def test_grimoire_add_persists(tmp_path):
    """add() persists entry to disk immediately."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    g.add("I prefer terse answers", "style")
    # Reload from disk
    g2 = Grimoire(store_path=tmp_path / "grimoire.json")
    assert len(g2.get_active()) == 1
    assert g2.get_active()[0].content == "I prefer terse answers"

def test_grimoire_remove_soft_deletes(tmp_path):
    """remove() deactivates but does not delete the entry."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    entry = g.add("I prefer terse answers", "style")
    result = g.remove(entry.entry_id)
    assert result == True
    assert len(g.get_active()) == 0
    assert len(g.get_all()) == 1  # Still in store
    assert g.get_all()[0].active == False

def test_grimoire_restore_reactivates(tmp_path):
    """restore() re-activates a soft-deleted entry."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    entry = g.add("test content", "style")
    g.remove(entry.entry_id)
    g.restore(entry.entry_id)
    assert len(g.get_active()) == 1

def test_grimoire_remove_returns_false_for_unknown_id(tmp_path):
    """remove() returns False for unknown entry_id."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    assert g.remove("grim_nonexistent_0000") == False

def test_grimoire_edit_updates_content(tmp_path):
    """edit() updates content and persists."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    entry = g.add("old content", "style")
    g.edit(entry.entry_id, "new content")
    assert g.get_active()[0].content == "new content"


# ── Injection String Tests ────────────────────────────────────────────────

def test_build_injection_string_empty_when_no_entries(tmp_path):
    """build_injection_string() returns empty string with no active entries."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    assert g.build_injection_string() == ""

def test_build_injection_string_contains_entry_content(tmp_path):
    """build_injection_string() includes active entry content."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    g.add("I prefer bullet points", "style")
    result = g.build_injection_string()
    assert "I prefer bullet points" in result
    assert "GRIMOIRE" in result

def test_build_injection_string_excludes_inactive(tmp_path):
    """build_injection_string() excludes inactive entries."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    entry = g.add("should be excluded", "style")
    g.remove(entry.entry_id)
    assert g.build_injection_string() == ""

def test_build_injection_string_respects_token_budget(tmp_path):
    """build_injection_string() stays within token budget."""
    from memory.grimoire import Grimoire
    # Very small budget to force truncation
    g = Grimoire(store_path=tmp_path / "grimoire.json",
                 max_injection_tokens=30)
    g.add("First entry — short", "style")
    g.add("Second entry — this one is quite long and should not fit", "work")
    result = g.build_injection_string()
    estimated = g._estimate_tokens(result)
    assert estimated <= 30

def test_token_budget_oldest_entries_prioritized(tmp_path):
    """Oldest entries are included first when budget is tight."""
    from memory.grimoire import Grimoire
    import time
    g = Grimoire(store_path=tmp_path / "grimoire.json",
                 max_injection_tokens=40)
    e1 = g.add("First oldest entry", "style")  # Added first = oldest
    time.sleep(0.01)
    e2 = g.add("Second newer entry that may not fit if budget tight", "work")
    result = g.build_injection_string()
    assert "First oldest entry" in result


# ── Persistence & Recovery Tests ─────────────────────────────────────────

def test_grimoire_atomic_write(tmp_path):
    """_save() does not leave .tmp file on successful write."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    g.add("test", "style")
    tmp_file = tmp_path / "grimoire.tmp"
    assert not tmp_file.exists(), ".tmp file left behind after save"

def test_grimoire_loads_empty_on_missing_file(tmp_path):
    """Grimoire initializes empty when file absent — not an error."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "nonexistent.json")
    assert g.get_active() == []

def test_grimoire_handles_corrupt_json(tmp_path):
    """Corrupt grimoire.json is backed up and Grimoire initializes empty."""
    from memory.grimoire import Grimoire
    store = tmp_path / "grimoire.json"
    store.write_text("{corrupt json{{{")
    g = Grimoire(store_path=store)
    assert g.get_active() == []
    bak = tmp_path / "grimoire.json.bak"
    assert bak.exists(), "Corrupt file not backed up"


# ── Token Usage Tests ────────────────────────────────────────────────────

def test_token_usage_returns_correct_structure(tmp_path):
    """token_usage() returns dict with expected keys."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    usage = g.token_usage()
    assert "used" in usage
    assert "budget" in usage
    assert "pct" in usage
    assert "entry_count" in usage

def test_token_usage_empty_grimoire(tmp_path):
    """Empty Grimoire reports 0 tokens used."""
    from memory.grimoire import Grimoire
    g = Grimoire(store_path=tmp_path / "grimoire.json")
    usage = g.token_usage()
    assert usage["used"] == 0
    assert usage["entry_count"] == 0
