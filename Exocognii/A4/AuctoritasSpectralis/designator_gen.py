# Auctoritas Spectralis — designator_gen.py
# v1.0.0
"""Generate a Latin compound designator from palette characteristics."""

import math
import random

from .derivatio import hex_to_oklab, _oklab_to_lch

# Hue families mapped to Latin color words (OKLAB hue angles)
# OKLAB hue distribution: red ~29°, gold ~91°, yellow ~110°,
# green ~142°, teal ~195°, blue ~264°, purple ~310°
HUE_VOCABULARY = {
    (0, 50):    ["Rubeus", "Sanguinis", "Igneus", "Ferreus"],
    (50, 80):   ["Croceus", "Melleus", "Sulphureus", "Flammeus"],
    (80, 120):  ["Aureus", "Chryseus", "Aurifex", "Solaris"],
    (120, 160): ["Viridis", "Smaragdinus", "Prasinus", "Herbaceus"],
    (160, 220): ["Thalassinus", "Glaucus", "Caeruleus", "Aquilinus"],
    (220, 280): ["Lazulinus", "Sapphirinus", "Caeruleus", "Coelestis"],
    (280, 340): ["Purpureus", "Violaceus", "Amethystinus", "Regalis"],
    (340, 360): ["Roseus", "Rhodinus", "Rubicundus", "Carneus"],
}

# Lightness modifiers
LIGHTNESS_VOCABULARY = {
    (0.0, 0.15): ["Profundus", "Abyssalis", "Noctis"],
    (0.15, 0.30): ["Obscurus", "Umbralis", "Crepuscularis"],
    (0.30, 0.50): ["Mediocris", "Temperatus", "Aequalis"],
    (0.50, 0.70): ["Lucidus", "Clarus", "Matutinus"],
    (0.70, 1.0):  ["Candidus", "Vespertinus", "Luminaris"],
}


def _get_hue_word(hue_degrees: float) -> str:
    """Select a Latin hue word from vocabulary."""
    for (lo, hi), words in HUE_VOCABULARY.items():
        if lo <= hue_degrees < hi:
            return random.choice(words)
    return "Arcanus"


def _get_lightness_word(lightness: float) -> str:
    """Select a Latin lightness modifier from vocabulary."""
    for (lo, hi), words in LIGHTNESS_VOCABULARY.items():
        if lo <= lightness < hi:
            return random.choice(words)
    return "Ignotus"


def suggest_designator(tokens: dict) -> str:
    """Suggest a two-word Latin designator based on dominant hue + lightness.

    Analyses the FG (gold/accent) color to determine hue family,
    and the BG lightness to determine the modifier.
    """
    fg_hex = tokens.get('c_gold', '#d4af37')
    bg_hex = tokens.get('c_bg', '#050507')

    fg_l, fg_a, fg_b = hex_to_oklab(fg_hex)
    bg_l, bg_a, bg_b = hex_to_oklab(bg_hex)

    _, _, fg_hue = _oklab_to_lch(fg_l, fg_a, fg_b)

    hue_word = _get_hue_word(fg_hue)
    lightness_word = _get_lightness_word(bg_l)

    return f"{hue_word} {lightness_word}"
