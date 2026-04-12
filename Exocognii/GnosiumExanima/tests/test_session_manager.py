# GNOSIUM EXANIMA — tests/test_session_manager.py
# v1.0.0

from __future__ import annotations

from pathlib import Path

import pytest

from Exocognii.GnosiumExanima.constants import MODE_CHAMBER
from Exocognii.GnosiumExanima.session.manager import SessionManager
from Exocognii.GnosiumExanima.session.store import SessionStore


@pytest.fixture
def mgr(tmp_path: Path):
    store = SessionStore(tmp_path / "g.db")
    yield SessionManager(store)
    store.close()


def test_get_or_create_current(mgr: SessionManager) -> None:
    s1 = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    s2 = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    assert s1.id == s2.id


def test_entity_roster_update(mgr: SessionManager) -> None:
    s1 = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    s2 = mgr.get_or_create_current(MODE_CHAMBER, ["a", "b"])
    assert s1.id == s2.id
    assert s2.active_entities == ["a", "b"]


def test_auto_title_applied(mgr: SessionManager) -> None:
    s = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    title = mgr.apply_auto_title_if_needed(s, "Hello there, entities")
    assert title == "Hello there, entities"
    assert s.title == "Hello there, entities"


def test_auto_title_truncates_long(mgr: SessionManager) -> None:
    s = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    long = "x" * 200
    title = mgr.apply_auto_title_if_needed(s, long)
    assert title.endswith("…")
    assert len(title) <= 60


def test_auto_title_skipped_if_present(mgr: SessionManager) -> None:
    s = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    s.title = "existing"
    assert mgr.apply_auto_title_if_needed(s, "new text") is None


def test_new_session(mgr: SessionManager) -> None:
    a = mgr.get_or_create_current(MODE_CHAMBER, ["a"])
    b = mgr.new_session(MODE_CHAMBER, ["a"])
    assert a.id != b.id
