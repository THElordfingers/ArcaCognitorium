#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/assessor.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

"""
The Assessor — Background Observation Engine

Silent. Never summoned for this purpose. Never visible during operation.
Fires on a turn interval, analyses recent exchanges, writes new observations
to the Grimoire. The Wizard sees the Grimoire indicator pulse. Nothing else.

Distinct from the foreground Assessor summon (one-on-one session, v1.2).
This is the machine watching. That is the machine speaking.

DEV NOTE: Diagnostic stderr logging is active. Search for ASSESSOR_DIAG
to find and remove all diagnostic prints before release.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.config import AppConfig
    from client.router import ModelRouter
    from memory.grimoire import Grimoire
    from memory.chronicle import Chronicle
    from entities.entity_compiler import EntityCompiler

log = logging.getLogger(__name__)

# ── Dev diagnostic — remove before release ──────────────────────────────────
_DIAG_LOG = Path("storage/logs/assessor_diag.log")

def _diag(msg: str) -> None:
    """ASSESSOR_DIAG: Write to log file for dev debugging. Remove before release."""
    try:
        _DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG, "a") as f:
            f.write(f"[ASSESSOR_DIAG] {msg}\n")
            f.flush()
    except Exception:
        pass
# ────────────────────────────────────────────────────────────────────────────


@dataclass
class AssessorResult:
    """Result of a single background assessment cycle."""
    written: int
    skipped: int
    total_observed: int
    fired: bool


class BackgroundAssessor:
    """
    Fires silently after every N completed turns.
    Reads recent thread exchanges + existing Grimoire.
    Writes new observations to Grimoire.
    Never surfaces to the Wizard directly.
    """

    MIN_TURNS_REQUIRED = 3
    MAX_SIMILARITY_RATIO = 0.55

    def __init__(
        self,
        config: "AppConfig",
        grimoire: "Grimoire",
        chronicle: "Chronicle",
        compiler: "EntityCompiler",
    ) -> None:
        self.cfg = config
        self.grimoire = grimoire
        self.chronicle = chronicle
        self.compiler = compiler
        self._turn_counter: int = 0
        self._assessor_compiled = None

        raw_mem = getattr(config, 'raw', {}).get('memory', {})
        self._interval: int = int(raw_mem.get('assessor_interval_turns', 5))
        _diag(f"Assessor initialised. Interval: {self._interval} turns.")

    # ── Public API ──────────────────────────────────────────────────────

    def tick(
        self,
        *,
        thread_messages: list[dict],
        conversation_id: str,
        router: "ModelRouter",
    ) -> AssessorResult:
        """
        Called after every completed turn.
        router must be the ModelRouter instance (self.router in app.py),
        NOT the inner Router signal-scoring engine (self.router.router).
        """
        self._turn_counter += 1
        _diag(f"Tick {self._turn_counter} — interval={self._interval} — messages={len(thread_messages)}")

        if self._interval <= 0 or (self._turn_counter % self._interval) != 0:
            return AssessorResult(written=0, skipped=0, total_observed=0, fired=False)

        if len(thread_messages) < self.MIN_TURNS_REQUIRED * 2:
            _diag(f"Skipping — not enough messages ({len(thread_messages)} < {self.MIN_TURNS_REQUIRED * 2})")
            return AssessorResult(written=0, skipped=0, total_observed=0, fired=False)

        _diag(f"Firing assessment cycle at tick {self._turn_counter}...")
        try:
            result = self._run_cycle(
                thread_messages=thread_messages,
                conversation_id=conversation_id,
                router=router,
            )
            _diag(f"Cycle complete. written={result.written} skipped={result.skipped} total={result.total_observed}")
            return result
        except Exception as e:
            _diag(f"CYCLE FAILED: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return AssessorResult(written=0, skipped=0, total_observed=0, fired=False)

    # ── Internal ────────────────────────────────────────────────────────

    def _run_cycle(
        self,
        *,
        thread_messages: list[dict],
        conversation_id: str,
        router: "ModelRouter",
    ) -> AssessorResult:

        _diag("Compiling assessor entity...")
        assessor = self._get_assessor()
        _diag(f"Assessor compiled: {assessor.display_name}")

        _diag("Building messages...")
        messages = self._build_messages(thread_messages, conversation_id)
        _diag(f"Messages built: {len(messages)} items")

        _diag("Making routing decision...")
        decision = router.decide("assessor background observation")
        _diag(f"Model selected: {decision.model}")

        _diag("Calling API...")
        gen, _meta = router.stream_response_text(
            decision.model,
            messages,
            max_output_tokens=600,
            instructions=assessor.instruction_str,
        )
        raw_response = "".join(gen).strip()
        _diag(f"API response received. Length: {len(raw_response)} chars.")
        _diag(f"Raw response preview: {raw_response[:300]}")

        _diag("Parsing response...")
        observations = self._parse_response(raw_response)
        _diag(f"Parsed {len(observations)} observations.")

        _diag("Writing to grimoire...")
        written, skipped = self._write_to_grimoire(observations)
        _diag(f"Written: {written}  Skipped: {skipped}")

        return AssessorResult(
            written=written,
            skipped=skipped,
            total_observed=len(observations),
            fired=True,
        )

    def _get_assessor(self):
        if self._assessor_compiled is None:
            self._assessor_compiled = self.compiler.compile("assessor")
        return self._assessor_compiled

    def _build_messages(
        self,
        thread_messages: list[dict],
        conversation_id: str,
    ) -> list[dict]:
        messages = []

        # Existing Grimoire — Assessor reads this to avoid repeating entries
        grimoire_str = self.grimoire.build_injection_string()
        if grimoire_str:
            messages.append({
                "role": "user",
                "content": f"EXISTING GRIMOIRE ENTRIES — do not repeat these:\n{grimoire_str}"
            })
            messages.append({
                "role": "assistant",
                "content": "Grimoire context received. I will not duplicate these observations."
            })

        # Chronicle fragments — do NOT filter by thread_id here.
        # The assessor wants cross-session patterns, not thread-restricted results.
        # Passing thread_by_conversation=None allows all items for this conversation.
        try:
            retrieved = self.chronicle.query(
                "wizard communication style preferences patterns behaviour",
                top_k=3,
                conversation_ids=[conversation_id],
                thread_by_conversation=None,
            )
            if retrieved:
                blob = "\n\n".join(r['text'] for r in retrieved)
                messages.append({
                    "role": "user",
                    "content": f"CHRONICLE FRAGMENTS — cross-session patterns:\n{blob}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "Chronicle context received."
                })
                _diag(f"Chronicle: {len(retrieved)} fragments injected.")
            else:
                _diag("Chronicle: no fragments retrieved.")
        except Exception as e:
            _diag(f"Chronicle query failed (non-fatal): {type(e).__name__}: {e}")

        # Recent thread exchanges — the primary evidence
        recent = [
            m for m in thread_messages[-20:]
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
                "Analyse the conversation above. "
                "Produce new Grimoire observations not already captured. "
                "Return only the JSON object as instructed."
            )
        })

        return messages

    def _parse_response(self, raw: str) -> list[dict]:
        if not raw:
            _diag("Parse: empty response.")
            return []

        # Strip markdown fences if model added them despite instructions
        cleaned = raw
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                l for l in lines
                if not l.strip().startswith("```")
            ).strip()
            _diag("Parse: stripped markdown fences.")

        try:
            data = json.loads(cleaned)
            observations = data.get("observations", [])
            valid = []
            for obs in observations:
                if (
                    isinstance(obs, dict)
                    and isinstance(obs.get("category"), str)
                    and isinstance(obs.get("content"), str)
                    and obs["category"].strip()
                    and obs["content"].strip()
                ):
                    valid.append({
                        "category": obs["category"].strip().lower(),
                        "content": obs["content"].strip()
                    })
            _diag(f"Parse: {len(observations)} raw, {len(valid)} valid.")
            return valid
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            _diag(f"Parse FAILED: {e}")
            _diag(f"Cleaned text was: {cleaned[:400]}")
            return []

    def _write_to_grimoire(self, observations: list[dict]) -> tuple[int, int]:
        written = 0
        skipped = 0
        existing = [e.content.lower() for e in self.grimoire.get_active()]

        for obs in observations:
            content = obs["content"]
            category = obs["category"]

            if not content:
                skipped += 1
                continue

            content_tokens = set(content.lower().split())
            is_duplicate = any(
                len(content_tokens & set(e.split()))
                / max(len(content_tokens), 1)
                > self.MAX_SIMILARITY_RATIO
                for e in existing
            )

            if is_duplicate:
                _diag(f"Skipping duplicate: {content[:60]}")
                skipped += 1
                continue

            self.grimoire.add(content, category, source="assessor")
            existing.append(content.lower())
            _diag(f"Wrote to grimoire [{category}]: {content[:60]}")
            written += 1

        return written, skipped
