╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                    ◥ ║
║                                                                       ║
║    ＥＸＯＣＯＧＮＩＩ — ＢＵＩＬＤ ＣＨＲＯＮＩＣＬＥ                 ║
║                                                                       ║
║◣                                                                    ◢ ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║    Project   ·  Arca Cognitorium                                      ║
║    Scope     ·  Exocognii Suite — Ordered Build Sequence              ║
║    Opened    ·  2026-03-27                                            ║
║    Last Entry·  2026-04-01                                            ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

╭─────────────────────────────────────────────────────────────────╮
│  TIER II — PRAESIDIUM: LAYOUT & PERSISTENCE                     │
│  Completed: 2026-04-01                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ✦  Layout persistence — layout.json empty write resolved       │
│  ✦  Widget proliferation — top-level windows on X11 resolved    │
│  ✦  Storage path — widget_registry wrong path resolved          │
│  ✦  ReferentiaAggregator — service endpoints wired              │
╰─────────────────────────────────────────────────────────────────╯

2026-04-01 · Tier II · PRAESIDIUM — Layout Persistence
  Status   : Complete
  Outcome  : layout.json now writes correctly. Stale entry accumulation
             resolved. Widget positions survive restart.
  Notes    : Root causes: empty _layout dict written during load (partial
             save), double signal connections, accumulated 20-entry
             layout.json from prior sessions.

2026-04-01 · Tier II · PRAESIDIUM — Widget Proliferation (Top-Level Windows)
  Status   : Complete
  Outcome  : Widgets embed correctly in canvas on X11. No spurious
             top-level windows on launch.
  Notes    : Root cause: singleShot(0) fired before X11 assigned a native
             window handle to canvas. Fixed: 150ms defer + explicit
             setParent() + raise_() after window is visible.

2026-04-01 · Tier II · PRAESIDIUM — Storage Path
  Status   : Complete
  Outcome  : TodoBoard and TokenTracker write to correct path:
             ArcaCognitorium/Exocognii/Praesidium/storage/
  Notes    : Root cause: arca_repo_path.parent / "Praesidium" resolved to
             ~/Praesidium. Fixed: arca_repo_path / "Exocognii" / "Praesidium"
             / "storage".

2026-04-01 · Tier II · PRAESIDIUM — ReferentiaAggregator Service Wiring
  Status   : Complete
  Outcome  : Corrected configuus.py port defaults: Exvacua Loricum → 8731,
             Perpetuum Aedificare → 8732. Endpoints updated to /nodi and
             /lorixii. Local fallback confirmed working.


╭─────────────────────────────────────────────────────────────────╮
│  OPEN — PENDING / IN QUEUE                                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ·  ChatWidget — bus.on() subscription audit                    │
│  ·  PRAESIDIUM Phase 4 — INGENIUM pipeline + dockables          │
│  ·  Exocognii FastAPI — full control panel / systems status     │
╰─────────────────────────────────────────────────────────────────╯


╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
