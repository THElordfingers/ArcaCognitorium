# GNOSIUM EXANIMA — tests/test_store.py
# v1.0.0
"""SQLite store CRUD."""

from __future__ import annotations

from pathlib import Path

import pytest

from Exocognii.GnosiumExanima.constants import MODE_CHAMBER, MODE_SOLO
from Exocognii.GnosiumExanima.session.store import SessionStore


@pytest.fixture
def store(tmp_path: Path) -> SessionStore:
    s = SessionStore(tmp_path / "g.db")
    yield s
    s.close()


def test_create_session_is_current(store: SessionStore) -> None:
    row = store.create_session(MODE_CHAMBER, ["a", "b"])
    assert row.is_current
    assert row.active_entities == ["a", "b"]
    assert store.current_session(MODE_CHAMBER).id == row.id


def test_only_one_current_per_mode(store: SessionStore) -> None:
    a = store.create_session(MODE_CHAMBER, ["x"])
    b = store.create_session(MODE_CHAMBER, ["y"])
    current = store.current_session(MODE_CHAMBER)
    assert current.id == b.id
    # a should no longer be current
    a_reloaded = store.get_session(a.id)
    assert a_reloaded.is_current is False


def test_modes_isolated(store: SessionStore) -> None:
    c = store.create_session(MODE_CHAMBER, ["x"])
    s = store.create_session(MODE_SOLO, ["y"])
    assert store.current_session(MODE_CHAMBER).id == c.id
    assert store.current_session(MODE_SOLO).id == s.id


def test_messages_and_count(store: SessionStore) -> None:
    row = store.create_session(MODE_CHAMBER, ["a"])
    for i in range(5):
        store.append_message(row.id, "wizard", f"msg{i}")
    assert store.message_count(row.id) == 5
    messages = store.load_messages(row.id)
    assert [m.content for m in messages] == [f"msg{i}" for i in range(5)]


def test_distillation(store: SessionStore) -> None:
    row = store.create_session(MODE_CHAMBER, ["a"])
    m1 = store.append_message(row.id, "wizard", "a")
    m2 = store.append_message(row.id, "entity", "b")
    store.write_distillation(row.id, "summary", m1.id, m2.id, token_estimate=10)
    distillations = store.load_distillations(row.id)
    assert len(distillations) == 1
    assert distillations[0].summary == "summary"
    assert distillations[0].token_estimate == 10


def test_delete_cascade(store: SessionStore) -> None:
    row = store.create_session(MODE_CHAMBER, ["a"])
    store.append_message(row.id, "wizard", "msg")
    store.delete_session(row.id)
    assert store.message_count(row.id) == 0
    assert store.get_session(row.id) is None


def test_update_title_and_entities(store: SessionStore) -> None:
    row = store.create_session(MODE_CHAMBER, ["a"])
    store.update_session(row.id, title="new title", active_entities=["a", "b"])
    reloaded = store.get_session(row.id)
    assert reloaded.title == "new title"
    assert reloaded.active_entities == ["a", "b"]


def test_touch_entity_idempotent(store: SessionStore) -> None:
    store.touch_entity("a")
    store.touch_entity("a")  # no exception
