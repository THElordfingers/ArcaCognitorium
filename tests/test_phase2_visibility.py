"""
Phase 2 — Status Visibility Test Suite
Run: pytest tests/test_phase2_visibility.py -v
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from dataclasses import replace


# ── StatusState Tests ─────────────────────────────────────────────────────

def test_status_state_defaults():
    """StatusState initializes with safe defaults."""
    from ui.panes.status_layer import StatusState
    s = StatusState()
    assert s.model_id == '—'
    assert s.entity_name == 'LUMINARIOUS'
    assert s.context_pct == 0
    assert s.streaming == False

def test_status_state_partial_update():
    """replace() on StatusState updates only specified fields."""
    from ui.panes.status_layer import StatusState
    s = StatusState()
    s2 = replace(s, model_id='gpt-4o', context_pct=72)
    assert s2.model_id == 'gpt-4o'
    assert s2.context_pct == 72
    assert s2.entity_name == 'LUMINARIOUS'  # unchanged


# ── StatusLayer Render Tests ──────────────────────────────────────────────

def test_status_layer_renders_model():
    """Status layer render includes model_id string."""
    from ui.panes.status_layer import StatusLayer, StatusState
    layer = StatusLayer()
    layer.state = StatusState(model_id='gpt-4o-mini')
    rendered = layer.render()
    assert 'gpt-4o-mini' in rendered.plain

def test_status_layer_context_bar_segments():
    """Context bar has correct segment count for given percentage."""
    from ui.panes.status_layer import StatusLayer, StatusState
    layer = StatusLayer()
    layer.state = StatusState(context_pct=50)
    rendered = layer.render()
    # 50% of 8 segments = 4 filled
    assert '▓▓▓▓░░░░' in rendered.plain

def test_status_layer_streaming_indicator():
    """Streaming state appends ellipsis to model id."""
    from ui.panes.status_layer import StatusLayer, StatusState
    layer = StatusLayer()
    layer.state = StatusState(model_id='gpt-4o', streaming=True)
    rendered = layer.render()
    assert 'gpt-4o…' in rendered.plain

def test_status_layer_distillation_count_hidden_when_zero():
    """Distillation marker does not appear when count is 0."""
    from ui.panes.status_layer import StatusLayer, StatusState
    layer = StatusLayer()
    layer.state = StatusState(distillation_count=0)
    rendered = layer.render()
    assert 'P0' not in rendered.plain

def test_status_layer_distillation_count_shown_when_nonzero():
    """Distillation marker appears when count > 0."""
    from ui.panes.status_layer import StatusLayer, StatusState
    layer = StatusLayer()
    layer.state = StatusState(distillation_count=2)
    rendered = layer.render()
    assert 'P2' in rendered.plain


# ── BubbleMessage Tests ───────────────────────────────────────────────────

def test_bubble_message_wizard_creates_wizard_bubble():
    """BubbleFactory returns WizardBubble for wizard speaker."""
    from ui.rendering.bubbles import BubbleFactory, BubbleMessage, WizardBubble
    msg = BubbleMessage(
        speaker_id='wizard', display_name='WIZARD',
        content='Hello', model_id='—', timestamp='14:22',
        color_hex='D4C8A8'
    )
    bubble = BubbleFactory.create(msg)
    assert isinstance(bubble, WizardBubble)

def test_bubble_message_luminarious_creates_luminarious_bubble():
    """BubbleFactory returns LuminariousBubble for luminarious speaker."""
    from ui.rendering.bubbles import BubbleFactory, BubbleMessage, LuminariousBubble
    msg = BubbleMessage(
        speaker_id='luminarious', display_name='LUMINARIOUS',
        content='The fire is lit.', model_id='gpt-4o-mini',
        timestamp='14:22', color_hex='C9A84C'
    )
    bubble = BubbleFactory.create(msg)
    assert isinstance(bubble, LuminariousBubble)

def test_luminarious_bubble_append_chunk():
    """append_chunk() accumulates content correctly."""
    from ui.rendering.bubbles import LuminariousBubble, BubbleMessage
    msg = BubbleMessage(
        speaker_id='luminarious', display_name='LUMINARIOUS',
        content='The ', model_id='gpt-4o', timestamp='14:22', color_hex='C9A84C'
    )
    bubble = LuminariousBubble(msg)
    bubble.append_chunk('fire ')
    bubble.append_chunk('is lit.')
    assert bubble._content == 'The fire is lit.'


# ── AnimationController Tests ─────────────────────────────────────────────

def test_animation_circuit_breaker_disables_layer():
    """_check_perf() disables layer when budget exceeded."""
    from ui.rendering.animations import AnimationController, AnimationConfig
    mock_app = MagicMock()
    ctrl = AnimationController(app=mock_app, config=AnimationConfig())
    result = ctrl._check_perf('glyph_drift', elapsed_ms=25.0)  # > 16ms
    assert result == False
    assert 'glyph_drift' in ctrl._disabled_layers

def test_animation_circuit_breaker_passes_within_budget():
    """_check_perf() returns True when within perf budget."""
    from ui.rendering.animations import AnimationController, AnimationConfig
    mock_app = MagicMock()
    ctrl = AnimationController(app=mock_app, config=AnimationConfig())
    result = ctrl._check_perf('glyph_drift', elapsed_ms=4.0)  # < 16ms
    assert result == True
    assert 'glyph_drift' not in ctrl._disabled_layers

def test_animation_master_disabled_skips_start():
    """start_idle() does nothing when master_enabled=False."""
    from ui.rendering.animations import AnimationController, AnimationConfig
    mock_app = MagicMock()
    ctrl = AnimationController(mock_app, AnimationConfig(master_enabled=False))
    ctrl.start_idle()
    mock_app.run_worker.assert_not_called()

def test_event_effects_disabled_skips_fire():
    """fire_event() does nothing when event_effects=False."""
    from ui.rendering.animations import AnimationController, AnimationConfig
    mock_app = MagicMock()
    ctrl = AnimationController(mock_app, AnimationConfig(event_effects=False))
    ctrl.fire_event('distillation')
    mock_app.run_worker.assert_not_called()


# ── Boot Sequence Tests ───────────────────────────────────────────────────

def test_sigils_directory_exists():
    """sigils/ directory exists after Phase 2 setup."""
    from pathlib import Path
    assert Path('sigils').is_dir(), 'sigils/ directory missing'

def test_sigils_default_file_exists():
    """At least one sigil file exists for boot sequence fallback."""
    from pathlib import Path
    sigil_files = list(Path('sigils').glob('*.txt'))
    assert len(sigil_files) >= 1, 'No .txt sigil files found in sigils/'

def test_pyfiglet_renders_title():
    """pyfiglet renders LUMINARIOUS with a valid font without error."""
    import pyfiglet
    result = pyfiglet.figlet_format('LUMINARIOUS', font='slant')
    assert 'LUMINARIOUS' not in result  # figlet transforms the text
    assert len(result) > 20  # but produces substantial ASCII art

def test_boot_lines_in_config():
    """config.yaml boot.boot_lines list is non-empty."""
    import yaml
    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    assert 'boot' in cfg
    assert 'boot_lines' in cfg['boot']
    assert len(cfg['boot']['boot_lines']) >= 1
