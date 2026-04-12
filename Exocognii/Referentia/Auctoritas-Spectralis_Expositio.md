```
╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║              AUCTORITAS SPECTRALIS                                    ║
║              Spectral Compliance Authority                            ║
║              Codexium Chromaticus · Sequentiae Umbrarum               ║
║                                                                       ║
║              ✦  EXPOSITIO  ✦                                         ║
║              Foundational Record                                      ║
║                                                                       ║
║              Bureau I of III — Triumviratus Aestheticus Imperialis    ║
║              Aesthetic Authoritarian Associative Alliance             ║
║                                                                       ║
║◣                                                                     ◢║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## VERIFICATIO CANONICA

╭─────────────────────────────────────────────────────────────────────╮
│  VERIFICATIO CANONICA                                               │
│  ─────────────────────────────────────────────────────────────────  │
│  All identity content, nomenclature, mottos, and canonical          │
│  references have been verified against ratified sources prior       │
│  to composition. No content has been invented where canonical       │
│  content exists.                                                    │
│                                                                     │
│  Bureau:   Auctoritas Spectralis                                    │
│  Document: Expositio                                                │
│  Version:  1.0                                                      │
│  Date:     2026-04-08                                               │
╰─────────────────────────────────────────────────────────────────────╯

---

## I. IDENTITY

╭─────────────────────────────────────────────────────────────────────╮
│  Primary Title   ·  AUCTORITAS SPECTRALIS                           │
│  English Name    ·  Spectral Compliance Authority                   │
│  Motto           ·  Codexium Chromaticus · Sequentiae Umbrarum      │
│  Bureau          ·  I of III — Triumviratus Aestheticus Imperialis  │
│  Alliance        ·  Aesthetic Authoritarian Associative Alliance    │
│  Author          ·  LordFingers, the Absent Architect               │
│  Entered Build   ·  2026-04-08                                      │
╰─────────────────────────────────────────────────────────────────────╯

---

## II. THE WHY

The Cogniverse is a chromatic problem. Every application in the
Exocognii Suite renders in ModusArcanus — the canonical aesthetic
of dark void, Aurum gold, and Georgia serif. But the tokens that
define that aesthetic have, until now, existed only as hardcoded
hex values scattered across QSS files, referenced by convention
and maintained by memory.

This is not governance. This is coincidence.

The Cogniverse requires a chromatic authority: one application
whose sole mandate is to own the colour contract, enforce its
logic, ratify its palettes with cryptographic identity, and
distribute sealed themes to every consuming system. Without this
authority, the Triumviratus cannot function — Bureau II and
Bureau III both depend on `theme.json` existing before they can
operate. The dependency is constitutional, not optional.

The apparatus does not merely select colours. It governs them.
It arbitrates. It ratifies. It remembers. It does not explain
itself. It is felt.

---

## III. THE WHAT

AUCTORITAS SPECTRALIS is a PyQt6 desktop application. It is the
sole writer of `theme.json` — the inter-application colour
contract shared across the Exocognii Suite and any downstream
consumer in the Cogniverse.

Its responsibilities are:

**Chromatic Governance** — Maintain the canonical ten-token
colour hierarchy for every Cogniverse application. The hierarchy
is: c_bg, c_gold, c_panel, c_subtle, c_gold_dark, c_gold_dim,
c_text, c_white, c_crimson, c_teal.

**Palette Forge** — Accept a Lead Pair (Fundus and Scriptura)
from the Wizard. Derive the remaining eight tokens through
harmony algorithms operating in OKLAB LCH space, with structured
randomness via `oklab_jitter()`. Six harmony models: Complementary,
Analogous, Monochromatic, Split-Complementary, Triadic, Tetradic.

**Perceptual Evaluation** — Score every meaningful token pairing
against six contrast metrics: WCAG 2.1, WCAG 3.0 / APCA, DeltaE
2000, Luminance Ratio, Chroma Distance, and Hue Distance. Surface
compliance badges. Flag failures.

**Ratification** — Seal approved palettes with SHA-256 hashes.
Assign two-word Latin designators. Write canonical `theme.json`.
Emit interim filesystem signal to downstream consumers.

**Archive** — Maintain the Chromatic Registry: a SQLite archive
of every ratified palette. The Registry is permanent. Nothing
is deleted.

**Distribution** — Export sealed palettes in four formats:
JSON (theme.json), QSS (PyQt6 stylesheet), Markdown (documentation
fragment), CSS (web consumption). Multi-format export on every
ratification.

**Preview** — Live Specularium: four PyQt6 display contexts
(Instrumentum, Documentum, Insignia, Token Strip) updating
on every palette change, all ten tokens explicitly exercised
in every context.

---

## IV. THE HOW

### Architecture Overview

AUCTORITAS SPECTRALIS is a single PyQt6 application following
the A4 Common Shell layout ratified by the Convocatio Iudicii.
It is structured around four canonical zones:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        ┃  ZONE III — FASCIA                     ┃
┃  ZONE I — TITULUM      ┃  Feature-specific action buttons       ┃
┃  Bureau identity.      ┠────────────────────────────────────────┨
┃  Fixed. Never scrolls. ┃                                        ┃
┃  Never changes.        ┃  ZONE IV — SCRIPTORIUM CANVAS          ┃
┃                        ┃  Full remaining canvas.                ┃
┣━━━━━━━━━━┯━━━━━━━━━━━━━┛  One feature at a time.               ┃
┃  ZONE II │                                                      ┃
┃  FEATURE │                                                      ┃
┃  CODEX   │                                                      ┃
┃          │                                                      ┗
┗━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

Zone I (Titulum, 220px): Bureau identity. Fixed. Never changes.
Zone II (Feature Codex, 220px): Five feature selectors.
Zone III (Fascia, 52px): Context-sensitive feature actions.
Zone IV (Canvas): The active feature's workspace.

A persistent status bar occupies the bottom edge. A
CONFIGURATIO modal overlays the canvas when invoked.

### Feature Set

Five features. No more, no less.

```
╭──────────────────────╮
│  ✦  COLORES          │  ← Palette forge. Lead Pair + harmony engine.
│     SCRUTINIUM       │  ← Contrast audit workspace.
│     SPECULARIUM      │  ← Live preview. Four display contexts.
│     BIBLIOTHECA      │  ← Registry browser with swatch strips.
│     REGISTRUM        │  ← Full SQLite ledger. Read only. Permanent.
╰──────────────────────╯
```

CONFIGURATIO is not a feature. It is a persistent toolbar modal
accessed via a dedicated button in the Fascia. It contains:
default harmony algorithm, default contrast algorithm, export
directory, Mundana State Bus connection target, filesystem watch
signal path, Specularium default context.

### Key Technologies

╭──────────────────────────┬─────────────────────────────────────────╮
│  Component               │  Technology                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  GUI framework           │  PyQt6 (exclusive)                      │
│  Colour space            │  OKLAB / LCH (via colormath or manual)  │
│  Randomness engine       │  oklab_jitter() — bounded LCH jitter    │
│  Seal algorithm          │  SHA-256                                │
│  Registry storage        │  SQLite                                 │
│  Export formats          │  JSON, QSS, Markdown, CSS               │
│  Inter-app contract      │  theme.json                             │
│  State broadcast         │  Interim: filesystem signal file        │
│                          │  Future: Mundana State Bus (mundana.    │
│                          │  resolver channel)                      │
│  Python version          │  3.11                                   │
│  Venv                    │  venv-SPECTRALIS (to be created)        │
│  Path                    │  Exocognii/AuctoritasSpectralis/        │
│  Launch standard         │  python3 -m AuctoritasSpectralis        │
╰──────────────────────────┴─────────────────────────────────────────╯

### The Colour Engine

All ten derived tokens flow through four sequential operations
on every GENERATE invocation:

1. **Role derivation** — L, C, H values computed per token's
   role rules (lightness ratio, chroma scaling, hue offset
   per harmony model).

2. **Harmony hue assignment** — selected model sets the hue
   family for each derived token.

3. **Lock pass** — locked tokens restored to locked values,
   overriding derivation. Harmonic conflict detection runs here.
   Flags set if any locked token deviates >30° from expected
   hue family.

4. **Jitter pass** — `oklab_jitter()` applies bounded random
   perturbation to all unlocked derived tokens. Ranges vary by
   role: tight for backgrounds, wide for accents.

The Lead Pair (c_bg / c_gold) is never touched by the engine.
It is the Wizard's input and is sacrosanct.

### Downstream Dependencies

Bureau I is the chromatic foundation of the entire Triumviratus.
`theme.json` must exist before Bureau II (Agentia Architecturalis)
or Bureau III (Departamentum Documentalis) can operate.

Interim notification of downstream consumers uses the filesystem
signal file `~/.arca/signals/theme_updated`. When the Mundana
State Bus is live, this is replaced by publication to the
`mundana.resolver` channel. No changes to the Bureau I seal
pipeline are required for that migration.

PRAESIDIUM and GNOSIUM EXANIMA both read `theme.json` on launch
and monitor the signal file for changes.

### Special Behaviours

**Inductio Chromatica** — First-launch ceremony. Runs once.
Titulum fades in line by line. Feature Codex items light up
in sequence. Default ModusArcanus palette silently derived.
Total duration approximately eight seconds. A flag in user
config marks completion. Never runs again unless manually reset.

**Dirty State Marker** — ◌ (U+25CC). Appears in status bar
beside stage label whenever the working palette has unsaved
changes. Disappears on save. Does not pulse. Does not flash.
Simply is or is not.

**LAT/EN Toggle** — Persistent preference. Lives in Titulum.
Switches UI labels between Latin and English register.

---

## V. SUITE POSITION

AUCTORITAS SPECTRALIS is Bureau I of the Triumviratus Aestheticus
Imperialis. It is the first bureau to be built. Its outputs are
consumed by all other bureau applications and by the broader
Exocognii Suite.

The building order is not advisory. It is mandatory. Bureau I
builds first. The apparatus must exist before the Cogniverse's
chromatic contract can be honoured.

---

## VI. OPEN ITEMS AT BUILD ENTRY

╭─────────────────────────────────────────────────────────────────────╮
│  ·  Venv not yet created — venv-SPECTRALIS                         │
│  ·  Mundana State Bus not yet built — interim mechanism active     │
│  ·  Specularium "full application shell" context — v1.1 scope,    │
│     not this build                                                 │
│  ·  Bibliotheca search/filter — future cycle (>30 entries)        │
│  ·  Celestial Resolver integration — not in scope                 │
│  ·  Exvacua Loricum integration — when built; Bibliotheca         │
│     data model pre-positioned for it                              │
╰─────────────────────────────────────────────────────────────────────╯

---

*AUCTORITAS SPECTRALIS · Spectral Compliance Authority*
*Expositio · Bureau I of III — Triumviratus Aestheticus Imperialis*
*MMXXVI · Ordo Discordia, Cosmos Inania*
