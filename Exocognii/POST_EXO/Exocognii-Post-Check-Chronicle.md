╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║    ＥＸＯＣＯＧＮＩＩ — ＶＥＲＩＦＩＣＡＴＩＯ ＣＨＲＯＮＩＣＬＥ     ║
║                                                                       ║
║◣                                                                     ◢║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║    Project    ·  Arca Cognitorium — Exocognii Suite                   ║
║    Scope      ·  POST_EXOCOGNII — Full Suite Systems Verification     ║
║    Checks     ·  10 — one per tool / subsystem                        ║
║    Opened     ·  2026-04-01                                           ║
║    Last Entry ·  2026-04-01                                           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

------------------------------------------------------------------------------------

  01 · PRAESIDIUM v1.4            ·  ✦ Complete   · 2026-04-01
  02 · DOLIUM v2                  ·  ✦ Complete   · 2026-04-01
  03 · VIGILARUM v2               ·  ✦ Complete   · 2026-04-03
  04 · Auctoritas Spectralis      ·  ⏳ Pending
  05 · Agentia Architecturalis    ·  ⏳ Pending
  06 · Departamentum Documentalis ·  ⏳ Pending
  07 · Exvacua Loricum            ·  ⏳ Pending
  08 · Perpetuum Aedificare       ·  ⏳ Pending
  09 · Celestial Chain            ·  ⏳ Pending
  10 · Lore Corpus                ·  ⏳ Pending

------------------------------------------------------------------------------------

╭─────────────────────────────────────────────────────────────────╮
│  PRAESIDIUM v1.4 — SYSTEMS CHECK & BUGFIX                       │
│  Completed: 2026-04-01                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ✦  Layout persistence — layout.json empty write resolved       │
│  ✦  Widget proliferation — top-level windows on X11 resolved    │
│  ✦  Storage path — widget_registry wrong path resolved          │
│  ✦  ReferentiaAggregator — service endpoints wired              │
│  ✦  configuus.py — service port defaults corrected              │
╰─────────────────────────────────────────────────────────────────╯
2026-04-01 · PRAESIDIUM v1.4 — Systems Check & Bugfix Session
  Status   : Complete
  Outcome  : Layout persistence working. Widget positions survive restart.
             No spurious top-level windows on launch. Storage paths correct.
             ReferentiaAggregator local fallback operational.
  Fixes    :
    · Layout persistence — _loading guard added to LayoutManager.
      blockSignals() during geometry restore prevents mid-load save.
      Synchronous clean write after load().
    · Double signal connections — _wire_widget() now the single canonical
      wiring point. praesidium_app no longer re-connects layout signals
      after load().
    · Widget proliferation — singleShot(0) fired before X11 assigned
      native window handle to canvas. Fixed: 150ms defer + setParent()
      + raise_() after window visible.
    · Storage path — widget_registry used arca_repo_path.parent /
      'Praesidium', resolving to ~/Praesidium. Fixed: arca_repo_path /
      'Exocognii' / 'Praesidium' / 'storage'.
    · configuus.py port defaults — Exvacua Loricum corrected to 8731,
      Perpetuum Aedificare corrected to 8732.
    · ReferentiaAggregator endpoints — updated to query /nodi and
      /lorixii on correct services. Local fallback confirmed working.
    · Stale layout.json — 20-entry accumulation from prior sessions.
      Cleaned. Purge logic now active on load.
  Deferred :
    · bus.on() subscription audit in ChatWidget — deferred.
    · PRAESIDIUM Phase 4 — INGENIUM pipeline widget + remaining dockables.
    · Exocognii FastAPI full control panel / systems status wiring.


------------------------------------------------------------------------------------

╭─────────────────────────────────────────────────────────────────╮
│  DOLIUM v2 — SYSTEMS CHECK & BUGFIX                             │
│  Completed: 2026-04-01                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ✦  AmbientWorker crash — sip.isdeleted() guard                 │
│  ✦  Streaming dead — box.stream() replaces send_threaded()      │
│  ✦  ClaudeBox import — pyyaml installed in venv-DOLIUM          │
│  ✦  Storage path — app-relative Path(__file__).parent fix       │
│  ✦  Token ledger — delta write, baseline tracking               │
│  ✦  Token feed wired to Praesidium TokenTracker                 │
╰─────────────────────────────────────────────────────────────────╯

2026-04-01 · Dolium v2 — Systems Check & Bugfix Session
  Status   : Complete
  Outcome  : Dolium v2 fully operational. 74/74 tests passing.
             All checklist items green. Token feed wired to Praesidium.
  Fixes    :
    · AmbientWorker crash — RuntimeError on deleted C++ object resolved.
      Root cause: finished.connect(deleteLater) leaving stale Python ref.
      Fixed: PyQt6.sip.isdeleted() guard in on_whisper_requested().
    · Streaming dead — ClaudeBox send_threaded() uses bus.once() for
      on_token, firing exactly once then dying. Fixed: replaced with
      box.stream() generator in both AmbientWorker and ConversationWorker.
    · ClaudeBox import failure — pyyaml not installed in venv-DOLIUM.
      Fixed: pip install pyyaml.
    · Storage path — files writing to ~/Dolium/storage. Root cause:
      hardcoded Path.home() / "Dolium" / "storage" fallback in app.py.
      Fixed: Path(__file__).parent / "storage".
    · Token ledger double-counting — get_token_usage() returns cumulative
      totals; repeated writes inflated the log. Fixed: module-level
      baseline dict tracks last-written totals, only delta is written.
  Deferred :
    · Praesidium pipeline state feed — Mundana State Bus not built.
    · Shared knowledge context injection — deferred.
    · Token budget display / session summarisation — deferred.
    · Theme resolution from Auctoritas Spectralis — deferred.
    · .wiz export — Node.js dependency; degrades gracefully.


------------------------------------------------------------------------------------



╭─────────────────────────────────────────────────────────────────╮
│  VIGILARUM OMNIA v2 — FULL BUILD & SYSTEMS CHECK                │
│  Completed: 2026-04-03                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ✦  Full cold build — all source files written from zero        │
│  ✦  41 widget types across 9 categories                         │
│  ✦  Uranus, Neptune, Pluto added to engine and painters         │
│  ✦  Rahu/Ketu correctly typed as lunar nodes throughout         │
│  ✦  Free-float canvas — drag to position, resize by grip        │
│  ✦  Layout persists to display_N.json per widget                │
│  ✦  info.py — floating reference window with live context       │
│  ✦  All widget fields labelled; category headers in control     │
│  ✦  Sky summary redundancy fixed                                │
│  ✦  TEMPORALIA (seasonal engine) integrated                     │
╰─────────────────────────────────────────────────────────────────╯

2026-04-03 · VIGILARUM OMNIA v2 — Full Build & Systems Check
  Status   : Complete
  Outcome  : Full PyQt6 application built from scratch. Engine live,
             state.json writing, all 41 widgets operational. Free-float
             canvas with drag/resize replacing grid layout. info.py
             floating reference window with live widget context.
  Fixes    :
    · Cold start — all files written via installer script due to MCP
      filesystem tool instability on large writes.
    · painters.py — f-string backslash in draw_planet_strip; extracted
      conditional to variable.
    · info.py — same f-string backslash in _live_context; same fix.
    · Column buttons — state not updating on click; corrected.
    · Sky summary — "Full Moon Moon" redundancy; engine.py corrected.
    · Moon distance gauge — "Apogee" label duplicated; fixed.
    · Ghost/orphan widgets — stale display_N.json entries cleaned.
    · Rahu/Ketu — incorrectly classified as planets; corrected to
      lunar nodes throughout registry, labels, painters, info.
  Deferred :
    · Sunrise/sunset fixed at 06:00. Location-aware swe.rise_trans()
      deferred; depends on ~/.arca/config.json lat/lon keys.
    · Weather widgets (METEOROLOGICA) — deferred to named session.
    · Moon disc terminator softness at quarter phases — QPainter
      geometry constraint, logged.
