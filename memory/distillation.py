#╔══════════════════════════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/memory/distillation.py
#║ ⛨
#╚═════════════════════════════════════════════════════════



from __future__ import annotations
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from memory.chronicle import Chronicle
    from client.reflection import Reflection


@dataclass
class DistillationResult:
    """Complete output of one distillation cycle."""
    compressed_message: dict        # {"role":"system","content":"..."} — replaces Thread
    muscle_entries: list[str]       # Extracted high-value strings sent to Chronicle
    fat_count: int                  # Number of messages classified as fat
    muscle_count: int               # Number of messages classified as muscle
    routing_signals: dict           # Extracted for Reflection (Phase 7 uses)


class Distillation:
    """
    Thread compression engine — upgraded in Phase 5.
    Pipeline: classify → extract muscle to Chronicle → compress fat+muscle to summary.

    The key insight: distillation has two outputs, not one.
    Output 1: A lean summary that replaces the Thread in the context window.
    Output 2: Extracted muscle entries that enter the Chronicle permanently.
    """

    # ── Fat signal patterns — heuristic classifiers ─────────────────────
    FAT_PATTERNS = [
        r"^(thanks|thank you|got it|makes sense|sure|sure thing|right|exactly|yes|yep|ok|okay|perfect|great|sounds good)[!.]?$",
        r"^(i understand|understood|i see|i get it)[.!]?$",
        r"^what do you mean( by .+)?\??$",
        r"^(yes,? )?(that|this) (makes sense|is (right|correct|good))[.!]?$",
    ]

    # ── Muscle signal patterns ───────────────────────────────────────────
    MUSCLE_PATTERNS = [
        r"\b(decided|decision|we will|we are going to|chosen|chose)\b",
        r"\b(must|required|requirement|constraint|non.negotiable)\b",
        r"\b(conclusion|concluded|therefore|thus|established)\b",
        r"\b(solution|solved|resolved|fix is|answer is)\b",
        r"\b(still unresolved|open question|tbd|to be determined)\b",
        r"\b(we call|named|lore name|vocabulary|henceforth)\b",
        r"\b(phase \d+|gospel code|do not|never|always)\b",
    ]

    def __init__(self, api_client=None) -> None:
        """
        api_client: the OpenAI client for the _compress() LLM call.
        May be None for testing — _compress() will use a fallback stub.
        """
        self.api_client = api_client
        self._fat_re = [re.compile(p, re.IGNORECASE) for p in self.FAT_PATTERNS]
        self._muscle_re = [re.compile(p, re.IGNORECASE) for p in self.MUSCLE_PATTERNS]

    # ── Public API ──────────────────────────────────────────────────────

    def should_distill(self, messages: list[dict], token_budget: int) -> bool:
        """
        Return True if distillation should fire.
        Fires when estimated token count of messages exceeds token_budget.
        Uses conservative word-count estimate (words * 1.3).
        Does NOT fire if messages list has fewer than 6 entries — too short to meaningfully distill.
        """
        if len(messages) < 6:
            return False
        estimated = sum(len(m.get("content","").split()) * 1.3 for m in messages)
        return estimated > token_budget

    def distill(self,
                messages: list[dict],
                extract_to_chronicle: bool = False,
                chronicle: "Chronicle | None" = None,
                reflection: "Reflection | None" = None) -> DistillationResult:
        """
        Full distillation pipeline. Three stages:

        Stage 1 — Classify:
          For each message, classify as fat or muscle.
          Classification uses _classify_message().
          Result: fat_messages list, muscle_messages list.

        Stage 2 — Extract (if extract_to_chronicle=True):
          For each muscle message, extract Chronicle-worthy strings.
          Call chronicle.add_from_distillation() for each extraction.
          Call reflection.extract_routing_signals() on full message set.

        Stage 3 — Compress:
          Build a compression prompt from muscle_messages only.
          Call _compress() to get a dense summary string.
          Wrap in {"role":"system","content":summary} for context replacement.

        Returns DistillationResult with all outputs.
        """
        # Stage 1: Classify
        fat_messages = []
        muscle_messages = []
        for msg in messages:
            if self._classify_message(msg) == "muscle":
                muscle_messages.append(msg)
            else:
                fat_messages.append(msg)

        # Stage 2: Extract to Chronicle
        muscle_entries = []
        routing_signals = {}
        if extract_to_chronicle and chronicle and muscle_messages:
            muscle_entries = self._extract_chronicle_entries(muscle_messages)
            for entry in muscle_entries:
                chronicle.add_from_distillation(entry)
            if reflection:
                routing_signals = reflection.extract_routing_signals(messages)

        # Stage 3: Compress
        source = muscle_messages if muscle_messages else messages
        summary_text = self._compress(source)
        compressed_message = {"role": "system", "content": summary_text}

        return DistillationResult(
            compressed_message=compressed_message,
            muscle_entries=muscle_entries,
            fat_count=len(fat_messages),
            muscle_count=len(muscle_messages),
            routing_signals=routing_signals
        )

    # ── Classification ──────────────────────────────────────────────────

    def _classify_message(self, message: dict) -> str:
        """
        Return "fat" or "muscle" for a single message dict.

        Classification algorithm:
          1. Extract content string from message.
          2. If content is empty or whitespace only: return "fat".
          3. Strip to first 300 chars for pattern matching (efficiency).
          4. Check fat patterns first (cheap negative filter):
             if ANY fat pattern matches the FULL content (stripped/lowercased):
               return "fat"
          5. Check muscle patterns:
             if ANY muscle pattern matches anywhere in content:
               return "muscle"
          6. Length heuristic:
             if word count < 8: return "fat"  (too short to be substantive)
             if word count >= 8: return "muscle"  (assume substance)
          7. Default: return "fat" (conservative — prefer leaner summaries)
        """
        content = message.get("content", "").strip()
        if not content:
            return "fat"
        content_lower = content.lower()
        # Fat check — exact short-form matches
        for pattern in self._fat_re:
            if pattern.match(content_lower):
                return "fat"
        # Muscle check — keyword signals anywhere in content
        for pattern in self._muscle_re:
            if pattern.search(content):
                return "muscle"
        # Length heuristic
        word_count = len(content.split())
        return "muscle" if word_count >= 8 else "fat"

    # ── Chronicle Extraction ─────────────────────────────────────────────

    def _extract_chronicle_entries(self,
                                   muscle_messages: list[dict]) -> list[str]:
        """
        Extract Chronicle-worthy strings from muscle messages.
        These are the specific facts, decisions, and conclusions that
        should be semantically retrievable in future conversations.

        Extraction algorithm:
          1. Iterate muscle_messages.
          2. For each assistant message:
             a. Split into sentences (split on ". ", "! ", "? ").
             b. For each sentence, check muscle patterns.
             c. If muscle pattern matches: add sentence to extraction list.
          3. For each user message:
             a. If content word count >= 15 and muscle pattern matches:
                add full content to extraction list.
          4. Deduplicate extraction list.
          5. Return list of strings (not dicts — Chronicle.add() takes strings).

        Note: This extracts at sentence granularity for assistant messages
        to avoid dumping entire long responses into the Chronicle.
        """
        entries = []
        seen = set()
        for msg in muscle_messages:
            content = msg.get("content","").strip()
            if not content:
                continue
            role = msg.get("role","user")
            if role == "assistant":
                # Sentence-level extraction
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
                # Full-message extraction for substantive user inputs
                if len(content.split()) >= 15:
                    for pattern in self._muscle_re:
                        if pattern.search(content):
                            if content not in seen:
                                entries.append(content)
                                seen.add(content)
                            break
        return entries

    # ── Compression ─────────────────────────────────────────────────────

    def _compress(self, messages: list[dict]) -> str:
        """
        Compress muscle messages into a dense summary string via LLM call.
        If api_client is None (testing), returns a stub summary.

        Returns the summary string (content only, not a message dict).
        Wrapping into {"role":"system","content":...} happens in distill().
        """
        if not self.api_client:
            # Stub for testing
            decisions = [m["content"][:80] for m in messages[:3]]
            return "DISTILLED THREAD:\n" + "\n".join(f"- {d}" for d in decisions)

        formatted = "\n".join(
            f"{m.get('role','?').upper()}: {m.get('content','')}"
            for m in messages
        )
        response = self.api_client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role":"system","content":(
                    "You are a compression engine. Produce the densest possible "
                    "factual record of decisions made, conclusions reached, "
                    "constraints established, and problems solved in this conversation. "
                    "No pleasantries. No hedging. No filler. Pure signal. "
                    "Present tense. Bullet points."
                )},
                {"role":"user","content":f"Compress this conversation:\n\n{formatted}"}
            ],
            max_output_tokens=400
        )
        return "DISTILLED THREAD:\n" + response.output_text
