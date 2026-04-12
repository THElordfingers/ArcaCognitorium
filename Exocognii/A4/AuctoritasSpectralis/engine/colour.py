"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/colour.py — OKLAB/LCH colour space operations

Manual implementation — no external colour library required.
All operations: sRGB ↔ Linear RGB ↔ OKLAB ↔ LCH
"""

import math
from dataclasses import dataclass


# ── Data types ──────────────────────────────────────────────────────────

@dataclass
class RGB:
    r: float  # 0.0–1.0
    g: float
    b: float

@dataclass
class OKLab:
    L: float  # 0.0–1.0 (perceptual lightness)
    a: float  # green–red axis
    b: float  # blue–yellow axis

@dataclass
class LCH:
    L: float  # 0.0–1.0
    C: float  # chroma ≥ 0
    H: float  # hue angle 0–360°


# ── sRGB ↔ Linear RGB ──────────────────────────────────────────────────

def srgb_to_linear(v: float) -> float:
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4


def linear_to_srgb(v: float) -> float:
    if v <= 0.0031308:
        return v * 12.92
    return 1.055 * (v ** (1.0 / 2.4)) - 0.055


def rgb_linearise(rgb: RGB) -> RGB:
    return RGB(srgb_to_linear(rgb.r), srgb_to_linear(rgb.g), srgb_to_linear(rgb.b))


def rgb_delinearise(rgb: RGB) -> RGB:
    return RGB(linear_to_srgb(rgb.r), linear_to_srgb(rgb.g), linear_to_srgb(rgb.b))


# ── Linear RGB ↔ OKLAB ─────────────────────────────────────────────────
# Reference: Björn Ottosson — https://bottosson.github.io/posts/oklab/

def linear_rgb_to_oklab(rgb: RGB) -> OKLab:
    l = 0.4122214708 * rgb.r + 0.5363325363 * rgb.g + 0.0514459929 * rgb.b
    m = 0.2119034982 * rgb.r + 0.6806995451 * rgb.g + 0.1073969566 * rgb.b
    s = 0.0883024619 * rgb.r + 0.2817188376 * rgb.g + 0.6299787005 * rgb.b

    l_ = l ** (1.0 / 3.0)
    m_ = m ** (1.0 / 3.0)
    s_ = s ** (1.0 / 3.0)

    return OKLab(
        L =  0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        a =  1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        b =  0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear_rgb(lab: OKLab) -> RGB:
    l_ = lab.L + 0.3963377774 * lab.a + 0.2158037573 * lab.b
    m_ = lab.L - 0.1055613458 * lab.a - 0.0638541728 * lab.b
    s_ = lab.L - 0.0894841775 * lab.a - 1.2914855480 * lab.b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    return RGB(
        r =  4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


# ── OKLAB ↔ LCH ────────────────────────────────────────────────────────

def oklab_to_lch(lab: OKLab) -> LCH:
    C = math.sqrt(lab.a ** 2 + lab.b ** 2)
    H = math.degrees(math.atan2(lab.b, lab.a)) % 360.0
    return LCH(L=lab.L, C=C, H=H)


def lch_to_oklab(lch: LCH) -> OKLab:
    h_rad = math.radians(lch.H)
    return OKLab(
        L=lch.L,
        a=lch.C * math.cos(h_rad),
        b=lch.C * math.sin(h_rad),
    )


# ── Full pipeline helpers ───────────────────────────────────────────────

def hex_to_rgb(hex_str: str) -> RGB:
    """Parse '#rrggbb' or 'rrggbb' to RGB(0–1)."""
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Invalid hex colour: {hex_str!r}")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return RGB(r, g, b)


def rgb_to_hex(rgb: RGB) -> str:
    """Clamp and convert RGB(0–1) to '#rrggbb'."""
    r = max(0, min(255, round(rgb.r * 255)))
    g = max(0, min(255, round(rgb.g * 255)))
    b = max(0, min(255, round(rgb.b * 255)))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_lch(hex_str: str) -> LCH:
    rgb = hex_to_rgb(hex_str)
    lin = rgb_linearise(rgb)
    lab = linear_rgb_to_oklab(lin)
    return oklab_to_lch(lab)


def lch_to_hex(lch: LCH) -> str:
    lab = lch_to_oklab(lch)
    lin = oklab_to_linear_rgb(lab)
    rgb = rgb_delinearise(lin)
    return rgb_to_hex(rgb)


def hex_to_oklab(hex_str: str) -> OKLab:
    return linear_rgb_to_oklab(rgb_linearise(hex_to_rgb(hex_str)))


# ── Colour properties ───────────────────────────────────────────────────

def relative_luminance(hex_str: str) -> float:
    """WCAG relative luminance for a hex colour."""
    rgb = rgb_linearise(hex_to_rgb(hex_str))
    return 0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b


def is_valid_hex(hex_str: str) -> bool:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        return False
    try:
        int(h, 16)
        return True
    except ValueError:
        return False


def clamp_lch(lch: LCH) -> LCH:
    """Clamp LCH values to physically meaningful ranges."""
    return LCH(
        L=max(0.0, min(1.0, lch.L)),
        C=max(0.0, lch.C),
        H=lch.H % 360.0,
    )


def lch_hex_roundtrip(lch: LCH) -> str:
    """Convert LCH to hex, clamping out-of-gamut values."""
    lab = lch_to_oklab(lch)
    lin = oklab_to_linear_rgb(lab)
    # Gamut clamp
    lin = RGB(
        r=max(0.0, min(1.0, lin.r)),
        g=max(0.0, min(1.0, lin.g)),
        b=max(0.0, min(1.0, lin.b)),
    )
    rgb = rgb_delinearise(lin)
    return rgb_to_hex(rgb)
