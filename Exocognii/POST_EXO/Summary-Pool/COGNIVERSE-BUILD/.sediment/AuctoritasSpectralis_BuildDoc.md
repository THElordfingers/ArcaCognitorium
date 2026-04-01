# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ       AuctoritasSpectralis_BuildDoc.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# CODEXIUM CHROMATICUS — Sequentiae Umbrarum
## Bureau I · The Spectral Compliance Authority · Auctoritas Spectralis
### Developer-Ready Build Document · v1.0

> **Parent Alliance:** Aesthetic Authoritarian Associative Alliance (A4)
> *Triumviratus Aestheticus Imperialis*
>
> **Bureau Seal:** *Auctoritas Spectralis*
> **Mandate:** Every palette issued by this bureau is law.

---

## Table of Contents

1.  Overview & Architecture
2.  Tech Stack
3.  Directory Tree & Database Schema
4.  Module Breakdown
5.  UI Wireframe
6.  Data Flow
7.  Code Stubs
8.  Error Handling
9.  Setup & Testing
10. Packaging
11. Extensibility

---

## 1. Overview & Architecture

Codexium Chromaticus is a PyQt6 desktop application that composes,
audits, ratifies, and exports authoritative color theme packages for
the entire Tower jurisdiction. The Wizard constructs a palette by
setting a background/foreground base pair via hex input or OKLAB
coordinate sliders. The system continuously derives the full
chromatic token hierarchy from that pair, runs real-time perceptual
contrast auditing across all token combinations, and reskins its own
interface live as the Wizard works. When satisfied, the Wizard
ratifies the palette — it receives a SHA-256 seal, a Latin
designator (system-suggested, Wizard-ratified), and enters the
Chromatic Registry. Ratified themes export as `theme.json` (the
Tower canonical contract), `.qss` (Qt stylesheet), and `.md`
(human-readable palette card).

It is Bureau I of the A4. Its output (`theme.json`) is a dependency
for Bureau II (Agentia Architecturalis) and Bureau III
(Departamentum Documentalis). Neither downstream bureau can operate
at full authority without a ratified theme from this bureau.

### Architecture Stages

╭──────────────┬──────────────────────────────────────────────────╮
│ Stage        │ Role                                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Compositio   │ BG/FG hex + OKLAB slider input; derives full    │
│              │ token hierarchy in real-time from the base pair  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Scrutinium   │ Real-time WCAG 2.1 + APCA contrast matrix       │
│              │ across all token pairs; vision simulation        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Auto-Render  │ QSS regenerated on every change, applied via    │
│              │ setStyleSheet(); 150ms debounce                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Ratificatio  │ SHA-256 seal + Latin designator + Registry      │
│              │ entry; Wizard approval required                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Promulgatio  │ Export theme.json + .qss + .md palette card;    │
│              │ Tower broadcast stub present                    │
╰──────────────┴──────────────────────────────────────────────────╯

### Keyboard Shortcuts

╭──────────────┬──────────────────────────────────────────────────╮
│ Binding      │ Action                                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ q            │ Exire — quit application                        │
│ Ctrl+R       │ Ratificare — ratify current palette             │
│ Ctrl+E       │ Promulgare — export ratified palette            │
│ Ctrl+S       │ Sigillare — save working state                  │
│ Ctrl+Z       │ Revocare — undo last base pair change           │
│ Ctrl+Shift+Z │ Restituere — redo                               │
│ Ctrl+G       │ Registrum — toggle Registry drawer              │
│ Ctrl+V       │ Visio — cycle vision simulation overlays        │
│ Ctrl+1       │ Focus Compositio panel                          │
│ Ctrl+2       │ Focus Scrutinium panel                          │
│ Ctrl+3       │ Focus preview panel                             │
│ F1           │ Auxilium — help                                  │
╰──────────────┴──────────────────────────────────────────────────╯

---

## 2. Tech Stack

╭───────────────────────┬───────────┬──────────────────────────────╮
│ Tool                  │ Version   │ Justification                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Python                │ 3.11+     │ Suite standard               │
│ PyQt6                 │ 6.6+      │ ModusArcanus framework       │
│ colour-science        │ 0.4.4+    │ OKLAB/APCA perceptual math   │
│ numpy                 │ (transi-  │ Required by colour-science   │
│                       │  tive)    │                              │
│ sqlite3               │ stdlib    │ Chromatic Registry storage    │
│ hashlib               │ stdlib    │ SHA-256 seal generation       │
│ json                  │ stdlib    │ theme.json serialization      │
│ pathlib               │ stdlib    │ Path resolution              │
╰───────────────────────┴───────────┴──────────────────────────────╯

No ClaudeBox. No AI integration. No network dependency. Fully
offline standalone.

---

## 3. Directory Tree & Database Schema

### File Tree

```
~/ArcaCognitorium/Exocognii/
└── AestheticAuthoritarianAssociativeAlliance/
    └── AuctoritasSpectralis/
        ├── __init__.py
        ├── __main__.py                 # Entry point
        ├── app.py                      # QApplication setup + main window
        ├── compositio.py               # Forge panel: hex input + OKLAB sliders
        ├── scrutinium.py               # Contrast matrix engine + vision sim
        ├── auto_render.py              # QSS generation + debounced application
        ├── ratificatio.py              # Seal generation + designator suggestion
        ├── promulgatio.py              # Export engine: theme.json, .qss, .md
        ├── registry.py                 # SQLite operations for Chromatic Registry
        ├── derivatio.py                # OKLAB token derivation pipeline
        ├── designator_gen.py           # Latin designator suggestion engine
        ├── schema.py                   # TypedDict definitions + theme.json contract
        ├── constants.py                # ModusArcanus defaults + color constants
        ├── workers.py                  # QRunnable + WorkerSignals for IO ops
        ├── widgets/
        │   ├── __init__.py
        │   ├── forge_panel.py          # Compositio UI assembly
        │   ├── contrast_grid.py        # Scrutinium matrix widget
        │   ├── preview_panel.py        # Self-rendering preview widgets
        │   ├── registry_drawer.py      # Collapsible bottom drawer
        │   ├── sequence_viewer.py      # Luminance ladder + OKLAB projection
        │   ├── vision_overlay.py       # Deuteranopia/protanopia/achroma sim
        │   └── hex_input.py            # Validated hex color input widget
        ├── storage/
        │   └── chromatic_registry.db   # SQLite (created on first run)
        ├── exports/                    # Ratified theme exports land here
        │   ├── theme.json
        │   ├── theme.qss
        │   └── theme.md
        └── tests/
            ├── test_derivatio.py
            ├── test_scrutinium.py
            ├── test_ratificatio.py
            ├── test_registry.py
            ├── test_promulgatio.py
            └── test_integration.py
```

### Database Schema — Chromatic Registry

```sql
CREATE TABLE IF NOT EXISTS chromatic_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    designator      TEXT    NOT NULL,
    seal_hash       TEXT    NOT NULL UNIQUE,
    created_at      TEXT    NOT NULL,  -- ISO 8601
    c_bg            TEXT    NOT NULL,
    c_panel         TEXT    NOT NULL,
    c_gold          TEXT    NOT NULL,
    c_gold_dim      TEXT    NOT NULL,
    c_gold_dark     TEXT    NOT NULL,
    c_crimson       TEXT    NOT NULL,
    c_teal          TEXT    NOT NULL,
    c_text          TEXT    NOT NULL,
    c_subtle        TEXT    NOT NULL,
    c_white         TEXT    NOT NULL,
    oklab_bg_l      REAL    NOT NULL,
    oklab_bg_a      REAL    NOT NULL,
    oklab_bg_b      REAL    NOT NULL,
    oklab_fg_l      REAL    NOT NULL,
    oklab_fg_a      REAL    NOT NULL,
    oklab_fg_b      REAL    NOT NULL,
    wcag_min_ratio  REAL    NOT NULL,  -- lowest pair ratio in the set
    apca_min_lc     REAL    NOT NULL,  -- lowest APCA Lc value in the set
    passes_aa       INTEGER NOT NULL DEFAULT 0,  -- 1 = all pairs pass AA
    passes_aaa      INTEGER NOT NULL DEFAULT 0,  -- 1 = all pairs pass AAA
    notes           TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS seal_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_id     INTEGER NOT NULL REFERENCES chromatic_registry(id),
    seal_hash       TEXT    NOT NULL,
    sealed_at       TEXT    NOT NULL,  -- ISO 8601
    canonical_json  TEXT    NOT NULL   -- the exact JSON that was hashed
);

CREATE TABLE IF NOT EXISTS export_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_id     INTEGER NOT NULL REFERENCES chromatic_registry(id),
    format          TEXT    NOT NULL,  -- 'theme.json' | 'qss' | 'md'
    export_path     TEXT    NOT NULL,
    exported_at     TEXT    NOT NULL,  -- ISO 8601
    success         INTEGER NOT NULL DEFAULT 1
);
```

---

## 4. Module Breakdown

╭────────────────────┬─────────────┬──────────────────────────┬──────────────────────┬──────────────────────┬──────────────────╮
│ Module             │ Stage       │ Responsibility           │ Inputs               │ Outputs              │ Dependencies     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py             │ —           │ QApplication init,       │ sys.argv             │ Running window       │ all modules      │
│                    │             │ main window assembly     │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ compositio.py      │ Compositio  │ Parse hex input, emit    │ Hex string or        │ (bg_hex, fg_hex)     │ colour-science   │
│                    │             │ OKLAB coords, handle     │ OKLAB slider values   │ tuple + OKLAB        │                  │
│                    │             │ slider↔hex sync          │                      │ coordinates          │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ derivatio.py       │ Compositio  │ OKLAB derivation         │ (bg_hex, fg_hex)     │ TokenDict: all 10    │ colour-science   │
│                    │             │ pipeline: compute full   │                      │ token hex values     │                  │
│                    │             │ token hierarchy from     │                      │ + OKLAB coords       │                  │
│                    │             │ base pair                │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ scrutinium.py      │ Scrutinium  │ WCAG 2.1 + APCA          │ TokenDict            │ ContrastMatrix:      │ colour-science   │
│                    │             │ contrast computation     │                      │ per-pair ratios,     │                  │
│                    │             │ for all token pairs;     │                      │ APCA Lc, pass/fail   │                  │
│                    │             │ vision sim transforms    │                      │ + SimulatedTokens    │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ auto_render.py     │ Auto-Render │ Generate QSS from        │ TokenDict            │ Complete QSS string; │ constants        │
│                    │             │ tokens; debounce at      │                      │ applied to QApp      │                  │
│                    │             │ 150ms; apply via         │                      │                      │                  │
│                    │             │ setStyleSheet()          │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ratificatio.py     │ Ratificatio │ Generate SHA-256 seal    │ TokenDict +          │ SealRecord: hash,    │ hashlib, json    │
│                    │             │ from canonical token     │ designator string    │ timestamp,           │ designator_gen   │
│                    │             │ JSON; store in registry  │                      │ designator           │ registry         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ promulgatio.py     │ Promulgatio │ Export ratified palette   │ SealRecord +         │ Files: theme.json,   │ schema, workers  │
│                    │             │ to theme.json, .qss,     │ TokenDict            │ theme.qss, theme.md  │                  │
│                    │             │ and .md palette card     │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ registry.py        │ —           │ SQLite CRUD for          │ SQL operations       │ Query results,       │ sqlite3          │
│                    │             │ chromatic_registry,      │                      │ row objects          │                  │
│                    │             │ seal_log, export_log     │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ designator_gen.py  │ Ratificatio │ Generate Latin compound  │ TokenDict (hue/      │ Suggested designator │ —                │
│                    │             │ name suggestion from     │ lightness analysis)  │ string               │                  │
│                    │             │ palette characteristics  │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ schema.py          │ —           │ TypedDict definitions    │ —                    │ ThemePackage,        │ —                │
│                    │             │ for theme.json contract  │                      │ TokenDict types      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ constants.py       │ —           │ ModusArcanus defaults,   │ —                    │ Default hex values,  │ —                │
│                    │             │ token names, font stack  │                      │ font constants       │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ workers.py         │ —           │ QRunnable + signals      │ Callable tasks       │ Signals: finished,   │ PyQt6            │
│                    │             │ for background IO        │                      │ error, result        │                  │
╰────────────────────┴─────────────┴──────────────────────────┴──────────────────────┴──────────────────────┴──────────────────╯

---

## 5. UI Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  ☰  ✦  CODEXIUM CHROMATICUS  ✦           Auctoritas Spectralis    [Visio] [?] ║
╠════════════════════╦═══════════════════════════════╦═════════════════════════════╣
║  COMPOSITIO        ║  SCRUTINIUM                   ║  SPECULARIUM VIVUM          ║
║                    ║                               ║                             ║
║  ┌──────────────┐  ║  Contrast Matrix              ║  ┌─────────────────────┐   ║
║  │ FUNDUS       │  ║  ╭─────┬─────┬─────┬─────╮   ║  │  Section Header     │   ║
║  │ #050507   [◈]│  ║  │     │ BG  │ PNL │ TXT │   ║  │  ✦  Titulus  ✦     │   ║
║  │ L ═══○══════ │  ║  ├─────┼─────┼─────┼─────┤   ║  │                     │   ║
║  │ a ═══○══════ │  ║  │ GLD │ 8.2 │ 7.1 │ 3.4 │   ║  │  Body text in the   │   ║
║  │ b ═══○══════ │  ║  │ GDM │ 4.1 │ 3.5 │ 1.8 │   ║  │  parchment tone     │   ║
║  └──────────────┘  ║  │ CRM │ 3.2 │ 2.8 │ 2.1 │   ║  │  renders here as    │   ║
║                    ║  │ TEL │ 3.0 │ 2.6 │ 2.0 │   ║  │  a live preview.    │   ║
║  ┌──────────────┐  ║  │ TXT │ 9.1 │ 7.8 │ --- │   ║  │                     │   ║
║  │ SCRIPTURA    │  ║  │ WHT │11.2 │ 9.6 │ 1.3 │   ║  │  [⚗ Manifest]       │   ║
║  │ #c8b88a   [◈]│  ║  ╰─────┴─────┴─────┴─────╯   ║  │  [🜲 Sigillare]     │   ║
║  │ L ═══○══════ │  ║                               ║  │  [✕ Dissolvere]     │   ║
║  │ a ═══○══════ │  ║  WCAG AA: ✦ PASS   AAA: ⌬    ║  │                     │   ║
║  │ b ═══○══════ │  ║  APCA Lc min: 62.4            ║  ├─────────────────────┤   ║
║  └──────────────┘  ║                               ║  │  ◈ Slider  ═══○═══ │   ║
║                    ║  ┌───────────────────────────┐ ║  │  ComboBox ▼         │   ║
║  CHROMATA DERIVATA ║  │ Vision Sim: [OFF]         │ ║  │  Input: __________ │   ║
║  ┌──────────────┐  ║  │ [Deuter] [Protan] [Achro]│ ║  │                     │   ║
║  │ ██ C_BG      │  ║  └───────────────────────────┘ ║  │  Status: The        │   ║
║  │ ██ C_PANEL   │  ║                               ║  │  apparatus awaits.  │   ║
║  │ ██ C_GOLD    │  ║  SEQUENTIA LUMINIS            ║  └─────────────────────┘   ║
║  │ ██ C_GOLD_DIM│  ║  ┌───────────────────────────┐ ║                             ║
║  │ ██ C_GOLD_DK │  ║  │ Luminance ladder:         │ ║                             ║
║  │ ██ C_CRIMSON │  ║  │ ▁▂▃▄▅▆▇ (10 tokens)      │ ║                             ║
║  │ ██ C_TEAL    │  ║  │ Min ΔL: 0.12              │ ║                             ║
║  │ ██ C_TEXT    │  ║  └───────────────────────────┘ ║                             ║
║  │ ██ C_SUBTLE  │  ║                               ║                             ║
║  │ ██ C_WHITE   │  ║                               ║                             ║
║  └──────────────┘  ║                               ║                             ║
╠════════════════════╩═══════════════════════════════╩═════════════════════════════╣
║  REGISTRUM CHROMATICUM                                                     [▲] ║
║  ╭──────┬───────────────────────┬──────────┬────────┬────────┬───────────────╮  ║
║  │  #   │ Designator            │ Sealed   │ AA     │ AAA    │ Actions       │  ║
║  ├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤  ║
║  │  1   │ Umbra Profunda        │ MMXXVI   │ ✦      │ ✦      │ [Load] [Exp]  │  ║
║  │  2   │ Aurum Vespertinum     │ MMXXVI   │ ✦      │ ⌬      │ [Load] [Exp]  │  ║
║  ╰──────┴───────────────────────┴──────────┴────────┴────────┴───────────────╯  ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║  ⚙ The Spectral Authority awaits.                         Compositio · Unsaved  ║
╚════════════════════════════════════════════════════════════════════════════════════╝
```

### Wireframe Legend

╭─────────────────────┬────────────────────────────────────────────────╮
│ Element             │ Description                                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TopBar              │ QFrame, 52px. Hamburger toggle, app title,     │
│                     │ vision sim toggle, help button.                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ COMPOSITIO (left)   │ Two input groups — FUNDUS (background) and     │
│                     │ SCRIPTURA (foreground). Each: hex QLineEdit    │
│                     │ with color swatch button [◈] + three OKLAB     │
│                     │ sliders (L, a, b). Below: CHROMATA DERIVATA    │
│                     │ — vertical swatch list of all 10 derived       │
│                     │ tokens with their hex values.                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ SCRUTINIUM (centre) │ Contrast matrix: NxN grid of all token pairs.  │
│                     │ Each cell shows WCAG ratio. Green = pass AA,   │
│                     │ gold = pass AA not AAA, red = fail. Below      │
│                     │ matrix: summary line (AA pass/fail, AAA        │
│                     │ pass/fail, APCA Lc minimum). Vision sim        │
│                     │ toggle buttons. SEQUENTIA LUMINIS: luminance   │
│                     │ ladder bar graph of all tokens.                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ SPECULARIUM VIVUM   │ Self-rendering preview. A miniature arcane UI  │
│ (right)             │ using real ModusArcanus widget patterns —       │
│                     │ section header, body text, buttons (manifest,  │
│                     │ seal, discard), slider, combobox, input, and   │
│                     │ status bar — all rendered in the live palette.  │
│                     │ This is where the Wizard sees the theme on     │
│                     │ real widget anatomy, not abstract swatches.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ REGISTRUM (bottom)  │ Collapsible drawer (Ctrl+G toggle). Shows all  │
│                     │ ratified palettes from the SQLite registry.    │
│                     │ Columns: id, designator, sealed date, AA       │
│                     │ pass, AAA pass, action buttons (load into      │
│                     │ Compositio, export). Collapsed by default.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ StatusBar           │ QFrame, 28px. Left: declarative status message │
│                     │ (archaic register). Right: current stage +     │
│                     │ save state indicator.                          │
╰─────────────────────┴────────────────────────────────────────────────╯

---

## 6. Data Flow

### Path (a) — Happy path: compose → derive → audit → ratify → export

```
1. Wizard adjusts BG hex or OKLAB slider
2. compositio.py emits palette_changed signal with (bg_hex, fg_hex)
3. derivatio.py receives base pair, converts to OKLAB via colour-science
4. derivatio.py computes full token hierarchy:
   a. C_BG      = bg_hex (identity)
   b. C_PANEL   = bg + L*1.15, shift a/b toward neutral
   c. C_GOLD    = fg_hex (identity — foreground IS the gold)
   d. C_GOLD_DIM= fg at L*0.55, desaturate chroma by 30%
   e. C_GOLD_DARK= fg at L*0.28, desaturate chroma by 50%
   f. C_TEXT    = fg at L*0.78, shift toward warm neutral
   g. C_SUBTLE  = bg at L*1.6, shift toward warm neutral
   h. C_WHITE   = fg at L*0.92, near-desaturated
   i. C_CRIMSON = hue-rotated to ~25° (red), L*0.35, C*0.12
   j. C_TEAL    = hue-rotated to ~195° (teal), L*0.35, C*0.08
5. derivatio.py emits tokens_derived signal with TokenDict
6. scrutinium.py receives TokenDict, computes:
   a. WCAG 2.1 relative luminance ratio for every foreground/background pair
   b. APCA Lc value for every pair
   c. Mark each pair: AA pass (≥4.5:1), AAA pass (≥7:1)
   d. Apply current vision sim if active (CVD matrix transform)
7. scrutinium.py emits audit_complete signal with ContrastMatrix
8. auto_render.py receives TokenDict (debounced 150ms via QTimer):
   a. Generates complete QSS string from token values
   b. Calls QApplication.instance().setStyleSheet(qss)
   c. Preview panel and entire window reskin immediately
9. Wizard reviews preview + contrast matrix
10. Wizard presses Ctrl+R (Ratificare):
    a. ratificatio.py generates suggested designator via designator_gen.py
    b. Ratification dialog appears with pre-filled designator field
    c. Wizard keeps or edits designator, confirms
    d. Canonical token JSON serialized (sorted keys, no whitespace)
    e. SHA-256 computed over: canonical_json + ISO_timestamp + designator
    f. Entry written to chromatic_registry + seal_log (via worker thread)
11. Wizard presses Ctrl+E (Promulgare):
    a. promulgatio.py reads selected registry entry
    b. Exports theme.json (Tower canonical format)
    c. Exports .qss (complete Qt stylesheet)
    d. Exports .md (palette card with swatches described)
    e. export_log entry written
    f. Status bar: "✦  Theme promulgated: {designator}"
```

### Path (b) — Ratification blocked: WCAG AA failure

```
1. Steps 1–7 as above
2. ContrastMatrix reports one or more pairs below AA (4.5:1)
3. Scrutinium panel highlights failing cells in C_CRIMSON
4. Wizard presses Ctrl+R
5. ratificatio.py queries current ContrastMatrix
6. Ratification refused — dialog appears:
   "⌬  Ratificatio Denegata"
   "The following token pairs fail WCAG AA minimum contrast:"
   - C_GOLD_DIM on C_PANEL: 3.5:1 (requires 4.5:1)
   - C_TEAL on C_BG: 2.8:1 (requires 4.5:1)
   "Adjust the base pair or accept reduced compliance."
7. Dialog offers: [Revise] returns to Compositio, [Override] ratifies
   with passes_aa=0 flag and a note in the registry
8. No seal issued unless Wizard explicitly overrides
```

### Path (c) — Export failure: disk write error

```
1. Wizard selects a ratified palette and presses Ctrl+E
2. promulgatio.py runs on worker thread
3. Worker attempts to write theme.json to exports/ directory
4. Disk write fails (permissions, disk full, path not found)
5. Worker emits error signal with exception details
6. promulgatio.py catches error, does NOT mark export in export_log
7. Status bar: "✕  Promulgation failed: {error_description}"
8. Error dialog: "✕  Inscriptio Defecta — the seal could not be
   committed to disk. Verify write permissions on the exports
   directory." + full path shown
9. Registry entry remains valid — no data corrupted
10. Wizard resolves filesystem issue, retries Ctrl+E
```

---

## 7. Code Stubs

### schema.py — The Tower Contract

```python
"""Tower canonical theme.json schema — the inter-app contract."""

from typing import TypedDict


class TokenSet(TypedDict):
    """The ten canonical color tokens."""
    c_bg: str        # Hex. Void — primary background.
    c_panel: str     # Hex. Obsidian — panels, cards, dialogs.
    c_gold: str      # Hex. Aurum — primary accent.
    c_gold_dim: str  # Hex. Aurum Dimmus — hints, subtitles.
    c_gold_dark: str # Hex. Aurum Nox — borders, separator lines.
    c_crimson: str   # Hex. Sanguis — destructive, warnings.
    c_teal: str      # Hex. Viridis — confirmations, saves.
    c_text: str      # Hex. Parchment — body text.
    c_subtle: str    # Hex. Umbra — inactive borders.
    c_white: str     # Hex. Vellum — emphasis text.


class OklabCoords(TypedDict):
    """OKLAB coordinates for a single color."""
    l: float  # Lightness [0.0, 1.0]
    a: float  # Green-red axis [-0.4, 0.4]
    b: float  # Blue-yellow axis [-0.4, 0.4]


class BasePair(TypedDict):
    """The two input colors from which all tokens are derived."""
    bg_hex: str
    bg_oklab: OklabCoords
    fg_hex: str
    fg_oklab: OklabCoords


class ContrastEntry(TypedDict):
    """Contrast metrics for a single foreground/background pair."""
    fg_token: str
    bg_token: str
    wcag_ratio: float
    apca_lc: float
    passes_aa: bool   # wcag_ratio >= 4.5
    passes_aaa: bool  # wcag_ratio >= 7.0


class SealRecord(TypedDict):
    """Immutable ratification seal."""
    seal_hash: str      # SHA-256 hex digest
    sealed_at: str      # ISO 8601 timestamp
    designator: str     # Wizard-ratified Latin designator
    canonical_json: str # The exact JSON string that was hashed


class ThemePackage(TypedDict):
    """The complete theme.json — Tower canonical format.

    This is the inter-app contract. Every Tower application that
    consumes a theme reads this schema. Do not add fields without
    updating all downstream consumers.
    """
    schema_version: str   # "1.0"
    bureau: str           # "auctoritas_spectralis"
    alliance: str         # "a4"
    designator: str       # Wizard-ratified name
    seal_hash: str        # SHA-256 of canonical token JSON
    sealed_at: str        # ISO 8601
    base_pair: BasePair
    tokens: TokenSet
    oklab_tokens: dict[str, OklabCoords]  # token_name -> OKLAB coords
    contrast_summary: dict  # min_wcag_ratio, min_apca_lc, passes_aa, passes_aaa
    font_stack: str       # "Georgia, Constantia, serif"
    font_stack_mono: str  # "excalib-nf, Courier New, monospace"
```

### derivatio.py — OKLAB Derivation Pipeline

```python
"""Token derivation from base pair via OKLAB perceptual space."""

import colour
import numpy as np


def hex_to_oklab(hex_color: str) -> tuple[float, float, float]:
    """Convert #RRGGBB hex to OKLAB (L, a, b) coordinates."""
    # hex -> sRGB [0,1] -> CIE XYZ -> OKLAB
    ...


def oklab_to_hex(l: float, a: float, b: float) -> str:
    """Convert OKLAB (L, a, b) back to #RRGGBB hex, clamped to sRGB gamut."""
    # OKLAB -> CIE XYZ -> sRGB [0,1] -> clamp [0,1] -> hex
    ...


def derive_tokens(bg_hex: str, fg_hex: str) -> dict:
    """Compute the full 10-token hierarchy from a BG/FG base pair.

    Pipeline (all operations in OKLAB space):
    1. Parse BG and FG to OKLAB coordinates
    2. C_BG      = BG (identity)
    3. C_PANEL   = BG lightness * 1.15, chroma shifted toward neutral
    4. C_GOLD    = FG (identity — the foreground IS the accent)
    5. C_GOLD_DIM= FG lightness * 0.55, chroma desaturated 30%
    6. C_GOLD_DARK= FG lightness * 0.28, chroma desaturated 50%
    7. C_TEXT    = FG lightness * 0.78, hue shifted toward warm neutral
    8. C_SUBTLE  = BG lightness * 1.6, shifted toward warm neutral
    9. C_WHITE   = FG lightness * 0.92, near-full desaturation
    10. C_CRIMSON = hue rotated to ~25°, L=0.35, C=0.12
    11. C_TEAL    = hue rotated to ~195°, L=0.35, C=0.08
    12. All results clamped to sRGB gamut
    13. Return TokenSet dict with hex values + OklabCoords per token
    """
    ...


def _scale_lightness(l: float, a: float, b: float,
                     factor: float) -> tuple[float, float, float]:
    """Multiply OKLAB lightness by factor, clamp to [0, 1]."""
    ...


def _desaturate(l: float, a: float, b: float,
                amount: float) -> tuple[float, float, float]:
    """Reduce chroma (distance from neutral axis) by proportion [0, 1]."""
    ...


def _rotate_hue(l: float, a: float, b: float,
                target_degrees: float) -> tuple[float, float, float]:
    """Rotate hue in OKLAB a/b plane to target angle."""
    ...


def _shift_toward_neutral(l: float, a: float, b: float,
                          warmth: float = 0.02) -> tuple[float, float, float]:
    """Move color toward warm neutral axis, retaining lightness."""
    ...
```

### scrutinium.py — Contrast Engine

```python
"""WCAG 2.1 and APCA contrast computation engine."""

import colour
import numpy as np


def compute_wcag_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG 2.1 relative luminance contrast ratio.

    Formula: (L_lighter + 0.05) / (L_darker + 0.05)
    where L = relative luminance per WCAG 2.1 §1.4.3.
    """
    ...


def compute_apca_lc(fg_hex: str, bg_hex: str) -> float:
    """APCA Lightness Contrast (Lc) value.

    Uses the APCA-W3 algorithm (Somers 2022). Returns signed Lc.
    Positive = light text on dark bg. Negative = dark text on light bg.
    """
    ...


def build_contrast_matrix(tokens: dict) -> list[dict]:
    """Compute contrast for all meaningful foreground/background pairs.

    Not all pairs are meaningful — C_CRIMSON on C_TEAL is not a
    realistic combination. The matrix covers:
    - Every text/accent token (GOLD, GOLD_DIM, TEXT, WHITE, CRIMSON, TEAL)
      against every background token (BG, PANEL, SUBTLE, GOLD_DARK)
    """
    ...


def simulate_cvd(hex_color: str,
                 deficiency: str) -> str:
    """Simulate color vision deficiency on a single hex color.

    deficiency: 'deuteranopia' | 'protanopia' | 'achromatopsia'
    Uses Viénot/Brettel simulation matrices via colour-science.
    """
    ...


def audit_passes(matrix: list[dict]) -> dict:
    """Summarize pass/fail across the full matrix.

    Returns: {
        'passes_aa': bool,    # all pairs >= 4.5:1
        'passes_aaa': bool,   # all pairs >= 7.0:1
        'min_wcag_ratio': float,
        'min_apca_lc': float,
        'failing_pairs': list[dict]  # pairs below AA
    }
    """
    ...
```

### ratificatio.py — Seal Generation

```python
"""Palette ratification and seal generation."""

import hashlib
import json
from datetime import datetime, timezone


def generate_seal(tokens: dict, designator: str) -> dict:
    """Generate a SHA-256 ratification seal.

    The seal covers:
    1. Canonical JSON of the token set (sorted keys, no whitespace)
    2. ISO 8601 timestamp (UTC)
    3. The designator string

    These three are concatenated and hashed. The canonical JSON is
    stored alongside the hash so the seal is independently verifiable.
    """
    canonical = json.dumps(tokens, sort_keys=True, separators=(',', ':'))
    timestamp = datetime.now(timezone.utc).isoformat()
    seal_input = f"{canonical}|{timestamp}|{designator}"
    seal_hash = hashlib.sha256(seal_input.encode('utf-8')).hexdigest()
    return {
        'seal_hash': seal_hash,
        'sealed_at': timestamp,
        'designator': designator,
        'canonical_json': canonical,
    }
```

### auto_render.py — QSS Generation

```python
"""Live QSS generation and debounced application."""

from PyQt6.QtCore import QTimer


class AutoRenderer:
    """Generates and applies QSS from a TokenDict on every change."""

    def __init__(self, app):
        self._app = app
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._apply)
        self._pending_tokens = None

    def schedule(self, tokens: dict) -> None:
        """Queue a re-render. Debounced at 150ms."""
        self._pending_tokens = tokens
        self._timer.start()

    def _apply(self) -> None:
        """Generate and apply QSS."""
        if self._pending_tokens is None:
            return
        qss = generate_qss(self._pending_tokens)
        self._app.setStyleSheet(qss)

    @staticmethod
    def generate_qss(tokens: dict) -> str:
        """Produce complete QSS string from token dict.

        Covers: QMainWindow, QWidget, QPushButton, QLabel,
        QLineEdit, QSlider, QComboBox, QFrame, QScrollBar,
        QTableView, QHeaderView, QToolTip — all per ModusArcanus
        widget patterns with token values substituted.
        """
        t = tokens
        return f"""
        QMainWindow, QWidget {{
            background-color: {t['c_bg']};
            color: {t['c_text']};
            font-family: Georgia, Constantia, serif;
        }}
        QPushButton {{
            background: {t['c_panel']};
            color: {t['c_gold']};
            border: 1px solid {t['c_gold_dark']};
            font-family: Georgia, serif;
            font-size: 11px;
            padding: 6px 14px;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background: {t['c_gold_dark']};
            border-color: {t['c_gold']};
        }}
        QPushButton:pressed {{
            background: {t['c_subtle']};
        }}
        QLabel {{
            color: {t['c_text']};
            font-family: Georgia, serif;
        }}
        QLineEdit {{
            background: {t['c_bg']};
            color: {t['c_text']};
            border: 1px solid {t['c_subtle']};
            padding: 6px;
            font-family: Georgia, serif;
            font-size: 11px;
        }}
        QLineEdit:focus {{
            border-color: {t['c_gold']};
            color: {t['c_white']};
        }}
        QSlider::groove:horizontal {{
            background: {t['c_subtle']};
            height: 4px;
        }}
        QSlider::handle:horizontal {{
            background: {t['c_gold']};
            width: 12px; height: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }}
        QSlider::sub-page:horizontal {{
            background: {t['c_gold_dim']};
        }}
        QComboBox {{
            background: {t['c_bg']};
            color: {t['c_gold']};
            border: 1px solid {t['c_gold_dark']};
        }}
        QScrollBar:vertical {{
            background: {t['c_panel']};
            width: 8px; border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {t['c_gold_dark']};
            border-radius: 4px; min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QToolTip {{
            background: {t['c_panel']};
            color: {t['c_gold']};
            border: 1px solid {t['c_gold_dark']};
            font-family: Georgia, serif;
            padding: 4px;
        }}
        QTableView {{
            background: {t['c_bg']};
            color: {t['c_text']};
            gridline-color: {t['c_subtle']};
        }}
        QHeaderView::section {{
            background: {t['c_panel']};
            color: {t['c_gold']};
            font-weight: bold;
            border: 1px solid {t['c_gold_dark']};
            padding: 4px;
        }}
        """
```

### designator_gen.py — Latin Compound Suggestion

```python
"""Generate a Latin compound designator from palette characteristics."""

import math

# Hue families mapped to Latin color words
HUE_VOCABULARY = {
    (0, 30):    ["Rubeus", "Sanguinis", "Igneus", "Ferreus"],
    (30, 60):   ["Aureus", "Croceus", "Melleus", "Sulphureus"],
    (60, 90):   ["Viridans", "Chartaceus", "Herbaceus"],
    (90, 150):  ["Viridis", "Smaragdinus", "Prasinus"],
    (150, 210): ["Caeruleus", "Thalassinus", "Glaucus"],
    (210, 270): ["Caeruleus", "Lazulinus", "Sapphirinus"],
    (270, 330): ["Purpureus", "Violaceus", "Amethystinus"],
    (330, 360): ["Roseus", "Rhodinus", "Rubicundus"],
}

# Lightness modifiers
LIGHTNESS_VOCABULARY = {
    (0.0, 0.15): ["Profundus", "Abyssalis", "Noctis"],
    (0.15, 0.30): ["Obscurus", "Umbralis", "Crepuscularis"],
    (0.30, 0.50): ["Mediocris", "Temperatus", "Aequalis"],
    (0.50, 0.70): ["Lucidus", "Clarus", "Matutinus"],
    (0.70, 1.0):  ["Candidus", "Vespertinus", "Luminaris"],
}


def suggest_designator(tokens: dict) -> str:
    """Suggest a two-word Latin designator based on dominant hue + lightness.

    Analyses the FG (gold/accent) color to determine hue family,
    and the BG lightness to determine the modifier. Returns a
    compound like "Aureus Profundus" or "Viridis Crepuscularis".
    """
    ...
```

### workers.py — Background IO

```python
"""QRunnable workers for non-blocking IO operations."""

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal


class WorkerSignals(QObject):
    """Signals emitted by background workers."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)


class IoWorker(QRunnable):
    """Execute a callable on the thread pool."""

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        """Execute the callable; emit result or error."""
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
```

### constants.py — ModusArcanus Defaults

```python
"""ModusArcanus canonical defaults and token names."""

# Default palette — the canonical ModusArcanus dark theme
MODUS_ARCANUS_DEFAULTS = {
    'c_bg':        '#050507',
    'c_panel':     '#0a0a12',
    'c_gold':      '#d4af37',
    'c_gold_dim':  '#7a6a2a',
    'c_gold_dark': '#3a2e10',
    'c_crimson':   '#8b1a1a',
    'c_teal':      '#1a5a5a',
    'c_text':      '#c8b88a',
    'c_subtle':    '#3a3528',
    'c_white':     '#e8e0cc',
}

TOKEN_NAMES = [
    'c_bg', 'c_panel', 'c_gold', 'c_gold_dim', 'c_gold_dark',
    'c_crimson', 'c_teal', 'c_text', 'c_subtle', 'c_white',
]

TOKEN_LABELS = {
    'c_bg':        'Void',
    'c_panel':     'Obsidian',
    'c_gold':      'Aurum',
    'c_gold_dim':  'Aurum Dimmus',
    'c_gold_dark': 'Aurum Nox',
    'c_crimson':   'Sanguis',
    'c_teal':      'Viridis',
    'c_text':      'Parchment',
    'c_subtle':    'Umbra',
    'c_white':     'Vellum',
}

FONT_STACK = 'Georgia, Constantia, serif'
FONT_STACK_MONO = 'excalib-nf, Courier New, monospace'

APP_TITLE = '✦  CODEXIUM CHROMATICUS  ✦'
APP_SUBTITLE = 'Sequentiae Umbrarum'
BUREAU_FULL = 'The Spectral Compliance Authority'
BUREAU_LATIN = 'Auctoritas Spectralis'
```

---

## 8. Error Handling

╭─────────────────────┬──────────────────────────┬─────────────────────────────────╮
│ Module              │ Error                    │ Strategy                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py              │ colour-science import    │ Show error dialog at startup:   │
│                     │ failure                  │ "colour-science not found.      │
│                     │                          │ pip install colour-science."    │
│                     │                          │ App exits with code 1.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py              │ PyQt6 import failure     │ Print to stderr and exit.       │
│                     │                          │ Cannot show GUI without Qt.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ registry.py         │ DB file cannot be        │ Attempt to create storage/      │
│                     │ created or opened        │ directory. If fails: show       │
│                     │                          │ error dialog with full path.    │
│                     │                          │ App continues with registry     │
│                     │                          │ disabled (Wizard can still      │
│                     │                          │ compose and preview but not     │
│                     │                          │ ratify).                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ derivatio.py        │ OKLAB computation        │ Clamp all intermediate values   │
│                     │ returns NaN or Inf       │ to valid ranges. If clamping    │
│                     │                          │ produces a degenerate result    │
│                     │                          │ (all tokens identical), emit    │
│                     │                          │ warning signal. Swatch list     │
│                     │                          │ shows "⌬  Derivation anomaly"  │
│                     │                          │ and ratification is blocked.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ derivatio.py        │ Gamut clipping: derived  │ Clamp sRGB to [0, 1] per       │
│                     │ color falls outside sRGB │ channel. Mark clipped tokens    │
│                     │                          │ with a visual indicator in the  │
│                     │                          │ swatch list (⌬ icon).          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ auto_render.py      │ QSS application causes   │ Wrap setStyleSheet in          │
│                     │ Qt paint error           │ try/except. On failure: revert  │
│                     │                          │ to MODUS_ARCANUS_DEFAULTS QSS. │
│                     │                          │ Status: "⌬  Render fallback." │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ promulgatio.py      │ theme.json validation    │ Validate exported dict against  │
│                     │ fails against TypedDict  │ ThemePackage keys before write. │
│                     │                          │ Missing/extra keys: abort       │
│                     │                          │ export, show specific error.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ promulgatio.py      │ Disk write failure       │ Worker emits error signal.      │
│                     │ (permissions, full disk) │ No export_log entry written.    │
│                     │                          │ Error dialog with path + errno. │
│                     │                          │ Registry entry unaffected.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ compositio.py       │ Invalid hex input        │ QLineEdit validator rejects     │
│                     │                          │ non-hex chars. If paste         │
│                     │                          │ produces invalid value: revert  │
│                     │                          │ to previous valid hex. Border   │
│                     │                          │ flashes C_CRIMSON briefly.      │
╰─────────────────────┴──────────────────────────┴─────────────────────────────────╯

---

## 9. Setup & Testing

### requirements.txt

```
PyQt6>=6.6.0
colour-science>=0.4.4
numpy>=1.24.0
```

### Install & Run

```bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/AuctoritasSpectralis

# Create venv (first time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python -m AuctoritasSpectralis
# or:
python __main__.py
```

### Unit Tests (one per core module)

**test_derivatio.py** — Given the ModusArcanus default BG/FG pair,
assert that all 10 tokens are valid hex strings, all OKLAB L values
fall within [0, 1], and no two adjacent tokens in the luminance
ladder have identical lightness.

**test_scrutinium.py** — Given the ModusArcanus defaults, assert
that C_GOLD on C_BG passes WCAG AA (ratio >= 4.5), that
C_GOLD_DIM on C_PANEL has a ratio > 1.0, and that CVD simulation
of C_CRIMSON under deuteranopia returns a valid hex string distinct
from the input.

**test_ratificatio.py** — Generate a seal from a fixed token dict
and designator. Assert the seal_hash is a 64-char hex string, the
timestamp parses as valid ISO 8601, and regenerating with the same
inputs produces a different hash (timestamp differs).

**test_registry.py** — Create an in-memory SQLite database, insert
a registry entry, read it back, assert all fields match. Insert a
duplicate seal_hash and assert IntegrityError is raised.

**test_promulgatio.py** — Export a ratified palette to a temp
directory. Assert theme.json is valid JSON, contains all
ThemePackage keys, and the seal_hash field matches the registry
entry. Assert .qss file is non-empty and contains the C_BG hex
value. Assert .md file contains the designator string.

### Integration Test

**test_integration.py** — End-to-end critical path:

```
1. Set BG = "#050507", FG = "#d4af37" (ModusArcanus defaults)
2. Call derive_tokens() → assert 10 tokens returned
3. Call build_contrast_matrix() → assert passes_aa is True
4. Call generate_seal() with designator "Aureus Profundus"
5. Insert into in-memory registry → assert row count is 1
6. Read back → assert designator matches
7. Export to temp dir → assert theme.json exists
8. Load theme.json → validate against ThemePackage schema
9. Assert theme.json seal_hash matches registry seal_hash
```

---

## 10. Packaging

### Desktop File

```ini
[Desktop Entry]
Name=Codexium Chromaticus
Comment=The Spectral Compliance Authority — color theme governance
Exec=bash -c "cd $HOME/ArcaCognitorium && python -m Exocognii.AestheticAuthoritarianAssociativeAlliance.AuctoritasSpectralis"
Icon=codexium-chromaticus
Terminal=false
Type=Application
Categories=Development;Graphics;
Keywords=color;theme;palette;arcane;
StartupWMClass=codexium-chromaticus
```

Place at: `~/.local/share/applications/CodexiumChromaticus.desktop`

Icon at: `~/.local/share/icons/codexium-chromaticus.png`

Launch script at:
`~/ArcaCognitorium/launch_codexium_chromaticus.sh`

```bash
#!/bin/bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/AuctoritasSpectralis
source .venv/bin/activate
python -m AuctoritasSpectralis
```

### PyInstaller Command

```bash
pyinstaller \
    --name "CodexiumChromaticus" \
    --onefile \
    --windowed \
    --add-data "storage:storage" \
    --hidden-import colour \
    --hidden-import numpy \
    __main__.py
```

### Runtime Path Resolution

```python
from pathlib import Path

def get_app_root() -> Path:
    """Resolve application root for both dev and packaged modes."""
    return Path(__file__).resolve().parent

def get_storage_path() -> Path:
    """Resolve storage directory, creating if needed."""
    storage = get_app_root() / 'storage'
    storage.mkdir(exist_ok=True)
    return storage

def get_exports_path() -> Path:
    """Resolve exports directory, creating if needed."""
    exports = get_app_root() / 'exports'
    exports.mkdir(exist_ok=True)
    return exports
```

---

## 11. Extensibility

╭───────────────────────────┬──────────────────────────────┬──────────────────────────────────╮
│ Feature                   │ User Value                   │ Implementation Approach           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Tower Broadcast           │ Ratified theme pushes live   │ ZMQ PUB socket on ratification   │
│                           │ to all running Tower tools   │ event. Subscribers bind to a      │
│                           │ without restart              │ well-known port. Payload:         │
│                           │                              │ theme.json bytes. v1 stubs the    │
│                           │                              │ socket without binding.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Import Mode               │ Ingest an existing .qss or   │ Parse QSS/CSS into key-value     │
│                           │ CSS-variable file and        │ pairs. Reverse-map to nearest    │
│                           │ reverse-derive token         │ TokenSet via OKLAB proximity.     │
│                           │ structure into Compositio    │ Load into sliders for            │
│                           │                              │ refinement.                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ AI Palette Oracle         │ Prompt a Council entity      │ ClaudeBox call with lore prompt. │
│                           │ with a lore description;     │ Response parsed for two hex      │
│                           │ receive a proposed base      │ values. Loaded into Compositio   │
│                           │ pair and rationale           │ as starting point.               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Delta-E Lock              │ Configurable minimum         │ Compute OKLAB Delta-E (CIEDE2000 │
│                           │ perceptual distance between  │ or Euclidean in OKLAB) between   │
│                           │ all token pairs; blocks      │ every token pair. If any pair    │
│                           │ ratification if not met      │ falls below threshold:           │
│                           │                              │ ratification blocked with        │
│                           │                              │ specific pair report.            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Palette Lineage           │ Visual diff between two      │ Side-by-side registry entries    │
│                           │ registered themes; show      │ with per-token OKLAB delta       │
│                           │ which tokens changed and     │ displayed as arrows in an OKLAB  │
│                           │ by how much in OKLAB space   │ projection plot.                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Chromatic Covenant        │ One-click commit of ratified │ Git subprocess: stage            │
│                           │ theme.json to the Arca       │ theme.json, commit with          │
│                           │ Cognitorium repository       │ standardized message             │
│                           │                              │ "[CHROM] {designator}", push     │
│                           │                              │ to origin/main.                  │
╰───────────────────────────┴──────────────────────────────┴──────────────────────────────────╯

---

## Appendix: Suite Manifest Entry

```json
{
    "id": "auctoritas_spectralis",
    "name": "Codexium Chromaticus",
    "bureau": "Auctoritas Spectralis",
    "alliance": "A4",
    "path": "Exocognii/AestheticAuthoritarianAssociativeAlliance/AuctoritasSpectralis",
    "entry": "__main__.py",
    "version": "1.0.0",
    "status": "development"
}
```

---

*⟁*

*Ordo Discordia, Cosmos Inania*

*IdeaForge · Bureau I · Auctoritas Spectralis · ＭＭＸＸＶＩ*
