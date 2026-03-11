#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/memory/distillation.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════




from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from memory.chronicle import Chronicle
    from client.reflection import Reflection
    from claudebox import ClaudeBox


@dataclass
class DistillationResult:
    """Complete output of one distillation cycle."""
    compressed_message: dict
    muscle_entries: list[str]
    fat_count: int
    muscle_count: int
    routing_signals: dict


class Distillation:
    """
    Thread compression engine — Phase 5.
    Pipeline: classify → extract muscle to Chronicle → compress fat+muscle to summary.

    Two entry points:
      distill()  — full pipeline, used by _build_context when context window is near limit.
      rollup()   — lightweight summary update, used by ConversationStore._maybe_summarize
                   to maintain a rolling thread summary as messages accumulate.
    """

    FAT_PATTERNS = [
        r"^(thanks|thank you|got it|makes sense|sure|sure thing|right|exactly|yes|yep|ok|okay|perfect|great|sounds good)[!.]?$",
        r"^(i understand|understood|i see|i get it)[.!]?$",
        r"^what do you mean( by .+)?\??$",
        r"^(yes,? )?(that|this) (makes sense|is (right|correct|good))[.!]?$",
    ]

    MUSCLE_PATTERNS = [
        r"\b(decided|decision|we will|we are going to|chosen|chose)\b",
        r"\b(must|required|requirement|constraint|non.negotiable)\b",
        r"\b(conclusion|concluded|therefore|thus|established)\b",
        r"\b(solution|solved|resolved|fix is|answer is)\b",
        r"\b(still unresolved|open question|tbd|to be determined)\b",
        r"\b(we call|named|lore name|vocabulary|henceforth)\b",
        r"\b(phase \d+|gospel code|do not|never|always)\b",
    ]

    def __init__(self, box: Optional["ClaudeBox"] = None, cfg=None) -> None:
        self.box = box
        self.cfg = cfg
        self._fat_re = [re.compile(p, re.IGNORECASE) for p in self.FAT_PATTERNS]
        self._muscle_re = [re.compile(p, re.IGNORECASE) for p in self.MUSCLE_PATTERNS]

    def should_distill(self, messages: list[dict], token_budget: int) -> bool:
        if len(messages) < 6:
            return False
        estimated = sum(len(m.get("content", "").split()) * 1.3 for m in messages)
        return estimated > token_budget

    def distill(
        self,
        messages: list[dict],
        extract_to_chronicle: bool = False,
        chronicle: "Chronicle | None" = None,
        reflection: "Reflection | None" = None,
    ) -> DistillationResult:
        fat_messages = []
        muscle_messages = []
        for msg in messages:
            if self._classify_message(msg) == "muscle":
                muscle_messages.append(msg)
            else:
                fat_messages.append(msg)

        muscle_entries = []
        routing_signals = {}
        if extract_to_chronicle and chronicle and muscle_messages:
            muscle_entries = self._extract_chronicle_entries(muscle_messages)
            for entry in muscle_entries:
                chronicle.add_from_distillation(entry)
            if reflection:
                routing_signals = reflection.extract_routing_signals(messages)

        source = muscle_messages if muscle_messages else messages
        summary_text = self._compress(source)
        compressed_message = {"role": "system", "content": summary_text}

        return DistillationResult(
            compressed_message=compressed_message,
            muscle_entries=muscle_entries,
            fat_count=len(fat_messages),
            muscle_count=len(muscle_messages),
            routing_signals=routing_signals,
        )

    def rollup(self, existing_summary: str, transcript: str) -> str:
        """
        Lightweight rolling summary update used by ConversationStore._maybe_summarize.

        Takes the existing thread summary (may be empty on first call) and a
        transcript of the older messages being rotated out, and returns an
        updated summary that incorporates both.

        Unlike distill(), this does not touch the Chronicle or Reflection systems.
        It is purely a text compression operation.
        """
        existing_summary = (existing_summary or "").strip()
        transcript = (transcript or "").strip()

        if not transcript:
            return existing_summary

        # No API box available — fall back to deterministic extraction
        if not self.box:
            return self._rollup_fallback(existing_summary, transcript)

        model = "claude-haiku-4-5-20251001"
        if self.cfg:
            try:
                model = self.cfg.raw.get("memory", {}).get(
                    "distillation_compress_model", model
                )
            except Exception:
                pass

        prior_block = (
            f"PRIOR SUMMARY:\n{existing_summary}\n\n" if existing_summary else ""
        )

        prompt = (
            f"{prior_block}"
            f"NEW TRANSCRIPT TO INCORPORATE:\n{transcript}"
        )

        system = (
            "You are a compression engine maintaining a rolling summary of a conversation. "
            "Produce the densest possible factual record: decisions made, conclusions reached, "
            "constraints established, problems solved, open questions. "
            "If a prior summary exists, merge it with the new transcript — do not duplicate. "
            "No pleasantries. No hedging. No filler. Pure signal. "
            "Present tense. Bullet points. 300 tokens maximum."
        )

        try:
            response = self.box.send(
                prompt,
                model=model,
                system=system,
                max_tokens=300,
                stream=False,
            )
            return "THREAD SUMMARY:\n" + response.text
        except Exception:
            return self._rollup_fallback(existing_summary, transcript)

    def _rollup_fallback(self, existing_summary: str, transcript: str) -> str:
        """
        Deterministic fallback when no API box is available.
        Extracts muscle sentences from transcript and appends to existing summary.
        Caps total length to avoid unbounded growth.
        """
        lines = []

        if existing_summary:
            lines.append(existing_summary)

        # Extract muscle sentences from transcript
        muscle_lines = []
        for line in transcript.splitlines():
            line = line.strip()
            if not line:
                continue
            for pattern in self._muscle_re:
                if pattern.search(line):
                    muscle_lines.append(f"- {line[:120]}")
                    break

        if muscle_lines:
            lines.append("THREAD SUMMARY:")
            lines.extend(muscle_lines[:20])  # cap at 20 entries

        result = "\n".join(lines)

        # Hard cap — prevent unbounded growth across many rollup cycles
        max_chars = 2000
        if len(result) > max_chars:
            result = result[:max_chars] + "\n[…truncated]"

        return result

    def _classify_message(self, message: dict) -> str:
        content = message.get("content", "").strip()
        if not content:
            return "fat"
        content_lower = content.lower()
        for pattern in self._fat_re:
            if pattern.match(content_lower):
                return "fat"
        for pattern in self._muscle_re:
            if pattern.search(content):
                return "muscle"
        word_count = len(content.split())
        return "muscle" if word_count >= 8 else "fat"

    def _extract_chronicle_entries(self, muscle_messages: list[dict]) -> list[str]:
        entries = []
        seen = set()
        for msg in muscle_messages:
            content = msg.get("content", "").strip()
            if not content:
                continue
            role = msg.get("role", "user")
            if role == "assistant":
                sentences = re.split(r"(?<=[.!?])\s+", content)
                for s in sentences:
                    s = s.strip()
                    if not s or s in seen:
                        continue
                    for pattern in self._muscle_re:
                        if pattern.search(s):
                            entries.append(s)
                            seen.add(s)
                            break
            elif role == "user":
                if len(content.split()) >= 15:
                    for pattern in self._muscle_re:
                        if pattern.search(content):
                            if content not in seen:
                                entries.append(content)
                                seen.add(content)
                            break
        return entries

    def _compress(self, messages: list[dict]) -> str:
        if not self.box:
            decisions = [m["content"][:80] for m in messages[:3]]
            return "DISTILLED THREAD:\n" + "\n".join(f"- {d}" for d in decisions)

        model = "claude-haiku-4-5-20251001"
        if self.cfg:
            try:
                model = self.cfg.raw.get("memory", {}).get("memory", {}).get(
                    "distillation_compress_model", model
                )
            except Exception:
                pass

        formatted = "\n".join(
            f"{m.get('role', '?').upper()}: {m.get('content', '')}"
            for m in messages
        )

        response = self.box.send(
            f"Compress this conversation:\n\n{formatted}",
            model=model,
            system=(
                "You are a compression engine. Produce the densest possible "
                "factual record of decisions made, conclusions reached, "
                "constraints established, and problems solved in this conversation. "
                "No pleasantries. No hedging. No filler. Pure signal. "
                "Present tense. Bullet points."
            ),
            max_tokens=400,
            stream=False,
        )

        return "DISTILLED THREAD:\n" + response.text
