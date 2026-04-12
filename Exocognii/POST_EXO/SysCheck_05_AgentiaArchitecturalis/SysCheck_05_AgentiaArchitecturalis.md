# SYSTEMS CHECK — AGENTIA ARCHITECTURALIS (Bureau II)

*A4 · Triumviratus Aestheticus Imperialis · Arca Cognitorium · MMXXVI*

---

## Summary

Visual PyQt6 UI component designer. Replaces the retired Fenestrium.
QGraphicsScene canvas with 16px grid and snap-to-grid. 28 element types
across 7 palette categories. Context-sensitive property inspector with
token-based colour dropdowns. Live preview renders real PyQt6 widgets at
200ms debounce. Component Library in SQLite: save, load, fork, version,
archive, search. Code generation emits clean Python/PyQt6 using token
constants validated by ast.parse() before export. 21/21 tests passing.

Motto: *In Linea, In Parallelo, In Perpetuum.*

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  QGraphicsScene canvas            │  16px grid, snap-to-grid, zoom 25–400%     │
│  (Tabula Designandi)              │  (Ctrl+scroll)                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  28 element types                 │  7 categories: Receptacula, Ingressus,     │
│  (Elementarium palette)           │  Ostensio, Actiones, Tabulae, Ornamentum,  │
│                                   │  Composita                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Container nesting                │  Automatic child layout within containers  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Inspectorium                     │  Context-sensitive property editor.        │
│                                   │  Colours as token names (not hex).         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Specularium Vivum                │  Live preview — real PyQt6 widgets.        │
│                                   │  200ms debounce. Not a mockup.             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Armarium Componentium            │  SQLite Component Library. Save, load,     │
│                                   │  fork, version, archive, search.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Code generation (Promulgatio)    │  Python/PyQt6 with ModusArcanus headers.   │
│                                   │  Token constants (C_GOLD not "#d4af37").   │
│                                   │  Validated by ast.parse() before export.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Undo/redo                        │  Serialized canvas snapshots (max 50)      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Bureau I integration             │  Consumes theme.json. Falls back to        │
│                                   │  ModusArcanus defaults if absent.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  21/21 tests passing              │                                            │
╰───────────────────────────────────┴────────────────────────────────────────────╯

Generated code is static composition only — no signal/slot wiring, no app
logic. The Wizard wires those by hand in the target application.

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  theme.json from Bureau I (or ModusArcanus defaults)    │
│              │  ~/.arca/config.json                                    │
│              │  SQLite Component Library (saved designs)               │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  SQLite Component Library (saved designs)               │
│              │  Python/PyQt6 .py code file (export)                    │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  PyQt6 6.6+                                             │
│              │  Bureau I theme.json (optional — has fallback)          │
│              │  No ClaudeBox, no API calls                             │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Launch
cd ~/ArcaCognitorium/Exocognii/A4/AgentiaArchitecturalis
python -m AgentiaArchitecturalis

# Tests
pytest tests/ -v
```

Verification steps:

1. Canvas opens with visible 16px grid
2. Place an element from Elementarium palette — appears on canvas
3. Select element — Inspectorium shows its properties
4. Open Specularium — real PyQt6 widget renders (not a mockup)
5. Save to Component Library — entry created and searchable
6. Generate code — Python output visible, passes ast.parse()

Checklist:

- 21/21 tests passing
- theme.json loads from Bureau I if present; defaults otherwise
- Specularium renders real widgets (not placeholder graphics)
- Token constants in generated code (C_GOLD, not "#d4af37")
- ast.parse() validates all exported code
- Library saves persist across restart

---

## Open Items

Bureau I/II path at full `AestheticAuthoritarianAssociativeAlliance/` path.
Bureau III at `Exocognii/A4/`. Unification pending.

---

## Claude.ai Collaboration Prompt

```
You are assisting with AGENTIA ARCHITECTURALIS (Bureau II) — the visual
UI component designer of the Arca Cognitorium. PyQt6, Python 3.11.

Architecture:
- QGraphicsScene canvas (Tabula Designandi): 16px grid, snap, zoom
- Element factory pattern: CanvasElement abstract base, 28 concrete types
  across 7 categories (Receptacula, Ingressus, Ostensio, Actiones,
  Tabulae, Ornamentum, Composita)
- Specularium Vivum: real PyQt6 widgets at 200ms debounce (not mockups)
- Code generation: token constants only (C_GOLD not "#d4af37").
  Validated via ast.parse() before export.
- Component Library in SQLite: versioned, forkable designs
- Undo/redo via serialized canvas snapshots (max 50)
- Consumes Bureau I theme.json; ModusArcanus defaults as fallback
- Static compositions only — no signal/slot wiring in generated code
- No ClaudeBox, no API calls
- 21/21 tests must pass after any change

Path: AestheticAuthoritarianAssociativeAlliance/AgentiaArchitecturalis/

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＡＧＥＮＴＩＡ ＡＲＣＨＩＴＥＣＴＵＲＡＬＩＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ  ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Agentia Architecturalis (Bureau II)                  ║
║    Version      ·  1.0                                                  ║
║    Tests        ·  21/21 passing                                        ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
