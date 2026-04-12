# GNOSIUM EXANIMA — prompt/composite.py
# v1.0.0
"""
Composite system prompt assembly for Chamber and Solo modes.

Chamber mode drops multiple entities into a single ClaudeBox with a
preamble that instructs the model to voice whichever entity (or
entities) has something to say, prefixing each contribution with the
entity's display name in square brackets. This yields personality-
driven self-selection without per-entity API calls.

Solo mode strips the preamble and keeps only the target entity's block.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from ..entity.models import EntityPackage
from .tower_memory import read_tower_memory


CHAMBER_PREAMBLE = """\
You are operating in the GNOSIUM EXANIMA chamber.

Multiple entities are present. For each response, speak as whichever
entity or entities have something relevant to contribute. Prefix each
entity's speech with their display name in square brackets, one entity
per block, for example:

    [The Contrarian] I disagree because...
    [The Socratic]   But have you considered...

If the Wizard addresses an entity by name — for example "Contrarian,
what do you think?" — that entity responds first. Others may follow if
they have something relevant to add.

If no entity has a strong opinion on what the Wizard has said, say so
briefly and stop. Do not force participation. Do not summarise the
others' positions. Do not narrate stage directions. Speak as the
entity, not about the entity.

Each entity's definition appears below. Stay inside the behavioural
envelope their role and traits describe. When the Wizard's lore_origin
or lore_nature is relevant, reach for it. Do not invent new lore.
"""


SOLO_PREAMBLE_TEMPLATE = """\
You are {display_name} ({entity_id}).

Your role, traits, and lore are given below. Stay inside that
envelope. Speak in the first person. Do not narrate stage directions.
Do not refer to yourself in the third person. Do not invent lore
outside what is given.
"""


def build_chamber_prompt(
    entities: Iterable[EntityPackage],
    *,
    mundana_context: Optional[str] = None,
    tower_memory_root: Optional[Path] = None,
) -> str:
    """
    Assemble the Chamber composite prompt.

    Args:
        entities:          Active entities, in display order.
        mundana_context:   Optional ambient state summary block. Injected
                           beneath the entity blocks only if non-empty.
        tower_memory_root: Optional path to ~/ArcaCognitorium/storage/entities/.
                           If provided, per-entity memory.json contents
                           are seeded into their prompt sections.

    Returns:
        The assembled prompt string.
    """
    entity_list = list(entities)
    if not entity_list:
        # Defensive — caller should have routed to empty-vault view.
        return CHAMBER_PREAMBLE + "\n(No entities are currently active.)"

    sections: list[str] = [CHAMBER_PREAMBLE.strip(), ""]
    for entity in entity_list:
        memory = None
        if tower_memory_root is not None:
            memory = read_tower_memory(tower_memory_root, entity.entity_id)
        sections.append(entity.prompt_section(tower_memory=memory))

    if mundana_context and mundana_context.strip():
        sections.append("─── AMBIENT CONTEXT ───")
        sections.append(mundana_context.strip())
        sections.append("")

    return "\n".join(sections)


def build_solo_prompt(
    entity: EntityPackage,
    *,
    tower_memory_root: Optional[Path] = None,
) -> str:
    """Assemble the Solo prompt for a single entity."""
    preamble = SOLO_PREAMBLE_TEMPLATE.format(
        display_name=entity.display_name,
        entity_id=entity.entity_id,
    )
    memory = None
    if tower_memory_root is not None:
        memory = read_tower_memory(tower_memory_root, entity.entity_id)
    return "\n".join([preamble.strip(), "", entity.prompt_section(tower_memory=memory)])
