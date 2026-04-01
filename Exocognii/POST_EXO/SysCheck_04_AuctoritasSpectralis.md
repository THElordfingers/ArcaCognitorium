# SYSTEMS CHECK — AUCTORITAS SPECTRALIS (Bureau I)

*A4 · Triumviratus Aestheticus Imperialis · Arca Cognitorium · MMXXVI*

---

## Summary

The ultimate colour theme authority. Sole writer of `theme.json` — the
inter-app colour contract for the entire Exocognii suite. Derives a 10-token
palette hierarchy in OKLAB perceptual colour space from a BG/FG base pair.
Audits WCAG 2.1 + APCA contrast, simulates CVD, ratifies with SHA-256 seal
and Latin designator. Chromatic Registry in SQLite with full history. Live
self-reskinning preview with 150ms debounced QSS application. 26/26 tests.

Motto: *Codexium Chromaticus — Sequentiae Umbrarum.*

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  OKLAB derivation engine          │  10-token hierarchy derived                │
│                                   │  mathematically from BG/FG base pair       │
│                                   │  in perceptual colour space                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Contrast audit                   │  WCAG 2.1 + APCA for all token pairs       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  CVD simulation                   │  Protanopia, deuteranopia, tritanopia      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Ratification                     │  SHA-256 seal + Latin designator           │
│                                   │  (e.g. "Aureus Abyssalis")                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  QSS auto-renderer                │  150ms debounce live self-reskinning       │
│                                   │  preview                                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Chromatic Registry               │  SQLite — full theme history, ratification │
│                                   │  states                                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Export                           │  theme.json (canonical inter-app contract) │
│                                   │  .qss (Qt stylesheet)                      │
│                                   │  .md palette card                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  26/26 tests passing              │                                            │
╰───────────────────────────────────┴────────────────────────────────────────────╯

**Note on keyboard:** Ctrl+V is reserved — paste is `Ctrl+Shift+V`.
Hue vocabulary is mapped to OKLAB actual angles: gold at ~91° (not sRGB gold).

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  ~/.arca/config.json                                    │
│              │  SQLite Chromatic Registry (existing themes)            │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  theme.json (canonical inter-app colour contract)       │
│              │  theme.qss (Qt stylesheet)                              │
│              │  palette_card.md (palette card)                         │
│              │  SQLite Chromatic Registry (ratified themes + history)  │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  PyQt6, colour-science 0.4.4+                           │
│              │  No ClaudeBox, no API calls                             │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Launch
cd ~/ArcaCognitorium/Exocognii/A4/AuctoritasSpectralis
python -m AuctoritasSpectralis

# Tests
pytest tests/ -v
```

Verification steps:

1. App launches with live self-reskinning preview
2. Set a BG/FG hex pair — 10 tokens appear in palette view
3. Contrast audit runs — WCAG and APCA scores visible
4. CVD simulation produces three visually distinct previews
5. Ratify a theme — SHA-256 seal and Latin designator assigned
6. Export — theme.json written, check it is valid JSON with all 10 tokens
7. Restart — SQLite registry retains history

Checklist:

- 26/26 tests passing
- theme.json has: bg, fg, and all 8 derived tokens
- SHA-256 seal changes when palette changes
- OKLAB hue angles correct (gold ~91° not falling into green bucket)
- Chromatic Registry persists across restarts
- No API calls, no network dependency

---

## Open Items

theme.json not yet consumed by any other app except Bureau II. The aesthetic
wire to the rest of the suite is the most consequential unwired connection in
the Exocognii. This is Step 3 of the Cohesion Respec.

Bureau I/II path at full `AestheticAuthoritarianAssociativeAlliance/` path.
Bureau III at `Exocognii/A4/`. Path unification pending.

---

## Claude.ai Collaboration Prompt

```
You are assisting with AUCTORITAS SPECTRALIS (Bureau I) — the colour theme
governance tool of the Arca Cognitorium. PyQt6, Python 3.11, Debian Trixie.

Architecture:
- OKLAB colour space for all derivation — perceptually uniform
- 10-token hierarchy derived mathematically from BG/FG base pair
- theme.json is the canonical inter-app colour contract — sole
  writer is Bureau I. All other apps should read it.
- SHA-256 seal: changes when theme changes
- Latin designator: one two-word Latin name per ratified theme
- Hue vocabulary remapped to OKLAB actual hue angles.
  Gold at ~91° (not sRGB gold bucket)
- Ctrl+V reserved — paste is Ctrl+Shift+V
- SQLite Chromatic Registry owns full history
- colour-science 0.4.4+ required
- No ClaudeBox, no API calls
- 26/26 tests must continue passing after any change

Path: AestheticAuthoritarianAssociativeAlliance/AuctoritasSpectralis/

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＡＵＣＴＯＲＩＴＡＳ ＳＰＥＣＴＲＡＬＩＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ     ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Auctoritas Spectralis (Bureau I)                     ║
║    Version      ·  1.0                                                  ║
║    Tests        ·  26/26 passing                                        ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
