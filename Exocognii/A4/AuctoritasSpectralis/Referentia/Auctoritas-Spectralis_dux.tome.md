```
╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║              AUCTORITAS SPECTRALIS                                    ║
║              Spectral Compliance Authority                            ║
║              Codexium Chromaticus · Sequentiae Umbrarum               ║
║                                                                       ║
║              ✦  DUX TOME  ✦                                          ║
║              Application Manual                                       ║
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
│  Document: Dux Tome                                                 │
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
│  Path            ·  Exocognii/AuctoritasSpectralis/                 │
│  Venv            ·  venv-SPECTRALIS                                 │
│  Launch          ·  python3 -m AuctoritasSpectralis                 │
│  Config Key      ·  CLAUDE_API_KEY (env var, suite-wide)            │
╰─────────────────────────────────────────────────────────────────────╯

---

## II. LAUNCH PROCEDURE

Standard Exocognii launch pattern:

```bash
cd ~/ArcaCognitorium/Exocognii
source venv-SPECTRALIS/bin/activate
PYTHONPATH=. python3 -m AuctoritasSpectralis
```

Via launcher script: `launch_auctoritasspectralis.sh`

Desktop entry: `AuctoritasSpectralis.desktop`
Icon: `auctoritasspectralis.png` → `~/.local/share/icons/`

On first launch, the Inductio Chromatica ceremony runs.
On all subsequent launches, the application opens directly to
the COLORES feature with the last active palette loaded.

---

## III. THE SHELL — ZONES AND NAVIGATION

### Zone I — Titulum (220px, full left height)

The bureau's permanent identity panel. Never scrolls.
Never changes during a session. Displays:

```
AUCTORITAS SPECTRALIS
Spectral Compliance Authority
Codexium Chromaticus · Sequentiae Umbrarum

"The apparatus adjudicates chromatic disputes
 with the gravity of a Roman senate and the
 flexibility of a sealed vault. It does not
 negotiate. It ratifies."

Active Theme:  [Designator Name]
               [sha256_truncated…]

              [ LAT | EN ]
```

The LAT/EN toggle switches the application's label register
between Latin and English. It persists across sessions via
user config. It lives in Titulum and nowhere else.

### Zone II — Feature Codex (220px, below Titulum)

Five features. Selection is instant stack swap — no animation,
no slide, no transition. The canvas changes. That is all.

```
╭──────────────────────╮
│  ✦  COLORES          │  ← palette forge
│     SCRUTINIUM       │  ← contrast audit
│     SPECULARIUM      │  ← live preview
│     BIBLIOTHECA      │  ← registry browser
│     REGISTRUM        │  ← chromatic ledger
╰──────────────────────╯
```

The active feature is marked ✦. Click any item to switch.

### Zone III — Fascia (52px, top-right)

Context-sensitive buttons belonging to the active feature.
HELP (? Auxilium) is always the rightmost element.
⚙ Config (CONFIGURATIO access) is always present, left of HELP.
All other buttons are feature-owned and change on feature switch.

### Zone IV — Canvas

The active feature's workspace. Full remaining space.
One feature renders at a time.

### Status Bar

The bottom edge of the shell. Two sections: left (status
message and dirty state marker), right (context summary).

Dirty state marker: ◌ (U+25CC)

```
  Compositio  ◌  Unsaved         ← dirty
  Compositio     Saved            ← clean
  Ratificatio    Aureus Crep...   ← ratified
```

---

## IV. FEATURE REFERENCE

### Feature I — COLORES

**The palette forge.**

Two tabs within the canvas: **Compositio** (manual token entry)
and **Forgia** (algorithm-driven generation).

**Compositio tab:**

The Wizard enters or edits the Lead Pair directly:
- c_bg (Fundus) — the background seed
- c_gold (Scriptura) — the foreground seed

All ten token rows are displayed. Each row shows:
- Token key (c_bg, c_gold, etc.)
- Swatch (live colour block)
- Hex value (editable for Lead Pair; derived for others)
- Generated Nomen (two-word Latin name, updates on generation)
- L value (OKLAB lightness, displayed for reference)
- Lock control (⊗ = locked, ○ = unlocked; Lead Pair always unlocked)
- Conflict flag (⚑ — appears when token lock creates harmonic conflict)

**Forgia tab:**

- Harmony model selector: Complementary · Analogous ·
  Monochromatic · Split-Complementary · Triadic · Tetradic
- GENERATE button — fires the harmony engine with fresh
  `oklab_jitter()` on every press
- When harmonic constraints are active, GENERATE shows:
  ```
  ┌─────────────────────────────────────────────────────┐
  │  ⚑  GENERATE PALETTE  ·  Harmonic constraints active │
  └─────────────────────────────────────────────────────┘
  ```
  Border: Aurum Dimmus instead of Aurum. Does not block generation.

**Fascia buttons (COLORES active):**

```
[ Novum ] [ Aperire ] [ Servare ] [ Servare Ut ] [ Ratificare ] [ Promulgare ] [ ⚙ Config ] [ ? Auxilium ]
```

- **Novum** — new empty palette, clears working state
- **Aperire** — load a palette from the Registry
- **Servare** — save working palette to session state (not ratified)
- **Servare Ut** — save as new draft with name prompt
- **Ratificare** — seal the palette: SHA-256 hash, Latin designator
  assigned, `theme.json` written, signal file emitted,
  Registry entry created, multi-format export executed
- **Promulgare** — export current palette to all four formats
  without ratifying (no seal, no Registry entry)

### Feature II — SCRUTINIUM

**Contrast audit workspace.**

Two panels:

**Parium Colorum** — Single pair display. Select any two tokens.
Shows headline WCAG 2.1 ratio. Five secondary metrics displayed
below: WCAG 3.0 / APCA, DeltaE 2000, Luminance Ratio, Chroma
Distance, Hue Distance. Pass/fail badges per metric.

**Contrast Matrix** — Full token grid. FG tokens as rows,
BG tokens as columns. Cell value: selected metric score.
Metric selector in Fascia. Cell hover tooltip reveals all
six metrics simultaneously.

**Fascia buttons (SCRUTINIUM active):**

```
[ Metric: WCAG ▾ ] [ Export Report ] [ ⚙ Config ] [ ? Auxilium ]
```

- **Metric selector** — switches the matrix display metric
- **Export Report** — exports full contrast report as Markdown

### Feature III — SPECULARIUM VIVUM

**Live preview.**

Four display contexts, selectable via tab strip:

- **Instrumentum** — dark instrument panel (PyQt6 widget preview)
- **Documentum** — document surface (light/dark page simulation)
- **Insignia** — badge and seal display surface
- **Token Strip** — all ten tokens displayed as labelled blocks

All ten tokens are explicitly exercised in every context.
Preview updates live on every palette change. No refresh required.

**Fascia buttons (SPECULARIUM active):**

```
[ Context: Instrumentum ▾ ] [ ⚙ Config ] [ ? Auxilium ]
```

**Scope note:** The "full application shell" context (a facsimile
of a complete application window) is planned for v1.1 of the
application build, not this build cycle.

### Feature IV — BIBLIOTHECA

**Registry browser.**

Left panel: Palette card list. Each card shows swatch strip
(all ten token colours), designator name, seal date, and
compliance badges (WCAG AA / AAA pass/fail).

Right panel (on card selection): Mini Specularium preview
(Instrumentum context), full token list with Nomina and hex
values, action buttons.

**Actions:**
- **Onerare** — load the selected palette as the working palette
  in COLORES
- **Ramificare** — fork the selected palette as a new draft in
  COLORES (base pair preserved, derivation runs fresh)
- **Comparare** — open side-by-side comparison of selected
  palette and current working palette

**Fascia buttons (BIBLIOTHECA active):**

```
[ Onerare ] [ Ramificare ] [ Comparare ] [ ⚙ Config ] [ ? Auxilium ]
```

**Future scope note:** Search and filter surface will be required
when registry exceeds approximately 30 entries. Flagged for the
next design revision cycle.

**Data model note:** Bibliotheca is built from the outset
anticipating Exvacua Loricum integration. Palette designators
and Nomina are available for lore corpus consumption.

### Feature V — REGISTRUM

**The permanent ledger.**

Full SQLite registry displayed as a sortable, filterable table.

Columns:

```
╭──────────────────────────────────────────────────────────────────────╮
│  #  │  Designator  │  Sealed  │  WCAG Min  │  APCA Min  │  AA  │  AAA  │  Seal Hash  │  Notes  │
╰──────────────────────────────────────────────────────────────────────╯
```

Row click opens a detail panel. Detail shows: full token hex
values with swatches, all six contrast metrics, export list,
record metadata.

**Constraints:**
- Read only. Not editable. Not deletable.
- The Chromatic Registry is an archive. It does not forget.

**Fascia buttons (REGISTRUM active):**

```
[ Export Registry ] [ ⚙ Config ] [ ? Auxilium ]
```

- **Export Registry** — exports the full registry as a Markdown
  document or CSV (format selectable on invoke)

---

## V. CONFIGURATIO MODAL

Accessed via ⚙ Config in the Fascia. Available regardless of
active feature. Opens as a modal overlay on the canvas.
Closed by Escape or the ✕ Discede button.

Settings contained:

```
╭─────────────────────────────────────────────────────────────────────╮
│  Default Harmony          │  [Complementary ▾]                      │
│  Default Contrast Algo    │  [WCAG-Forced ▾]                        │
│  Export Directory         │  [~/ArcaCognitorium/…/exports]          │
│  Mundana State Bus        │  [Not connected (interim)]              │
│  Signal File Path         │  [~/.arca/signals/theme_updated]        │
│  Specularium Default      │  [Instrumentum ▾]                       │
╰─────────────────────────────────────────────────────────────────────╯
```

Buttons: **Servare** (save) · **Reset Defaults** · **✕ Discede** (close)

---

## VI. THE COLOUR ENGINE — OPERATOR REFERENCE

### Token Hierarchy

```
╭──────────────┬────────────────────────────────────────────────────╮
│  Token       │  Role                                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  c_bg        │  Fundus — background seed. Lead Pair. Wizard input.│
│  c_gold      │  Scriptura — foreground seed. Lead Pair. Wizard.   │
│  c_panel     │  Surface panel background. Tight jitter.           │
│  c_subtle    │  Recessed panel. Tight jitter.                     │
│  c_gold_dark │  Dark accent band. Tight jitter.                   │
│  c_gold_dim  │  Muted foreground / secondary text. Med jitter.    │
│  c_text      │  Primary readable text. Medium jitter.             │
│  c_white     │  Near-white highlight. Tight jitter.               │
│  c_crimson   │  Sanguis — error / warning accent. Wide jitter.    │
│  c_teal      │  Viridis — success / info accent. Wide jitter.     │
╰──────────────┴────────────────────────────────────────────────────╯
```

### Jitter Envelope

```
╭──────────────────────┬─────────┬─────────┬─────────╮
│  Token               │  L ±    │  C ±    │  H ±    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┤
│  c_bg / c_gold       │  —      │  —      │  —      │
│  (Lead Pair)         │         │         │         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┤
│  c_panel             │  0.02   │  0.01   │  4.0    │
│  c_subtle            │  0.02   │  0.01   │  4.0    │
│  c_gold_dark         │  0.02   │  0.01   │  4.0    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┤
│  c_gold_dim          │  0.04   │  0.02   │  8.0    │
│  c_text              │  0.03   │  0.015  │  6.0    │
│  c_white             │  0.02   │  0.01   │  4.0    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┤
│  c_crimson           │  0.04   │  0.03   │  12.0   │
│  c_teal              │  0.04   │  0.03   │  12.0   │
╰──────────────────────┴─────────┴─────────┴─────────╯
```

### Harmonic Conflict

A conflict is declared when any locked derived token's hue angle
deviates from the active harmony model's expected hue family by
more than 30° in OKLAB space. On conflict:

- ⚑ flag appears beside the offending token row in COLORES
- GENERATE button enters warning state (Aurum Dimmus border)
- Status bar displays conflict message naming the offending tokens

Generation is not blocked. The apparatus informs; it does not prevent.

To resolve: unlock the flagged token or change the harmony model.

---

## VII. RATIFICATION PROCEDURE

1. Build or load a palette in COLORES
2. Verify contrast scores in SCRUTINIUM (optional but advisable)
3. Preview in SPECULARIUM across all four contexts
4. Press **Ratificare** in the Fascia

On Ratificare:

1. SHA-256 hash computed from canonical token set (hex values,
   sorted by token key, concatenated)
2. Two-word Latin designator assigned (perceptually derived from
   the palette's dominant L and H values)
3. `theme.json` written to configured export directory and to
   `~/.arca/theme.json` (suite-wide contract location)
4. Signal file written: `~/.arca/signals/theme_updated`
   (timestamp + designator, plain text, overwritten on every seal)
5. Chromatic Registry entry created in SQLite
6. Multi-format export: `.json`, `.qss`, `.md`, `.css`
7. Status bar: `Ratificatio  Aureus Crepuscularis  ·  3f9a2c1d…`

The seal is permanent. The Registry entry cannot be deleted.
The designator cannot be changed after ratification.

---

## VIII. FILE SYSTEM LAYOUT

```
~/ArcaCognitorium/
  Exocognii/
    AuctoritasSpectralis/       ← application package
      __main__.py
      app.py
      shell.py                  ← A4 zone layout
      features/
        colores.py
        scrutinium.py
        specularium.py
        bibliotheca.py
        registrum.py
        configuratio.py
      engine/
        colour.py               ← OKLAB/LCH ops
        harmony.py              ← six harmony algorithms
        jitter.py               ← oklab_jitter()
        contrast.py             ← six contrast metrics
        seal.py                 ← SHA-256 + designator
        nomen.py                ← Latin Nomen generator
      registry/
        db.py                   ← SQLite interface
        schema.py
      export/
        theme_json.py
        qss.py
        markdown.py
        css.py
      ceremony/
        inductio.py             ← Inductio Chromatica
      config.py                 ← reads ~/.arca/config.json
      assets/
        styles/
          base.qss
    venv-SPECTRALIS/

~/.arca/
  config.json                   ← suite-wide config
  theme.json                    ← inter-app contract (sole writer: Bureau I)
  signals/
    theme_updated               ← interim broadcast signal
  token_log.jsonl               ← suite-wide token ledger

~/ArcaCognitorium/
  Exocognii/
    AuctoritasSpectralis/
      data/
        chromatic_registry.db   ← SQLite Registry
```

---

## IX. DOWNSTREAM CONSUMER PROTOCOL

Applications consuming `theme.json` from the Cogniverse:

**On launch:** Read `~/.arca/theme.json`. Parse token map.
Apply QSS generated from token values.

**Interim watch (until Mundana State Bus):** Poll
`~/.arca/signals/theme_updated` every 2000ms. On
modification detection, reload `theme.json` and reapply QSS.

**On Mundana State Bus availability:** Subscribe to
`mundana.resolver` channel. Handle palette events. No
changes to the consumer's read logic are required.

Current consumers: PRAESIDIUM, GNOSIUM EXANIMA, Bureau II,
Bureau III.

---

## X. GLOSSARY

```
╭──────────────────────────┬────────────────────────────────────────────────╮
│  Term                    │  Definition                                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Lead Pair               │  c_bg + c_gold. The Wizard's input. Sacrosanct│
│  Fundus                  │  c_bg — the background seed                    │
│  Scriptura               │  c_gold — the foreground seed                  │
│  oklab_jitter()          │  Bounded random perturbation in LCH space      │
│  Harmonic conflict       │  Locked token >30° from harmony family         │
│  Nomen                   │  Two-word Latin name per derived token         │
│  Designator              │  Two-word Latin name for a whole palette       │
│  Seal                    │  SHA-256 hash of the canonical token set       │
│  Ratification            │  The act of sealing and writing to registry    │
│  Chromatic Registry      │  SQLite archive of all ratified palettes       │
│  theme.json              │  Inter-app colour contract. Bureau I sole      │
│                          │  writer. Lives at ~/.arca/theme.json           │
│  Inductio Chromatica     │  First-launch ceremony. Runs once only.        │
│  ◌                       │  Dirty state marker (U+25CC). Unsaved changes  │
│  Mundana State Bus       │  Future event bus. mundana.resolver channel    │
│  Interim signal file     │  ~/.arca/signals/theme_updated                 │
│  CONFIGURATIO            │  Settings modal. Not a feature.                │
╰──────────────────────────┴────────────────────────────────────────────────╯
```

---

*AUCTORITAS SPECTRALIS · Spectral Compliance Authority*
*Dux Tome · Bureau I of III — Triumviratus Aestheticus Imperialis*
*MMXXVI · Ordo Discordia, Cosmos Inania*
