#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/archivist_chronicler.py
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


"""
The Archivist — Background Chronicle Writer

The Archivist's observational role: watches conversations for significant
moments, patterns, and knowledge worth preserving in the long-term Chronicle.
Where the Assessor builds a portrait of the Wizard (who they are), the
Archivist preserves the record of what occurred (what happened).

The Assessor writes to the Grimoire — permanent identity layer.
The Archivist writes to the Chronicle — retrievable long-term memory.

Both are silent background operations. Neither is announced.
The Wizard notices their effects, not their presence.
"""

from __future__ import annotations

import json
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.config import AppConfig
    from client.router import ModelRouter
    from memory.chronicle import Chronicle
    from entities.entity_compiler import EntityCompiler

log = logging.getLogger(__name__)
_DIAG_LOG_ARCHIVIST = Path("storage/logs/archivist_diag.log")

def _diag(msg: str) -> None:
    try:
        _DIAG_LOG_ARCHIVIST.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG_ARCHIVIST, "a") as f:
            f.write(f"[ARCHIVIST_DIAG] {msg}\n")
            f.flush()
    except Exception:
        pass


_DIAG_LOG = Path("storage/logs/archivist_diag.log")

def _diag(msg: str) -> None:
    """ARCHIVIST_DIAG: Write to log file for dev debugging."""
    try:
        _DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG, "a") as f:
            f.write(f"[ARCHIVIST_DIAG] {msg}\n")
            f.flush()
    except Exception:
        pass


@dataclass
class ArchivistResult:
    """Result of a single background chronicle cycle."""
    written: int
    fired: bool


class BackgroundArchivist:
    """
    Fires silently after every N completed turns.
    Analyses recent exchanges for knowledge worth long-term preservation.
    Writes distilled entries to the Chronicle with archivist metadata.

    The Chronicle is already fed raw turn data automatically. The Archivist's
    contribution is different — synthesised observations, thematic patterns,
    notable decisions, and meaningful moments that raw turn logging misses.
    """

    MIN_TURNS_REQUIRED = 5       # Needs more context than Assessor
    ARCHIVIST_CHRONICLE_TYPE = "archivist_observation"

    def __init__(
        self,
        config: "AppConfig",
        chronicle: "Chronicle",
        compiler: "EntityCompiler",
    ) -> None:
        self.cfg = config
        self.chronicle = chronicle
        self.compiler = compiler
        self._turn_counter: int = 0
        self._archivist_compiled = None

        raw_mem = getattr(config, 'raw', {}).get('memory', {})
        # Archivist fires less frequently than Assessor — default every 8 turns
        self._interval: int = int(raw_mem.get('archivist_interval_turns', 8))

    # ── Public API ──────────────────────────────────────────────────────

    def tick(
        self,
        *,
        thread_messages: list[dict],
        conversation_id: str,
        thread_id: str,
        router: "ModelRouter",
    ) -> ArchivistResult:
        """
        Called after every completed turn.
        router must be the ModelRouter instance.
        """
        self._turn_counter += 1
        _diag(f"Tick {self._turn_counter} — interval={self._interval} — messages={len(thread_messages)}")

        if self._interval <= 0 or (self._turn_counter % self._interval) != 0:
            return ArchivistResult(written=0, fired=False)

        if len(thread_messages) < self.MIN_TURNS_REQUIRED * 2:
            return ArchivistResult(written=0, fired=False)

        try:
            return self._run_cycle(
                thread_messages=thread_messages,
                conversation_id=conversation_id,
                thread_id=thread_id,
                router=router,
            )
        except Exception as e:
            log.warning(f"Background Archivist cycle failed silently: {e}")
            return ArchivistResult(written=0, fired=False)

    # ── Internal ────────────────────────────────────────────────────────

    def _run_cycle(
        self,
        *,
        thread_messages: list[dict],
        conversation_id: str,
        thread_id: str,
        router: "ModelRouter",
    ) -> ArchivistResult:
        _diag("Firing archivist cycle...")
        archivist = self._get_archivist()
        _diag(f"Archivist compiled: {archivist.display_name}")
        messages = self._build_messages(thread_messages)
        _diag(f"Messages built: {len(messages)} items")

        decision = router.decide("archivist chronicle observation")
        _diag(f"Model: {decision.model}")

        gen, _meta = router.stream_response_text(
            decision.model,
            messages,
            max_output_tokens=500,
            instructions=archivist.instruction_str,
        )
        raw_response = "".join(gen).strip()
        _diag(f"Response received. Length: {len(raw_response)} chars")
        _diag(f"Preview: {raw_response[:200]}")

        entries = self._parse_response(raw_response)
        written = 0

        for entry_text in entries:
            if not entry_text.strip():
                continue
            try:
                self.chronicle.add(
                    entry_text,
                    metadata={
                        "type": self.ARCHIVIST_CHRONICLE_TYPE,
                        "conversation_id": conversation_id,
                        "thread_id": thread_id,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                )
                written += 1
            except Exception as e:
                log.warning(f"Archivist chronicle write failed: {e}")

        _diag(f"Cycle complete. Written: {written} entries")
        _diag(f"Done. Written: {written}")
        return ArchivistResult(written=written, fired=True)

    def _get_archivist(self):
        if self._archivist_compiled is None:
            self._archivist_compiled = self.compiler.compile("archivist")
        return self._archivist_compiled

    def _build_messages(self, thread_messages: list[dict]) -> list[dict]:
        messages = []

        recent = [
            m for m in thread_messages[-30:]
            if m.get("role") in ("user", "assistant")
            and m.get("content", "").strip()
        ]
        for m in recent:
            messages.append({
                "role": m["role"],
                "content": m["content"].strip()
            })

        messages.append({
            "role": "user",
            "content": (
                "Review this conversation. Identify moments, decisions, knowledge, "
                "or patterns worth preserving in long-term memory. "
                "Return only the JSON object as instructed."
            )
        })

        return messages

    def _parse_response(self, raw: str) -> list[str]:
        """
        Parse JSON response. Returns list of entry strings to write to Chronicle.
        Returns empty list on any failure.
        """
        if not raw:
            return []

        cleaned = raw
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                l for l in lines if not l.strip().startswith("```")
            ).strip()

        try:
            data = json.loads(cleaned)
            entries = data.get("entries", [])
            result = []
            for e in entries:
                if isinstance(e, str) and e.strip():
                    result.append(e.strip())
                elif isinstance(e, dict) and isinstance(e.get("content"), str):
                    result.append(e["content"].strip())
            return result
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            log.warning(f"Archivist response parse failed: {e} | raw: {raw[:200]}")
            return []
