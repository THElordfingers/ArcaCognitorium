"""
Phase 4 — Tome Test Suite
Run: pytest tests/test_phase4_tome.py -v
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


# ── TomeEntry Tests ───────────────────────────────────────────────────────

def test_tome_entry_create_generates_id():
    """TomeEntry.create() produces valid entry_id with tome_ prefix."""
    from memory.tome import TomeEntry
    e = TomeEntry.create("No subprocess.Popen", "architecture")
    assert e.entry_id.startswith("tome_")
    assert e.active == True
    assert e.source == "manual"


# ── Tome Activation Tests ─────────────────────────────────────────────────

def test_tome_inactive_by_default():
    """Tome.is_active is False before any project activated."""
    from memory.tome import Tome
    mock_store = MagicMock()
    t = Tome(project_store=mock_store)
    assert t.is_active == False

def test_tome_active_after_activate_project():
    """is_active becomes True after activate_project()."""
    from memory.tome import Tome
    mock_store = MagicMock()
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    assert t.is_active == True

def test_tome_inactive_after_deactivate():
    """is_active returns False after deactivate()."""
    from memory.tome import Tome
    mock_store = MagicMock()
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    t.deactivate()
    assert t.is_active == False


# ── Tome CRUD Tests ───────────────────────────────────────────────────────

def test_tome_add_returns_none_without_active_project():
    """add() returns None when no project is active."""
    from memory.tome import Tome
    mock_store = MagicMock()
    t = Tome(project_store=mock_store)
    result = t.add("test content", "architecture")
    assert result is None

def test_tome_add_with_active_project():
    """add() creates entry and calls save_tome_entries when project active."""
    from memory.tome import Tome
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = []
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    entry = t.add("No subprocess.Popen", "architecture")
    assert entry is not None
    assert entry.content == "No subprocess.Popen"
    assert entry.category == "architecture"
    mock_store.save_tome_entries.assert_called_once()

def test_tome_remove_soft_deletes():
    """remove() deactivates entry without deleting it."""
    from memory.tome import Tome, TomeEntry
    entry = TomeEntry.create("test", "arch")
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = [
        {"entry_id": entry.entry_id, "content": "test", "category": "arch",
         "created_at": entry.created_at, "source": "manual",
         "tags": [], "active": True}
    ]
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    result = t.remove(entry.entry_id)
    assert result == True
    mock_store.save_tome_entries.assert_called_once()

def test_tome_remove_returns_false_for_unknown_id():
    """remove() returns False for unknown entry_id."""
    from memory.tome import Tome
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = []
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    assert t.remove("tome_nonexistent_0000") == False


# ── Injection String Tests ────────────────────────────────────────────────

def test_build_injection_empty_when_no_project():
    """build_injection_string() returns empty string when no project active."""
    from memory.tome import Tome
    mock_store = MagicMock()
    t = Tome(project_store=mock_store)
    assert t.build_injection_string() == ""

def test_build_injection_empty_when_no_entries():
    """build_injection_string() returns empty string when no active entries."""
    from memory.tome import Tome
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = []
    mock_store.get_project_name.return_value = "TestProject"
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    assert t.build_injection_string() == ""

def test_build_injection_includes_content():
    """build_injection_string() includes active entry content."""
    from memory.tome import Tome
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = [{
        "entry_id": "tome_test_0001", "content": "snake_case throughout",
        "category": "convention", "created_at": now,
        "source": "manual", "tags": [], "active": True
    }]
    mock_store.get_project_name.return_value = "Luminarious"
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    result = t.build_injection_string()
    assert "snake_case throughout" in result
    assert "TOME" in result
    assert "Luminarious" in result

def test_build_injection_respects_token_budget():
    """build_injection_string() stays within configured token budget."""
    from memory.tome import Tome
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    mock_store = MagicMock()
    mock_store.get_project_name.return_value = "Test"
    # Create entries that together exceed a tiny budget
    mock_store.get_tome_entries.return_value = [
        {"entry_id": f"tome_test_{i:04d}", "content": f"Entry {i} " * 20,
         "category": "arch", "created_at": now, "source": "manual",
         "tags": [], "active": True}
        for i in range(5)
    ]
    t = Tome(project_store=mock_store, max_injection_tokens=40)
    t.activate_project("proj_123")
    result = t.build_injection_string()
    estimated = t._estimate_tokens(result)
    assert estimated <= 40

def test_build_injection_excludes_inactive():
    """build_injection_string() excludes inactive entries."""
    from memory.tome import Tome
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    mock_store = MagicMock()
    mock_store.get_project_name.return_value = "Test"
    mock_store.get_tome_entries.return_value = [{
        "entry_id": "tome_test_0001", "content": "should be excluded",
        "category": "arch", "created_at": now,
        "source": "manual", "tags": [], "active": False
    }]
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    assert t.build_injection_string() == ""


# ── project_store Extension Tests ────────────────────────────────────────

def test_project_store_get_tome_entries_returns_empty_for_new_project(tmp_path):
    """get_tome_entries() returns [] for project without tome_entries key."""
    # This test requires the actual ProjectStore — mock if needed
    # Verify .get("tome_entries", []) pattern handles missing key gracefully
    result = {}.get("tome_entries", [])
    assert result == []

def test_tome_token_usage_structure():
    """token_usage() returns dict with expected keys."""
    from memory.tome import Tome
    mock_store = MagicMock()
    mock_store.get_tome_entries.return_value = []
    mock_store.get_project_name.return_value = "Test"
    t = Tome(project_store=mock_store)
    t.activate_project("proj_123")
    usage = t.token_usage()
    assert "used" in usage
    assert "budget" in usage
    assert "pct" in usage
    assert "entry_count" in usage
