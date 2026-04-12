"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/nomen.py — Latin Nomen generator

Each derived token receives a two-word Latin name (Nomen)
perceptually derived from its LCH values.
Updates on every generation cycle.
"""

from AuctoritasSpectralis.engine.colour import hex_to_lch
from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER


# ── Word tables ─────────────────────────────────────────────────────────

# First word: lightness descriptor
LIGHT_WORDS = [
    (0.0,  0.08, ["Nox",       "Erebus",    "Umbra",    "Tenebris"]),
    (0.08, 0.18, ["Obscurus",  "Caecus",    "Fuscus",   "Ater"    ]),
    (0.18, 0.30, ["Dimmus",    "Opacus",    "Calidus",  "Subobscurus"]),
    (0.30, 0.45, ["Medius",    "Neutrum",   "Sobrius",  "Temperatus"]),
    (0.45, 0.62, ["Clarus",    "Lucens",    "Nitens",   "Liquidus"]),
    (0.62, 0.78, ["Splendidus","Candidus",  "Limpidus", "Fulgens"]),
    (0.78, 1.01, ["Albus",     "Niveus",    "Purus",    "Lucidus" ]),
]

# Second word: hue descriptor
HUE_WORDS = [
    (0.0,   20.0,  ["Sanguineus", "Rubeus",     "Phoeniceus", "Igneus"    ]),
    (20.0,  45.0,  ["Aureus",     "Fulvus",     "Croceus",    "Rutilus"   ]),
    (45.0,  75.0,  ["Flavus",     "Citrinus",   "Luteus",     "Gilvus"    ]),
    (75.0,  135.0, ["Viridis",    "Smaragdinus","Herbeus",    "Prasinus"  ]),
    (135.0, 195.0, ["Aereus",     "Caeruleus",  "Venetus",    "Cyanus"    ]),
    (195.0, 255.0, ["Indicus",    "Lazulinus",  "Caelestinus","Hyacinthinus"]),
    (255.0, 315.0, ["Amethystinus","Purpureus", "Violaceus",  "Porphyreus"]),
    (315.0, 360.0, ["Roseus",     "Carneus",    "Rubellus",   "Miniatus"  ]),
]

# Low-chroma override: achromatic descriptors
ACHROMATIC_WORDS = [
    "Cinereus", "Lividus", "Griseus", "Pallidus", "Glaucus",
    "Argyreus", "Candens", "Decolor",
]


def _pick_by_range(
    table: list[tuple],
    value: float,
    seed: int,
) -> str:
    for lo, hi, words in table:
        if lo <= value < hi:
            return words[seed % len(words)]
    return table[-1][2][seed % len(table[-1][2])]


def nomen_for_token(hex_str: str, token_key: str = "") -> str:
    """Generate a two-word Latin Nomen for a single token hex."""
    try:
        lch = hex_to_lch(hex_str)
    except (ValueError, ZeroDivisionError):
        return "Incognitus Locus"

    # Use token_key as part of seed for variety across tokens at same LCH
    seed = abs(hash(token_key + hex_str)) % 4

    # Achromatic handling: very low chroma → use achromatic second word
    if lch.C < 0.04:
        light_word = _pick_by_range(LIGHT_WORDS, lch.L, seed)
        achro_word = ACHROMATIC_WORDS[seed % len(ACHROMATIC_WORDS)]
        return f"{light_word} {achro_word}"

    light_word = _pick_by_range(LIGHT_WORDS, lch.L, seed)
    hue_word   = _pick_by_range(HUE_WORDS,   lch.H, seed)

    return f"{light_word} {hue_word}"


def generate_nomina(palette: dict[str, str]) -> dict[str, str]:
    """Generate Nomina for all tokens in a palette."""
    return {
        key: nomen_for_token(hex_val, key)
        for key, hex_val in palette.items()
        if key in TOKEN_ORDER
    }
