# Auctoritas Spectralis — scrutinium.py
# v1.0.0
"""WCAG 2.1 and APCA contrast computation engine with CVD simulation."""

import math

import colour
import numpy as np

from .derivatio import hex_to_srgb
from .constants import FG_TOKENS, BG_TOKENS


def _relative_luminance(srgb: np.ndarray) -> float:
    """WCAG 2.1 relative luminance from linear sRGB."""
    # Linearize sRGB
    linear = np.where(
        srgb <= 0.04045,
        srgb / 12.92,
        ((srgb + 0.055) / 1.055) ** 2.4
    )
    return float(0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2])


def compute_wcag_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG 2.1 relative luminance contrast ratio.

    Formula: (L_lighter + 0.05) / (L_darker + 0.05)
    """
    l_fg = _relative_luminance(hex_to_srgb(fg_hex))
    l_bg = _relative_luminance(hex_to_srgb(bg_hex))
    lighter = max(l_fg, l_bg)
    darker = min(l_fg, l_bg)
    return (lighter + 0.05) / (darker + 0.05)


def compute_apca_lc(fg_hex: str, bg_hex: str) -> float:
    """APCA Lightness Contrast (Lc) value.

    Simplified APCA-W3 implementation (Somers 2022).
    Positive = light text on dark bg. Negative = dark on light.
    """
    fg_srgb = hex_to_srgb(fg_hex)
    bg_srgb = hex_to_srgb(bg_hex)

    # Linearize
    def _linearize(c):
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    fg_lin = _linearize(fg_srgb)
    bg_lin = _linearize(bg_srgb)

    # APCA coefficients for Y (luminance)
    fg_y = float(0.2126729 * fg_lin[0] + 0.7151522 * fg_lin[1] + 0.0721750 * fg_lin[2])
    bg_y = float(0.2126729 * bg_lin[0] + 0.7151522 * bg_lin[1] + 0.0721750 * bg_lin[2])

    # Soft clamp
    fg_y = max(fg_y, 0.0)
    bg_y = max(bg_y, 0.0)

    # SAPC perceptual lightness
    fg_s = fg_y ** 0.56
    bg_s = bg_y ** 0.56

    # Polarity
    if bg_s > fg_s:
        # Light bg, dark text (negative Lc)
        sapc = (bg_s - fg_s) * 1.14
        if sapc < 0.1:
            return 0.0
        lc = -(sapc - 0.027) * 100.0
    else:
        # Dark bg, light text (positive Lc)
        sapc = (fg_s - bg_s) * 1.14
        if sapc < 0.1:
            return 0.0
        lc = (sapc - 0.027) * 100.0

    return round(lc, 1)


def build_contrast_matrix(tokens: dict) -> list[dict]:
    """Compute contrast for all meaningful foreground/background pairs.

    Covers every text/accent token against every background token.
    """
    matrix = []
    for fg_name in FG_TOKENS:
        fg_hex = tokens.get(fg_name)
        if fg_hex is None:
            continue
        for bg_name in BG_TOKENS:
            bg_hex = tokens.get(bg_name)
            if bg_hex is None:
                continue
            ratio = compute_wcag_ratio(fg_hex, bg_hex)
            lc = compute_apca_lc(fg_hex, bg_hex)
            matrix.append({
                'fg_token': fg_name,
                'bg_token': bg_name,
                'wcag_ratio': round(ratio, 2),
                'apca_lc': lc,
                'passes_aa': ratio >= 4.5,
                'passes_aaa': ratio >= 7.0,
            })
    return matrix


def audit_passes(matrix: list[dict]) -> dict:
    """Summarize pass/fail across the full matrix."""
    if not matrix:
        return {
            'passes_aa': False,
            'passes_aaa': False,
            'min_wcag_ratio': 0.0,
            'min_apca_lc': 0.0,
            'failing_pairs': [],
        }

    ratios = [e['wcag_ratio'] for e in matrix]
    lcs = [abs(e['apca_lc']) for e in matrix]
    failing = [e for e in matrix if not e['passes_aa']]

    return {
        'passes_aa': all(e['passes_aa'] for e in matrix),
        'passes_aaa': all(e['passes_aaa'] for e in matrix),
        'min_wcag_ratio': min(ratios),
        'min_apca_lc': min(lcs),
        'failing_pairs': failing,
    }


# ── Color Vision Deficiency Simulation ──────────────────────────────

# Viénot/Brettel CVD simulation matrices (applied in linear sRGB)
_CVD_MATRICES = {
    'deuteranopia': np.array([
        [0.625, 0.375, 0.0],
        [0.700, 0.300, 0.0],
        [0.000, 0.300, 0.700],
    ]),
    'protanopia': np.array([
        [0.567, 0.433, 0.0],
        [0.558, 0.442, 0.0],
        [0.000, 0.242, 0.758],
    ]),
    'achromatopsia': None,  # special case — luminance only
}


def _linearize_srgb(srgb: np.ndarray) -> np.ndarray:
    """sRGB [0,1] to linear RGB."""
    return np.where(
        srgb <= 0.04045,
        srgb / 12.92,
        ((srgb + 0.055) / 1.055) ** 2.4
    )


def _delinearize_srgb(linear: np.ndarray) -> np.ndarray:
    """Linear RGB to sRGB [0,1]."""
    return np.where(
        linear <= 0.0031308,
        linear * 12.92,
        1.055 * np.power(np.clip(linear, 0.0, None), 1.0 / 2.4) - 0.055
    )


def simulate_cvd(hex_color: str, deficiency: str) -> str:
    """Simulate color vision deficiency on a single hex color.

    deficiency: 'deuteranopia' | 'protanopia' | 'achromatopsia'
    """
    srgb = hex_to_srgb(hex_color)
    linear = _linearize_srgb(srgb)

    if deficiency == 'achromatopsia':
        # Convert to luminance-only greyscale
        y = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
        simulated = np.array([y, y, y])
    else:
        mat = _CVD_MATRICES.get(deficiency)
        if mat is None:
            return hex_color
        simulated = mat @ linear

    result = _delinearize_srgb(np.clip(simulated, 0.0, 1.0))
    from .derivatio import srgb_to_hex
    return srgb_to_hex(result)


def simulate_all_tokens(tokens: dict, deficiency: str) -> dict:
    """Apply CVD simulation to all tokens, returning simulated hex dict."""
    return {name: simulate_cvd(hex_val, deficiency) for name, hex_val in tokens.items()}
