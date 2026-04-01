"""
╭──────────────────────────╮
│⛓                        ⛓│
│⛓ Ｄｉｓｐｏｓｉｔｉｏｎ ⛓│
│⛓     Ｓｌｉｄｅｒｓ     ⛓│
│󱢿                        󱢿│
╰──────────────────────────╯ 

# ─────────────────────────────────────────────────────────────────────────────
# DISPOSITION SLIDERS  (INCLINATIONES)
# ─────────────────────────────────────────────────────────────────────────────
"""

DISPOSITION_LABELS  = ["Benevolent", "Neutral", "Adversarial", "Unknowable"]
REGISTER_LABELS     = ["Formal", "Institutional", "Colloquial", "Cryptic"]
PRESENCE_LABELS     = ["Quiet", "Measured", "Pronounced", "Overwhelming", "Procedural", "Residual"]
OPACITY_LABELS      = ["Transparent", "Guarded", "Evasive", "Sealed", "Redacted", "Duly Filed"]
STABILITY_LABELS    = ["Grounded", "Volatile", "Fractured", "Transcendent", "Procedurally Stable", "Load-Bearing"]

# Image bgo ~?ias strings fed into portrait prompt
DISPOSITION_IMAGE_BIAS = {
    "Benevolent":   "warm halo light, gentle presence, open posture, soft gold luminance",
    "Neutral":      "balanced composition, no directional light bias, measured stillness",
    "Adversarial":  "sharp shadow angles, confrontational stance, cold edge lighting, tension",
    "Unknowable":   "ambiguous form, dissolving edges, impossible geometry, presence without face",
}
REGISTER_IMAGE_BIAS = {
    "Formal":        "formal robes, precise iconographic detail, structured symmetry",
    "Institutional": "insignia of office, ceremonial vestments, architectural framing",
    "Colloquial":    "informal bearing, lived-in aesthetic, worn materials",
    "Cryptic":       "obscured symbolism, layered glyphs, meaning withheld from view",
}
PRESENCE_IMAGE_BIAS = {
    "Quiet":        "small figure, vast negative space, whisper of presence",
    "Measured":     "centred composition, deliberate scale, controlled weight",
    "Pronounced":   "dominant figure, high visual mass, commanding the frame",
    "Overwhelming": "fills the frame entirely, environmental presence, cannot be contained",
    "Procedural":   "present the way a system is present — not felt until needed, administrative stillness",
    "Residual":     "the entity has already spoken; weight of it remains, afterimage quality",
}
OPACITY_IMAGE_BIAS = {
    "Transparent":  "clearly defined, readable iconography, no hidden registers",
    "Guarded":      "half-visible, partial concealment, selective revelation",
    "Evasive":      "figure obscured, identity suggested not stated, veiled",
    "Sealed":       "total concealment, only surface visible, void within",
    "Redacted":     "legible structure, contents removed — shape of absence visible, redaction marks",
    "Duly Filed":   "everything disclosed, nothing revealed — form-and-stamp aesthetic, bureaucratic surface",
}
STABILITY_IMAGE_BIAS = {
    "Grounded":             "solid form, anchored base, stable vertical axis",
    "Volatile":             "dynamic pose, energy crackling, motion implied",
    "Fractured":            "broken symmetry, visible cracks, held-together tension",
    "Transcendent":         "dissolving into light or void, boundary between being and absence",
    "Procedurally Stable":  "holds form because the process holds, not the entity — procedural rigidity",
    "Load-Bearing":         "stable under weight specifically, compressed posture, structural tension",
}
