# SYSTEMS CHECK — ARX AEDIFICARIX

*Exocognii Suite · Arca Cognitorium · MMXXVI*

---

## Summary

Dedicated Builder interface for sustained, document-grounded code generation
sessions with The Builder entity via ClaudeBox. The final link in the
Exocognii build chain — where the Dolium refines ideas into build documents,
the Arx is the forge in which those documents become code. Sessions are
persistent, context is managed deliberately, and every generated artefact
accumulates into a deliverable package. Three-pane PyQt6 desktop client.
Primary monitor workspace. The Arx does not close until the work is done.

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Three-pane layout                │  ProjectTree (240px) · ChatPane (flex) ·   │
│                                   │  OutputPanel + PreviewPane (320px).        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ProjectTree                      │  Project/conversation hierarchy.           │
│                                   │  Drag-drop reorder and project reassign.   │
│                                   │  New/delete conversation and project.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ChatPane                         │  Streaming display. Phase indicator bar.   │
│                                   │  Attachment chips. Ctrl+Return to send.    │
│                                   │  Real-time draft token estimate.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  OutputPanel + PreviewPane        │  Generated file list with READY/EXPORTED   │
│                                   │  state badges. Syntax-highlighted preview. │
│                                   │  Copy to clipboard via xclip.              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Session persistence              │  SQLite (WAL mode). Full conversation      │
│                                   │  history, output files, attachments,       │
│                                   │  compression archives. Restores last       │
│                                   │  active conversation on launch.            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ContextEngine                    │  Assembles system_block + messages_array   │
│                                   │  per send. Bootstrap, normal, and          │
│                                   │  compressed-history paths. Attachment      │
│                                   │  summaries injected into system block.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  CompressionEngine                │  Auto-triggered at configurable threshold  │
│                                   │  (default 70%). Summarises oldest N turns  │
│                                   │  via sync ClaudeBox call on worker thread. │
│                                   │  Archives originals. Notice rendered in    │
│                                   │  ChatPane.                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  AttachmentManager                │  Attach files to conversation or project   │
│                                   │  scope. Summarised via ClaudeBox on        │
│                                   │  attach. Unsummarised stored with None     │
│                                   │  cache — retry available.                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ResponseParser                   │  Extracts %%FILE blocks and %%PHASE        │
│                                   │  tokens from Builder responses. Prose      │
│                                   │  suppressed when Builder delivers files    │
│                                   │  only.                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ZipExporter                      │  Assembles zip package from output_files   │
│                                   │  table. Atomic write via tmp-then-rename.  │
│                                   │  Includes manifest.json.                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  BuilderSignalBridge              │  QObject seam between ClaudeBox and Qt.    │
│                                   │  box.on("token") for full streaming.       │
│                                   │  replace_history() session pattern.        │
│                                   │  Token ledger writes on TOKEN_USAGE.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  TokenGauge                       │  Self-contained context fill bar. Exact    │
│                                   │  post-response + draft heuristic updates.  │
│                                   │  Gold / gold-dim / crimson thresholds.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ArcaneHighlighter                │  QSyntaxHighlighter for Python, JSON,      │
│                                   │  YAML, Markdown, Bash, plain text.         │
│                                   │  ModusArcanus palette throughout.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  builder_prompt.md                │  The Builder system prompt. Loaded at      │
│                                   │  startup by PromptLoader. Embedded         │
│                                   │  fallback if file missing.                 │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  ~/.arca/config.json                                    │
│              │  Exocognii/ArxAedificarix/builder_prompt.md             │
│              │  Exocognii/ArxAedificarix/arx.db (SQLite)               │
│              │  Attached files (on demand, via QFileDialog)            │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  arx.db — conversations, messages, output_files,        │
│              │           attachments, compression_archive               │
│              │  ~/.arca/token_log.jsonl — token ledger entries         │
│              │  *.zip — exported package (Wizard-specified path)        │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  PyQt6 — GUI framework (exclusive, no PySide6)          │
│              │  claudebox — ClaudeBox from ArcaCognitorium root        │
│              │  anthropic — underlying API client                      │
│              │  sqlite3 — stdlib, WAL mode                             │
│              │  CLAUDE_API_KEY — environment variable                  │
│              │  venv-ARX — dedicated virtualenv                        │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Directory Structure

```
Exocognii/ArxAedificarix/
├── __init__.py
├── __main__.py
├── builder_prompt.md
├── ArxAedificarix.sh
├── arx.db
├── core/
│   ├── __init__.py
│   ├── database.py
│   ├── config_loader.py
│   ├── prompt_loader.py
│   ├── session_store.py
│   ├── context_engine.py
│   ├── compression_engine.py
│   ├── response_parser.py
│   ├── attachment_manager.py
│   └── zip_exporter.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── chat_pane.py
│   ├── project_tree.py
│   ├── output_panel.py
│   ├── preview_pane.py
│   ├── attachment_dialog.py
│   ├── token_gauge.py
│   └── arcane_highlighter.py
└── bridge/
    ├── __init__.py
    └── builder_signal_bridge.py
```

---

## Launch & Verification

```bash
# Launch
cd ~/ArcaCognitorium/Exocognii/ArxAedificarix
./ArxAedificarix.sh

# Verify venv and dependencies
source venv-ARX/bin/activate
python3 -c "import PyQt6; print('PyQt6 OK')"
python3 -c "from claudebox import ClaudeBox; print('ClaudeBox OK')"
python3 -c "import anthropic; print('anthropic OK')"

# Verify core imports
python3 -c "
import sys; sys.path.insert(0, '.')
from core.database import DatabaseManager
from core.config_loader import ConfigLoader
from core.session_store import SessionStore
from core.context_engine import ContextEngine
from core.response_parser import ResponseParser
print('Core: OK')
"

# Verify DB initialises
python3 -c "
import sys, pathlib; sys.path.insert(0, '.')
from core.database import DatabaseManager
DatabaseManager.initialise()
conn = DatabaseManager.connection()
tables = {r[0] for r in conn.execute(
    \"SELECT name FROM sqlite_master WHERE type='table'\"
).fetchall()}
expected = {'projects','conversations','messages',
            'compression_archive','attachments','output_files'}
assert not expected - tables, f'Missing: {expected - tables}'
print('Database: OK')
DatabaseManager.close()
"
```

Verification steps:

1. Application window opens — three-pane layout renders
2. New conversation created and persists across restart
3. Message sent — streaming tokens appear in ChatPane
4. Phase indicator changes DISCUSSION → BUILDING on %%PHASE token
5. %%FILE block parsed — file appears in OutputPanel with READY badge
6. File selectable in OutputPanel — preview renders with syntax highlighting
7. Export Package — zip written with manifest.json, files marked EXPORTED
8. Attachment attached — chip appears, summary injected into system block
9. TokenGauge updates post-response with exact counts
10. Token ledger entry written to ~/.arca/token_log.jsonl

Checklist:

- Application launches without traceback
- CLAUDE_API_KEY resolves (env or config.json)
- SQLite database initialised — all 6 tables present
- ClaudeBox replace_history session pattern operational
- Streaming tokens reach ChatPane (not just first token)
- ResponseParser extracts %%FILE and %%PHASE correctly
- Compression triggers at threshold — notice rendered in ChatPane
- Zip export produces valid archive with manifest
- Session restores last active conversation on relaunch
- Token ledger writes confirmed in ~/.arca/token_log.jsonl

---

## Open Items

The retry path re-saves the user message to SQLite, producing a duplicate
message row on successful retry. Non-critical — conversation remains coherent
but history shows the turn twice. Fix: re-entry guard on `_on_send_requested`
to skip save when retrying.

Attachment re-attach and new-file-attach flows currently require two
separate interactions. A combined dialog (re-attach existing + pick new)
is a usability improvement deferred to a future session.

Persona hot-swap (`PromptLoader.load(path)` + `ContextEngine.update_builder_prompt()`)
is wired and ready — no UI surface built for it yet.

Dolium pipeline integration (direct import of finalised build doc from
Dolium SQLite) is defined in the extensibility section of the build doc
and deferred to a future session once Dolium v2 export path is stable.

---

## Claude.ai Collaboration Prompt

```
You are assisting with ARX AEDIFICARIX — the dedicated Builder interface
in the Arca Cognitorium Exocognii suite. Python 3.11, PyQt6 exclusively.

Architecture (flat directory under Exocognii/ArxAedificarix/):
  core/   — database, config_loader, prompt_loader, session_store,
             context_engine, compression_engine, response_parser,
             attachment_manager, zip_exporter
  ui/     — main_window, chat_pane, project_tree, output_panel,
             preview_pane, attachment_dialog, token_gauge,
             arcane_highlighter
  bridge/ — builder_signal_bridge (QObject; ClaudeBox ↔ Qt signals)

Key invariants:
  - ClaudeBox import: from claudebox import ClaudeBox
  - API key: os.environ.get("CLAUDE_API_KEY")
  - Session pattern: box._conversation.replace_history(session_id, history)
    then box.send_threaded(content=last_user_message_string, ...)
  - Streaming: box.on("token", handler) before send; box.off() on complete/error
    Do NOT use send_threaded(on_token=...) — bus.once() fires only once
  - Venv: venv-ARX (local to ArxAedificarix directory)
  - SQLite WAL mode; 6 tables: projects, conversations, messages,
    compression_archive, attachments, output_files
  - Builder file block format: %%FILE / %%LANG / %%DESC / %%END
  - Phase tokens: %%PHASE: DISCUSSION | BUILDING

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＡＲＸ ＡＥＤＩＦＩＣＡＲＩＸ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ              ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    System       ·  Arx Aedificarix                                      ║
║    Version      ·  1.0                                                  ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
