"""
AUCTORITAS SPECTRALIS — v1.0.0
i18n.py — Translation table for all UI strings

All user-visible strings that change with LAT/EN mode live here.
Features call i18n.t(key, mode) to get the current string.
"""

from __future__ import annotations

# ── Translation table ─────────────────────────────────────────────────────
# Format: key → {"LAT": latin_string, "EN": english_string}

_T: dict[str, dict[str, str]] = {

    # ── Fascia — Colores ──────────────────────────────────────────────────
    "btn.novum":        {"LAT": "Novum",       "EN": "New"},
    "btn.aperire":      {"LAT": "Aperire",     "EN": "Open"},
    "btn.servare":      {"LAT": "Servare",     "EN": "Save"},
    "btn.servare_ut":   {"LAT": "Servare Ut",  "EN": "Save As"},
    "btn.ratificare":   {"LAT": "Ratificare",  "EN": "Ratify"},
    "btn.promulgare":   {"LAT": "Promulgare",  "EN": "Export"},

    # ── Fascia — Observatory (Scrutinium) ─────────────────────────────────
    "btn.export_report":{"LAT": "Exporta Relatio", "EN": "Export Report"},
    "btn.metric_label": {"LAT": "Metrica",          "EN": "Metric"},

    # ── Fascia — Specularium ──────────────────────────────────────────────
    "btn.context_label":{"LAT": "Contextus",   "EN": "Context"},

    # ── Fascia — Bibliotheca ──────────────────────────────────────────────
    "btn.onerare":      {"LAT": "Onerare",     "EN": "Load"},
    "btn.ramificare":   {"LAT": "Ramificare",  "EN": "Fork"},
    "btn.comparare":    {"LAT": "Comparare",   "EN": "Compare"},

    # ── Fascia — Registrum ────────────────────────────────────────────────
    "btn.export_reg":   {"LAT": "Exporta Registrum", "EN": "Export Registry"},

    # ── Fascia — Configuratio ─────────────────────────────────────────────
    "btn.config":       {"LAT": "Configuratio", "EN": "Config"},

    # ── Fascia — Help ─────────────────────────────────────────────────────
    "btn.help":         {"LAT": "Auxilium",     "EN": "Help"},

    # ── Colores — control strip ───────────────────────────────────────────
    "gen.lead_pair":    {"LAT": "PARIUM DUCENS",  "EN": "LEAD PAIR"},
    "gen.generate":     {"LAT": "GENERARE",       "EN": "GENERATE"},
    "gen.void":         {"LAT": "Void",           "EN": "Void"},
    "gen.aurum":        {"LAT": "Aurum",          "EN": "Gold"},
    "gen.forge":        {"LAT": "Forgia",         "EN": "Forge"},
    "tab.lead":         {"LAT": "Ducens",         "EN": "Lead"},
    "tab.bg":           {"LAT": "BG",             "EN": "BG"},
    "tab.aurum_family": {"LAT": "Aurum",          "EN": "Gold"},
    "tab.accents":      {"LAT": "Accentus",       "EN": "Accents"},
    "tab.algo":         {"LAT": "Algo",           "EN": "Algo"},
    "section.constraint":{"LAT": "RESTRICTIO GENERATIONIS", "EN": "GENERATION CONSTRAINT"},
    "section.harmony":  {"LAT": "HARMONIA",       "EN": "HARMONY"},
    "section.derivation":{"LAT": "DERIVATIO",     "EN": "DERIVATION"},
    "slider.chroma_scale":   {"LAT": "Scala Chromatis", "EN": "Chroma Scale"},
    "slider.bg_depth":       {"LAT": "Profunditas BG",  "EN": "BG Depth"},
    "slider.text_brightness":{"LAT": "Claritas Textus", "EN": "Text Brightness"},
    "slider.accent_hue":     {"LAT": "Offset Coloris",  "EN": "Accent Hue Offset"},
    "slider.accent_intensity":{"LAT": "Intensitas",     "EN": "Accent Intensity"},
    "note.sliders":     {
        "LAT": "Scopuli fixant limites randomisationis.\nClausus = hex fixum, limites ignorantur.",
        "EN":  "Sliders set the randomisation envelope.\nLocked = hex frozen, envelope ignored.",
    },

    # ── Specularium — context names ───────────────────────────────────────
    "ctx.instrumentum": {"LAT": "Instrumentum",  "EN": "Interface"},
    "ctx.documentum":   {"LAT": "Documentum",    "EN": "Document"},
    "ctx.insignia":     {"LAT": "Insignia",      "EN": "Insignia"},
    "ctx.token_strip":  {"LAT": "Tenia Signorum","EN": "Token Strip"},

    # ── Observatory — section labels ──────────────────────────────────────
    "obs.parium":       {"LAT": "Parium Colorum",    "EN": "Colour Pair"},
    "obs.matrix":       {"LAT": "Matrix Contrastus", "EN": "Contrast Matrix"},

    # ── Bibliotheca — section labels ──────────────────────────────────────
    "lib.registry":     {"LAT": "Registrum Chromaticum", "EN": "Chromatic Registry"},

    # ── Registrum ─────────────────────────────────────────────────────────
    "reg.readonly":     {"LAT": "Lectu Solum", "EN": "Read Only"},

    # ── Configuratio modal ────────────────────────────────────────────────
    "cfg.title":        {"LAT": "⚙  Configuratio",    "EN": "⚙  Settings"},
    "cfg.save":         {"LAT": "Servare",             "EN": "Save"},
    "cfg.reset":        {"LAT": "Restitue Defaults",   "EN": "Reset Defaults"},
    "cfg.close":        {"LAT": "✕  Discede",          "EN": "✕  Close"},
    "cfg.harmony":      {"LAT": "Harmonia Defalta",    "EN": "Default Harmony"},
    "cfg.contrast":     {"LAT": "Algo Contrastus",     "EN": "Default Contrast Algo"},
    "cfg.export_dir":   {"LAT": "Directio Exportandi", "EN": "Export Directory"},
    "cfg.bus":          {"LAT": "Mundana State Bus",   "EN": "Mundana State Bus"},
    "cfg.signal":       {"LAT": "Via Signi",           "EN": "Signal File Path"},
    "cfg.spec_default": {"LAT": "Specularium Defaltum","EN": "Specularium Default"},

    # ── Status bar ────────────────────────────────────────────────────────
    "status.colores":       {"LAT": "Colores",       "EN": "Colours"},
    "status.observatory":   {"LAT": "Observatorium", "EN": "Observatory"},
    "status.specularium":   {"LAT": "Specularium",   "EN": "Preview"},
    "status.bibliotheca":   {"LAT": "Bibliotheca",   "EN": "Library"},
    "status.registrum":     {"LAT": "Registrum",     "EN": "Registry"},
}


def t(key: str, mode: str = "LAT") -> str:
    """Return the translated string for key in the given mode."""
    entry = _T.get(key)
    if entry is None:
        return key   # fallback: return the key itself
    return entry.get(mode, entry.get("LAT", key))


def context_names(mode: str = "LAT") -> list[str]:
    return [
        t("ctx.instrumentum", mode),
        t("ctx.documentum",   mode),
        t("ctx.insignia",     mode),
        t("ctx.token_strip",  mode),
    ]
