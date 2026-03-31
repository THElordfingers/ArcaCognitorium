# Auctoritas Spectralis — derivatio.py
# v1.0.0
"""Token derivation from base pair via OKLAB perceptual space."""

import math

import colour
import numpy as np

from .schema import OklabCoords


def hex_to_srgb(hex_color: str) -> np.ndarray:
    """Convert #RRGGBB hex to sRGB [0, 1] array."""
    h = hex_color.lstrip('#')
    return np.array([int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)])


def srgb_to_hex(rgb: np.ndarray) -> str:
    """Convert sRGB [0, 1] array to #RRGGBB hex, clamped."""
    clamped = np.clip(rgb, 0.0, 1.0)
    return '#{:02x}{:02x}{:02x}'.format(
        int(round(clamped[0] * 255)),
        int(round(clamped[1] * 255)),
        int(round(clamped[2] * 255)),
    )


def hex_to_oklab(hex_color: str) -> tuple[float, float, float]:
    """Convert #RRGGBB hex to OKLAB (L, a, b) coordinates."""
    srgb = hex_to_srgb(hex_color)
    # sRGB -> linear RGB -> CIE XYZ -> OKLAB
    xyz = colour.sRGB_to_XYZ(srgb)
    lab = colour.XYZ_to_Oklab(xyz)
    return float(lab[0]), float(lab[1]), float(lab[2])


def oklab_to_hex(l: float, a: float, b: float) -> str:
    """Convert OKLAB (L, a, b) back to #RRGGBB hex, clamped to sRGB gamut."""
    lab = np.array([l, a, b])
    xyz = colour.Oklab_to_XYZ(lab)
    srgb = colour.XYZ_to_sRGB(xyz)
    return srgb_to_hex(srgb)


def _oklab_to_lch(l: float, a: float, b: float) -> tuple[float, float, float]:
    """Convert OKLAB to LCH (lightness, chroma, hue in degrees)."""
    c = math.sqrt(a * a + b * b)
    h = math.degrees(math.atan2(b, a)) % 360.0
    return l, c, h


def _lch_to_oklab(l: float, c: float, h: float) -> tuple[float, float, float]:
    """Convert LCH back to OKLAB."""
    h_rad = math.radians(h)
    a = c * math.cos(h_rad)
    b = c * math.sin(h_rad)
    return l, a, b


def _scale_lightness(l: float, a: float, b: float,
                     factor: float) -> tuple[float, float, float]:
    """Multiply OKLAB lightness by factor, clamp to [0, 1]."""
    return max(0.0, min(1.0, l * factor)), a, b


def _desaturate(l: float, a: float, b: float,
                amount: float) -> tuple[float, float, float]:
    """Reduce chroma (distance from neutral axis) by proportion [0, 1]."""
    scale = 1.0 - amount
    return l, a * scale, b * scale


def _rotate_hue(l: float, a: float, b: float,
                target_degrees: float) -> tuple[float, float, float]:
    """Set hue in OKLAB a/b plane to target angle, preserving L and chroma."""
    _, c, _ = _oklab_to_lch(l, a, b)
    return _lch_to_oklab(l, c, target_degrees)


def _shift_toward_neutral(l: float, a: float, b: float,
                          warmth: float = 0.02) -> tuple[float, float, float]:
    """Move color toward warm neutral axis, retaining lightness.

    Warm neutral sits at a slight positive b (yellow bias) with near-zero a.
    """
    target_a = 0.0
    target_b = warmth
    blend = 0.6  # how far toward neutral
    new_a = a + (target_a - a) * blend
    new_b = b + (target_b - b) * blend
    return l, new_a, new_b


def _set_chroma(l: float, a: float, b: float,
                target_c: float) -> tuple[float, float, float]:
    """Set chroma to a specific value, preserving hue and lightness."""
    _, _, h = _oklab_to_lch(l, a, b)
    return _lch_to_oklab(l, target_c, h)


def derive_tokens(bg_hex: str, fg_hex: str) -> dict:
    """Compute the full 10-token hierarchy from a BG/FG base pair.

    All operations in OKLAB space. Returns dict with:
      'tokens': {token_name: hex_string}
      'oklab':  {token_name: OklabCoords}
      'clipped': [list of token names that were gamut-clipped]
    """
    bg_l, bg_a, bg_b = hex_to_oklab(bg_hex)
    fg_l, fg_a, fg_b = hex_to_oklab(fg_hex)

    derived = {}
    clipped = []

    def _register(name: str, l: float, a: float, b: float):
        """Clamp, convert to hex, track clipping, store."""
        l_c = max(0.0, min(1.0, l))
        hex_val = oklab_to_hex(l_c, a, b)
        # Check if sRGB clipping occurred
        back_l, back_a, back_b = hex_to_oklab(hex_val)
        dist = math.sqrt((l_c - back_l)**2 + (a - back_a)**2 + (b - back_b)**2)
        if dist > 0.01:
            clipped.append(name)
        derived[name] = {
            'hex': hex_val,
            'oklab': {'l': round(back_l, 6), 'a': round(back_a, 6), 'b': round(back_b, 6)},
        }

    # C_BG — identity
    _register('c_bg', bg_l, bg_a, bg_b)

    # C_PANEL — bg lightness * 1.15, chroma shifted toward neutral
    pl, pa, pb = _scale_lightness(bg_l, bg_a, bg_b, 1.15)
    pl, pa, pb = _shift_toward_neutral(pl, pa, pb)
    _register('c_panel', pl, pa, pb)

    # C_GOLD — fg identity (foreground IS the accent)
    _register('c_gold', fg_l, fg_a, fg_b)

    # C_GOLD_DIM — fg lightness * 0.55, desaturate 30%
    gdl, gda, gdb = _scale_lightness(fg_l, fg_a, fg_b, 0.55)
    gdl, gda, gdb = _desaturate(gdl, gda, gdb, 0.30)
    _register('c_gold_dim', gdl, gda, gdb)

    # C_GOLD_DARK — fg lightness * 0.28, desaturate 50%
    gkl, gka, gkb = _scale_lightness(fg_l, fg_a, fg_b, 0.28)
    gkl, gka, gkb = _desaturate(gkl, gka, gkb, 0.50)
    _register('c_gold_dark', gkl, gka, gkb)

    # C_TEXT — fg lightness * 0.78, shift toward warm neutral
    tl, ta, tb = _scale_lightness(fg_l, fg_a, fg_b, 0.78)
    tl, ta, tb = _shift_toward_neutral(tl, ta, tb)
    _register('c_text', tl, ta, tb)

    # C_SUBTLE — bg lightness * 1.6, shift toward warm neutral
    sl, sa, sb = _scale_lightness(bg_l, bg_a, bg_b, 1.6)
    sl, sa, sb = _shift_toward_neutral(sl, sa, sb)
    _register('c_subtle', sl, sa, sb)

    # C_WHITE — fg lightness * 0.92, near-full desaturation
    wl, wa, wb = _scale_lightness(fg_l, fg_a, fg_b, 0.92)
    wl, wa, wb = _desaturate(wl, wa, wb, 0.85)
    _register('c_white', wl, wa, wb)

    # C_CRIMSON — hue rotated to ~25° (red), L=0.35, C=0.12
    cl, ca, cb = _lch_to_oklab(0.35, 0.12, 25.0)
    _register('c_crimson', cl, ca, cb)

    # C_TEAL — hue rotated to ~195° (teal), L=0.35, C=0.08
    tll, tla, tlb = _lch_to_oklab(0.35, 0.08, 195.0)
    _register('c_teal', tll, tla, tlb)

    # Assemble output
    tokens = {name: derived[name]['hex'] for name in derived}
    oklab = {name: derived[name]['oklab'] for name in derived}

    return {
        'tokens': tokens,
        'oklab': oklab,
        'clipped': clipped,
    }
