# GNOSIUM EXANIMA — tests/test_integration.py
# v1.0.0
"""
Integration test — full message → persist → reload cycle with a
monkeypatched ClaudeBoxManager that does NOT touch the network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from Exocognii.GnosiumExanima.constants import MODE_CHAMBER, VAULT_FORMAT_JSON
from Exocognii.GnosiumExanima.entity.models import EntityPackage
from Exocognii.GnosiumExanima.prompt.composite import build_chamber_prompt
from Exocognii.GnosiumExanima.session.manager import SessionManager
from Exocognii.GnosiumExanima.session.store import SessionStore


def _fake_entity(eid: str) -> EntityPackage:
    return EntityPackage(
        entity_id=eid,
        display_name=eid.upper(),
        source_path=Path("/tmp"),
        source_format=VAULT_FORMAT_JSON,
        role_text=f"role for {eid}",
        traits_text="verbosity: 0.5",
    )


class _FakeBoxManager:
    """Minimal stand-in for ClaudeBoxManager — no network, deterministic."""

    def __init__(self):
        self.history: list = []
        self.system_prompt: str = ""
        self.rebuilt_count = 0

    def rebuild(self, system_prompt, history=None):
        self.system_prompt = system_prompt
        self.history = list(history or [])
        self.rebuilt_count += 1

    def send(self, text, *, on_token, on_complete, on_error):
        # Simulate streaming a canned response
        tokens = ["[TEST] ", "hello ", text]
        for t in tokens:
            on_token(type("T", (), {"text": t})())
        full = "".join(tokens)
        on_complete(type("R", (), {"text": full, "usage": None})())


def test_full_cycle(tmp_path: Path) -> None:
    db = tmp_path / "g.db"
    store = SessionStore(db)
    mgr = SessionManager(store)

    entity = _fake_entity("alpha")
    session = mgr.get_or_create_current(MODE_CHAMBER, [entity.entity_id])

    # Build prompt and "rebuild" the fake box
    box = _FakeBoxManager()
    prompt = build_chamber_prompt([entity])
    box.rebuild(prompt, history=store.load_messages(session.id))
    assert box.rebuilt_count == 1
    assert "alpha" in box.system_prompt.lower() or "ALPHA" in box.system_prompt

    # Append wizard message, run fake stream, persist entity response
    wizard_row = store.append_message(session.id, "wizard", "ping")
    collected: list[str] = []
    final_holder: list[object] = []

    def on_token(tok):
        collected.append(tok.text)

    def on_complete(resp):
        final_holder.append(resp)

    def on_error(exc):
        raise AssertionError(f"unexpected error: {exc}")

    box.send("ping", on_token=on_token, on_complete=on_complete, on_error=on_error)
    assert final_holder, "on_complete must fire"
    final_text = final_holder[0].text
    store.append_message(session.id, "entity", final_text)

    # Verify persistence
    messages = store.load_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "wizard"
    assert messages[1].role == "entity"
    assert "ping" in messages[1].content

    # Reopen store — simulate crash/restart
    store.close()
    store2 = SessionStore(db)
    mgr2 = SessionManager(store2)
    current = mgr2.get_or_create_current(MODE_CHAMBER, [entity.entity_id])
    assert current.id == session.id
    reloaded = store2.load_messages(current.id)
    assert len(reloaded) == 2
    store2.close()


def test_entity_toggle_rebuilds_prompt(tmp_path: Path) -> None:
    """Toggling entities rebuilds the prompt with the new roster."""
    store = SessionStore(tmp_path / "g.db")
    mgr = SessionManager(store)
    alpha = _fake_entity("alpha")
    beta = _fake_entity("beta")
    session = mgr.get_or_create_current(MODE_CHAMBER, [alpha.entity_id])

    box = _FakeBoxManager()
    box.rebuild(build_chamber_prompt([alpha]))
    assert "ALPHA" in box.system_prompt
    assert "BETA" not in box.system_prompt

    # Toggle beta on
    store.update_session(session.id, active_entities=["alpha", "beta"])
    box.rebuild(
        build_chamber_prompt([alpha, beta]),
        history=store.load_messages(session.id),
    )
    assert box.rebuilt_count == 2
    assert "BETA" in box.system_prompt
    store.close()
