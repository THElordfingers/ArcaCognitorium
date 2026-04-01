# SYSTEMS CHECK — THE DOLIUM v2

*Arca Cognitorium · Exocognii Suite · MMXXVI*

---

## Summary

Four-chamber ideation pipeline. Raw ideas enter the Fomentary and pass
through the Cultivation House, the Vestibule, and the Codex under increasing
pressure. The pipeline is gated — advancement requires genuine field content.
An ambient entity observes field changes and whispers unprompted observations
after 1500ms of typing inactivity. 74 tests passing across models, store, and
gate logic. Session ID equals Idea ID — history is replayed on load.

Chambers: Fomentary → Cultivation House → Vestibule → Codex.

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Four-chamber pipeline            │  Fomentary, Cultivation House, Vestibule,  │
│                                   │  Codex. Gated advancement.                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  AmbientWorker                    │  1500ms debounced whisper. Fires when no   │
│                                   │  conversation is active (_conv_active).    │
│                                   │  Shares session with ConversationWorker.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  GateResult                       │  Pure function per chamber. Returns        │
│                                   │  passed bool + list of unmet conditions.   │
│                                   │  UI renders this directly.                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  IdeaStore                        │  JSON persistence, in-memory cache,        │
│                                   │  backup on corruption                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Session continuity               │  Session ID = Idea ID. History replays     │
│                                   │  on load. Conversation context unified.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Cull and resurrect               │  Culled ideas never deleted. Cull register │
│                                   │  preserves all. Resurrection available.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Export                           │  .md, .txt, .json, .docx, .wiz on          │
│                                   │  Declaration from the Codex                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Pipeline panel                   │  Chamber tree, idea list, search           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  74 tests passing                 │  models, store, gate logic                 │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  ~/.arca/config.json (arca_repo_path for ClaudeBox)     │
│              │  DOLIUM_STORAGE env var or ~/Dolium/storage/            │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/Dolium/storage/*.json (idea persistence)             │
│              │  ~/.arca/token_log.jsonl (completions)                  │
│              │  Export files on Declaration (.md .txt .json .docx .wiz)│
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  ClaudeBox at ~/ArcaCognitorium/claudebox/              │
│              │  CLAUDE_API_KEY environment variable                    │
│              │  python-docx (optional, .docx export)                   │
│              │  Node.js + docx npm (optional, .wiz export)             │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
cd ~/ArcaCognitorium && python -m Dolium
```

Verification steps:

1. App opens — three-panel layout visible
2. Create a new idea — title and Fomentary fields accept input
3. Type in a Fomentary field — entity whisper appears within ~2 seconds
4. Try to advance with thin content — gate should block
5. Send a chat message — streams into conversation pane
6. Restart app — idea and conversation history restore

Checklist:

- Storage directory exists and is writable
- ClaudeBox import resolves without error
- AmbientWorker fires within 1500ms of typing inactivity
- Whisper and conversation do not collide — `_conv_active` working
- Gate correctly blocks advancement with minimal content
- Export produces valid .md file on Declaration
- App runs without entity if ClaudeBox unavailable (graceful degrade)

---

## Open Items

Praesidium pipeline state feed — not wired (infrastructure not ready).
Shared knowledge center context injection — deferred.
Token budget display / session summarisation — deferred.
Theme resolution from Codexium Chromaticus — deferred.
wiz_export.js Node dependency — degrades gracefully without Node.js.

---

## Claude.ai Collaboration Prompt

```
You are assisting with THE DOLIUM v2 — a four-chamber ideation pipeline
in the Arca Cognitorium. PyQt6, Python 3.11, Debian Trixie.

Architecture:
- Chambers: Fomentary → Cultivation House → Vestibule → Codex
- AmbientWorker: QTimer on main thread only (1500ms). Worker thread
  fires ClaudeBox call. _conv_active prevents collision with
  ConversationWorker.
- Both workers share ONE ClaudeBox session per idea.
  Session ID = Idea ID. History replays on load.
- IdeaStore: JSON, in-memory cache, backup on corrupt data
- Gate logic in gates.py — GateResult(passed, failures_list).
  Pure function. UI consumes directly.
- ClaudeBox: sys.path.insert(0, arca_repo_path from config)
- CLAUDE_API_KEY env var — never ANTHROPIC_API_KEY
- Modus Arcanus aesthetic throughout (style.py)
- 74 tests must continue passing after any change

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＴＨＥ ＤＯＬＩＵＭ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                      ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  The Dolium v2                                        ║
║    Version      ·  2.0                                                  ║
║    Tests        ·  74/74 passing                                        ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
