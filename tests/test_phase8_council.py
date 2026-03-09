"""
Phase 8 — The Council Test Suite
Run: pytest tests/test_phase8_council.py -v
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ── YAML File Existence Tests ─────────────────────────────────────────────────

def test_all_eight_role_yamls_exist():
    entities = [
        "archivist", "contrarian", "minimalist", "speculator",
        "pessimist", "toolsmith", "systems_thinker", "socratic",
    ]
    for e in entities:
        path = Path(f"entities/roles/{e}.yaml")
        assert path.exists(), f"Missing role YAML: {path}"

def test_all_eight_trait_yamls_exist():
    entities = [
        "archivist", "contrarian", "minimalist", "speculator",
        "pessimist", "toolsmith", "systems_thinker", "socratic",
    ]
    for e in entities:
        path = Path(f"entities/traits/{e}_traits.yaml")
        assert path.exists(), f"Missing traits YAML: {path}"


# ── EmergenceEngine Tests ─────────────────────────────────────────────────────

def test_emergence_no_file_returns_empty(tmp_path):
    from entities.emergence import EmergenceEngine
    engine = EmergenceEngine(tmp_path / "nonexistent.jsonl")
    council = MagicMock()
    council.get_emerged.return_value = set()
    result = engine.check_emergence(council)
    assert result == []

def test_emergence_empty_file_returns_empty(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    log.write_text("")
    engine = EmergenceEngine(log)
    council = MagicMock()
    result = engine.check_emergence(council)
    assert result == []

def test_emergence_single_entity_crosses_threshold(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    records = [
        {"dominant_topics": ["risk", "problem", "fail"], "code_present": False, "question_count": 0}
        for _ in range(8)
    ]
    with log.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    engine = EmergenceEngine(log)
    council = MagicMock()
    council.get_emerged.return_value = set()
    result = engine.check_emergence(council)
    assert "pessimist" in result

def test_emergence_already_emerged_not_returned_again(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    records = [
        {"dominant_topics": ["risk", "problem", "fail"], "code_present": False, "question_count": 0}
        for _ in range(8)
    ]
    with log.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    engine = EmergenceEngine(log)
    council = MagicMock()
    council.get_emerged.return_value = set()
    first = engine.check_emergence(council)
    assert "pessimist" in first
    second = engine.check_emergence(council)
    assert "pessimist" not in second

def test_emergence_skips_corrupt_lines(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    with log.open("w") as f:
        f.write('{"dominant_topics": ["risk", "problem"], "code_present": false, "question_count": 0}\n')
        f.write('NOT VALID JSON\n')
        f.write('{"dominant_topics": ["fail", "concern"], "code_present": false, "question_count": 0}\n')
    engine = EmergenceEngine(log)
    council = MagicMock()
    result = engine.check_emergence(council)
    assert isinstance(result, list)

def test_emergence_toolsmith_bonus_for_code(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    records = [
        {"dominant_topics": ["tool", "build"], "code_present": True, "question_count": 0}
        for _ in range(5)
    ]
    with log.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    engine = EmergenceEngine(log)
    council = MagicMock()
    engine.check_emergence(council)
    signals = engine.get_signal_strengths()
    assert signals["toolsmith"] > signals["archivist"]

def test_emergence_socratic_bonus_for_questions(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    records = [
        {"dominant_topics": ["why", "question"], "code_present": False, "question_count": 4}
        for _ in range(5)
    ]
    with log.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    engine = EmergenceEngine(log)
    council = MagicMock()
    engine.check_emergence(council)
    signals = engine.get_signal_strengths()
    assert signals["socratic"] > 0.5

def test_emergence_get_signal_strengths_all_entities():
    from entities.emergence import EmergenceEngine
    engine = EmergenceEngine("/nonexistent/path.jsonl")
    signals = engine.get_signal_strengths()
    expected = {"archivist", "contrarian", "minimalist", "speculator",
                "pessimist", "toolsmith", "systems_thinker", "socratic"}
    assert set(signals.keys()) == expected

def test_emergence_signal_decay_without_matches(tmp_path):
    from entities.emergence import EmergenceEngine
    log = tmp_path / "reflections.jsonl"
    records = [
        {"dominant_topics": ["risk"], "code_present": False, "question_count": 0},
    ] + [
        {"dominant_topics": ["unrelated_xyz"], "code_present": False, "question_count": 0}
        for _ in range(10)
    ]
    with log.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    engine = EmergenceEngine(log)
    council = MagicMock()
    engine.check_emergence(council)
    signals = engine.get_signal_strengths()
    assert signals["pessimist"] < 0.15


# ── InterruptionEngine Tests ──────────────────────────────────────────────────

def test_interruption_no_emerged_returns_no_interrupt():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = set()
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {}
    result = engine.check("hello", "hi there", council, emergence)
    assert result.should_interrupt is False
    assert result.entity_id is None

def test_interruption_domain_score_keyword_match():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    score = engine._domain_score("ready to ship and deploy this now", "pessimist")
    assert score > 0.0

def test_interruption_domain_score_no_match():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    score = engine._domain_score("the weather is nice today", "pessimist")
    assert score == 0.0

def test_interruption_domain_score_caps_at_one():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    score = engine._domain_score(
        "ship deploy launch release push publish go live merge finalize done ready", "pessimist"
    )
    assert score == 1.0

def test_interruption_fires_for_pessimist_shipping():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = {"pessimist"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"pessimist": 1.4}
    with patch("entities.interruption.random.random", return_value=0.1):
        result = engine.check(
            "OK we are ready to ship and deploy, done!",
            "Great, the feature is ready.",
            council, emergence,
        )
    assert result.should_interrupt is True
    assert result.entity_id == "pessimist"

def test_interruption_gate1_fails_low_domain_score():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = {"pessimist"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"pessimist": 1.4}
    result = engine.check("what is two plus two", "four", council, emergence)
    assert result.should_interrupt is False

def test_interruption_gate2_fails_probability():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = {"pessimist"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"pessimist": 1.4}
    with patch("entities.interruption.random.random", return_value=0.99):
        result = engine.check("ready to ship deploy and launch", "all done", council, emergence)
    assert result.should_interrupt is False

def test_interruption_gate3_fails_low_signal():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = {"pessimist"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"pessimist": 0.1}
    with patch("entities.interruption.random.random", return_value=0.1):
        result = engine.check("ready to ship deploy and launch", "all done", council, emergence)
    assert result.should_interrupt is False

def test_interruption_only_one_per_turn():
    from entities.interruption import InterruptionEngine
    engine = InterruptionEngine()
    council = MagicMock()
    council.get_emerged.return_value = {"pessimist", "contrarian"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"pessimist": 1.4, "contrarian": 1.2}
    with patch("entities.interruption.random.random", return_value=0.1):
        result = engine.check(
            "obviously this is definitely done and ready to ship",
            "agreed",
            council, emergence,
        )
    assert result.should_interrupt is True
    assert result.entity_id is not None

def test_interruption_silence_rule_respected():
    from entities.interruption import InterruptionEngine
    from entities.dynamics import InterEntityDynamics
    engine = InterruptionEngine()
    dynamics = InterEntityDynamics()
    dynamics.record_speaker("contrarian")
    council = MagicMock()
    council.get_emerged.return_value = {"speculator"}
    emergence = MagicMock()
    emergence.get_signal_strengths.return_value = {"speculator": 1.5}
    with patch("entities.interruption.random.random", return_value=0.1):
        result = engine.check(
            "this is the only option and the answer is clear",
            "agreed",
            council, emergence,
            dynamics=dynamics,
        )
    assert result.should_interrupt is False


# ── InterEntityDynamics Tests ─────────────────────────────────────────────────

def test_dynamics_reset_turn_clears_speakers():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    d.record_speaker("contrarian")
    d.reset_turn()
    assert d.speakers_this_turn() == []

def test_dynamics_silence_rule_contrarian():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    d.record_speaker("contrarian")
    assert d.is_silenced("speculator") is True
    assert d.is_silenced("minimalist") is True
    assert d.is_silenced("archivist") is False

def test_dynamics_no_silence_after_reset():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    d.record_speaker("contrarian")
    d.reset_turn()
    assert d.is_silenced("speculator") is False

def test_dynamics_socratic_boosts_contrarian():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    d.record_speaker("socratic")
    assert d._next_turn_multipliers.get("contrarian", 1.0) >= 2.0

def test_dynamics_presence_multiplier_default_is_one():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    assert d.get_presence_multiplier("archivist") == 1.0

def test_dynamics_get_relationships_returns_list():
    from entities.dynamics import InterEntityDynamics
    d = InterEntityDynamics()
    rels = d.get_relationships()
    assert len(rels) > 0
    for r in rels:
        assert hasattr(r, "entity_a")
        assert hasattr(r, "relationship_type")


# ── Council Phase 8 Additions ─────────────────────────────────────────────────

@pytest.fixture
def entity_dir(tmp_path):
    import yaml as _yaml
    (tmp_path / "roles").mkdir()
    (tmp_path / "traits").mkdir()
    (tmp_path / "profiles").mkdir()
    (tmp_path / "canon").mkdir()
    (tmp_path / "roles" / "luminarious.yaml").write_text(_yaml.dump({
        "entity_id": "luminarious", "display_name": "LUMINARIOUS", "color_hex": "C9A84C",
        "purpose": "You are the oracle.", "trait_ceilings": {},
        "presentation": {"default_sampling_profile": "anchor", "bubble_width_pct": 80},
        "summoned_only": False, "uninvited_eligible": False,
    }))
    (tmp_path / "traits" / "luminarious_traits.yaml").write_text(_yaml.dump({
        "entity_id": "luminarious", "traits": {"verbosity": 0.65}
    }))
    (tmp_path / "profiles" / "profiles.yaml").write_text(_yaml.dump({
        "profiles": {"anchor": {"temperature": 0.7, "top_p": 0.9, "max_output_tokens": 2000}}
    }))
    return tmp_path

def _add_entity_to_dir(tmp_path, entity_id, color, profile="anchor"):
    import yaml as _yaml
    (tmp_path / "roles" / f"{entity_id}.yaml").write_text(_yaml.dump({
        "entity_id": entity_id, "display_name": entity_id.upper(), "color_hex": color,
        "purpose": "Test.", "trait_ceilings": {}, "summoned_only": False,
        "presentation": {"default_sampling_profile": profile, "bubble_width_pct": 75},
    }))
    (tmp_path / "traits" / f"{entity_id}_traits.yaml").write_text(_yaml.dump({
        "entity_id": entity_id, "traits": {"verbosity": 0.5}
    }))

def test_council_emerge_adds_to_emerged(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    _add_entity_to_dir(entity_dir, "pessimist", "556B2F")
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    council.emerge("pessimist")
    assert council.has_emerged("pessimist")

def test_council_get_emerged_returns_set(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    assert isinstance(council.get_emerged(), set)

def test_council_has_emerged_false_initially(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    assert council.has_emerged("pessimist") is False

def test_council_luminarious_not_in_emerged_by_default(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    assert "luminarious" not in council.get_emerged()

def test_council_emerge_multiple_entities(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    _add_entity_to_dir(entity_dir, "pessimist", "556B2F")
    _add_entity_to_dir(entity_dir, "archivist", "4682B4", "precise")
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    council.emerge("pessimist")
    council.emerge("archivist")
    emerged = council.get_emerged()
    assert "pessimist" in emerged
    assert "archivist" in emerged

def test_council_emerge_idempotent(entity_dir):
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    _add_entity_to_dir(entity_dir, "pessimist", "556B2F")
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    council.emerge("pessimist")
    council.emerge("pessimist")
    assert len([e for e in council.get_emerged() if e == "pessimist"]) == 1
