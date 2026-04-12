# GNOSIUM EXANIMA — tests/test_composite_prompt.py
# v1.0.0
"""Composite prompt builder — chamber, solo, mundana context, tokens."""

from __future__ import annotations

from pathlib import Path

from Exocognii.GnosiumExanima.constants import VAULT_FORMAT_JSON
from Exocognii.GnosiumExanima.entity.models import EntityPackage
from Exocognii.GnosiumExanima.prompt.composite import (
    build_chamber_prompt, build_solo_prompt,
)
from Exocognii.GnosiumExanima.prompt.tokens import estimate_tokens


def _fake_entity(entity_id: str, display_name: str) -> EntityPackage:
    return EntityPackage(
        entity_id=entity_id,
        display_name=display_name,
        source_path=Path("/tmp"),
        source_format=VAULT_FORMAT_JSON,
        role_text=f"Role of {display_name}",
        traits_text=f"verbosity: 0.5\nprecision: 0.7",
        lore_text=f"Origin: {display_name} arrived.",
    )


def test_chamber_prompt_includes_all_entities() -> None:
    ents = [_fake_entity("a", "Alpha"), _fake_entity("b", "Beta")]
    prompt = build_chamber_prompt(ents)
    assert "ENTITY: Alpha" in prompt
    assert "ENTITY: Beta" in prompt
    assert "GNOSIUM EXANIMA chamber" in prompt
    assert "square brackets" in prompt


def test_chamber_preserves_order() -> None:
    ents = [_fake_entity("a", "Alpha"), _fake_entity("b", "Beta")]
    prompt = build_chamber_prompt(ents)
    assert prompt.index("Alpha") < prompt.index("Beta")


def test_chamber_with_mundana_context() -> None:
    ents = [_fake_entity("a", "Alpha")]
    prompt = build_chamber_prompt(ents, mundana_context="palette=void")
    assert "AMBIENT CONTEXT" in prompt
    assert "palette=void" in prompt


def test_chamber_empty_entity_list() -> None:
    prompt = build_chamber_prompt([])
    assert "No entities" in prompt


def test_solo_prompt_is_first_person() -> None:
    ent = _fake_entity("solo", "Solo One")
    prompt = build_solo_prompt(ent)
    assert "You are Solo One" in prompt
    assert "ENTITY: Solo One" in prompt


def test_estimate_tokens() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello") >= 1
    # Chamber prompt should be in the thousand-token range even for 2 entities
    ents = [_fake_entity(f"e{i}", f"Entity{i}") for i in range(2)]
    t = estimate_tokens(build_chamber_prompt(ents))
    assert 100 < t < 5000
