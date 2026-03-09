"""
Phase 7 — Routing Intelligence Test Suite
Run: pytest tests/test_phase7_routing.py -v
"""
import json
import pytest
from pathlib import Path


# ── Signal Scoring Tests ─────────────────────────────────────────────────────

def test_score_length_zero_for_empty():
    from client.router import Router
    r = Router()
    assert r._score_length("") == 0.0

def test_score_length_caps_at_one():
    from client.router import Router
    r = Router()
    assert r._score_length("word " * 200) == 1.0

def test_score_length_linear_midpoint():
    from client.router import Router
    r = Router()
    assert abs(r._score_length("word " * 50) - 0.5) < 0.05

def test_score_code_detects_backticks():
    from client.router import Router
    r = Router()
    assert r._score_code("here is ```python\ncode\n```") == 1.0

def test_score_code_detects_def():
    from client.router import Router
    r = Router()
    assert r._score_code("def my_function(x): return x") == 1.0

def test_score_code_zero_for_plain_text():
    from client.router import Router
    r = Router()
    assert r._score_code("what is the meaning of life?") == 0.0

def test_score_question_depth_zero_no_question():
    from client.router import Router
    r = Router()
    assert r._score_question_depth("tell me about routing") == 0.0

def test_score_question_depth_multipart():
    from client.router import Router
    r = Router()
    msg = "What causes the Chronicle to miss entries? And how does this affect the Grimoire?"
    assert r._score_question_depth(msg) == 1.0

def test_score_question_depth_single_short():
    from client.router import Router
    r = Router()
    assert r._score_question_depth("what time is it?") == 0.3

def test_score_analytical_zero_for_casual():
    from client.router import Router
    r = Router()
    assert r._score_analytical("hi how are you") == 0.0

def test_score_analytical_one_trigger():
    from client.router import Router
    r = Router()
    score = r._score_analytical("can you compare these two approaches?")
    assert abs(score - 1/3) < 0.05

def test_score_analytical_caps_at_one():
    from client.router import Router
    r = Router()
    score = r._score_analytical("compare analyze design architect trade-off evaluate critique")
    assert score == 1.0

def test_score_topic_novelty_neutral_no_history():
    from client.router import Router
    r = Router()
    r._recent_topics = []
    assert r._score_topic_novelty("something about routing") == 0.5

def test_score_topic_novelty_high_overlap():
    from client.router import Router
    r = Router()
    r._recent_topics = ["routing", "signal", "model", "score"]
    score = r._score_topic_novelty("routing signal score model selection")
    assert score < 0.5

def test_score_topic_novelty_no_overlap():
    from client.router import Router
    r = Router()
    r._recent_topics = ["pancakes", "breakfast", "morning"]
    score = r._score_topic_novelty("architecture routing signals distillation")
    assert score > 0.5


# ── route() and route_full() Tests ───────────────────────────────────────────

def test_route_returns_string():
    from client.router import Router
    r = Router()
    result = r.route("hello there")
    assert isinstance(result, str)

def test_route_empty_message_returns_fast():
    from client.router import Router
    r = Router()
    assert r.route("") == r.fast_model
    assert r.route("   ") == r.fast_model

def test_route_none_safe():
    from client.router import Router
    r = Router()
    result = r.route(None or "")
    assert result == r.fast_model

def test_route_simple_greeting_is_fast():
    from client.router import Router
    r = Router()
    result = r.route("hi")
    assert result == r.fast_model

def test_route_complex_analytical_is_smart():
    """Multi-signal message: long + analytical triggers + multi-part question → smart."""
    from client.router import Router
    r = Router()
    msg = (
        "Can you compare and analyze the trade-offs between the fat/muscle "
        "classification approach and a pure keyword system? How does this affect "
        "Chronicle quality, why does the session baseline matter for routing decisions, "
        "and what architectural implications should we evaluate before committing to "
        "this design pattern across the entire codebase? Please also walk me through "
        "the implications of switching to a different approach later in the project."
    )
    result = r.route(msg)
    assert result == r.smart_model

def test_route_code_signals_score_is_nonzero():
    """Code presence scores 1.0 on code_signals — verify the signal fires correctly."""
    from client.router import Router
    r = Router()
    msg = "```python\ndef route(self, message):\n    return self.fast_model\n```\nWhat does this do?"
    result = r.route_full(msg)
    assert result.signals["code_signals"] == 1.0

def test_route_full_returns_route_result():
    from client.router import Router, RouteResult
    r = Router()
    result = r.route_full("explain why the signal scoring works")
    assert isinstance(result, RouteResult)
    assert isinstance(result.model_id, str)
    assert isinstance(result.score, float)
    assert isinstance(result.signals, dict)
    assert isinstance(result.reason, str)

def test_route_full_signals_have_all_keys():
    from client.router import Router
    r = Router()
    result = r.route_full("tell me something")
    for key in ("message_length", "code_signals", "question_depth",
                "analytical_markers", "topic_novelty", "session_baseline", "explicit_override"):
        assert key in result.signals

def test_route_full_signals_in_range():
    from client.router import Router
    r = Router()
    result = r.route_full("analyze the architectural implications of the routing system design")
    for k, v in result.signals.items():
        assert 0.0 <= v <= 1.0, f"Signal {k} out of range: {v}"

def test_session_signals_accumulate():
    from client.router import Router
    r = Router()
    for _ in range(5):
        r.route("some message about architecture and design trade-offs for the system")
    assert len(r._session_signals) == 5

def test_session_signals_cap_at_50():
    from client.router import Router
    r = Router()
    for _ in range(55):
        r.route("word " * 10)
    assert len(r._session_signals) == 50


# ── Pin / Unpin Tests ─────────────────────────────────────────────────────────

def test_pin_model_overrides_routing():
    from client.router import Router
    r = Router()
    r.pin_model(r.smart_model)
    assert r.route("hi") == r.smart_model

def test_pin_model_was_pinned_flag():
    from client.router import Router, RouteResult
    r = Router()
    r.pin_model(r.fast_model)
    result = r.route_full("analyze everything deeply")
    assert result.was_pinned is True

def test_unpin_model_restores_routing():
    from client.router import Router
    r = Router()
    r.pin_model(r.smart_model)
    r.unpin_model()
    assert r._pinned_model is None
    assert r.route("hi") == r.fast_model


# ── Reflection Baseline Tests ─────────────────────────────────────────────────

def test_reflection_baseline_neutral_on_missing_file():
    from client.router import Router
    r = Router(reflection_log_path="/nonexistent/path/reflections.jsonl")
    assert r._reflection_baseline.get("avg_complexity") == 0.5

def test_reflection_baseline_loads_valid_records(tmp_path):
    from client.router import Router
    log = tmp_path / "reflections.jsonl"
    records = [
        {"message_length_avg": 80, "code_present": True, "dominant_topics": ["architecture", "routing"]},
        {"message_length_avg": 60, "code_present": False, "dominant_topics": ["grimoire", "memory"]},
    ]
    with log.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    router = Router(reflection_log_path=str(log))
    assert router._reflection_baseline["avg_complexity"] > 0.0
    assert len(router._recent_topics) > 0

def test_reflection_baseline_skips_corrupt_lines(tmp_path):
    from client.router import Router
    log = tmp_path / "reflections.jsonl"
    with log.open("w") as f:
        f.write('{"message_length_avg": 50, "code_present": false, "dominant_topics": ["test"]}\n')
        f.write('THIS IS NOT JSON\n')
        f.write('{"message_length_avg": 70, "code_present": true, "dominant_topics": ["code"]}\n')
    router = Router(reflection_log_path=str(log))
    assert router._reflection_baseline.get("avg_complexity", 0) > 0

def test_refresh_reflection_baseline(tmp_path):
    from client.router import Router
    log = tmp_path / "reflections.jsonl"
    log.write_text("")
    router = Router(reflection_log_path=str(log))
    assert router._reflection_baseline.get("avg_complexity") == 0.5
    with log.open("a") as f:
        f.write('{"message_length_avg": 90, "code_present": true, "dominant_topics": ["arch"]}\n')
    router.refresh_reflection_baseline()
    assert router._reflection_baseline.get("avg_complexity", 0) > 0.5


# ── Threshold Clamping ────────────────────────────────────────────────────────

def test_smart_threshold_clamped_below_zero():
    import warnings
    from client.router import Router
    with warnings.catch_warnings(record=True):
        r = Router(smart_threshold=-0.5)
    assert r.smart_threshold == 0.0

def test_smart_threshold_clamped_above_one():
    import warnings
    from client.router import Router
    with warnings.catch_warnings(record=True):
        r = Router(smart_threshold=1.5)
    assert r.smart_threshold == 1.0


# ── ModelRouter Integration ───────────────────────────────────────────────────

def test_model_router_decide_returns_model_decision():
    from unittest.mock import MagicMock, patch
    from client.router import ModelRouter, ModelDecision
    mock_cfg = MagicMock()
    mock_cfg.models.fast = "claude-sonnet-4-6"
    mock_cfg.models.smart = "claude-opus-4-6"
    mock_cfg.routing.smart_threshold = 0.55
    mock_cfg.routing.reflection_window = 50
    mock_cfg.storage.reflection_log_path = "/nonexistent/reflections.jsonl"
    with patch("client.router.ClaudeBox"):
        mr = ModelRouter(mock_cfg, api_key="test-key")
    result = mr.decide("hello")
    assert isinstance(result, ModelDecision)
    assert isinstance(result.model, str)

def test_model_router_forced_smart():
    from unittest.mock import MagicMock, patch
    from client.router import ModelRouter
    mock_cfg = MagicMock()
    mock_cfg.models.fast = "claude-sonnet-4-6"
    mock_cfg.models.smart = "claude-opus-4-6"
    mock_cfg.routing.smart_threshold = 0.55
    mock_cfg.routing.reflection_window = 50
    mock_cfg.storage.reflection_log_path = "/nonexistent/reflections.jsonl"
    with patch("client.router.ClaudeBox"):
        mr = ModelRouter(mock_cfg, api_key="test-key")
    result = mr.decide("hi", forced="smart")
    assert result.model == "claude-opus-4-6"

def test_model_router_forced_fast():
    from unittest.mock import MagicMock, patch
    from client.router import ModelRouter
    mock_cfg = MagicMock()
    mock_cfg.models.fast = "claude-sonnet-4-6"
    mock_cfg.models.smart = "claude-opus-4-6"
    mock_cfg.routing.smart_threshold = 0.55
    mock_cfg.routing.reflection_window = 50
    mock_cfg.storage.reflection_log_path = "/nonexistent/reflections.jsonl"
    with patch("client.router.ClaudeBox"):
        mr = ModelRouter(mock_cfg, api_key="test-key")
    result = mr.decide("analyze everything deeply with complex reasoning", forced="fast")
    assert result.model == "claude-sonnet-4-6"
