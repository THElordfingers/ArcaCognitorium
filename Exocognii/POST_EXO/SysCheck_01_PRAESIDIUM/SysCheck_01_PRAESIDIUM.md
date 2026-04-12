# SYSTEMS CHECK — PRAESIDIUM v1.4

*Arca Cognitorium · Exocognii Suite · MMXXVI*

---

## Summary

Persistent ambient desktop dashboard. Free-floating PyQt6 widget canvas on
the secondary monitor. The operational nerve centre of the Exocognii suite.
Git workflow, Claude chat, token tracking, todo, art, diff, glyph browsing —
all on one surface that never demands attention and never forgets where it was.
Layout persists via atomically-written layout.json with 500ms debounce.
Phases 1–3 complete and functional. Phase 4 pending.

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ArcaneWidget base class          │  Drag, resize, lock, animated blind        │
│                                   │  collapse, font scale, status dot          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  LayoutManager                    │  Atomic layout.json write, 500ms debounce, │
│                                   │  SAVE DEFAULT snapshot                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  GitWidget                        │  Branch, status, file picker, commit,      │
│                                   │  push, pull, fetch, live streaming output, │
│                                   │  lock file detection + auto-clear          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ChatWidget                       │  ClaudeBox streaming, context selector     │
│                                   │  (Tower / Praesidium / General), token     │
│                                   │  forwarding                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  TokenTracker                     │  Cross-app ledger via QFileSystemWatcher,  │
│                                   │  session + daily totals, per-app breakdown │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  TodoBoard v2                     │  Tabbed multi-list, persistent             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  AppLauncher                      │  Configurable app shortcuts                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  DisplayPanel                     │  Plain / markdown / diff / image + file    │
│                                   │  drop universal renderer                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  DiffViewer                       │  Git modes + two-file drop                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  RepoActivity                     │  Commit feed + file watcher                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  QuickFileDrop                    │  Ingest zone with clipboard + display      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ReferentiaAggregator             │  Local file + Exocognii service search     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ArtWidget                        │  Image viewer — fit/fill/actual/zoom, SVG  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  GlyphBrowser                     │  Unicode sheet browser, click-to-copy      │
│                                   │  with Glyptorum integration                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  StyleReference                   │  Chromata Arcana palette reference         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  StatusLegend                     │  Aggregated widget status display          │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  ~/.arca/config.json                                    │
│              │  ~/.arca/layout.json                                    │
│              │  ~/.arca/layout_default.json                            │
│              │  ~/.arca/token_log.jsonl (live file watch)              │
│              │  git repo at arca_repo_path (subprocess)                │
│              │  Exocognii FastAPI services (optional, graceful degrade)│
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/.arca/layout.json (debounced, atomic)                │
│              │  ~/.arca/token_log.jsonl (ChatWidget completions)       │
│              │  git repo via subprocess (commit, push, pull, fetch)    │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  ClaudeBox at ~/ArcaCognitorium/claudebox/              │
│              │  git, xclip (system), PyQt6                             │
│              │  CLAUDE_API_KEY environment variable                    │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
cd ~/ArcaCognitorium && python -m Praesidium
```

Verification steps:

1. Canvas opens on secondary monitor without crash
2. All widgets restore to correct positions from layout.json
3. GitWidget shows current branch and repo status
4. ChatWidget — send a message, confirm streaming response
5. TokenTracker updates within 1 second of chat completion
6. Restart app — widget positions are identical on relaunch

Checklist:

- layout.json exists at `~/.arca/layout.json` after launch
- Widget geometry survives app restart (no reset)
- Git operations stream live — UI does not freeze
- ClaudeBox import resolves — no ImportError in console
- Lock / unlock state persists across restart
- `bus.on()` subscription pattern in ChatWidget (not `bus.once()`)

---

## Open Items

Phase 4 (INGENIUM pipeline widget + remaining dockables) — pending.
Stale layout entry accumulation — cleanup deferred.
Exocognii FastAPI service integration (build node status, drift flags)
not yet wired — ReferentiaAggregator degrades gracefully.

---

## Claude.ai Collaboration Prompt

```
You are assisting with PRAESIDIUM — the ambient desktop dashboard of the
Arca Cognitorium. PyQt6, Python 3.11, Debian Trixie, KDE Plasma 6, X11.

Architecture:
- All widgets inherit ArcaneWidget (widget_base.py)
- Absolute canvas positioning — no Qt layout managers
- LayoutManager: layout.json, 500ms debounce, atomic write
- ClaudeBox from ~/ArcaCognitorium/claudebox/ via arca_repo_path
  in ~/.arca/config.json
- Token log: ~/.arca/token_logger.py → ~/.arca/token_log.jsonl
- ClaudeBox streaming: bus.on() persistent subscription, not bus.once()
- setParent() never called after widget construction
- QThread for all git ops (Popen line-by-line, not subprocess.run)
- CLAUDE_API_KEY env var — never ANTHROPIC_API_KEY
- PyQt6 exclusively — never mix PySide6

Aesthetic: ModusArcanus — void backgrounds, Aurum accents, Georgia serif.
Constants in style.py. The word atelier does not exist.

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＰＲＡＥＳＩＤＩＵＭ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                     ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  PRAESIDIUM                                           ║
║    Version      ·  1.4                                                  ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
