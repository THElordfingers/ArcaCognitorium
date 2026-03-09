"""
Phase 6 — Entity Foundation Test Suite
Run: pytest tests/test_phase6_entities.py -v
"""
import pytest
from pathlib import Path
import yaml
import tempfile, os


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def entity_dir(tmp_path):
    """Create a minimal entity directory structure for testing."""
    (tmp_path/"roles").mkdir()
    (tmp_path/"traits").mkdir()
    (tmp_path/"profiles").mkdir()
    (tmp_path/"canon").mkdir()

    # Minimal Luminarious role
    (tmp_path/"roles"/"luminarious.yaml").write_text(yaml.dump({
        "entity_id": "luminarious",
        "display_name": "LUMINARIOUS",
        "color_hex": "C9A84C",
        "purpose": "You are Luminarious, the oracle.",
        "trait_ceilings": {"verbosity":0.85,"challenge":0.6,"speculation":0.7,
                           "structure":0.8,"warmth":0.9,"precision":0.8},
        "memory_policy": {"can_read_grimoire":True,"can_write_grimoire":False},
        "presentation": {"default_sampling_profile":"anchor","bubble_width_pct":80},
    }))

    # Minimal Assessor role
    (tmp_path/"roles"/"assessor.yaml").write_text(yaml.dump({
        "entity_id": "assessor",
        "display_name": "THE ASSESSOR",
        "color_hex": "8B2020",
        "purpose": "You observe and profile.",
        "trait_ceilings": {"verbosity":0.7,"challenge":0.2,"speculation":0.1,
                           "structure":1.0,"warmth":0.0,"precision":1.0},
        "memory_policy": {"can_read_grimoire":True,"can_write_grimoire":True},
        "presentation": {"default_sampling_profile":"precise","bubble_width_pct":70},
        "summoned_only": True,
    }))

    # Traits
    (tmp_path/"traits"/"luminarious_traits.yaml").write_text(yaml.dump({
        "entity_id": "luminarious",
        "traits": {"verbosity":0.65,"challenge":0.45,"speculation":0.55,
                   "structure":0.60,"warmth":0.75,"precision":0.70}
    }))
    (tmp_path/"traits"/"assessor_traits.yaml").write_text(yaml.dump({
        "entity_id": "assessor",
        "traits": {"verbosity":0.60,"challenge":0.05,"speculation":0.05,
                   "structure":0.95,"warmth":0.00,"precision":0.98}
    }))

    # Profiles
    (tmp_path/"profiles"/"profiles.yaml").write_text(yaml.dump({
        "profiles": {
            "anchor":  {"temperature":0.7,"top_p":0.9,"max_output_tokens":2000},
            "precise": {"temperature":0.2,"top_p":0.85,"max_output_tokens":1500},
        }
    }))

    return tmp_path


# ── EntityCompiler Tests ─────────────────────────────────────────────────

def test_compiler_compiles_luminarious(entity_dir):
    """EntityCompiler produces valid CompiledEntity for luminarious."""
    from entities.entity_compiler import EntityCompiler
    compiler = EntityCompiler(entity_dir)
    compiled = compiler.compile("luminarious")
    assert compiled.entity_id == "luminarious"
    assert compiled.display_name == "LUMINARIOUS"
    assert compiled.color_hex == "C9A84C"
    assert len(compiled.instruction_str) > 50
    assert "BEHAVIORAL PARAMETERS" in compiled.instruction_str

def test_compiler_instruction_contains_purpose(entity_dir):
    """Compiled instruction string starts with the role purpose text."""
    from entities.entity_compiler import EntityCompiler
    compiler = EntityCompiler(entity_dir)
    compiled = compiler.compile("luminarious")
    assert "You are Luminarious" in compiled.instruction_str

def test_compiler_uses_correct_sampling_profile(entity_dir):
    """Luminarious uses anchor profile; Assessor uses precise profile."""
    from entities.entity_compiler import EntityCompiler
    compiler = EntityCompiler(entity_dir)
    lum = compiler.compile("luminarious")
    asm = compiler.compile("assessor")
    assert lum.sampling_profile["temperature"] == 0.7
    assert asm.sampling_profile["temperature"] == 0.2

def test_compiler_caches_results(entity_dir):
    """Second compile() call returns cached object (same id)."""
    from entities.entity_compiler import EntityCompiler
    compiler = EntityCompiler(entity_dir)
    first = compiler.compile("luminarious")
    second = compiler.compile("luminarious")
    assert first is second

def test_compiler_invalidate_cache(entity_dir):
    """invalidate_cache() forces recompilation."""
    from entities.entity_compiler import EntityCompiler
    compiler = EntityCompiler(entity_dir)
    first = compiler.compile("luminarious")
    compiler.invalidate_cache("luminarious")
    second = compiler.compile("luminarious")
    assert first is not second

def test_compiler_raises_on_missing_role(entity_dir):
    """EntityCompilationError raised for unknown entity_id."""
    from entities.entity_compiler import EntityCompiler, EntityCompilationError
    compiler = EntityCompiler(entity_dir)
    with pytest.raises(EntityCompilationError):
        compiler.compile("nonexistent_entity")

def test_compiler_caps_traits_at_ceiling(entity_dir):
    """Traits exceeding role ceilings are clamped to ceiling value."""
    from entities.entity_compiler import EntityCompiler
    import yaml as _yaml
    # Override traits with value exceeding ceiling
    (entity_dir/"traits"/"luminarious_traits.yaml").write_text(_yaml.dump({
        "entity_id": "luminarious",
        "traits": {"verbosity": 0.99, "challenge": 0.99, "speculation": 0.99,
                   "structure": 0.99, "warmth": 0.99, "precision": 0.99}
    }))
    compiler = EntityCompiler(entity_dir)
    validated = compiler._validate_traits(
        {"verbosity": 0.99, "challenge": 0.99},
        {"verbosity": 0.85, "challenge": 0.6}
    )
    assert validated["verbosity"] == 0.85
    assert validated["challenge"] == 0.6


# ── Council Tests ────────────────────────────────────────────────────────

def test_council_compiles_luminarious_on_init(entity_dir):
    """Council compiles Luminarious automatically on instantiation."""
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    assert council.active.entity_id == "luminarious"

def test_council_summon_changes_active(entity_dir):
    """council.summon() changes the active Entity."""
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    council.summon("assessor")
    assert council.active.entity_id == "assessor"

def test_council_dismiss_returns_to_luminarious(entity_dir):
    """council.dismiss() restores Luminarious as active."""
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    council.summon("assessor")
    council.dismiss()
    assert council.active.entity_id == "luminarious"

def test_council_caches_summoned_entities(entity_dir):
    """Summoning the same entity twice does not recompile."""
    from entities.entity_compiler import EntityCompiler
    from entities.council import Council
    compiler = EntityCompiler(entity_dir)
    council = Council(compiler)
    first = council.summon("assessor")
    second = council.summon("assessor")
    assert first is second


# ── Entity YAML Files Tests ───────────────────────────────────────────────

def test_luminarious_yaml_exists():
    """entities/roles/luminarious.yaml exists in project."""
    assert Path("entities/roles/luminarious.yaml").exists()

def test_assessor_yaml_exists():
    """entities/roles/assessor.yaml exists in project."""
    assert Path("entities/roles/assessor.yaml").exists()

def test_luminarious_traits_yaml_exists():
    """entities/traits/luminarious_traits.yaml exists."""
    assert Path("entities/traits/luminarious_traits.yaml").exists()

def test_profiles_yaml_has_required_profiles():
    """profiles.yaml contains at minimum anchor and precise profiles."""
    import yaml as _yaml
    data = _yaml.safe_load(Path("entities/profiles/profiles.yaml").read_text())
    profiles = data.get("profiles", {})
    assert "anchor" in profiles
    assert "precise" in profiles

def test_entity_canon_yaml_has_ten_entities():
    """entity_canon.yaml defines all 10 canonical Entities."""
    import yaml as _yaml
    data = _yaml.safe_load(Path("entities/canon/entity_canon.yaml").read_text())
    entities = data.get("entities", [])
    assert len(entities) == 10

def test_all_canon_entities_have_required_fields():
    """Every canon Entity has entity_id, display_name, color_hex."""
    import yaml as _yaml
    data = _yaml.safe_load(Path("entities/canon/entity_canon.yaml").read_text())
    for entity in data.get("entities", []):
        assert "entity_id" in entity, f"Missing entity_id in {entity}"
        assert "display_name" in entity, f"Missing display_name in {entity}"
        assert "color_hex" in entity, f"Missing color_hex in {entity}"
