# GNOSIUM EXANIMA — connectivity/context_assembler.py
# v1.0.0
"""
Context Assembler — queries Perpetuum and Exvacua, formats results
for injection into composite system prompts.

All queries degrade silently. If a service is down, the corresponding
context section is omitted from the prompt — never blocks.
"""

from __future__ import annotations

import logging
from typing import Optional

from .cognosis import CognosisClient, CognosisError

logger = logging.getLogger("gnosium.context_assembler")


class ContextAssembler:
    """Assembles ambient context from Perpetuum and Exvacua for prompt injection."""

    def __init__(self, cognosis: CognosisClient) -> None:
        self._cognosis = cognosis

    def perpetuum_summary(self) -> Optional[str]:
        """
        Query Perpetuum /build/nodi for active build nodes.
        Returns a formatted summary string, or None on failure.
        """
        try:
            data = self._cognosis.build_nodes()
        except CognosisError as e:
            logger.debug("Perpetuum query failed: %s", e)
            return None

        if not data:
            return None

        # Handle list of nodi or paginated response
        nodi = data if isinstance(data, list) else data.get("nodi", data.get("items", []))
        if not nodi:
            return None

        lines = ["Active build nodes (from Perpetuum Aedificare):"]
        for node in nodi[:10]:  # cap at 10 to limit token cost
            title = node.get("title", "untitled")
            status = node.get("status", "?")
            nodicum = node.get("nodicum", "")
            lines.append(f"  - [{status}] {title}" + (f" ({nodicum})" if nodicum else ""))

        questions = []
        for node in nodi[:5]:
            for q in (node.get("open_questions") or []):
                questions.append(f"  ? {q}")
        if questions:
            lines.append("Open questions:")
            lines.extend(questions[:5])

        return "\n".join(lines)

    def exvacua_summary(self) -> Optional[str]:
        """
        Query Exvacua /cards for ratified lore cards.
        Returns a formatted summary string, or None on failure.
        """
        try:
            data = self._cognosis.lore_search("")  # empty term = all
        except CognosisError as e:
            logger.debug("Exvacua query failed: %s", e)
            return None

        if not data:
            return None

        cards = data if isinstance(data, list) else data.get("cards", data.get("items", []))
        if not cards:
            return None

        lines = ["Ratified lore (from Exvacua Loricum):"]
        for card in cards[:8]:  # cap at 8
            title = card.get("title", card.get("heading", "untitled"))
            domain = card.get("domain", "")
            status = card.get("status", "")
            lines.append(f"  - {title}" + (f" [{domain}]" if domain else "") + (f" ({status})" if status else ""))

        return "\n".join(lines)
