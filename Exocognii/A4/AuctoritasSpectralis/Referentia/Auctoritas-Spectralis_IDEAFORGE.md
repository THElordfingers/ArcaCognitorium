```
╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║              AUCTORITAS SPECTRALIS                                    ║
║              Spectral Compliance Authority                            ║
║              Codexium Chromaticus · Sequentiae Umbrarum               ║
║                                                                       ║
║              ✦  IDEAFORGE BUILD DOCUMENT  ✦                          ║
║              Phase 1: Idea Brief + Phase 2: Seed Prompt              ║
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
│  Document: IdeaForge Build Document                                 │
│  Version:  1.0                                                      │
│  Date:     2026-04-08                                               │
╰─────────────────────────────────────────────────────────────────────╯

---

═══════════════════════════════════════════════════════════════════════
                    PHASE 1 — IDEA BRIEF
═══════════════════════════════════════════════════════════════════════

## 1. APPLICATION IDENTITY

╭─────────────────────────────────────────────────────────────────────╮
│  Primary Title   ·  AUCTORITAS SPECTRALIS                           │
│  English Name    ·  Spectral Compliance Authority                   │
│  Motto           ·  Codexium Chromaticus · Sequentiae Umbrarum      │
│  Bureau          ·  I of III — Triumviratus Aestheticus Imperialis  │
│  Alliance        ·  Aesthetic Authoritarian Associative Alliance    │
╰─────────────────────────────────────────────────────────────────────╯

---

## 2. WHAT IS BEING BUILT

A PyQt6 desktop application that governs colour for the entire
Exocognii Suite. It accepts a Lead Pair (background + foreground),
derives ten canonical colour tokens through OKLAB LCH harmony
algorithms with structured randomness, evaluates every meaningful
pair against six contrast metrics, ratifies approved palettes with
cryptographic seals, and distributes the result as `theme.json` to
every consuming application in the Cogniverse.

This application is Bureau I of the Triumviratus Aestheticus
Imperialis. It builds first. It writes the colour contract that
all other bureaus depend on.

---

## 3. CORE FUNCTIONAL REQUIREMENTS

### 3.1 Colour Engine

- OKLAB / LCH as the sole colour space for derivation
- Ten canonical tokens: c_bg, c_gold, c_panel, c_subtle,
  c_gold_dark, c_gold_dim, c_text, c_white, c_crimson, c_teal
- Lead Pair (c_bg, c_gold) is the Wizard's input; never altered
  by the engine
- Six harmony algorithms: Complementary, Analogous,
  Monochromatic, Split-Complementary, Triadic, Tetradic
- Four sequential operations per GENERATE:
  role derivation → harmony hue assignment → lock pass → jitter pass
- `oklab_jitter()` — bounded LCH perturbation, per-token ranges
  (tight for backgrounds, wide for accents; see jitter table)
- Per-token lock controls (⊗ locked / ○ unlocked)
- Harmonic conflict detection: locked token >30° from harmony
  family triggers ⚑ flag (on token, on GENERATE, in status bar)
  — generation is not blocked

### 3.2 Contrast Evaluation (SCRUTINIUM)

Six metrics: WCAG 2.1 ratio, WCAG 3.0 / APCA, DeltaE 2000,
Luminance Ratio, Chroma Distance, Hue Distance.

Parium Colorum: single-pair display with headline WCAG + five
secondary metrics and pass/fail badges.

Contrast Matrix: FG × BG grid. Metric-switchable via Fascia.
Cell hover shows all six metrics.

### 3.3 Ratification Pipeline

On RATIFICARE:
1. SHA-256 hash from sorted hex token concatenation
2. Two-word Latin designator assigned (perceptually derived)
3. `~/.arca/theme.json` written
4. `~/.arca/signals/theme_updated` written (timestamp + designator)
5. SQLite Chromatic Registry entry created
6. Multi-format export: `.json`, `.qss`, `.md`, `.css`

The seal is permanent. No Registry entry is ever deleted.

### 3.4 Chromatic Registry (SQLite)

SQLite database. Columns: id, designator, sealed_at, tokens_json,
wcag_min, apca_min, aa_pass, aaa_pass, seal_hash, notes.

REGISTRUM (Feature V) renders this as a read-only sortable table.
Row click expands detail panel. Nothing editable. Nothing deletable.

### 3.5 Specularium (Live Preview)

Four contexts: Instrumentum (dark instrument panel), Documentum
(page surface), Insignia (badge/seal display), Token Strip (all
ten labelled blocks).

All ten tokens exercised in every context. Updates live on every
palette change. No refresh required.

Context selectable via tab strip in the canvas.

### 3.6 Bibliotheca (Registry Browser)

Palette card list: swatch strip + designator + date + compliance
badges. Detail panel on selection: mini Specularium preview,
full token list with Nomina, three action buttons.

Actions: Onerare (load into COLORES), Ramificare (fork as draft),
Comparare (side-by-side comparison with current working palette).

### 3.7 Nomen System

Each derived token receives a two-word Latin name (Nomen)
perceptually derived from its L and H values. The whole palette
receives a two-word Latin Designator at ratification.

Both update on every generation cycle.

### 3.8 Multi-Format Export

Four formats produced on ratification (and on Promulgare without
sealing):

- `theme.json` — canonical token map with metadata
- `theme.qss` — PyQt6 stylesheet with CSS variables
- `theme.md` — Markdown documentation fragment with swatch table
- `theme.css` — CSS custom properties for web consumption

### 3.9 Downstream Broadcast

Interim mechanism: write `~/.arca/signals/theme_updated` as plain
text (ISO timestamp + designator) on every seal. Consumers poll
at 2000ms. On Mundana State Bus availability, Bureau I publishes
to `mundana.resolver` channel instead. No pipeline change required.

### 3.10 LAT/EN Toggle

Persistent preference. Lives in Titulum. Switches all application
labels between Latin and English register. Persists via config.

### 3.11 Inductio Chromatica

First-launch ceremony. Runs once. Controlled by a flag in user
config. Sequence:

- Canvas dark
- Titulum lines fade in: title (2s), then subtitle, then motto
  (600ms gap between each line, full opacity from zero)
- Feature Codex items light up top-to-bottom, 400ms intervals
  (Aurum Nox → Aurum Dimmus → Aurum)
- Canvas populates COLORES feature
- Default ModusArcanus palette silently derived
- Token rows appear with 60ms stagger

Total: ~8 seconds. Never repeats unless flag manually reset.

### 3.12 Dirty State Marker

◌ (U+25CC) in status bar beside stage label. Appears on any
unsaved change. Disappears on save. Does not pulse. Does not flash.

### 3.13 CONFIGURATIO Modal

Not a feature. Opened via ⚙ Config in Fascia. Available regardless
of active feature. Contains: default harmony algorithm, default
contrast algorithm, export directory, Mundana State Bus connection
target, signal file path, Specularium default context.

Closed by Escape or ✕ Discede button.

---

## 4. LAYOUT (A4 COMMON SHELL)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        ┃  ZONE III — FASCIA  (52px)             ┃
┃  ZONE I — TITULUM      ┃  Feature-specific + ⚙ Config + ? Help  ┃
┃  (220px, full height)  ┠────────────────────────────────────────┨
┃                        ┃                                        ┃
┃  Bureau identity.      ┃  ZONE IV — CANVAS                      ┃
┃  Fixed. Never changes. ┃  Active feature workspace              ┃
┣━━━━━━━━━━┯━━━━━━━━━━━━━┛  Full remaining space                  ┃
┃  ZONE II │                                                      ┃
┃  FEATURE │                                                      ┃
┃  CODEX   │                                                      ┃
┃  (220px) │                                                      ┃
┗━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  STATUS BAR  ◌  (full width, 26px)
```

Zone II is below Zone I on the left column. Both are 220px wide.

---

## 5. AESTHETIC (MODUSARCANUS)

```
--void:       #050507   (primary background)
--obsidian:   #0a0a12   (panel background)
--gold:       #d4af37   (primary accent / Aurum)
--gold-dim:   #7a6a2a   (secondary accent / Aurum Dimmus)
--gold-dark:  #3a2e10   (tertiary accent / Aurum Nox)
--crimson:    #8b1a1a   (error/warning)
--teal:       #1a5a5a   (success/info)
--parchment:  #c8b88a   (secondary text)
--vellum:     #e8e0cc   (primary text)
```

Typography:
- Display / headers: Cinzel (serif, classical Roman proportions)
- Body / labels: IM Fell English (humanist old-style)
- Monospace / data: Share Tech Mono

All borders: 1px solid `--gold-dark`. No rounded corners.
No gradients on interactive elements. No shadows.
The void does not glow. The gold does not pulse.

---

## 6. TECHNICAL STACK

```
╭──────────────────────────┬──────────────────────────────────────────╮
│  Python                  │  3.11                                    │
│  GUI                     │  PyQt6 (exclusive — no PySide6)          │
│  Colour math             │  Manual OKLAB/LCH ops or colormath lib   │
│  Database                │  SQLite (stdlib sqlite3)                 │
│  Config                  │  ~/.arca/config.json (json stdlib)       │
│  Hash                    │  hashlib.sha256 (stdlib)                 │
│  CLAUDE_API_KEY env var  │  Not required for this app               │
│  Launch                  │  python3 -m AuctoritasSpectralis         │
│  Path                    │  Exocognii/AuctoritasSpectralis/         │
│  Venv                    │  venv-SPECTRALIS                         │
╰──────────────────────────┴──────────────────────────────────────────╯
```

---

## 7. OUT OF SCOPE FOR THIS BUILD

- Specularium "full application shell" context (v1.1)
- Bibliotheca search/filter surface (>30 entries threshold)
- Mundana State Bus integration (interim filesystem watch is used)
- Celestial Resolver integration
- Exvacua Loricum integration (data model pre-positioned; no call)
- CAELESTIS dependency (does not exist yet)

---

═══════════════════════════════════════════════════════════════════════
                    PHASE 2 — SEED PROMPT
═══════════════════════════════════════════════════════════════════════

You are the Builder — a senior entity of the Arca Cognitorium.
You build with precision, lore-fidelity, and architectural clarity.
You do not invent canonical content. You do not approximate names,
mottos, or token values. You verify before you commit.

You are building **AUCTORITAS SPECTRALIS** — Bureau I of the
Triumviratus Aestheticus Imperialis, the chromatic governance
authority of the Cogniverse. This is a PyQt6 desktop application.
It runs on Debian Trixie / KDE Plasma 6 / X11 on a machine called
CastrumDigitos, under `/home/lordfingers/`.

The full specification exists across three pre-build documents
supplied to you in this session:
- Expositio.dux.tome.md — the foundational why/what/how
- dux-tome-dux.dux.tome.md — the operational manual
- AuctoritasSpectralis-DesignPlan-v1_1.md — the ratified design plan
- AuctoritasSpectralis-Wireframes-v1_1.html — ratified wireframes

Read all four documents in their entirety before writing a single
line of application code. Your implementation must be faithful to
the ratified wireframes and design plan without deviation.

**Critical invariants — these are non-negotiable:**

- PyQt6 exclusively. No PySide6. No mixing.
- `CLAUDE_API_KEY` env var (not `ANTHROPIC_API_KEY`).
  This app does not use ClaudeBox directly but must not violate
  the env var convention in any config read.
- Dirty state marker is ◌ (U+25CC). Not asterisk. Not dot.
- Dirty state marker ratified. It is not "proposed" anymore.
- Word "atelier" does not exist in the Cogniverse. Do not use it.
- Feature switches are instant stack swaps. No animation. No slide.
- Feature Codex contains exactly five features.
- CONFIGURATIO is a modal. It is not a feature. It does not
  appear in the Codex.
- LAT/EN toggle lives in Titulum. Not in the Fascia. Not in Codex.
- HELP is always the rightmost Fascia element.
- ⚙ Config is always the second-from-right Fascia element.
- All other Fascia buttons are feature-owned.
- `theme.json` is written to `~/.arca/theme.json`.
- Signal file is `~/.arca/signals/theme_updated`.
- Chromatic Registry is a SQLite database. Nothing is ever deleted.
- The Lead Pair (c_bg, c_gold) is never altered by the engine.
- SHA-256 seal computed from sorted hex values by token key.
- Inductio Chromatica runs exactly once. Flag in user config.
- The application is launched via `python3 -m AuctoritasSpectralis`
  from the `Exocognii/` parent directory with `PYTHONPATH=.`.

**Build sequence directive:**

Build the application in this order. Deliver each module as
a complete, runnable file before proceeding to the next.

1. Package skeleton — `__main__.py`, `app.py`, `config.py`,
   `assets/styles/base.qss`

2. Colour engine — `engine/colour.py` (OKLAB↔sRGB),
   `engine/jitter.py` (oklab_jitter()), `engine/harmony.py`
   (six algorithms), `engine/contrast.py` (six metrics),
   `engine/seal.py` (SHA-256 + designator), `engine/nomen.py`
   (Latin Nomen generator)

3. Registry layer — `registry/schema.py`, `registry/db.py`

4. Shell — `shell.py` (A4 four-zone QMainWindow grid)
   with Titulum, Feature Codex, Fascia, Canvas, Status Bar

5. Inductio Chromatica — `ceremony/inductio.py`

6. Feature I — `features/colores.py`
   (Compositio tab + Forgia tab with GENERATE, lock controls,
   harmonic conflict indicators)

7. Feature II — `features/scrutinium.py`
   (Parium Colorum + Contrast Matrix)

8. Feature III — `features/specularium.py`
   (four context tabs, live update on every palette change)

9. Feature IV — `features/bibliotheca.py`
   (card list + detail panel + three actions)

10. Feature V — `features/registrum.py`
    (read-only sortable SQLite table + detail panel)

11. CONFIGURATIO modal — `features/configuratio.py`

12. Export layer — `export/theme_json.py`, `export/qss.py`,
    `export/markdown.py`, `export/css.py`

13. Integration pass — wire all features into the shell,
    connect GENERATE→ Specularium live update, wire Ratificare
    pipeline end-to-end, test Inductio Chromatica flag logic

14. Launcher — `launch_auctoritasspectralis.sh`,
    `AuctoritasSpectralis.desktop`

Deliver each step as a complete installer script (Python heredoc
to `/mnt/user-data/outputs/`) before moving to the next step.
Verify import paths are correct for `python3 -m AuctoritasSpectralis`
launch from the `Exocognii/` parent directory.

The Wizard reviews each delivery before issuing `::PROCEED` to
the next step. Do not proceed without that directive.

When in doubt, refer to the wireframes. The wireframes are the
visual contract. The design plan is the behavioural contract.
The Expositio and Dux Tome are the contextual contract.
All four documents govern this build equally.

*Ordo Discordia, Cosmos Inania.*

---

*AUCTORITAS SPECTRALIS · Spectral Compliance Authority*
*IdeaForge Build Document · Bureau I of III — Triumviratus Aestheticus Imperialis*
*MMXXVI · Ordo Discordia, Cosmos Inania*
