╭──────────────────────────╮
│                        │
│ ＯＰＥＲＡＴＩＯＮＡＬ │
│󰟾  ＣＯＮＴＩＮＵＩＴＹ  󰟾│
│    ＲＥＧＩＳＴＥＲ    │
│                        │
╰──────────────────────────╯
### *State Assessment & Ordered Build Continuation*
*v2 — Interview answers incorporated: 2026-03-26*

---

## I. CONFIRMED STATE (post-interview)

**Praesidium** — running. Chat streams. Truncation unconfirmed (no long messages tested yet).
**Vigilarum** — not run recently. swisseph error unresolved. **Flagged for PyQt6 migration.**
**Mythotex-FP** — working well. Freepik is the canonical path going forward. sd.cpp retired.
**ENTITEX** — functional, producing portraits. Prompting tweaks needed (spiritual/tower alignment). Not daily use yet.
**Dolium v1** — abandoned. Token consumption unacceptable. **Go straight to v2 build.**
**Transitorius** — untouched since build. Lives at `~/ArcaCognitorium/Transitorius/`. Tower UI migration is post-Exocognii.
**Tower (Textual)** — still running. UI upgrade deferred until Exocognii is wrapped.
**Socratic** — dormant. No interruptions observed.
**Pairz** — standalone app, not in ArcaCognitorium repo. Review not done yet. Token-intensive — deferred.
**Memory services (Exvacua Loricum, Perpetuum Aedificare)** — complete non-starts. No files. Schema v0.4 is the only artefact.
**Two pending names (memory schema v0.4)** — still open.
**.bureau.json schema** — needs full dedicated pass. Nothing written beyond theory discussion.

---

## II. FULL INVENTORY

---

### EXOCOGNII INFRASTRUCTURE

| Item | State |
|---|---|
| `suite.manifest.json` | BUILT |
| `suite.py` loader | BUILT |
| `~/.arca/config.json` | BUILT |
| `Shared/` directory structure | BUILT |
| ClaudeBox canonicalisation | BUILT |
| GitHub repo — public, `main` branch | BUILT |
| `gen_init_urls.sh` + `init_urls.txt` | BUILT (project file copy is stale — fetch live from repo) |
| `push.sh` | BUILT |

---

### EXOCOGNII APPLICATIONS

| App | State | Action |
|---|---|---|
| **PRAESIDIUM** | BUILT — running | Watch for ChatWidget truncation on long responses |
| **VIGILARUM** | BUILT — broken (swisseph) | Migrate to PyQt6 — dedicated session |
| **LEXIFERIUM** | BUILT | No known issues |
| **MYTHOTEX-FP** | BUILT — working | Prompting tweaks (user-driven, not a build task) |
| **ENTITEX** | BUILT — working | Prompting tweaks + celestial.yaml integration (see Tier 2) |
| **OCULUS PRIME** | BUILT | No known issues |
| **INCITAMENTUM** | BUILT | Confirm path: `Exocognii/Incitamentum/` vs `tools/Incitamentum/` |
| **FENESTRIUM** | BUILT | Textual retirement decision still open |
| **DOLIUM v2** | DOC ONLY | IdeaForge build doc exists — build from scratch |
| **Codexium Chromaticus** | THEORY ONLY | Blocked on Pairz review |
| **AAEAgency** | THEORY ONLY | Blocked on theme.json |
| **The Bureau** | THEORY ONLY | Blocked on both schemas |
| **Exvacua Loricum** | DOC ONLY (schema v0.4) | No files at all |
| **Perpetuum Aedificare** | DOC ONLY (schema v0.4) | No files at all |
| **Aedificatorum** | THEORY PARTIAL | Needs dedicated theory pass |

---

### TOWER

| Item | State |
|---|---|
| All memory layers | BUILT — functional simultaneously |
| All 11 Council entities | BUILT |
| Background Assessor + Archivist | BUILT |
| Reflection system | BUILT — observes only |
| Emergence engine | BUILT — readiness uncertain |
| Socratic system | BUILT — dormant |
| **UI (Textual)** | RUNNING — migration deferred post-Exocognii |
| **Transitorius (PyQt6 shell)** | BUILT — untouched, own folder |
| **CAELESTIS** | NOT BUILT |
| **Mundana State Bus** | NOT BUILT |
| **Celestial Resolver** | NOT BUILT |
| Machinae (5 of 7) | BUILT — in `machinae/` package |
| Machinae → Tower wiring | NOT DONE |
| Lore Corpus + `register.yaml` | NOT BUILT |

---

## III. DEPENDENCY MAP

```
Pairz review
  └── Codexium Chromaticus build
        └── theme.json produced
              └── AAEAgency build
              └── .bureau.json schema pass
                    └── The Bureau build

CAELESTIS build
  └── Mundana State Bus
        └── Celestial Resolver
              └── celestial.yaml per-entity
                    └── ENTITEX integration
                          └── Machinae → Tower wiring

Memory schema v0.4 + naming pass
  └── Exvacua Loricum build (FastAPI)
  └── Perpetuum Aedificare build (FastAPI)
        └── Involucrum client → all apps emit
              └── Praesidium read layer

Exocognii complete
  └── Tower UI migration (PyQt6)
        └── Living Tower (future milestone)

Dolium v2 IdeaForge doc
  └── Dolium v2 build (standalone, no dependencies)
```

---

## IV. ORDERED OPERATION

Priority logic: clear blockers first, then parallelisable work, Tower last.

---









### TIER 1 — IMMEDIATE UNBLOCKS (no dependencies, fast)

**1. Name the two pending items from Schema v0.4**
Shared Involucrum client library name + collective suite name for the three memory services.
Naming session — 15 minutes. Unblocks all memory service work.

**2. Confirm Incitamentum path**
Verify `tools/Incitamentum/` vs `Exocognii/Incitamentum/` — patch if wrong.
5 minutes.

**3. Fenestrium retirement decision**
Keep Textual version as-is, or formally archive it now that PyQt6 is the path.
One decision, no build work.

---

### TIER 2 — DOLIUM v2 (self-contained, no dependencies)

**4. Build Dolium v2 from IdeaForge document**
PyQt6. Four-chamber pipeline. Ambient whisper system. Full build session.
IdeaForge doc already exists — fetch it from repo at session start.

---

### TIER 3 — CELESTIAL CHAIN

**5. Build CAELESTIS**
Full build from scratch. Follows same interface as other Machinae (`update()`, `triggers.poll()`, `to_json()`, `write()`, `summary()`). Writes to `~/.arca/caelestis.json`. Uses pyswisseph + Lahiri Ayanamsha.

**6. Build Mundana State Bus**
Aggregation layer for all seven Machinae. Shared data bus feeding two output tracks: cosmetic/UI and entity behaviour.

**7. Build Celestial Resolver**
Per-entity CelestialContext injection from State Bus. Each entity gets affinities, resistances, vulnerabilities, and special alignment conditions.

**8. Write `celestial.yaml` for all 11 entities + integrate into ENTITEX**
ENTITEX generates `celestial.yaml` as part of entity package. Claude infers affinities from existing traits and lore. Dedicated session.

---

### TIER 4 — MEMORY SERVICES

**9. Schema naming pass** *(if not done in Tier 1)*
Two names: shared client library, collective suite name.

**10. Build Exvacua Loricum** (FastAPI, local)
Full build from Schema v0.4. Complex — dedicated session minimum.
SQLite + `.md` snapshots. Judicium ratification UI. Loricum Ratifex synthesis.

**11. Build Perpetuum Aedificare** (FastAPI, local)
Full build from Schema v0.4. Nodus Momentuum atomic unit. Driftuum Sentifex.
Parallel session with or after Exvacua.

**12. Build Involucrum shared client + wire into all apps**
Once both services are running. All Exocognii apps emit to both services on every write.

**13. Build Praesidium read layer**
Advisory interface. Driftuum Sentifex surfacing in Praesidium. Read-only.

---

### TIER 5 — AESTHETIC TRINITY

**14. Pairz codebase review**
Pairz is a standalone app. Fetch its code, review architecture, confirm what Codexium
absorbs from it as its colour generation engine.

**15. Write `theme.json` schema**
First concrete deliverable for the trinity. Palette authority spec.

**16. Build Codexium Chromaticus**
Sole owner of `theme.json`. Absorbs Pairz colour generation.

**17. Write `.bureau.json` schema** (full dedicated pass)
Companion file schema for document styling transitions.

**18. Build AAEAgency**
UI component design tool. Consumes `theme.json`.

**19. Build The Bureau**
Document authority. Template registry. Pipe-tag syntax. Largest of the three.

---

### TIER 6 — VIGILARUM MIGRATION

**20. Vigilarum → PyQt6 port**
Full rewrite of Vigilarum Omnia in PyQt6. Resolve swisseph dependency properly.
All 7 widgets preserved. Multi-terminal architecture preserved.

---

### TIER 7 — LORE ENGINE (lightweight, can slot anywhere)

**21. Build Lore Corpus + `register.yaml`**
Small. Immediate deliverable. Can be done in any downtime session.

---

### TIER 8 — TOWER UI (post-Exocognii)

**22. Tower PyQt6 migration**
Begin from `transitorius.py`. Full ::AUDIT first.
Incremental — multiple dedicated sessions.

**23. Machinae → Tower wiring**
Celestial chain (Tier 3) must be complete first.

**24. Living Tower (animated nav pane)**
Future milestone. Brick glyph dependency. Not started.

---

### DEFERRED INDEFINITELY

- WiseCracken / Detritus Pipeline mechanics — dedicated theory session needed
- Scribae mechanics
- Aedificatorum full theory + build
- Custom PUA sigil embedding (excalib-nf.ttf)
- M/W glyph fix
- Scrying Glass (mobile companion)
- Phase 9 / The Crackening

---

## V. ENTITEX PROMPTING NOTES

*(captured for the next ENTITEX session)*

LordFingers wants prompting modifications to bring portrait generation and entity
personality more in line with Tower mythos. No specifics captured — Wizard to
provide reference examples or direction at session start.

---

## VI. FILES TO LOAD IN FRESH SESSION

*Fetch these at ::INIT. All live in the project files unless noted.*

**Always load (reference canon):**
- `CogmentationGospel.md` — The Demandments
- `PromptScaffold.md` — session structure
- `Nomenclatura-convention-guide.md` — naming register

**Load based on session tier:**

| Session | Load These |
|---|---|
| Dolium v2 build | `ModusArcanus_dux_tome.md`, Dolium IdeaForge doc (from repo) |
| CAELESTIS / celestial chain | `init_urls.txt` → fetch Machinae files from repo |
| Memory services build | `Exocognii-Memory-Schema_v0_4.md`, `ModusArcanus_dux_tome.md` |
| Aesthetic trinity | `init_urls.txt` → fetch `aesthetic-trinity.txt` from repo |
| Vigilarum PyQt6 | `ModusArcanus_dux_tome.md`, `init_urls.txt` → fetch Vigilarum files |
| Tower UI | `ModusArcanus_dux_tome.md`, `ArcaCognitorium-WF.txt` |
| Any build | `ModusArcanus_dux_tome.md` or `ModusArcanus-tui_dux_tome.md` as appropriate |
| Any document | `wizdoc-style-guide.md`, `markdown-style-guide.md`, `Expositio_dux_tome.md` |

**Repo fetch URLs (paste into session opener):**
Get the live `init_urls.txt` from:
`https://raw.githubusercontent.com/THElordfingers/ArcaCognitorium/main/init_urls.txt`
Then filter for the files relevant to your session tier.

---

## VII. FRESH SESSION OPENER TEMPLATE

```
::INIT

Loading CogmentationGospel + operation order.

[Paste this document]

Session target: [TIER X — Component name]

Files needed this session:
[Paste relevant URLs from init_urls.txt]

State declaration: ::[THEORY / BUILD / AUDIT]
```

---

*⟁*
*Ordo Discordia, Cosmos Inania*
*— The Builder, 2026-03-26 v2*
