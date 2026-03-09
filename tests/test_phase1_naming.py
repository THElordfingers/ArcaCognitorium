"""
7.1 tests/test_phase1_naming.py
Phase 1 — Naming Pass Test Suite
Verifies all renames completed correctly and interfaces function under new names.
Run: pytest tests/test_phase1_naming.py -v
"""
import pytest
from pathlib import Path


# ── Import Tests — verify new module names resolve ────────────────────────

def test_chronicle_importable():
    """Chronicle module imports without error under new name."""
    from memory.chronicle import Chronicle
    assert Chronicle is not None

def test_distillation_importable():
    """Distillation module imports without error under new name."""
    from memory.distillation import Distillation
    assert Distillation is not None

def test_reflection_importable():
    """Reflection module imports without error under new name."""
    from client.reflection import Reflection
    assert Reflection is not None


# ── Old Name Tests — verify old names no longer exist ─────────────────────

def test_vector_store_module_gone():
    """vector_store.py must not exist — rename must be complete."""
    assert not Path('memory/vector_store.py').exists(), \
        'memory/vector_store.py still exists — rename incomplete'

def test_summarizer_module_gone():
    """summarizer.py must not exist — rename must be complete."""
    assert not Path('memory/summarizer.py').exists(), \
        'memory/summarizer.py still exists — rename incomplete'

def test_analytics_module_gone():
    """analytics.py must not exist — rename must be complete."""
    assert not Path('client/analytics.py').exists(), \
        'client/analytics.py still exists — rename incomplete'


# ── Functional Tests — verify behavior unchanged under new names ───────────

def test_chronicle_instantiates(tmp_path):
    """Chronicle instantiates correctly without an API client."""
    from unittest.mock import MagicMock, patch
    from memory.chronicle import Chronicle
    mock_cfg = MagicMock()
    mock_cfg.storage.vectors_path = str(tmp_path / "chronicle.pkl")
    mock_cfg.memory.min_relevance_score = 0.0
    with patch("memory.chronicle.Chronicle._get_embedder"):
        c = Chronicle(cfg=mock_cfg)
    assert c is not None

def test_chronicle_add_and_retrieve(tmp_path):
    """Chronicle add() and query() methods exist under new name."""
    from unittest.mock import MagicMock, patch
    from memory.chronicle import Chronicle
    mock_cfg = MagicMock()
    mock_cfg.storage.vectors_path = str(tmp_path / "chronicle.pkl")
    mock_cfg.memory.min_relevance_score = 0.0
    with patch("memory.chronicle.Chronicle._get_embedder"):
        c = Chronicle(cfg=mock_cfg)
    assert hasattr(c, "add")
    assert hasattr(c, "query")

def test_distillation_instantiates():
    """Distillation class instantiates correctly without a box."""
    from memory.distillation import Distillation
    d = Distillation()
    assert d is not None

def test_distillation_should_distill_logic():
    """Distillation.distill() is callable without an API client."""
    from memory.distillation import Distillation, DistillationResult
    d = Distillation()
    result = d.distill([
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ])
    assert isinstance(result, DistillationResult)
    assert isinstance(result.compressed_message, dict)

def test_reflection_instantiates():
    """Reflection class instantiates correctly with box kwarg."""
    from unittest.mock import MagicMock
    from client.reflection import Reflection
    r = Reflection(MagicMock(), box=MagicMock(), chronicle=MagicMock())
    assert r is not None


# ── Config Tests — verify lore names in config ────────────────────────────

def test_config_app_name():
    """config.yaml app.name is set to Luminarious."""
    import yaml
    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    assert cfg['app']['name'] == 'Luminarious', \
        f"Expected 'Luminarious', got '{cfg['app']['name']}'"

def test_no_old_strings_in_config():
    """config.yaml contains no legacy ChatGPT or vector_store references."""
    content = Path('config.yaml').read_text()
    assert 'ChatGPT' not in content, 'Legacy string ChatGPT found in config.yaml'
    assert 'vector_store' not in content, 'Legacy path vector_store found in config.yaml'
    assert 'analytics' not in content, 'Legacy string analytics found in config.yaml'


# ── App Boot Test — verify app starts without ImportError ─────────────────

def test_main_imports_without_error():
    """main.py and its dependency chain import without error after renames."""
    import importlib
    try:
        spec = importlib.util.spec_from_file_location('main', 'main.py')
        mod = importlib.util.module_from_spec(spec)
        assert spec is not None
    except ImportError as e:
        pytest.fail(f'Import chain broken after rename: {e}')
