#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/router.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════




from __future__ import annotations

# token_logger — cross-app usage ledger
import sys as _sys
_sys.path.insert(0, str(__import__('pathlib').Path.home() / '.arca'))
try:
    from token_logger import log_usage as _log_usage
except ImportError:
    def _log_usage(*a, **kw): pass

import json
import re
import threading
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

from claudebox import ClaudeBox
from client.config import AppConfig


# ── Public data types ────────────────────────────────────────────────────────

@dataclass
class ModelDecision:
    """Legacy routing result — preserved for callers that use .model / .reason."""
    model: str
    reason: str


@dataclass
class RouteResult:
    """Full routing decision with signal breakdown. Used by /route command."""
    model_id: str
    score: float
    signals: Dict[str, float]
    reason: str
    was_pinned: bool


# ── Router — Phase 7 signal-scoring engine ───────────────────────────────────

class Router:
    """
    Pure heuristic signal-scoring router.
    No ML, no API call, zero latency.
    Self-improving as the Reflection log grows.
    """

    SIGNAL_WEIGHTS: Dict[str, float] = {
        "message_length":    0.20,
        "code_signals":      0.20,
        "question_depth":    0.15,
        "analytical_markers": 0.20,
        "topic_novelty":     0.10,
        "session_baseline":  0.10,
        "explicit_override": 0.05,
    }

    ANALYTICAL_TRIGGERS = [
        "compare", "analyze", "analyse", "design", "architect",
        "trade-off", "tradeoff", "trade off", "explain why",
        "implications", "evaluate", "critique", "contrast",
        "diagnose", "refactor", "optimize", "optimise",
        "what causes", "how does", "why does", "what would happen",
        "walk me through", "break down",
    ]

    def __init__(
        self,
        fast_model: str = "claude-sonnet-4-6",
        smart_model: str = "claude-opus-4-6",
        smart_threshold: float = 0.55,
        reflection_log_path: str = "storage/logs/reflections.jsonl",
        reflection_window: int = 50,
    ):
        # Clamp threshold to valid range
        if not (0.0 <= smart_threshold <= 1.0):
            warnings.warn(f"smart_threshold {smart_threshold} out of range — clamped to [0.0, 1.0]")
            smart_threshold = max(0.0, min(1.0, smart_threshold))

        self.fast_model = fast_model
        self.smart_model = smart_model
        self.smart_threshold = smart_threshold
        self.reflection_log_path = Path(reflection_log_path)
        self.reflection_window = reflection_window

        self._pinned_model: Optional[str] = None
        self._session_signals: List[Dict[str, float]] = []
        self._reflection_baseline: Dict = {}
        self._recent_topics: List[str] = []
        self._last_result: Optional[RouteResult] = None

        self._load_reflection_baseline()

    # ── Public Interface ─────────────────────────────────────────────────────

    def route(self, message: str) -> str:
        """
        Route a message to a model. Returns model_id string.
        Called by ModelRouter.decide() — signature is the stable public contract.
        """
        result = self.route_full(message or "")
        self._last_result = result
        return result.model_id

    def route_full(self, message: str) -> RouteResult:
        """Full routing decision with scoring breakdown. Used by /route command."""
        if not message or not message.strip():
            return RouteResult(
                model_id=self.fast_model,
                score=0.0,
                signals={k: 0.0 for k in self.SIGNAL_WEIGHTS},
                reason="Empty message — fast model default.",
                was_pinned=False,
            )

        if self._pinned_model:
            return RouteResult(
                model_id=self._pinned_model,
                score=1.0 if self._pinned_model == self.smart_model else 0.0,
                signals={},
                reason=f"Pinned to {self._pinned_model} by /model command.",
                was_pinned=True,
            )

        signals = self._score_signals(message)
        score = self._compute_score(signals)
        model_id = self.smart_model if score >= self.smart_threshold else self.fast_model

        top_signal = max(signals, key=lambda k: signals[k])
        reason = (
            f"Score {score:.2f} (threshold {self.smart_threshold}). "
            f"Dominant signal: {top_signal} ({signals[top_signal]:.2f})."
        )

        self._session_signals.append(signals)
        if len(self._session_signals) > 50:
            self._session_signals = self._session_signals[-50:]

        return RouteResult(
            model_id=model_id,
            score=score,
            signals=signals,
            reason=reason,
            was_pinned=False,
        )

    def pin_model(self, model_id: str) -> None:
        """Pin a specific model for all subsequent messages until unpinned."""
        self._pinned_model = model_id

    def unpin_model(self) -> None:
        """Remove model pin. Router resumes normal scoring."""
        self._pinned_model = None

    def refresh_reflection_baseline(self) -> None:
        """
        Reload Reflection log and recompute baseline.
        Called by app.py after each distillation cycle.
        """
        self._load_reflection_baseline()

    def last_result(self) -> Optional[RouteResult]:
        """Return the RouteResult from the most recent route() call."""
        return self._last_result

    def format_route_display(self, result: Optional[RouteResult] = None) -> str:
        """Format a RouteResult as a Wizard-readable breakdown for /route output."""
        r = result or self._last_result
        if r is None:
            return "◆ No routing decision recorded yet this session."

        lines = [
            "◆ ROUTING DECISION",
            f"  Model selected : {r.model_id}",
            f"  Score          : {r.score:.2f}  (threshold: {self.smart_threshold})",
            f"  Was pinned     : {'Yes' if r.was_pinned else 'No'}",
        ]
        if r.signals:
            lines.append("  Signal breakdown:")
            for sig, val in r.signals.items():
                w = self.SIGNAL_WEIGHTS.get(sig, 0.0)
                lines.append(f"    {sig:<22} {val:.2f}  (weight {w:.2f}) → {val*w:.3f}")
        lines.append(f"  Reason: {r.reason}")
        return "\n".join(lines)

    # ── Signal Scoring ────────────────────────────────────────────────────────

    def _score_signals(self, message: str) -> Dict[str, float]:
        return {
            "message_length":     self._score_length(message),
            "code_signals":       self._score_code(message),
            "question_depth":     self._score_question_depth(message),
            "analytical_markers": self._score_analytical(message),
            "topic_novelty":      self._score_topic_novelty(message),
            "session_baseline":   self._score_session_baseline(),
            "explicit_override":  1.0 if self._pinned_model == self.smart_model else 0.0,
        }

    def _compute_score(self, signals: Dict[str, float]) -> float:
        return sum(
            signals.get(k, 0.0) * w
            for k, w in self.SIGNAL_WEIGHTS.items()
        )

    def _score_length(self, message: str) -> float:
        """Normalize word count: 0 words → 0.0, 100+ words → 1.0."""
        return min(1.0, len(message.split()) / 100.0)

    def _score_code(self, message: str) -> float:
        """Binary: 1.0 if message contains code indicators, else 0.0."""
        patterns = [
            r"```", r"\bdef \b", r"\bclass \b", r"\bimport \b",
            r"\basync def\b", r"=>\s*{", r"<[a-zA-Z]+>",
        ]
        for p in patterns:
            if re.search(p, message):
                return 1.0
        return 0.0

    def _score_question_depth(self, message: str) -> float:
        """
        0.0 = no question mark.
        0.3 = single short question.
        0.6 = single question with subordinate clause.
        1.0 = multi-part or nested why/how.
        """
        if "?" not in message:
            return 0.0
        q_count = message.count("?")
        has_nested = bool(re.search(
            r"\b(why|how|what causes|when|whether)\b.*\?", message, re.I
        ))
        word_count = len(message.split())
        if q_count >= 2 or (has_nested and word_count > 20):
            return 1.0
        if has_nested:
            return 0.6
        return 0.3

    def _score_analytical(self, message: str) -> float:
        """Count analytical trigger word matches, normalize to 0.0–1.0. 3+ → 1.0."""
        msg_lower = message.lower()
        matches = sum(1 for t in self.ANALYTICAL_TRIGGERS if t in msg_lower)
        return min(1.0, matches / 3.0)

    def _score_topic_novelty(self, message: str) -> float:
        """
        Compare message topic words against recent Reflection dominant_topics.
        No recent topics → 0.5 (neutral).
        High overlap → low novelty. No overlap → high novelty.
        """
        if not self._recent_topics:
            return 0.5

        stopwords = {
            "the", "a", "an", "is", "it", "i", "to", "of", "in", "for",
            "that", "this", "and", "or", "but", "with", "be", "was", "are",
        }
        msg_words = {
            w.lower() for w in re.findall(r"\b\w{4,}\b", message)
            if w.lower() not in stopwords
        }
        if not msg_words:
            return 0.5

        recent_set = {t.lower() for t in self._recent_topics}
        overlap = len(msg_words & recent_set)
        novelty = 1.0 - min(1.0, overlap / max(len(msg_words), 1))
        return novelty

    def _score_session_baseline(self) -> float:
        """
        Average complexity of recent turns in this session.
        Falls back to reflection baseline if no session signals yet.
        """
        if self._session_signals:
            recent = self._session_signals[-10:]
            avg = sum(
                sum(s.get(k, 0.0) * w for k, w in self.SIGNAL_WEIGHTS.items())
                for s in recent
            ) / len(recent)
            return min(1.0, avg)
        return self._reflection_baseline.get("avg_complexity", 0.5)

    # ── Reflection Baseline ───────────────────────────────────────────────────

    def _load_reflection_baseline(self) -> None:
        """
        Read the Reflection log and compute a statistical baseline.
        Missing file → neutral baseline (0.5). Corrupt lines → skipped.
        """
        if not self.reflection_log_path.exists():
            self._reflection_baseline = {"avg_complexity": 0.5, "code_frequency": 0.0}
            self._recent_topics = []
            return

        records = []
        try:
            with self.reflection_log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        warnings.warn(f"Skipping corrupt reflection log line: {line[:60]}")
        except OSError:
            self._reflection_baseline = {"avg_complexity": 0.5, "code_frequency": 0.0}
            return

        # Use only the most recent N records
        records = records[-self.reflection_window:]

        if not records:
            self._reflection_baseline = {"avg_complexity": 0.5, "code_frequency": 0.0}
            self._recent_topics = []
            return

        # avg message length (as proxy for complexity)
        lengths = [r.get("message_length_avg", 10) for r in records if "message_length_avg" in r]
        avg_length = sum(lengths) / len(lengths) if lengths else 10.0
        avg_complexity = min(1.0, avg_length / 100.0)

        # code frequency
        code_flags = [1.0 if r.get("code_present") else 0.0 for r in records]
        code_frequency = sum(code_flags) / len(code_flags) if code_flags else 0.0

        # recent topics (flatten dominant_topics lists)
        topics: List[str] = []
        for r in records[-10:]:
            topics.extend(r.get("dominant_topics", []))
        self._recent_topics = list(dict.fromkeys(topics))[-20:]  # deduplicated, capped at 20

        self._reflection_baseline = {
            "avg_complexity": avg_complexity,
            "code_frequency": code_frequency,
        }

    def list_models(self, models_yaml_path: str = "entities/models.yaml") -> Optional[List[Dict]]:
        """Load and return model registry entries from models.yaml."""
        p = Path(models_yaml_path)
        if not p.exists():
            return None
        try:
            import yaml
            with p.open("r") as f:
                data = yaml.safe_load(f)
            return data.get("models", [])
        except Exception:
            return None


# ── ModelRouter — preserves Phase 6 public API ───────────────────────────────

class ModelRouter:
    """
    Phase 6-compatible wrapper.
    Delegates routing decisions to the Phase 7 Router signal-scoring engine.
    stream_response_text() is unchanged — same contract as Phase 6.
    """

    def __init__(self, cfg: AppConfig, api_key: str):
        self.cfg = cfg
        self._api_key = api_key
        self._box = ClaudeBox(api_key=api_key, stream=True)

        # Build Phase 7 Router from config
        routing = cfg.routing
        reflection_log = getattr(cfg.storage, "reflection_log_path", "storage/logs/reflections.jsonl")
        smart_threshold = float(getattr(routing, "smart_threshold", 0.55))
        reflection_window = int(getattr(routing, "reflection_window", 50))

        self.router = Router(
            fast_model=cfg.models.fast,
            smart_model=cfg.models.smart,
            smart_threshold=smart_threshold,
            reflection_log_path=reflection_log,
            reflection_window=reflection_window,
        )

    # ── Routing ───────────────────────────────────────────────────────────────

    def decide(self, user_text: str, *, forced: Optional[str] = None) -> ModelDecision:
        """
        Returns a ModelDecision. Phase 6 callers unchanged.
        forced='smart' / 'fast' pins the model for this one call only.
        """
        if forced == "smart":
            return ModelDecision(model=self.cfg.models.smart, reason="forced smart")
        if forced == "fast":
            return ModelDecision(model=self.cfg.models.fast, reason="forced fast")

        model_id = self.router.route(user_text)
        reason = self.router.last_result().reason if self.router.last_result() else "signal scoring"
        return ModelDecision(model=model_id, reason=reason)

    # ── Streaming — unchanged from Phase 6 ───────────────────────────────────

    def stream_response_text(
        self,
        model: str,
        input_messages: List[Dict],
        *,
        max_output_tokens: Optional[int] = None,
        instructions: Optional[str] = None,
    ) -> Tuple[Generator[str, None, None], Dict]:

        meta: Dict = {"usage": None}

        if instructions is None:
            system_parts = [m["content"] for m in input_messages if m.get("role") == "system"]
            if system_parts:
                instructions = "\n\n".join(system_parts)

        filtered = [m for m in input_messages if m.get("role") in ("user", "assistant")]

        session_id = f"stream_{threading.get_ident()}_{id(meta)}"
        self._box.create_session(session_id)

        history = filtered[:-1]
        for msg in history:
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            if msg["role"] == "user":
                self._box.conversation.add_user_message(content, session_id)
            elif msg["role"] == "assistant":
                self._box.conversation.add_assistant_message(content, session_id)
        _raw_last = next(
            (m["content"] for m in reversed(filtered) if m["role"] == "user"),
            None
        )
        last_user = (_raw_last or "").strip()
        if not last_user:
            import sys
            print(f"DEBUG: last_user empty! filtered={[(m['role'], repr((m.get('content') or '')[:40])) for m in filtered]}", file=sys.stderr)
            last_user = "Continue."

        send_kwargs: Dict = {"model": model, "session_id": session_id}
        if instructions:
            send_kwargs["system"] = instructions
        if max_output_tokens:
            send_kwargs["max_tokens"] = max_output_tokens

        def gen() -> Generator[str, None, None]:
            try:
                import sys
                if not (last_user or "").strip():
                    print(f"DEBUG EMPTY last_user: filtered={filtered}", file=sys.stderr)
                for token in self._box.stream(last_user, **send_kwargs):
                    yield token
                try:
                    usage = self._box.get_token_usage(session_id)
                    meta["usage"] = usage
                    try:
                        _log_usage(
                            app="tower",
                            model=getattr(usage, "model", "unknown"),
                            input_tokens=getattr(usage, "input_tokens", 0),
                            output_tokens=getattr(usage, "output_tokens", 0),
                            session_id=session_id,
                        )
                    except Exception:
                        pass
                except Exception:
                    pass
            finally:
                try:
                    self._box.delete_session(session_id)
                except Exception:
                    pass

        return gen(), meta
