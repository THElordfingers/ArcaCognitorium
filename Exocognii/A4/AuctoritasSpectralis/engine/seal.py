"""
AUCTORITAS SPECTRALIS — v1.0.0
engine/seal.py — SHA-256 seal and Latin designator assignment

The seal is computed from the canonical token hex set.
The designator is a two-word Latin name perceptually derived
from the palette's dominant L and H values.
"""

import hashlib
from AuctoritasSpectralis.engine.colour import hex_to_lch
from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER


# ── Seal ────────────────────────────────────────────────────────────────

def compute_seal(palette: dict[str, str]) -> str:
    """
    SHA-256 hash of the canonical token set.
    Input: hex values sorted by TOKEN_ORDER, concatenated.
    Returns: full 64-character hex digest.
    """
    canonical = "".join(
        palette.get(k, "").lstrip("#").lower()
        for k in TOKEN_ORDER
        if k in palette
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def seal_truncated(palette: dict[str, str]) -> str:
    """Return first 8 characters of the seal hash (display use)."""
    return compute_seal(palette)[:8] + "…"


# ── Latin Designator ────────────────────────────────────────────────────
# Two-word name: Adjective (colour/quality) + Noun (time/state/phenomenon)
# Selected from perceptual L (lightness) and H (hue angle) of c_bg and c_gold.

# Adjectives — keyed by hue family (from H of c_gold)
ADJECTIVES_BY_HUE: list[tuple[tuple[float, float], list[str]]] = [
    # (hue_range, options)
    ((0.0,   30.0),  ["Igneus", "Ruber", "Sanguineus", "Rutilus"]),
    ((30.0,  60.0),  ["Aureus", "Fulvus", "Croceus", "Amberinus"]),
    ((60.0,  90.0),  ["Flavus", "Citrinus", "Luteus", "Gilvus"]),
    ((90.0,  150.0), ["Viridis", "Smaragdinus", "Prasinus", "Herbeus"]),
    ((150.0, 210.0), ["Caeruleus", "Cyanus", "Aereus", "Venetus"]),
    ((210.0, 270.0), ["Indicus", "Lazulinus", "Caelestinus", "Hyacinthinus"]),
    ((270.0, 330.0), ["Amethystinus", "Purpureus", "Violaceus", "Porphyreus"]),
    ((330.0, 360.0), ["Roseus", "Carneus", "Phoeniceus", "Rubellus"]),
]

# Nouns — keyed by lightness quartile of c_bg
NOUNS_BY_LIGHTNESS: list[tuple[tuple[float, float], list[str]]] = [
    ((0.0,   0.15), ["Noctis", "Umbrae", "Abyssi", "Tenebrae"]),
    ((0.15,  0.35), ["Crepuscularis", "Vespertinus", "Obscurus", "Profundus"]),
    ((0.35,  0.65), ["Meridianus", "Aequalis", "Medius", "Temperatus"]),
    ((0.65,  1.0),  ["Lucidus", "Clarus", "Splendidus", "Diurnus"]),
]


def _pick(table: list[tuple[tuple[float, float], list[str]]], value: float, seed: int) -> str:
    for (lo, hi), words in table:
        if lo <= value < hi:
            return words[seed % len(words)]
    # Fallback: last group
    return table[-1][1][seed % len(table[-1][1])]


def assign_designator(palette: dict[str, str]) -> str:
    """
    Assign a two-word Latin designator to a palette.
    Derived perceptually from c_gold hue and c_bg lightness.
    """
    gold_hex = palette.get("c_gold", "#d4af37")
    bg_hex   = palette.get("c_bg",   "#050507")

    gold_lch = hex_to_lch(gold_hex)
    bg_lch   = hex_to_lch(bg_hex)

    # Use seal hash for deterministic variety within a lightness/hue band
    seal = compute_seal(palette)
    seed = int(seal[:4], 16)

    adj  = _pick(ADJECTIVES_BY_HUE,     gold_lch.H, seed)
    noun = _pick(NOUNS_BY_LIGHTNESS,    bg_lch.L,   seed // 4)

    return f"{adj} {noun}"


# ── Nomen system ────────────────────────────────────────────────────────
# (Delegated to nomen.py — stub imports here for convenience)

def make_ratification_record(
    palette: dict[str, str],
    designator: str | None = None,
) -> dict:
    """
    Produce the complete ratification record dict.
    """
    seal = compute_seal(palette)
    if designator is None:
        designator = assign_designator(palette)

    from AuctoritasSpectralis.engine.contrast import wcag21, wcag21_aa_pass, wcag21_aaa_pass, apca_lc
    from AuctoritasSpectralis.engine.nomen import generate_nomina

    # Compute headline contrast metrics (c_gold on c_bg)
    gold = palette.get("c_gold", "#d4af37")
    bg   = palette.get("c_bg",   "#050507")
    wcag = wcag21(gold, bg)
    lc   = apca_lc(gold, bg)

    nomina = generate_nomina(palette)

    import datetime
    return {
        "designator":  designator,
        "sealed_at":   datetime.datetime.now().isoformat(timespec="seconds"),
        "seal":        seal,
        "tokens":      palette,
        "nomina":      nomina,
        "wcag_min":    round(wcag, 2),
        "apca_min":    round(lc, 1),
        "aa_pass":     wcag21_aa_pass(wcag),
        "aaa_pass":    wcag21_aaa_pass(wcag),
    }
