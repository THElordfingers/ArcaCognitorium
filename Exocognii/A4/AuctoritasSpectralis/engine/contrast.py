"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/contrast.py — Six contrast metrics

Metrics:
  1. WCAG 2.1 ratio
  2. WCAG 3.0 / APCA (simplified Lc approximation)
  3. DeltaE 2000 (OKLAB approximation)
  4. Luminance Ratio (simple L2/L1)
  5. Chroma Distance (LCH)
  6. Hue Distance (LCH, angular)
"""

import math
from AuctoritasSpectralis.engine.colour import (
    relative_luminance, hex_to_lch, hex_to_oklab
)


# ── 1. WCAG 2.1 ─────────────────────────────────────────────────────────

def wcag21(fg_hex: str, bg_hex: str) -> float:
    """WCAG 2.1 contrast ratio. Range: 1–21."""
    lfg = relative_luminance(fg_hex)
    lbg = relative_luminance(bg_hex)
    lighter = max(lfg, lbg)
    darker  = min(lfg, lbg)
    return (lighter + 0.05) / (darker + 0.05)


def wcag21_aa_pass(ratio: float, large_text: bool = False) -> bool:
    threshold = 3.0 if large_text else 4.5
    return ratio >= threshold


def wcag21_aaa_pass(ratio: float, large_text: bool = False) -> bool:
    threshold = 4.5 if large_text else 7.0
    return ratio >= threshold


# ── 2. APCA / WCAG 3.0 (simplified) ────────────────────────────────────
# Simplified Lc model — not the full APCA 0.0.98G spec,
# but perceptually meaningful for comparative use.

def _srgb_to_y(hex_str: str) -> float:
    """Convert hex to APCA-style Y (linearised luminance)."""
    from AuctoritasSpectralis.engine.colour import hex_to_rgb, rgb_linearise
    rgb = hex_to_rgb(hex_str)
    lin = rgb_linearise(rgb)
    # APCA sRGB coefficients
    return 0.2126729 * lin.r + 0.7151522 * lin.g + 0.0721750 * lin.b


def apca_lc(fg_hex: str, bg_hex: str) -> float:
    """
    Simplified APCA Lc (lightness contrast).
    Positive: light fg on dark bg. Negative: dark fg on light bg.
    Range: approximately -108 to +106. |Lc| >= 60 is readable.
    """
    Y_fg = _srgb_to_y(fg_hex)
    Y_bg = _srgb_to_y(bg_hex)

    # SA98G constants (simplified)
    exponent = 0.56 if Y_fg < Y_bg else 0.57
    bg_exp   = 0.65 if Y_fg < Y_bg else 0.62

    s_fg = Y_fg ** exponent
    s_bg = Y_bg ** bg_exp

    if Y_fg < Y_bg:
        lc = (s_bg - s_fg) * 1.14 * 100.0
    else:
        lc = (s_fg - s_bg) * 1.14 * 100.0

    # Low clip
    if abs(lc) < 7.5:
        return 0.0
    return lc


def apca_pass(lc: float) -> bool:
    return abs(lc) >= 60.0


# ── 3. DeltaE 2000 (OKLAB approximation) ───────────────────────────────
# Using OKLAB Euclidean distance as a perceptual proxy.
# True CIEDE2000 requires CIELAB; this is a reasonable approximation.

def delta_e_oklab(hex_a: str, hex_b: str) -> float:
    """Perceptual colour difference (OKLAB Euclidean distance × 100)."""
    lab_a = hex_to_oklab(hex_a)
    lab_b = hex_to_oklab(hex_b)
    d = math.sqrt(
        (lab_a.L - lab_b.L) ** 2 +
        (lab_a.a - lab_b.a) ** 2 +
        (lab_a.b - lab_b.b) ** 2
    )
    return round(d * 100.0, 2)


# ── 4. Luminance Ratio ──────────────────────────────────────────────────

def luminance_ratio(hex_a: str, hex_b: str) -> float:
    """Simple luminance ratio (higher / lower). Always >= 1."""
    la = relative_luminance(hex_a)
    lb = relative_luminance(hex_b)
    if la == 0 and lb == 0:
        return 1.0
    return max(la, lb) / max(min(la, lb), 1e-6)


# ── 5. Chroma Distance ──────────────────────────────────────────────────

def chroma_distance(hex_a: str, hex_b: str) -> float:
    """Absolute difference in OKLAB chroma (C). Range: 0–~0.4."""
    lch_a = hex_to_lch(hex_a)
    lch_b = hex_to_lch(hex_b)
    return abs(lch_a.C - lch_b.C)


# ── 6. Hue Distance ─────────────────────────────────────────────────────

def hue_distance(hex_a: str, hex_b: str) -> float:
    """Shortest angular distance between LCH hues. Range: 0–180°."""
    lch_a = hex_to_lch(hex_a)
    lch_b = hex_to_lch(hex_b)
    delta = abs(lch_a.H - lch_b.H) % 360.0
    return min(delta, 360.0 - delta)


# ── Aggregate scorer ────────────────────────────────────────────────────

def score_pair(fg_hex: str, bg_hex: str) -> dict:
    """
    Compute all six metrics for a fg/bg pair.
    Returns a dict with keys:
        wcag21, wcag21_aa, wcag21_aaa,
        apca_lc, apca_pass,
        delta_e, luminance_ratio,
        chroma_distance, hue_distance
    """
    ratio = wcag21(fg_hex, bg_hex)
    lc    = apca_lc(fg_hex, bg_hex)

    return {
        "wcag21":          round(ratio, 2),
        "wcag21_aa":       wcag21_aa_pass(ratio),
        "wcag21_aaa":      wcag21_aaa_pass(ratio),
        "apca_lc":         round(lc, 1),
        "apca_pass":       apca_pass(lc),
        "delta_e":         delta_e_oklab(fg_hex, bg_hex),
        "luminance_ratio": round(luminance_ratio(fg_hex, bg_hex), 2),
        "chroma_distance": round(chroma_distance(fg_hex, bg_hex), 4),
        "hue_distance":    round(hue_distance(fg_hex, bg_hex), 1),
    }


def score_matrix(palette: dict[str, str]) -> dict[tuple[str, str], dict]:
    """
    Compute scores for all meaningful FG × BG token pairs.
    FG candidates: c_gold, c_text, c_white, c_parchment, c_crimson, c_teal, c_gold_dim
    BG candidates: c_bg, c_panel, c_subtle, c_gold_dark
    Returns: {(fg_key, bg_key): scores_dict}
    """
    FG_TOKENS = ["c_gold", "c_text", "c_white", "c_gold_dim", "c_crimson", "c_teal"]
    BG_TOKENS = ["c_bg", "c_panel", "c_subtle", "c_gold_dark"]

    result: dict[tuple[str, str], dict] = {}
    for fg in FG_TOKENS:
        for bg in BG_TOKENS:
            if fg in palette and bg in palette:
                result[(fg, bg)] = score_pair(palette[fg], palette[bg])

    return result
