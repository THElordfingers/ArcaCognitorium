# GNOSIUM EXANIMA — entity/models.py
# v1.0.0
"""EntityPackage dataclass — the normalised in-memory form of a vault entry."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EntityPackage:
    """
    Normalised representation of a single entity package.

    Constructed by vault_scanner. Loaders for both entity.json and the
    legacy YAML triple collapse into this shape.
    """

    entity_id: str           # stable identifier (snake_case)
    display_name: str        # shown in panel and as [Prefix] in responses
    source_path: Path        # package directory
    source_format: str       # 'json' or 'yaml'

    # Prompt-section text blocks (already formatted for inclusion in a
    # system prompt — no further templating required)
    role_text: str
    traits_text: str
    lore_text: str = ""

    portrait_path: Optional[Path] = None

    # Raw payload, retained for debugging and future introspection
    raw: dict = field(default_factory=dict)

    # ── Rendering helpers ─────────────────────────────────────────
    def prompt_section(self, tower_memory: Optional[str] = None) -> str:
        """Build this entity's block inside the Chamber composite prompt."""
        parts = [f"─── ENTITY: {self.display_name} ({self.entity_id}) ───",
                 "ROLE:", self.role_text.strip(),
                 "",
                 "TRAITS:", self.traits_text.strip()]
        if self.lore_text.strip():
            parts += ["", "LORE:", self.lore_text.strip()]
        if tower_memory:
            parts += ["", "TOWER MEMORY:", tower_memory.strip()]
        parts.append("")
        return "\n".join(parts)
