"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/jitter.py — oklab_jitter() structured randomness function

Applies bounded random perturbation in LCH space to derived tokens.
The Lead Pair (c_bg, c_gold) is never jittered.
Jitter envelopes vary by token role.
"""

import random
from AuctoritasSpectralis.engine.colour import LCH


# ── Per-token jitter envelopes ──────────────────────────────────────────
# (l_range, c_range, h_range)
# Lead pair tokens have zero range — they are never passed to jitter.

JITTER_ENVELOPES: dict[str, tuple[float, float, float]] = {
    "c_bg":       (0.0,   0.0,   0.0),   # Lead Pair — sacrosanct
    "c_gold":     (0.0,   0.0,   0.0),   # Lead Pair — sacrosanct
    "c_panel":    (0.02,  0.01,  4.0),
    "c_subtle":   (0.02,  0.01,  4.0),
    "c_gold_dark":(0.02,  0.01,  4.0),
    "c_gold_dim": (0.04,  0.02,  8.0),
    "c_text":     (0.03,  0.015, 6.0),
    "c_white":    (0.02,  0.01,  4.0),
    "c_crimson":  (0.04,  0.03,  12.0),
    "c_teal":     (0.04,  0.03,  12.0),
}

# Canonical token order
TOKEN_ORDER = [
    "c_bg", "c_gold", "c_panel", "c_subtle", "c_gold_dark",
    "c_gold_dim", "c_text", "c_white", "c_crimson", "c_teal",
]


def oklab_jitter(
    l: float,
    c: float,
    h: float,
    l_range: float = 0.04,
    c_range: float = 0.02,
    h_range: float = 8.0,
) -> tuple[float, float, float]:
    """
    Apply bounded random perturbation in LCH space.

    l_range: max absolute lightness shift (±)
    c_range: max absolute chroma shift (±)
    h_range: max hue angle shift in degrees (±)

    Lead pair tokens (c_bg, c_gold) are NOT jittered —
    they should not be passed here at all, but zero ranges
    are a safe fallback.
    """
    lj = l + random.uniform(-l_range, l_range)
    cj = max(0.0, c + random.uniform(-c_range, c_range))
    hj = (h + random.uniform(-h_range, h_range)) % 360.0
    return lj, cj, hj


def jitter_token(token_key: str, lch: LCH) -> LCH:
    """Apply the canonical jitter envelope for the given token key."""
    env = JITTER_ENVELOPES.get(token_key, (0.04, 0.02, 8.0))
    l_r, c_r, h_r = env
    if l_r == 0.0 and c_r == 0.0 and h_r == 0.0:
        return lch  # Lead Pair — no change
    lj, cj, hj = oklab_jitter(lch.L, lch.C, lch.H, l_r, c_r, h_r)
    return LCH(L=lj, C=cj, H=hj)


def jitter_palette(
    derived: dict[str, LCH],
    locked: set[str],
) -> dict[str, LCH]:
    """
    Apply jitter to all unlocked derived tokens.
    Lead Pair tokens are always treated as locked.
    Returns a new dict with jittered LCH values.
    """
    result: dict[str, LCH] = {}
    always_locked = {"c_bg", "c_gold"}

    for key, lch in derived.items():
        if key in always_locked or key in locked:
            result[key] = lch
        else:
            result[key] = jitter_token(key, lch)

    return result
