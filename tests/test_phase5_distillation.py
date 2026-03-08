"""
Phase 5 — Smarter Distillation Test Suite
Run: pytest tests/test_phase5_distillation.py -v
"""
import pytest
from unittest.mock import MagicMock, patch


# ── Classification Tests ─────────────────────────────────────────────────

def test_classify_thanks_is_fat():
    """Short acknowledgment messages classified as fat."""
    from memory.distillation import Distillation
    d = Distillation()
    assert d._classify_message({"role":"user","content":"Thanks!"}) == "fat"
    assert d._classify_message({"role":"user","content":"Got it"}) == "fat"
    assert d._classify_message({"role":"user","content":"Makes sense"}) == "fat"

def test_classify_decision_is_muscle():
    """Messages containing decision keywords classified as muscle."""
    from memory.distillation import Distillation
    d = Distillation()
    msg = {"role":"assistant","content":"We decided to use JSON for all persistence layers."}
    assert d._classify_message(msg) == "muscle"

def test_classify_constraint_is_muscle():
    """Messages with constraint keywords classified as muscle."""
    from memory.distillation import Distillation
    d = Distillation()
    msg = {"role":"assistant","content":"The stack must use Textual 0.47+ — this is a non-negotiable requirement."}
    assert d._classify_message(msg) == "muscle"

def test_classify_empty_content_is_fat():
    """Empty message classified as fat."""
    from memory.distillation import Distillation
    d = Distillation()
    assert d._classify_message({"role":"user","content":""}) == "fat"
    assert d._classify_message({"role":"user","content":"   "}) == "fat"

def test_classify_long_message_without_keywords_is_muscle():
    """Long messages (>=8 words) without fat patterns default to muscle."""
    from memory.distillation import Distillation
    d = Distillation()
    msg = {"role":"user","content":"The Wizard opened the application and began typing a long message about the architecture."}
    assert d._classify_message(msg) == "muscle"

def test_classify_short_message_without_keywords_is_fat():
    """Short messages (<8 words) without muscle patterns default to fat."""
    from memory.distillation import Distillation
    d = Distillation()
    msg = {"role":"user","content":"ok sounds good"}
    assert d._classify_message(msg) == "fat"


# ── should_distill Tests ─────────────────────────────────────────────────

def test_should_distill_false_when_too_short():
    """should_distill() returns False for threads with fewer than 6 messages."""
    from memory.distillation import Distillation
    d = Distillation()
    short = [{"role":"user","content":"hi"},{"role":"assistant","content":"hello"}]
    assert d.should_distill(short, token_budget=100) == False

def test_should_distill_false_within_budget():
    """should_distill() returns False when token estimate within budget."""
    from memory.distillation import Distillation
    d = Distillation()
    msgs = [{"role":"user","content":"short"} for _ in range(8)]
    assert d.should_distill(msgs, token_budget=100000) == False

def test_should_distill_true_over_budget():
    """should_distill() returns True when token estimate exceeds budget."""
    from memory.distillation import Distillation
    d = Distillation()
    msgs = [{"role":"user","content":"word " * 100} for _ in range(8)]
    assert d.should_distill(msgs, token_budget=100) == True


# ── distill() Pipeline Tests ─────────────────────────────────────────────

def test_distill_returns_distillation_result():
    """distill() returns a DistillationResult with all expected fields."""
    from memory.distillation import Distillation, DistillationResult
    d = Distillation(api_client=None)
    messages = [
        {"role":"user","content":"We decided to use Textual for the TUI."},
        {"role":"assistant","content":"That is correct. The stack must include Textual 0.47+."},
        {"role":"user","content":"Thanks"},
        {"role":"user","content":"What constraint applies to the API?"},
        {"role":"assistant","content":"The OpenAI Responses API is required — not chat.completions."},
        {"role":"user","content":"Got it"},
    ]
    result = d.distill(messages)
    assert isinstance(result, DistillationResult)
    assert result.compressed_message["role"] == "system"
    assert "DISTILLED" in result.compressed_message["content"]

def test_distill_separates_fat_and_muscle():
    """distill() correctly separates fat from muscle messages."""
    from memory.distillation import Distillation
    d = Distillation(api_client=None)
    messages = [
        {"role":"user","content":"Thanks!"},   # fat
        {"role":"user","content":"Got it"},     # fat
        {"role":"assistant","content":"We decided JSON persistence is required for all stores."},  # muscle
        {"role":"assistant","content":"The conclusion is that distillation fires before the API call."},  # muscle
    ]
    result = d.distill(messages)
    assert result.fat_count == 2
    assert result.muscle_count == 2

def test_distill_extracts_to_chronicle(tmp_path):
        """distill() with extract_to_chronicle=True calls chronicle.add_from_distillation()."""
        from unittest.mock import MagicMock, patch
        from memory.distillation import Distillation
        d = Distillation(api_client=None)
        mock_chronicle = MagicMock()
        mock_reflection = MagicMock()
        mock_reflection.extract_routing_signals.return_value = {}
        messages = [
            {"role": "user", "content": "We decided to use async workers for all background tasks and this is a firm architectural constraint that must be followed throughout the entire codebase without exception."},
            {"role": "assistant", "content": "Confirmed. The decision is to use async workers. The constraint is no blocking calls in the main thread. This is non-negotiable and required by the architecture."},
            {"role": "user", "content": "The requirement is that no blocking calls exist anywhere in the main thread. This constraint is non-negotiable and was established in the Phase 2 design review."},
            {"role": "assistant", "content": "Understood. We will use async workers throughout. No blocking calls allowed."},
        ]
        result = d.distill(messages, extract_to_chronicle=True,
                           chronicle=mock_chronicle, reflection=mock_reflection)
        assert mock_chronicle.add_from_distillation.called


# ── Chronicle Integration Tests ──────────────────────────────────────────

def test_chronicle_add_from_distillation(tmp_path):
        """add_from_distillation() adds entry with source=distillation metadata."""
        from unittest.mock import MagicMock
        from memory.chronicle import Chronicle
        mock_cfg = MagicMock()
        mock_cfg.storage.vectors_path = str(tmp_path / "chronicle.pkl")
        mock_cfg.models.embeddings = "text-embedding-3-small"
        mock_cfg.memory.min_relevance_score = 0.0
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value.data[0].embedding = [0.1] * 1536
        c = Chronicle(cfg=mock_cfg, client=mock_client)
        c.add_from_distillation("We decided to use async workers.")
        assert len(c.items) >= 1
        assert c.items[-1].metadata.get("source") == "distillation"


# ── Reflection Signal Tests ───────────────────────────────────────────────

def test_extract_routing_signals_returns_dict(tmp_path):
        """extract_routing_signals() returns dict with expected keys."""
        from unittest.mock import MagicMock
        from client.reflection import Reflection
        log = tmp_path / "reflections.jsonl"
        mock_cfg = MagicMock()
        mock_cfg.storage.reflection_log_path = str(log)
        r = Reflection(mock_cfg, client=MagicMock(), chronicle=MagicMock())
        messages = [{"role": "user", "content": "What is the best approach?"}]
        result = r.extract_routing_signals(messages)
        assert isinstance(result, dict)
        for key in ("dominant_topics", "message_length_avg", "code_present",
                    "question_count", "turn_count"):
            assert key in result

def test_extract_routing_signals_detects_code(tmp_path):
    """extract_routing_signals() sets code_present=True when code in Thread."""
    from unittest.mock import MagicMock
    from client.reflection import Reflection
    log = tmp_path / "reflections.jsonl"
    mock_cfg = MagicMock()
    mock_cfg.storage.reflection_log_path = str(log)
    r = Reflection(mock_cfg, client=MagicMock(), chronicle=MagicMock())
    messages = [{"role": "user", "content": "```python\ndef foo(): pass\n```"}]
    result = r.extract_routing_signals(messages)
    assert result["code_present"] is True

def test_extract_routing_signals_writes_to_log(tmp_path):
        """extract_routing_signals() writes signal record to reflections.jsonl."""
        import json
        from unittest.mock import MagicMock
        from client.reflection import Reflection
        log = tmp_path / "reflections.jsonl"
        mock_cfg = MagicMock()
        mock_cfg.storage.reflection_log_path = str(log)
        r = Reflection(mock_cfg, client=MagicMock(), chronicle=MagicMock())
        messages = [{"role": "user", "content": "How does this work?"}]
        r.extract_routing_signals(messages)
        assert log.exists()
        with open(log) as f:
            record = json.loads(f.readline())
        assert "timestamp" in record

