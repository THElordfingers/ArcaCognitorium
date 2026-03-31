# Auctoritas Spectralis — schema.py
# v1.0.0
"""Tower canonical theme.json schema — the inter-app contract."""

from typing import TypedDict


class TokenSet(TypedDict):
    """The ten canonical color tokens."""
    c_bg: str        # Hex. Void — primary background.
    c_panel: str     # Hex. Obsidian — panels, cards, dialogs.
    c_gold: str      # Hex. Aurum — primary accent.
    c_gold_dim: str  # Hex. Aurum Dimmus — hints, subtitles.
    c_gold_dark: str # Hex. Aurum Nox — borders, separator lines.
    c_crimson: str   # Hex. Sanguis — destructive, warnings.
    c_teal: str      # Hex. Viridis — confirmations, saves.
    c_text: str      # Hex. Parchment — body text.
    c_subtle: str    # Hex. Umbra — inactive borders.
    c_white: str     # Hex. Vellum — emphasis text.


class OklabCoords(TypedDict):
    """OKLAB coordinates for a single color."""
    l: float  # Lightness [0.0, 1.0]
    a: float  # Green-red axis [-0.4, 0.4]
    b: float  # Blue-yellow axis [-0.4, 0.4]


class BasePair(TypedDict):
    """The two input colors from which all tokens are derived."""
    bg_hex: str
    bg_oklab: OklabCoords
    fg_hex: str
    fg_oklab: OklabCoords


class ContrastEntry(TypedDict):
    """Contrast metrics for a single foreground/background pair."""
    fg_token: str
    bg_token: str
    wcag_ratio: float
    apca_lc: float
    passes_aa: bool   # wcag_ratio >= 4.5
    passes_aaa: bool  # wcag_ratio >= 7.0


class SealRecord(TypedDict):
    """Immutable ratification seal."""
    seal_hash: str      # SHA-256 hex digest
    sealed_at: str      # ISO 8601 timestamp
    designator: str     # Wizard-ratified Latin designator
    canonical_json: str # The exact JSON string that was hashed


class ContrastSummary(TypedDict):
    """Aggregate contrast audit results."""
    passes_aa: bool
    passes_aaa: bool
    min_wcag_ratio: float
    min_apca_lc: float
    failing_pairs: list[dict]


class ThemePackage(TypedDict):
    """The complete theme.json — Tower canonical format.

    This is the inter-app contract. Every Tower application that
    consumes a theme reads this schema. Do not add fields without
    updating all downstream consumers.
    """
    schema_version: str   # "1.0"
    bureau: str           # "auctoritas_spectralis"
    alliance: str         # "a4"
    designator: str       # Wizard-ratified name
    seal_hash: str        # SHA-256 of canonical token JSON
    sealed_at: str        # ISO 8601
    base_pair: BasePair
    tokens: TokenSet
    oklab_tokens: dict[str, OklabCoords]
    contrast_summary: ContrastSummary
    font_stack: str       # "Georgia, Constantia, serif"
    font_stack_mono: str  # "excalib-nf, Courier New, monospace"
