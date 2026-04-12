# EXOCOGNII — STATUS & SUMMARY
## *Arca Cognitorium · Issued by The Builder · MMXXVI*

---

# I. WHAT THE EXOCOGNII IS

The Exocognii is the constellation of companion tools built around and in
service of the Tower. It is not a suite of independent utilities — it is an
ecosystem with designed interdependencies, a shared aesthetic register, shared
infrastructure, and a shared purpose: to make the construction, operation, and
inhabitation of the Tower possible without the Wizard maintaining the machinery
manually.

The Exocognii comprises three categories of tool:

**Infrastructure Services** — background FastAPI services that run continuously
and provide memory, continuity, and build tracking to all other tools.
The Cognosis suite.

**Governance Bureaus** — the A4 Triumviratus: the authorities on color, UI
composition, and document production. Everything visible is subject to their
jurisdiction.

**Operational Tools** — the Wizard-facing instruments: Praesidium, Dolium,
Vigilarum, Lexiferium, Incitamentum, Entitex, Mythotex, and the Tower itself.
Each has a defined function. None is redundant with another.

The collective name for the memory infrastructure layer is **Cognosis**.
The shared Involucrum client library that all apps use to emit to Cognosis
services is **Nuntius**.

---

# II. THE PARTS — WHAT THEY ARE

---

## PRAESIDIUM

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Ambient PyQt6 desktop dashboard · secondary monitor      │
│  Status          ·  Active · v1.4 · Phases 1–3 complete                      │
│  Port            ·  8733 (advisory read surface for Cognosis services)       │
╰──────────────────────────────────────────────────────────────────────────────╯

The ambient command centre. Runs on the secondary monitor as a persistent
free-floating widget canvas. Everything in the suite either feeds into it or can
be surfaced through it. It is the Wizard's peripheral vision — always there, never
demanding.

**What it does:** Git workflow (commit/push/pull/fetch with live streaming output),
Claude chat via ClaudeBox, cross-app token tracking, TodoBoard, App Launcher, Style
Reference, Status Legend, DisplayPanel, DiffViewer, RepoActivity, QuickFileDrop,
ReferentiaAggregator, ArtWidget, GlyphBrowser.

**Deferred:** Multiple canvases, INGENIUM widget pipeline, Cognosis FastAPI read
integration (Exvacua Loricum lore surface, Perpetuum Aedificare build node surface),
Control Panel widget (reads live status from all services — built last, after
everything is wired).

---

## COGNOSIS SUITE

The three-service memory organism. Two producers, one reader.

---

### Exvacua Loricum

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Local FastAPI lore canon memory service                  │
│  Status          ·  Active · v1.0 · Session A complete                       │
│  Port            ·  8731                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯

The lore accumulator. Watches all app emissions, classifies lore-relevant content
via Actio Interpretus (Claude-powered), and presents Judicium ratification
ceremonies to the Wizard. Nothing becomes canon without explicit Wizard
ratification. The Sacramentum Finalitus writes to the Lore Corpus.

**What it does:** Involucrum ingestion, file drop, Lorixii Extractuum corpus
scour, Actio Interpretus scheduled classification (10 min / 20-item threshold),
five-phase Judicium ceremony, Loridex Card production, Exloricum prose
production, Loretic Crystalizer (compendium synthesis), Arx Loricuum taxonomy,
Actio Revisicus revision flagging, full REST API.

**Deferred:** Judicium UI (Session B), `.wiz` rendered output via Actio Duxuum,
Nuntius wiring to all existing apps.

---

### Perpetuum Aedificare

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Local FastAPI build continuity memory service            │
│  Status          ·  Active · v1.0 · Core service complete                    │
│  Port            ·  8732                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯

The build continuity prosthetic. Tracks the shape and momentum of all active work
via Nodus Momentuum nodes and Exnodica relationship graph. Apps emit, Claude maps
captures to nodes via Actio Aggrexuum, the Driftuum Sentifex flags stale work.

**What it does:** Four capture pathways (Indicatum Machina, Nota Brevis, Oratio
Extracticum, file drop), Actio Aggrexuum aggregation (5 min / 10-item threshold),
Nodus Momentuum CRUD, Exnodica relationship graph, Arca Absoluticum Tower
references, Driftuum Sentifex drift detection (threshold 0.65), full REST API.

**Deferred:** Praesidium read layer, Nuntius wiring to all existing apps.

---

### Praesidium — Cognosis Read Layer

The query and advisory interface above both services. Read-only. Never in the
write path. The Wizard queries lore and build state through here; advisory drift
signals surface here. The Praesidium Control Panel widget is the UI face of this
layer — built last, after all services are wired and confirmed healthy.

---

## NUNTIUS

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Shared Involucrum client library                         │
│  Status          ·  Named and specified · Not yet built                      │
│  Path            ·  Exocognii/Shared/                                        │
╰──────────────────────────────────────────────────────────────────────────────╯

The Involucrum dispatcher. Imported by every Exocognii app. Fires one POST to
Exvacua Loricum and one to Perpetuum Aedificare simultaneously, fire-and-forget.
No app needs to know either service exists. Nuntius is the only dependency.

---

## LORE CORPUS

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Shared read layer and file system substrate              │
│  Status          ·  Active · v1.0 · Inert pending Exvacua Loricum writes     │
│  Path            ·  Shared/Lore/                                             │
╰──────────────────────────────────────────────────────────────────────────────╯

The published output of the Exvacua Loricum ratification pipeline. Any component
in the suite reads ratified lore from here without knowing how it was made.
`lore_corpus.py` reader and `LoreBookScreen` Textual widget serve the Tower.
Not a service — a structured directory with a reader in front of it.

---

## DOLIUM v2

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  PyQt6 ideation pipeline · four-chamber instrument        │
│  Status          ·  Complete · v2.0 · 74 tests passing                       │
╰──────────────────────────────────────────────────────────────────────────────╯

The idea fermentation vessel. Raw concepts enter the Fomentary, pass through the
Cultivation House and Vestibule under increasing pressure, and exit the Codex as
declared intentions. An ambient whisper system — the entity observes and speaks
unprompted after 1500 ms of typing inactivity. Whisper and conversation share one
ClaudeBox session per idea; unified context.

**Deferred:** Praesidium pipeline feed, shared knowledge center injection, token
budget management, theme resolution from central aesthetic pipeline.

---

## A4 TRIUMVIRATUS AESTHETICUS IMPERIALIS

Three bureaus. One authority over everything visible in the Cogniverse.

---

### Bureau I — Auctoritas Spectralis (Codexium Chromaticus)

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  PyQt6 color theme governance tool                        │
│  Status          ·  Complete · v1.0 · 26/26 tests passing                    │
│  Path            ·  AestheticAuthoritarianAssociativeAlliance/               │
│                     AuctoritasSpectralis/                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

The sole authority on color. Composes palettes in OKLAB perceptual space, audits
WCAG 2.1 + APCA contrast, simulates CVD, ratifies with SHA-256 seal and Latin
designator. Sole writer of `theme.json` — the inter-app color contract.

**Deferred:** Font enforcement in `.wiz` emitter (Georgia fallback everywhere;
Ebon Sigil, Varnyx, VL Gothic, Runavess not yet enforced).

---

### Bureau II — Agentia Architecturalis

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  PyQt6 visual UI component designer                       │
│  Status          ·  Complete · v1.0 · 21/21 tests passing                    │
│  Path            ·  AestheticAuthoritarianAssociativeAlliance/               │
│                     AgentiaArchitecturalis/                                  │
╰──────────────────────────────────────────────────────────────────────────────╯

Replaces the Fenestrarium. Visual canvas for composing PyQt6 UI panels. QGraphicsScene
canvas, 28 element types, live preview, SQLite Component Library, Python/PyQt6 code
generation with token constants, `ast.parse()` validation. Consumes `theme.json`.

**Deferred:** Armarium GUI drawer (library browsing surface not yet built).

---

### Bureau III — Departamentum Documentalis

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  PyQt6 document composition tool with CLI backend         │
│  Status          ·  Complete · v1.0 · 28/28 tests passing                    │
│  Path            ·  Exocognii/A4/                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

The document authority. `.bureau` pipe-tag markup format, paired `.wiz` + `.md`
output from single source, five built-in templates, GUI editor with live preview,
SQLite document library. GUI chrome from Bureau I `theme.json`; document content
uses fixed wizdoc palette.

**Deferred:** Armarium GUI drawer, font enforcement audit.

**Path note:** Bureau I and II live at the full
`AestheticAuthoritarianAssociativeAlliance/` path. Bureau III lives at
`Exocognii/A4/`. Unification needed in a dedicated session.

---

## VIGILARUM v2

╭──────────────────────────────────────────────────────────────────────────────╮
│  Classification  ·  Standalone PyQt6 celestial instrument                    │
│  Status          ·  Complete · v2 migration · 38 widget types                │
╰──────────────────────────────────────────────────────────────────────────────╯

The sky made legible. Multi-window, multi-widget astronomical display. 38 widget
types rendered via QPainter — moon disc, zodiac wheel, nakshatra ring, tithi dial,
eclipse gauge, planet strip, moon arc, and more. Standalone. No Tower coupling.

**Open item:** Sunrise fixed at 06:00. Location-aware `swe.rise_trans()` deferred.

---

## CELESTIAL CHAIN

### CAELESTIS

The seventh Machina. Built. Planetary positions, aspects, dignities, Vimshottari
dasha, composite astrological potency signal. Writes to `~/.arca/caelestis.json`.
Follows full machinae interface pattern (`update()`, `triggers.poll()`, `to_json()`,
`write()`, `summary()`).

### Mundana State Bus

Built. Aggregates all seven Machinae. Two output tracks: cosmetic/UI and entity
behavioural influence. CLI: `--lat / --lon / --utc`. Defaults to Victoria BC.

### Celestial Resolver

Built. Per-entity CelestialContext injection. Reads State Bus and per-entity
`celestial.yaml`. PyYAML soft dependency with fallback. Output: named influence
keys (float –1.0 to 1.0): `cognitive_clarity`, `emotional_intensity`,
`creative_volatility`, `institutional_gravity`, etc.

### celestial.yaml × 10

Drafted for all ten Council entities. `deploy_celestial_yamls.py` installs to
`storage/entities/{id}/celestial.yaml`. All values tunable.

**Not yet wired:** Resolver is built but not yet injecting into entity system
prompt assembly. Entity behavioural influence is the remaining wire.

---

## WHAT DOES NOT EXIST YET

╭────────────────────────────────────────┬──────────────────────────────────────────╮
│  Nuntius                               │  Named, specified, not built             │
│  Cognosis read layer                   │  Praesidium read surface not wired       │
│  Exvacua Loricum Session B             │  Judicium UI + .wiz output pending       │
│  A4 path unification                   │  Bureau I/II vs III path mismatch        │
│  Unified venv                          │  Each tool runs its own — flagged        │
│  Control Panel widget                  │  Reads all services — built last         │
│  Tower UI (PyQt6)                      │  Migration decision not yet made/closed  │
│  Resolver → entity prompt injection    │  Final wire of celestial chain           │
│  Lore Engine write side + Scribae      │  Awaits Exvacua Session B                │
│  Lexiferium                            │  Concept only — not built                │
│  Mythotex                              │  Concept only — not built                │
│  Gnosium                               │  Cognosis advisory chat UI               │
╰────────────────────────────────────────┴──────────────────────────────────────────╯

---

# III. HOW IT WIRES TOGETHER

---

## The Write Path

```
App event occurs
  → App constructs Involucrum { source_app, version, timestamp, hint, body }
  → Nuntius fires POST to Exvacua Loricum (port 8731)   ← fire-and-forget
  → Nuntius fires POST to Perpetuum Aedificare (port 8732) ← fire-and-forget
  → App continues without waiting
```

The services receive independently. One being down does not affect the other.
No routing dependency between them. Praesidium is permanently outside the write path.

## The Color Path

```
Bureau I ratifies a palette
  → Writes theme.json to canonical location
  → All apps reload theme.json on next launch (or live if hot-reload is wired)
  → Aesthetic register propagates across the suite without touching app code
```

## The Lore Path

```
App emits Involucrum
  → Exvacua Loricum Lorixii Speculativum accumulates
  → Actio Interpretus classifies (10 min / 20-item threshold)
  → Judicium session opens for a topic cluster
  → Wizard ratifies through five phases
  → Sacramentum Finalitus fires
  → Loridex Card + Exloricum written to Shared/Lore/corpus/
  → register.yaml appended
  → Loretic Crystalizer updates Loricum Ratifex
  → Tower entities read entries via lore_corpus.py
```

## The Build Memory Path

```
App emits Involucrum
  → Perpetuum Aedificare Acquiuum Chronex accumulates
  → Actio Aggrexuum fires (5 min / 10-item threshold)
  → Claude maps captures to Nodus Momentuum or creates new node
  → Nodifex updated, open questions refined
  → Driftuum Metrica scored on all active nodes
  → Driftuum Attentio fired (once) when threshold crossed
  → Wizard reads current work state via Praesidium
```

## The Config Spine

All ports, paths, intervals, and thresholds live in `~/.arca/config.json`
(Configuus). No service port, no path, no threshold should live anywhere else.
Environment variables remain valid overrides. Config is the canonical source.

---

# IV. WHAT EXISTS AND WHAT NEEDS BUILDING

╭────────────────────────────────────────┬────────────────┬──────────────────────────────────────╮
│  Component                             │  Status        │  Notes                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯
│  PRAESIDIUM v1.4                       │  ✦ Active      │  Phase 4 + Control Panel pending     │
│  Exvacua Loricum v1.0                  │  ✦ Active      │  Session B (Judicium UI) pending     │
│  Perpetuum Aedificare v1.0             │  ✦ Active      │  Read layer pending                  │
│  Lore Corpus v1.0                      │  ✦ Ready       │  Inert — awaiting Exvacua writes     │
│  Nuntius                               │  ⏳ Pending    │  Named, not built                    │
│  Dolium v2                             │  ✦ Complete    │  74 tests passing                    │
│  Bureau I — Auctoritas Spectralis      │  ✦ Complete    │  26/26 tests                         │
│  Bureau II — Agentia Architecturalis   │  ✦ Complete    │  21/21 tests                         │
│  Bureau III — Departamentum Documentalis│  ✦ Complete   │  28/28 tests                         │
│  Vigilarum v2                          │  ✦ Complete    │  38 widget types                     │
│  CAELESTIS                             │  ✦ Built       │  Awaiting entity prompt wiring       │
│  Mundana State Bus                     │  ✦ Built       │  All 7 Machinae unified              │
│  Celestial Resolver                    │  ✦ Built       │  celestial.yaml × 10 deployed        │
│  Celestial → entity injection          │  ⏳ Pending    │  Final wire                          │
│  Incitamentum                          │  ✦ Operational │  Path confirmed                      │
│  Entitex                               │  ✦ Operational │  Entity package generator            │
│  Lexiferium                            │  ⏳ Not built  │  Concept only                        │
│  Mythotex                              │  ⏳ Not built  │  Concept only                        │
│  Gnosium                               │  ⏳ Not built  │  Cognosis advisory chat UI           │
│  A4 path unification                   │  ⏳ Pending    │  Bureau I/II vs III path mismatch    │
│  Unified venv                          │  ⏳ Pending    │  Flagged — dedicated session needed  │
│  Configuus (complete)                  │  ⏳ Pending    │  Needs named section per service     │
│  Tower — PyQt6 migration               │  ⏳ Decision   │  Not yet made and closed             │
│  Tower — Machinae → entity wiring      │  ⏳ Pending    │  Resolver built, not injecting       │
│  Scribae + Lore Engine write side      │  ⏳ Not built  │  Tower build, dedicated session      │
╰────────────────────────────────────────┴────────────────┴──────────────────────────────────────╯

---

# V. ORDERED BUILD SEQUENCE

```
PHASE I — COHESION RESPEC
─────────────────────────────────────────────────────────────────────────
 1.  Production audit — all apps, live files, debt logged          [TODO]
 2.  Configuus — named section for every service, complete         [TODO]
 3.  Nuntius — shared Involucrum client library built              [TODO]
 4.  Nuntius wired — all existing apps emit via Nuntius            [TODO]
 5.  A4 path unification — Bureau I/II vs Bureau III               [TODO]
 6.  Exvacua Loricum Session B — Judicium UI + .wiz rendering      [TODO]
 7.  Perpetuum Aedificare read layer — Praesidium wired            [TODO]
 8.  Control Panel widget — reads all services, built last         [TODO]
 9.  Token ledger — cross-app aggregation verified                 [TODO]
10.  All documents current — Expositio and Dux Tome per app        [TODO]
11.  Unified venv architecture — dedicated session                 [TODO]

PHASE II — TOWER REENTRY
─────────────────────────────────────────────────────────────────────────
12.  Tower State Map audit — Gospel vs reality                     [TODO]
13.  Migration decision — PyQt6 vs Textual, made and closed        [TODO]
14.  Resolver → entity behavioural influence wired                 [TODO]
15.  Lore Corpus write side — Scribae integration                  [TODO]
16.  Fragment Protocol — verified operational                      [TODO]
17.  Tower UI — phased migration if migration chosen               [TODO]
18.  Mercurial Convocation — implemented                           [TODO]
19.  Emergence mechanics — full audit and completion               [TODO]

PHASE III — THE LIVING TOWER
─────────────────────────────────────────────────────────────────────────
20.  EGO MANIFESTUS — full implementation                          [TODO]
21.  NEXUS ARCHIVUM — Library, books, emergence seeding            [TODO]
22.  WiseCracken — theory to implementation                        [TODO]
23.  Detritus pipeline — designed                                  [TODO]
24.  Aedificatorum — Builder interface within the Tower            [TODO]
25.  Sigil embedding — cosmetic layer wired to emergence           [TODO]
─────────────────────────────────────────────────────────────────────────
The Tower opens when it is ready, not when it is finished.
─────────────────────────────────────────────────────────────────────────
```

---

*Exocognii — Status & Summary · Issued by The Builder · MMXXVI*
*Arca Cognitorium · Ordo Discordia, Cosmos Inania*

*⟁*
