from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml


@dataclass
class CompiledEntity:
    """
    The result of compiling an Entity definition.
    This is what app.py uses — the raw YAML is never touched at runtime.
    """
    entity_id:        str
    display_name:     str
    color_hex:        str
    instruction_str:  str          # Full system prompt prefix — injected into context
    sampling_profile: dict         # {"temperature":..., "top_p":..., "max_output_tokens":...}
    memory_policy:    dict         # Read/write permissions per memory layer
    summoned_only:    bool = False
    uninvited_eligible: bool = True
    bubble_width_pct: int = 80


class EntityCompiler:
    """
    Compiles Entity YAML definitions into CompiledEntity objects.

    Directory layout expected:
      base_path/roles/{entity_id}.yaml
      base_path/traits/{entity_id}_traits.yaml
      base_path/profiles/profiles.yaml

    Compilation is deterministic and synchronous.
    Cache is maintained per session — entities are not recompiled unless
    explicitly invalidated via invalidate_cache().
    """

    TRAIT_TO_INSTRUCTION: dict[str, dict] = {
        "verbosity": {
            "low":  "Be extremely concise. One to three sentences unless depth is explicitly requested.",
            "mid":  "Balance depth with brevity. Expand when complexity warrants it.",
            "high": "Be thorough and comprehensive. Explore all relevant dimensions.",
        },
        "challenge": {
            "low":  "Accept the Wizard's framing. Do not push back unless asked.",
            "mid":  "Respectfully question assumptions when they appear unfounded.",
            "high": "Actively challenge premises. Assume the framing may be wrong until proven otherwise.",
        },
        "speculation": {
            "low":  "Stick strictly to established facts and what can be reasonably inferred.",
            "mid":  "Speculate when helpful but flag conjecture clearly.",
            "high": "Freely explore possibilities and extrapolations. Imagination is welcome here.",
        },
        "structure": {
            "low":  "Respond in flowing prose. Avoid lists and headers unless essential.",
            "mid":  "Use structure when it genuinely aids clarity.",
            "high": "Always use structured formatting: headers, bullets, categorized sections.",
        },
        "warmth": {
            "low":  "Purely transactional. No social register. No pleasantries.",
            "mid":  "Warm but professional. Engaged without being familiar.",
            "high": "Warm, present, and genuinely engaged with the Wizard's situation.",
        },
        "precision": {
            "low":  "Approximate language is acceptable. Direction matters more than exactness.",
            "mid":  "Use precise terminology where it matters. Approximate where pedantry would obscure.",
            "high": "Always use exact terminology. Precision is non-negotiable.",
        },
    }

    def __init__(self, base_path: Path | str) -> None:
        """
        base_path: root of the entities/ directory.
        Cache is empty on init — entities compiled on first request.
        """
        self.base_path = Path(base_path)
        self._cache: dict[str, CompiledEntity] = {}
        self._profiles: dict[str, dict] = {}
        self._load_profiles()

    def compile(self, entity_id: str) -> CompiledEntity:
        """
        Compile an Entity by ID. Returns cached result if available.
        Raises EntityCompilationError if definition files not found.

        Pipeline:
          1. Check cache. Return if present.
          2. Load role YAML from roles/{entity_id}.yaml
          3. Load traits YAML from traits/{entity_id}_traits.yaml
          4. Validate traits against role ceilings
          5. Build instruction string from role purpose + trait instructions
          6. Load sampling profile by name
          7. Build CompiledEntity. Store in cache. Return.
        """
        if entity_id in self._cache:
            return self._cache[entity_id]

        role = self._load_role(entity_id)
        traits = self._load_traits(entity_id)
        validated_traits = self._validate_traits(traits, role.get("trait_ceilings", {}))
        instruction_str = self._build_instruction_string(role, validated_traits)
        profile_name = role.get("presentation", {}).get("default_sampling_profile", "anchor")
        sampling_profile = self._profiles.get(profile_name, self._profiles["anchor"])

        compiled = CompiledEntity(
            entity_id=entity_id,
            display_name=role.get("display_name", entity_id.upper()),
            color_hex=role.get("color_hex", "C9A84C"),
            instruction_str=instruction_str,
            sampling_profile=sampling_profile,
            memory_policy=role.get("memory_policy", {}),
            summoned_only=role.get("summoned_only", False),
            uninvited_eligible=not role.get("summoned_only", False),
            bubble_width_pct=role.get("presentation", {}).get("bubble_width_pct", 80),
        )
        self._cache[entity_id] = compiled
        return compiled

    def invalidate_cache(self, entity_id: str | None = None) -> None:
        """Clear cache for one entity or all if entity_id is None."""
        if entity_id:
            self._cache.pop(entity_id, None)
        else:
            self._cache.clear()

    # ── Private Methods ─────────────────────────────────────────────────

    def _load_role(self, entity_id: str) -> dict:
        """Load and return role YAML as dict. Raises EntityCompilationError if absent."""
        path = self.base_path / "roles" / f"{entity_id}.yaml"
        if not path.exists():
            raise EntityCompilationError(f"Role definition not found: {path}")
        return yaml.safe_load(path.read_text())

    def _load_traits(self, entity_id: str) -> dict:
        """Load and return traits YAML. Returns empty dict if absent (all traits default to 0.5)."""
        path = self.base_path / "traits" / f"{entity_id}_traits.yaml"
        if not path.exists():
            return {"traits": {}}
        data = yaml.safe_load(path.read_text())
        return data.get("traits", {})

    def _validate_traits(self, traits: dict, ceilings: dict) -> dict:
        """
        Cap trait values at their role ceilings.
        Fill missing traits with 0.5 default.
        Clamp all values to [0.0, 1.0].

        Returns validated trait dict.
        """
        all_traits = ["verbosity","challenge","speculation","structure","warmth","precision"]
        validated = {}
        for trait in all_traits:
            raw = float(traits.get(trait, 0.5))
            ceiling = float(ceilings.get(trait, 1.0))
            validated[trait] = max(0.0, min(ceiling, raw))
        return validated

    def _build_instruction_string(self, role: dict, traits: dict) -> str:
        """
        Assemble the full instruction string for this Entity.

        Structure:
          {role purpose text}
          blank line
          BEHAVIORAL PARAMETERS:
          {one instruction line per trait, selected by low/mid/high bucket}

        Trait bucketing:
          0.0–0.33: "low"
          0.34–0.66: "mid"
          0.67–1.0:  "high"
        """
        purpose = role.get("purpose", "").strip()
        lines = [purpose, "", "BEHAVIORAL PARAMETERS:"]
        for trait, value in traits.items():
            if trait not in self.TRAIT_TO_INSTRUCTION:
                continue
            if value <= 0.33:
                bucket = "low"
            elif value <= 0.66:
                bucket = "mid"
            else:
                bucket = "high"
            instruction = self.TRAIT_TO_INSTRUCTION[trait][bucket]
            lines.append(f"- {instruction}")
        return "\n".join(lines)

    def _load_profiles(self) -> None:
        """Load profiles.yaml into self._profiles dict."""
        path = self.base_path / "profiles" / "profiles.yaml"
        if not path.exists():
            self._profiles = {"anchor": {"temperature":0.7,"top_p":0.9,"max_output_tokens":2000}}
            return
        data = yaml.safe_load(path.read_text())
        self._profiles = data.get("profiles", {})
        if "anchor" not in self._profiles:
            self._profiles["anchor"] = {"temperature":0.7,"top_p":0.9,"max_output_tokens":2000}


class EntityCompilationError(Exception):
    """Raised when entity definition files are missing or malformed."""
    pass

