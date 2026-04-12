"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/harmony.py — Six harmony algorithms operating in OKLAB LCH space

Algorithms: Complementary, Analogous, Monochromatic,
            Split-Complementary, Triadic, Tetradic

Each algorithm accepts the Lead Pair LCH values and returns a dict
of {token_key: LCH} for all ten tokens.
The Lead Pair tokens are returned unchanged.
Derived tokens receive hue, lightness, and chroma per their role rules.
After derivation, jitter.jitter_palette() is called by the caller.
"""

from AuctoritasSpectralis.engine.colour import LCH, clamp_lch


# ── Token role definitions ──────────────────────────────────────────────
# Each derived token has:
#   lightness_ratio   — L as fraction of bg L (or explicit override)
#   chroma_scale      — C as scale of bg C
#   hue_slot          — index into the harmony model's hue list

TOKEN_ROLES: dict[str, dict] = {
    # Panel bg — slightly lighter than bg, same hue family
    "c_panel":    {"l_ratio": None, "l_abs": 0.09, "c_scale": 0.6,  "hue_slot": 0},
    # Subtle bg — between bg and panel
    "c_subtle":   {"l_ratio": None, "l_abs": 0.07, "c_scale": 0.4,  "hue_slot": 0},
    # Dark accent band — deeper than bg, gold hue
    "c_gold_dark":{"l_ratio": None, "l_abs": 0.12, "c_scale": 0.7,  "hue_slot": 1},
    # Muted fg — dimmed version of gold
    "c_gold_dim": {"l_ratio": None, "l_abs": 0.38, "c_scale": 0.55, "hue_slot": 1},
    # Primary readable text
    "c_text":     {"l_ratio": None, "l_abs": 0.62, "c_scale": 0.35, "hue_slot": 1},
    # Near-white highlight
    "c_white":    {"l_ratio": None, "l_abs": 0.88, "c_scale": 0.12, "hue_slot": 1},
    # Accent: error/warning (Sanguis)
    "c_crimson":  {"l_ratio": None, "l_abs": 0.30, "c_scale": 1.2,  "hue_slot": 2},
    # Accent: success/info (Viridis)
    "c_teal":     {"l_ratio": None, "l_abs": 0.30, "c_scale": 1.0,  "hue_slot": 3},
}


# ── Harmony hue offsets ─────────────────────────────────────────────────
# Each model returns a list of 4 hues derived from the base hue (H of c_bg).
# Slot 0 = bg family, slot 1 = gold family, slot 2 = accent A, slot 3 = accent B

def _hues(base_h: float, offsets: tuple[float, float, float, float]) -> list[float]:
    return [(base_h + o) % 360.0 for o in offsets]


HARMONY_OFFSETS: dict[str, tuple[float, float, float, float]] = {
    "Complementary":       (0.0,  30.0, 180.0, 210.0),
    "Analogous":           (0.0,  30.0,  60.0,  90.0),
    "Monochromatic":       (0.0,   0.0,   0.0,   0.0),
    "Split-Complementary": (0.0,  30.0, 150.0, 210.0),
    "Triadic":             (0.0,  30.0, 120.0, 240.0),
    "Tetradic":            (0.0,  30.0,  90.0, 270.0),
}

HARMONY_MODELS = list(HARMONY_OFFSETS.keys())


# ── Core derivation ─────────────────────────────────────────────────────

def derive_palette(
    bg_hex_lch: LCH,
    gold_hex_lch: LCH,
    harmony_model: str,
    locked: dict[str, LCH],
) -> tuple[dict[str, LCH], list[str]]:
    """
    Derive all ten tokens from the Lead Pair.

    Returns:
        (palette: dict[token_key, LCH], conflict_tokens: list[str])

    The Lock Pass restores locked tokens to their locked values and
    detects harmonic conflicts (deviation >30° from expected hue family).

    Jitter is NOT applied here — caller applies jitter.jitter_palette()
    after this function returns.
    """
    offsets = HARMONY_OFFSETS.get(harmony_model, HARMONY_OFFSETS["Complementary"])
    hue_families = _hues(bg_hex_lch.H, offsets)

    palette: dict[str, LCH] = {
        "c_bg":   bg_hex_lch,
        "c_gold": gold_hex_lch,
    }

    # Derive each token
    for key, role in TOKEN_ROLES.items():
        l_abs    = role["l_abs"]
        c_scale  = role["c_scale"]
        hue_slot = role["hue_slot"]

        # Lightness: use absolute target (tuned for dark UI)
        L = l_abs

        # Chroma: scale from bg chroma, minimum floor
        base_c = max(bg_hex_lch.C, 0.04)  # prevent collapse on near-achromatic bg
        C = max(0.01, base_c * c_scale)

        # Hue from harmony family
        H = hue_families[hue_slot]

        palette[key] = clamp_lch(LCH(L=L, C=C, H=H))

    # Lock pass + conflict detection
    conflict_tokens: list[str] = []

    for key, locked_lch in locked.items():
        if key in ("c_bg", "c_gold"):
            continue  # Lead Pair handled separately

        # Detect conflict: is locked hue > 30° from expected family?
        if key in TOKEN_ROLES:
            slot = TOKEN_ROLES[key]["hue_slot"]
            expected_h = hue_families[slot]
            delta = abs((locked_lch.H - expected_h + 180.0) % 360.0 - 180.0)
            if delta > 30.0:
                conflict_tokens.append(key)

        # Restore locked value regardless of conflict
        palette[key] = locked_lch

    return palette, conflict_tokens


def generate(
    bg_hex: str,
    gold_hex: str,
    harmony_model: str,
    locked_hex: dict[str, str],
    apply_jitter: bool = True,
) -> tuple[dict[str, str], list[str]]:
    """
    High-level generation pipeline.

    Args:
        bg_hex:       hex for c_bg (Lead Pair)
        gold_hex:     hex for c_gold (Lead Pair)
        harmony_model: one of HARMONY_MODELS
        locked_hex:   {token_key: hex} for locked tokens
        apply_jitter: whether to run jitter pass (default True)

    Returns:
        (hex_palette: dict[token_key, hex_str], conflict_tokens: list[str])
    """
    from AuctoritasSpectralis.engine.colour import hex_to_lch, lch_hex_roundtrip
    from AuctoritasSpectralis.engine.jitter import jitter_palette

    bg_lch   = hex_to_lch(bg_hex)
    gold_lch = hex_to_lch(gold_hex)

    locked_lch = {k: hex_to_lch(v) for k, v in locked_hex.items()}

    palette_lch, conflicts = derive_palette(
        bg_lch, gold_lch, harmony_model, locked_lch
    )

    if apply_jitter:
        palette_lch = jitter_palette(palette_lch, set(locked_hex.keys()))

    hex_palette = {k: lch_hex_roundtrip(v) for k, v in palette_lch.items()}

    # Restore exact Lead Pair hexes (no rounding drift)
    hex_palette["c_bg"]   = bg_hex
    hex_palette["c_gold"] = gold_hex

    # Restore exact locked hexes
    for k, v in locked_hex.items():
        hex_palette[k] = v

    return hex_palette, conflicts
