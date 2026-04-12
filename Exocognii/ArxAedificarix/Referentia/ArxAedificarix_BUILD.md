# ARX AEDIFICARIX
## Construction Documentation · v1.0
### Exocognii Suite · Arca Cognitorium · CastrumDigitos

---

## TABLE OF CONTENTS

```
1.  Overview & Core Architecture
2.  Tech Stack
3.  Directory & File Tree + SQLite Schema
4.  Module Breakdown
5.  ASCII UI Wireframe
6.  Data Flow
7.  Code Stubs
      7.1  DatabaseManager
      7.2  ConfigLoader
      7.3  PromptLoader
      7.4  ContextEngine
      7.5  CompressionEngine
      7.6  ResponseParser
      7.7  AttachmentManager
      7.8  AttachmentDialog
      7.9  OutputPanel
      7.10 ZipExporter
      7.11 TokenGauge
      7.12 BuilderSignalBridge
      7.13 ProjectTree
      7.14 ChatPane
      7.15 ArcaneHighlighter
      7.16 SessionStore
      7.17 BUILDER_SYSTEM_PROMPT / builder_prompt.md
8.  Error Handling
9.  Requirements, Tests & Run Instructions
10. Packaging
11. Extensibility
```

---

## 1. OVERVIEW & CORE ARCHITECTURE

Arx Aedificarix is the final link in the Exocognii build chain — a
dedicated PyQt6 desktop client in which the Wizard conducts long-form,
document-grounded code generation sessions with The Builder entity via
ClaudeBox. Where the Dolium refines ideas into build documents and the
Praesidium handles ambient system queries, the Arx is a forge: a high-
intensity primary-monitor workspace for sustained, iterative construction.
Sessions are persistent, context is managed deliberately, and every
generated artefact accumulates into a deliverable package. The Arx does
not close until the work is done.

╭──────────────────────┬───────────────────────────────────┬────────────────────────────────╮
│ Layer                │ Role                              │ Key Classes                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Session Layer        │ SQLite persistence; schema init;  │ DatabaseManager, SessionStore  │
│                      │ conversation restore on launch    │                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Context Engine       │ Owns conversation history;        │ ContextEngine,                 │
│                      │ assembles API payload per send;   │ AttachmentManager,             │
│                      │ tracks token estimates            │ ConfigLoader, PromptLoader     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Compression Engine   │ Detects token threshold breach;   │ CompressionEngine              │
│                      │ summarises oldest turns via sync  │                                │
│                      │ ClaudeBox call; archives originals│                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ClaudeBox Integration│ send_threaded for all primary     │ BuilderSignalBridge, ClaudeBox │
│                      │ calls; signal bridge to Qt;       │                                │
│                      │ token ledger writes               │                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Output Layer         │ Parses file blocks from response; │ ResponseParser, OutputPanel,   │
│                      │ accumulates generated files;      │ ZipExporter, PreviewPane,      │
│                      │ zip export with manifest          │ ArcaneHighlighter              │
╰──────────────────────┴───────────────────────────────────┴────────────────────────────────╯

---

## 2. TECH STACK

╭─────────────────────┬───────────┬──────────────────────────────────────────────────╮
│ Tool                │ Version   │ Justification                                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Python              │ 3.11      │ Suite-wide standard; f-strings, match, tomllib   │
│ PyQt6               │ 6.6+      │ Exocognii suite standard; never PySide6          │
│ ClaudeBox           │ canonical │ Custom Anthropic wrapper; send_threaded; signals │
│ SQLite3             │ stdlib    │ Persistence; WAL mode; no server dependency       │
│ zipfile             │ stdlib    │ Package assembly; manifest inclusion              │
│ pathlib             │ stdlib    │ All path operations                              │
│ json                │ stdlib    │ Manifest, config, message serialisation          │
│ token_logger.py     │ local     │ Shared suite ledger writer; stdlib-only          │
│ anthropic           │ latest    │ Underlying API client used by ClaudeBox          │
╰─────────────────────┴───────────┴──────────────────────────────────────────────────╯

---

## 3. DIRECTORY & FILE TREE + SQLITE SCHEMA

```
ArcaCognitorium/
└── Exocognii/
    └── ArxAedificarix/
        ├── __init__.py                  — package entry: python -m Exocognii.ArxAedificarix
        ├── __main__.py                  — calls main(); bootstraps QApplication
        ├── builder_prompt.md            — The Builder system prompt; loaded at startup
        ├── launch_arxaedificarix.sh     — KDE launcher; venv + env + run
        ├── ArxAedificarix.desktop       — KDE .desktop entry
        ├── core/
        │   ├── __init__.py
        │   ├── database.py              — DatabaseManager; schema init; connection
        │   ├── config_loader.py         — ConfigLoader; reads ~/.arca/config.json
        │   ├── prompt_loader.py         — PromptLoader; loads builder_prompt.md
        │   ├── session_store.py         — SessionStore; CRUD for all SQLite tables
        │   ├── context_engine.py        — ContextEngine; payload assembly
        │   ├── compression_engine.py    — CompressionEngine; history compression
        │   ├── response_parser.py       — ResponseParser; file block extraction
        │   ├── attachment_manager.py    — AttachmentManager; file attach + summarise
        │   └── zip_exporter.py          — ZipExporter; package assembly
        ├── ui/
        │   ├── __init__.py
        │   ├── main_window.py           — MainWindow; three-pane + footer layout
        │   ├── project_tree.py          — ProjectTree; QTreeWidget; drag-drop
        │   ├── chat_pane.py             — ChatPane; streaming display; input area
        │   ├── output_panel.py          — OutputPanel; generated file list
        │   ├── preview_pane.py          — PreviewPane; syntax-highlighted display
        │   ├── token_gauge.py           — TokenGauge; reusable context fill widget
        │   ├── attachment_dialog.py     — AttachmentDialog; re-attach QDialog
        │   └── arcane_highlighter.py    — ArcaneHighlighter; QSyntaxHighlighter
        ├── bridge/
        │   ├── __init__.py
        │   └── builder_signal_bridge.py — BuilderSignalBridge; QObject + pyqtSignals
        └── arx.db                       — SQLite database (created on first run)
```

### SQLite Schema

```sql
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS projects (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    shared_instructions TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT PRIMARY KEY,
    project_id      TEXT REFERENCES projects(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    builder_prompt  TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL,
    last_active_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id                   TEXT PRIMARY KEY,
    conversation_id      TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                 TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content              TEXT NOT NULL,
    compressed           INTEGER NOT NULL DEFAULT 0,
    compression_group_id TEXT,
    token_count          INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS compression_archive (
    id                   TEXT PRIMARY KEY,
    compression_group_id TEXT NOT NULL,
    original_messages    TEXT NOT NULL,  -- JSON array of {role, content} dicts
    summary              TEXT NOT NULL,
    compressed_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attachments (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    project_id      TEXT REFERENCES projects(id) ON DELETE CASCADE,
    scope           TEXT NOT NULL CHECK(scope IN ('conversation', 'project')),
    filename        TEXT NOT NULL,
    full_content    TEXT NOT NULL,
    summary_cache   TEXT,               -- NULL until summarisation succeeds
    attached_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS output_files (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    language        TEXT NOT NULL DEFAULT 'plain',
    content         TEXT NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    export_status   TEXT NOT NULL DEFAULT 'pending'
                    CHECK(export_status IN ('pending', 'exported')),
    created_at      TEXT NOT NULL
);
```

---

## 4. MODULE BREAKDOWN

╭──────────────────────────┬────────────────────────────────────────┬────────────────────────┬──────────────────────────┬────────────────────────────────────╮
│ Module                   │ Responsibility                         │ Inputs                 │ Outputs                  │ Dependencies                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ DatabaseManager          │ Schema init; WAL; connection owner     │ db path                │ sqlite3.Connection       │ sqlite3, pathlib                   │
│ ConfigLoader             │ Reads ~/.arca/config.json              │ config path            │ dict                     │ json, pathlib                      │
│ PromptLoader             │ Loads builder_prompt.md; fallback      │ md path, fallback str  │ str (system prompt)      │ pathlib, logging                   │
│ SessionStore             │ CRUD for all tables                    │ DatabaseManager        │ dataclasses / dicts      │ DatabaseManager, uuid, datetime    │
│ ContextEngine            │ Assembles system_block + messages_array│ conversation_id,       │ tuple[str, list[dict]]   │ SessionStore, AttachmentManager    │
│                          │ per API call; token estimation         │ draft_text             │                          │                                    │
│ CompressionEngine        │ Detects threshold; summarises oldest N │ conversation_id, box   │ CompressionRecord        │ ClaudeBox, SessionStore,           │
│                          │ turns via sync box.send(); archives    │                        │                          │ DatabaseManager                    │
│ ResponseParser           │ Extracts file blocks + phase tokens    │ response_text: str     │ tuple[str|None,          │ re, dataclasses                    │
│                          │ from response text; strips from prose  │                        │ list[OutputFile],        │                                    │
│                          │                                        │                        │ str|None]                │                                    │
│ AttachmentManager        │ Attach file; summarise via ClaudeBox;  │ path, scope,           │ Attachment dataclass     │ ClaudeBox, SessionStore, pathlib   │
│                          │ failure path: store unsummarised       │ conversation_id,       │                          │                                    │
│                          │                                        │ project_id             │                          │                                    │
│ AttachmentDialog         │ QDialog listing all attachments for    │ conversation_id,       │ list[str] (selected ids) │ PyQt6, SessionStore                │
│                          │ current conversation + project;        │ project_id             │                          │                                    │
│                          │ checkbox re-attach                     │                        │                          │                                    │
│ OutputPanel              │ File list with state badges;           │ OutputFile objects     │ selection signal         │ PyQt6, SessionStore                │
│                          │ PENDING→READY→EXPORTED transitions     │                        │                          │                                    │
│ ZipExporter              │ Assembles zip from output_files;       │ conversation_id,       │ Path (zip location)      │ zipfile, json, SessionStore        │
│                          │ generates manifest.json                │ dest_path              │                          │                                    │
│ TokenGauge               │ Reusable context fill widget;          │ current: int,          │ visual gauge display     │ PyQt6 only; zero Arx imports       │
│                          │ exact + draft heuristic updates        │ total: int             │                          │                                    │
│ BuilderSignalBridge      │ QObject; callbacks → pyqtSignals;      │ ClaudeBox callbacks    │ Qt signals               │ PyQt6, ClaudeBox, token_logger     │
│                          │ token ledger writes                    │                        │                          │                                    │
│ ProjectTree              │ QTreeWidget; project/conversation       │ SessionStore           │ conversation_selected    │ PyQt6, SessionStore                │
│                          │ hierarchy; drag-drop reorder/move      │                        │ signal                   │                                    │
│ ChatPane                 │ Streaming display; phase indicator;    │ signals from Bridge,   │ send_requested signal    │ PyQt6, BuilderSignalBridge         │
│                          │ attachment chips; input field          │ user input             │                          │                                    │
│ PreviewPane              │ Syntax-highlighted read-only display   │ OutputFile             │ —                        │ PyQt6, ArcaneHighlighter           │
│ ArcaneHighlighter        │ QSyntaxHighlighter; Python/JSON/       │ language: str,         │ highlighted document     │ PyQt6                              │
│                          │ YAML/plain text rules                  │ QTextDocument          │                          │                                    │
╰──────────────────────────┴────────────────────────────────────────┴────────────────────────┴──────────────────────────┴────────────────────────────────────╯

---

## 5. ASCII UI WIREFRAME

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  ARX AEDIFICARIX                                                          v1.0          ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                         ║
║  ┌─────────────────────────┐  ┌──────────────────────────────┐  ┌─────────────────────┐║
║  │ [New Conv][New Proj][Del]│  │ ▌ DISCUSSION                 │  │ OUTPUT FILES        │║
║  ├─────────────────────────┤  ├──────────────────────────────┤  ├─────────────────────┤║
║  │ ▸ Project Alpha          │  │                              │  │ ⬡ main.py   [READY] │║
║  │   └─ ● Auth Module      │  │  [ASSISTANT]                 │  │ ⬡ models.py [READY] │║
║  │   └─  API Scaffold       │  │  The build plan is as        │  │ ⬡ utils.py  [PEND.] │║
║  │ ▸ Project Beta           │  │  follows. First we will...   │  │                     │║
║  │   └─  Database Layer     │  │                              │  │                     │║
║  │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │  │  [USER]                      │  │                     │║
║  │  Scratchpad              │  │  Agreed. Start with the      │  ├─────────────────────┤║
║  │  Untitled 2024-01-15     │  │  models layer.               │  │ PREVIEW             │║
║  │                          │  │                              │  ├─────────────────────┤║
║  │                          │  │  [ASSISTANT]                 │  │ class UserModel:    │║
║  │                          │  │  %%PHASE: BUILDING           │  │   id: int           │║
║  │                          │  │  [ context compressed —      │  │   name: str         │║
║  │                          │  │    47 turns archived ]       │  │   email: str        │║
║  │                          │  │                              │  │                     │║
║  │                          │  │  [ASSISTANT]                 │  │                     │║
║  │                          │  │  models.py is complete.      │  │           [Copy]    │║
║  │                          │  │  Moving to utils.py.         │  │                     │║
║  └─────────────────────────┘  │                              │  └─────────────────────┘║
║  240px fixed                  │  ┌──────────────────────────┐ │                         ║
║                               │  │ 📎 schema.md  ✕          │ │                         ║
║                               │  │ 📎 models.py  ✕  [+]     │ │                         ║
║                               │  └──────────────────────────┘ │                         ║
║                               │  ┌──────────────────────────┐ │                         ║
║                               │  │                          │ │                         ║
║                               │  │  (input field)           │ │                         ║
║                               │  │                          │ │                         ║
║                               │  └────────────── ~420 tok ──┘ │                         ║
║                               │                    [Send]      │                         ║
║                               └──────────────────────────────┘  320px fixed             ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║  CONTEXT  ████████░░░░░░  58%        Auth Module · 2024-01-15       [Export Package]   ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

### Legend

```
●  Active/selected conversation (C_GOLD left border)
▸  Collapsed project node
─ ─  Separator between grouped and ungrouped conversations
[READY]    Output file parsed and available for preview/export
[PEND.]    Output file registered but content not yet complete
[EXPORTED] File included in a completed zip export
📎 filename ✕   Attachment chip — ✕ dismisses from current turn injection only
[+]             Opens AttachmentDialog — re-attach previously dismissed files
(input field)   QPlainTextEdit — 3 lines default, expandable
~420 tok        Real-time token estimate of current draft (updates on keypress)
[Send]          C_TEAL — submits message
▌ DISCUSSION    Phase indicator bar — C_TEAL when discussing
▌ BUILDING      Phase indicator bar — C_GOLD when generating code
[ context compressed — N turns archived ]
                Compression notice — C_GOLD_DIM italic — not a chat bubble
CONTEXT ████░   TokenGauge — C_GOLD <60%, C_GOLD_DIM 60-85%, C_CRIMSON >85%
[Export Package] C_TEAL — opens QFileDialog; passes path to ZipExporter
[Copy]          C_GOLD — copies PreviewPane content to clipboard
[New Conv]      Creates new conversation in current project or ungrouped
[New Proj]      Creates new project; prompts for name + shared instructions
[Del]           Deletes selected conversation or project (confirm dialog)
```

---

## 6. DATA FLOW

### Path A — Happy Path

```
Wizard types message → [Send] clicked
  │
  ├─ ChatPane.on_send()
  │    saves draft user message to SQLite via SessionStore.save_message()
  │    updates conversation.last_active_at
  │
  ├─ ContextEngine.assemble_payload(conversation_id)
  │    produces (system_block: str, messages_array: list[dict])
  │    system_block = builder_prompt + project instructions + attachment summaries
  │    messages_array = all turns; compressed turns substituted with archive summary
  │
  ├─ CompressionEngine.check_threshold(estimated_tokens)
  │    if estimate < threshold → proceed
  │    if estimate >= threshold → trigger compression first (see Path B)
  │
  ├─ BuilderSignalBridge.send(system_block, messages_array)
  │    calls box.send_threaded(
  │        content=messages_array,
  │        system=system_block,
  │        on_token=bridge.on_token,
  │        on_complete=bridge.on_complete,
  │        on_error=bridge.on_error
  │    )
  │    returns immediately; background thread streams response
  │
  ├─ [background thread]
  │    on_token(text) → bridge.token_received.emit(text)
  │      → ChatPane appends token to streaming bubble
  │
  ├─ [background thread complete]
  │    on_complete(response) → bridge.response_complete.emit(full_text)
  │      → ResponseParser.parse(full_text)
  │           returns (prose: str|None, files: list[OutputFile], phase: str|None)
  │      → if prose not None → ChatPane renders assistant bubble
  │      → if prose is None → ChatPane suppresses bubble
  │      → if phase not None → bridge.phase_changed.emit(phase)
  │           → ChatPane updates phase indicator bar
  │      → for each OutputFile → OutputPanel.add_file(f) → state: PENDING→READY
  │           → SessionStore writes to output_files table
  │
  ├─ bus.on(TOKEN_USAGE) fires → bridge.on_token_usage(input_n, output_n)
  │    bridge.token_usage_updated.emit(input_n, output_n)
  │      → TokenGauge.update_exact(input_n, output_n)
  │    token_logger.write(app="arx_aedificarix",
  │                       input_tokens=input_n, output_tokens=output_n)
  │      → appends to ~/.arca/token_log.jsonl
  │    SessionStore updates message.token_count
  │
  └─ ChatPane re-enables [Send]
```

### Path B — Compression Trigger

```
ContextEngine.assemble_payload() returns token estimate
  │
  ├─ estimate >= arx_aedificarix.compression_threshold (default 0.70)
  │
  ├─ [QRunnable worker already running]
  │    CompressionEngine.trigger(conversation_id)
  │      selects oldest N uncompressed message pairs from SQLite
  │      constructs compression_prompt with turn content
  │      calls box.send() synchronously (already off main thread)
  │        → receives summary text
  │      generates compression_group_id (uuid4)
  │      writes compression_archive row:
  │        { id, compression_group_id, original_messages JSON, summary, compressed_at }
  │      updates messages rows:
  │        SET compressed=1, compression_group_id=<group_id>
  │        for each archived message id
  │      returns CompressionRecord
  │
  ├─ bridge.compression_complete.emit(summary_preview)
  │    → ChatPane inserts compression notice (C_GOLD_DIM italic):
  │      "[ context compressed — N turns archived ]"
  │
  ├─ ContextEngine.assemble_payload() called again with updated state
  │    compressed turns now appear as single assistant turn:
  │      { "role": "assistant", "content": archive.summary }
  │    token estimate resets to post-compression value
  │
  └─ TokenGauge updates to post-compression estimate
     normal send proceeds
```

### Path C — API Failure Mid-Stream

```
box.send_threaded() → background thread → API error raised
  │
  ├─ bridge.on_error(exception)
  │    bridge.error_occurred.emit(str(exception))
  │
  ├─ ChatPane.on_error(message)
  │    removes incomplete streaming bubble
  │    renders error notice in C_CRIMSON:
  │      "[ connection error — Builder could not be reached ]"
  │    shows [Retry] button beside error notice
  │    last user message remains in SQLite (not removed)
  │
  ├─ [Retry] clicked
  │    ChatPane.on_retry()
  │    re-runs assemble_payload() + send_threaded() from scratch
  │    same user message content re-used from SQLite
  │
  └─ [Send] re-enabled
     stream state cleared
```

---

## 7. CODE STUBS

### 7.1 DatabaseManager

```python
# core/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path("~/ArcaCognitorium/Exocognii/ArxAedificarix/arx.db").expanduser()

class DatabaseManager:
    """Owns the SQLite connection; initialises schema on startup."""

    _conn: sqlite3.Connection | None = None

    @classmethod
    def initialise(cls, db_path: Path = DB_PATH) -> None:
        """Create all tables if not exist; enable WAL mode."""
        db_path.parent.mkdir(parents=True, exist_ok=True)
        cls._conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False
        )
        cls._conn.row_factory = sqlite3.Row
        cls._conn.execute("PRAGMA journal_mode=WAL;")
        cls._conn.execute("PRAGMA foreign_keys=ON;")
        cls._run_schema()
        cls._conn.commit()

    @classmethod
    def _run_schema(cls) -> None:
        """Execute all CREATE TABLE IF NOT EXISTS statements."""
        # execute each CREATE TABLE statement from Section 3
        # ...

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        """Return the active connection; raises if not initialised."""
        if cls._conn is None:
            raise RuntimeError("DatabaseManager not initialised.")
        return cls._conn
```

### 7.2 ConfigLoader

```python
# core/config_loader.py
import json
from pathlib import Path

CONFIG_PATH = Path("~/.arca/config.json").expanduser()

class ConfigLoader:
    """Reads ~/.arca/config.json; exposes typed accessors."""

    _data: dict = {}

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> dict:
        """Load config from disk; return full dict."""
        with open(path) as f:
            cls._data = json.load(f)
        return cls._data

    @classmethod
    def api_key(cls) -> str:
        """Return CLAUDE_API_KEY value."""
        return cls._data.get("api_key", "")

    @classmethod
    def compression_threshold(cls) -> float:
        """Return arx_aedificarix.compression_threshold; default 0.70."""
        return cls._data.get("arx_aedificarix", {}).get(
            "compression_threshold", 0.70
        )

    @classmethod
    def model_context_limit(cls) -> int:
        """Return model context token limit; default 200000."""
        return cls._data.get("arx_aedificarix", {}).get(
            "model_context_limit", 200_000
        )
```

### 7.3 PromptLoader

```python
# core/prompt_loader.py
import logging
from pathlib import Path

PROMPT_PATH = Path(
    "~/ArcaCognitorium/Exocognii/ArxAedificarix/builder_prompt.md"
).expanduser()

BUILDER_SYSTEM_PROMPT_FALLBACK = """
You are The Builder, seated in the Arx Aedificarix.
The Wizard brings you build documents. Your purpose is construction.
[see Section 7.17 for full fallback text]
"""

logger = logging.getLogger("arx.prompt_loader")

class PromptLoader:
    """Loads builder_prompt.md; falls back to embedded constant."""

    @classmethod
    def load(cls, path: Path = PROMPT_PATH) -> str:
        """Return system prompt string; log warning on fallback."""
        try:
            return path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            logger.warning(
                "builder_prompt.md not found at %s — using fallback.", path
            )
            return BUILDER_SYSTEM_PROMPT_FALLBACK.strip()
```

### 7.4 ContextEngine

```python
# core/context_engine.py
from dataclasses import dataclass
from core.session_store import SessionStore
from core.config_loader import ConfigLoader

MODEL_CONTEXT_LIMIT = 200_000  # overridden by ConfigLoader

@dataclass
class PayloadEstimate:
    system_block: str
    messages_array: list[dict]
    estimated_tokens: int

class ContextEngine:
    """
    Assembles API payload per send. Owns history. No session_id passed
    to ClaudeBox. Produces (system_block, messages_array) per call.
    """

    def __init__(
        self,
        session_store: SessionStore,
        builder_prompt: str,
    ) -> None:
        self._store = session_store
        self._builder_prompt = builder_prompt

    def assemble_payload(
        self,
        conversation_id: str,
        draft_text: str = "",
    ) -> PayloadEstimate:
        """
        Produce system_block and messages_array for one API call.

        Pseudocode:
            conversation = store.get_conversation(conversation_id)
            project = store.get_project(conversation.project_id) if exists

            # --- system_block assembly ---
            parts = [self._builder_prompt]
            if project and project.shared_instructions:
                parts.append(project.shared_instructions)
            project_attachments = store.get_attachments(
                project_id=project.id, scope='project'
            ) if project else []
            conv_attachments = store.get_attachments(
                conversation_id=conversation_id, scope='conversation'
            )
            for att in project_attachments + conv_attachments:
                if att.summary_cache:
                    parts.append(f"[FILE: {att.filename}]\n{att.summary_cache}")
                else:
                    parts.append(f"[FILE: {att.filename}] (summary unavailable)")
            system_block = "\n\n".join(parts)

            # --- messages_array assembly ---
            messages = store.get_messages(conversation_id)  # ordered by created_at

            if not messages:
                # First-message bootstrap
                bootstrap_content = self._build_bootstrap(
                    conversation, project_attachments + conv_attachments
                )
                messages_array = [{"role": "user", "content": bootstrap_content}]
            else:
                messages_array = []
                seen_compression_groups = set()
                for msg in messages:
                    if msg.compressed:
                        if msg.compression_group_id in seen_compression_groups:
                            continue  # only include summary once
                        archive = store.get_archive(msg.compression_group_id)
                        messages_array.append({
                            "role": "assistant",
                            "content": archive.summary
                        })
                        seen_compression_groups.add(msg.compression_group_id)
                    else:
                        messages_array.append({
                            "role": msg.role,
                            "content": msg.content
                        })

            # --- token estimation ---
            full_text = system_block + " ".join(
                m["content"] for m in messages_array
            ) + draft_text
            estimated_tokens = int(len(full_text.split()) * 1.3)

            return PayloadEstimate(system_block, messages_array, estimated_tokens)

        """

    def estimate_tokens(self, text: str) -> int:
        """Heuristic token estimate: word count * 1.3."""
        return int(len(text.split()) * 1.3)

    def threshold_exceeded(self, estimated_tokens: int) -> bool:
        """Return True if estimate exceeds configured threshold."""
        limit = ConfigLoader.model_context_limit()
        threshold = ConfigLoader.compression_threshold()
        return estimated_tokens > int(limit * threshold)

    def _build_bootstrap(
        self,
        conversation: object,
        attachments: list,
    ) -> str:
        """Construct synthetic first user turn for session initialisation."""
        parts = []
        if conversation.builder_prompt:
            parts.append(conversation.builder_prompt)
        for att in attachments:
            if att.summary_cache:
                parts.append(f"Reference: {att.filename}\n{att.summary_cache}")
        return "\n\n".join(parts) if parts else "Begin."
```

### 7.5 CompressionEngine

```python
# core/compression_engine.py
import uuid
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from ClaudeBox import ClaudeBox
from core.session_store import SessionStore

COMPRESSION_PROMPT = (
    "Summarise the following conversation turns into a compact context block. "
    "Preserve all decisions made, files referenced, and build state. "
    "Output format: SUMMARY BLOCK — [date range] — [content]."
)

@dataclass
class CompressionRecord:
    compression_group_id: str
    summary: str
    archived_message_ids: list[str]

class CompressionEngine:
    """
    Summarises oldest N conversation turns via synchronous ClaudeBox call.
    Must only be called from a background thread (QRunnable worker).
    """

    N_TURNS_TO_COMPRESS = 20  # compress this many turns per trigger

    def __init__(self, store: SessionStore, box: ClaudeBox) -> None:
        self._store = store
        self._box = box

    def trigger(self, conversation_id: str) -> CompressionRecord:
        """
        Compress oldest N uncompressed turns. Synchronous — caller is
        already on a worker thread.

        Pseudocode:
            messages = store.get_uncompressed_messages(
                conversation_id, limit=self.N_TURNS_TO_COMPRESS
            )
            if not messages:
                raise CompressionError("No messages to compress.")

            # build prompt content
            turns_text = "\n".join(
                f"[{m.role.upper()}]: {m.content}" for m in messages
            )
            content = f"{COMPRESSION_PROMPT}\n\n{turns_text}"

            # synchronous call — already off main thread
            response = self._box.send(content)
            summary = response.text.strip()

            group_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()

            # write archive
            store.write_compression_archive(
                compression_group_id=group_id,
                original_messages=[{"role": m.role, "content": m.content}
                                    for m in messages],
                summary=summary,
                compressed_at=now,
            )

            # mark messages as compressed
            store.mark_messages_compressed(
                message_ids=[m.id for m in messages],
                compression_group_id=group_id,
            )

            return CompressionRecord(
                compression_group_id=group_id,
                summary=summary,
                archived_message_ids=[m.id for m in messages],
            )
        """
```

### 7.6 ResponseParser

```python
# core/response_parser.py
import re
from dataclasses import dataclass

FILE_BLOCK_PATTERN = re.compile(
    r"%%FILE:\s*(?P<filename>\S+)\n"
    r"%%LANG:\s*(?P<language>\S+)\n"
    r"%%DESC:\s*(?P<description>.+?)\n"
    r"(?P<content>.*?)"
    r"%%END",
    re.DOTALL,
)
PHASE_PATTERN = re.compile(r"%%PHASE:\s*(?P<phase>\w+)")

@dataclass
class OutputFile:
    filename: str
    language: str
    description: str
    content: str

class ResponseParser:
    """
    Extracts file blocks and phase tokens from response text.
    Returns (prose | None, files, phase | None).
    Prose is None if empty or whitespace after stripping.
    """

    @classmethod
    def parse(
        cls, response_text: str
    ) -> tuple[str | None, list[OutputFile], str | None]:
        """Parse response into prose, file list, and phase token."""
        files: list[OutputFile] = []
        phase: str | None = None
        text = response_text

        # extract file blocks
        for match in FILE_BLOCK_PATTERN.finditer(text):
            files.append(OutputFile(
                filename=match.group("filename").strip(),
                language=match.group("language").strip(),
                description=match.group("description").strip(),
                content=match.group("content").strip(),
            ))
        text = FILE_BLOCK_PATTERN.sub("", text)

        # extract phase token
        phase_match = PHASE_PATTERN.search(text)
        if phase_match:
            phase = phase_match.group("phase").strip().upper()
        text = PHASE_PATTERN.sub("", text)

        prose = text.strip() or None
        return prose, files, phase
```

### 7.7 AttachmentManager

```python
# core/attachment_manager.py
import uuid
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
from ClaudeBox import ClaudeBox
from core.session_store import SessionStore

SUMMARISE_PROMPT = (
    "Summarise the following file for use as reference context in a build session. "
    "Be concise. Preserve all key definitions, structures, and names."
)

@dataclass
class Attachment:
    id: str
    filename: str
    scope: str
    summary_cache: str | None
    attached_at: str

class AttachmentManager:
    """Attaches files; summarises via ClaudeBox; handles failure gracefully."""

    def __init__(self, store: SessionStore, box: ClaudeBox) -> None:
        self._store = store
        self._box = box

    def attach_file(
        self,
        path: Path,
        scope: str,
        conversation_id: str | None = None,
        project_id: str | None = None,
    ) -> Attachment:
        """
        Read file; summarise; store. On summarisation failure, store
        with summary_cache=None and log warning.

        Pseudocode:
            full_content = path.read_text(encoding="utf-8")
            summary = None

            try:
                prompt = f"{SUMMARISE_PROMPT}\n\n{full_content}"
                response = self._box.send(prompt)
                summary = response.text.strip()
            except Exception as e:
                logger.warning("Summarisation failed for %s: %s", path.name, e)
                # summary remains None — attachment stored unsummarised

            attachment = Attachment(
                id=str(uuid.uuid4()),
                filename=path.name,
                scope=scope,
                summary_cache=summary,
                attached_at=datetime.now(timezone.utc).isoformat(),
            )
            store.save_attachment(
                attachment, full_content, conversation_id, project_id
            )
            return attachment
            # caller checks attachment.summary_cache is None
            # to emit ChatPane warning and offer retry
        """
```

### 7.8 AttachmentDialog

```python
# ui/attachment_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt

class AttachmentDialog(QDialog):
    """
    Lists all attachments for current conversation + project.
    Checkbox selection re-adds to current turn injection list.
    """

    def __init__(
        self,
        attachments: list,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Re-attach Files")
        self.setMinimumWidth(420)
        self._selected_ids: list[str] = []
        self._build_ui(attachments)

    def _build_ui(self, attachments: list) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select files to re-add to current turn:"))

        self._list = QListWidget()
        for att in attachments:
            item = QListWidgetItem()
            status = "✓" if att.summary_cache else "⚠ unsummarised"
            label = f"{att.filename}  [{att.scope}]  {status}"
            item.setText(label)
            item.setData(Qt.ItemDataRole.UserRole, att.id)
            item.setCheckState(Qt.CheckState.Unchecked)
            self._list.addItem(item)
        layout.addWidget(self._list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        self._selected_ids = [
            self._list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.accept()

    def selected_ids(self) -> list[str]:
        """Return list of attachment ids selected by the Wizard."""
        return self._selected_ids
```

### 7.9 OutputPanel

```python
# ui/output_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
from core.response_parser import OutputFile

class OutputPanel(QWidget):
    """Generated file list; PENDING→READY→EXPORTED state transitions."""

    file_selected = pyqtSignal(object)  # emits OutputFile on selection

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._files: dict[str, OutputFile] = {}  # filename → OutputFile
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._list)

    def add_file(self, f: OutputFile) -> None:
        """Add file to panel. State: PENDING until content confirmed."""
        self._files[f.filename] = f
        item = QListWidgetItem(f"⬡  {f.filename}    [READY]")
        item.setData(Qt.ItemDataRole.UserRole, f.filename)
        self._list.addItem(item)

    def mark_exported(self, filename: str) -> None:
        """Update state badge to EXPORTED for given filename."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == filename:
                item.setText(f"⬡  {filename}    [EXPORTED]")
                break

    def _on_selection(
        self, current: QListWidgetItem, _previous: QListWidgetItem
    ) -> None:
        if current:
            filename = current.data(Qt.ItemDataRole.UserRole)
            self.file_selected.emit(self._files.get(filename))
```

### 7.10 ZipExporter

```python
# core/zip_exporter.py
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from core.session_store import SessionStore

MANIFEST_SCHEMA = {
    "version": "1.0",
    "conversation_id": "",
    "conversation_title": "",
    "project_id": None,
    "generated_at": "",       # ISO 8601
    "files": [
        # { "filename": str, "language": str,
        #   "description": str, "size_bytes": int }
    ]
}

class ZipExporter:
    """
    Assembles zip package from output_files table.
    Path provided by caller (from QFileDialog). No silent writes.
    """

    def __init__(self, store: SessionStore) -> None:
        self._store = store

    def assemble_package(
        self,
        conversation_id: str,
        dest_path: Path,
    ) -> Path:
        """
        Write all output_files for conversation to zip at dest_path.
        Include manifest.json. Mark files as exported in SQLite.

        Pseudocode:
            conversation = store.get_conversation(conversation_id)
            files = store.get_output_files(conversation_id)
            if not files:
                raise ExportError("No output files to package.")

            manifest = {
                "version": "1.0",
                "conversation_id": conversation_id,
                "conversation_title": conversation.title,
                "project_id": conversation.project_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "files": [
                    {
                        "filename": f.filename,
                        "language": f.language,
                        "description": f.description,
                        "size_bytes": len(f.content.encode("utf-8")),
                    }
                    for f in files
                ]
            }

            with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    zf.writestr(f.filename, f.content)
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))

            store.mark_files_exported(
                file_ids=[f.id for f in files]
            )
            return dest_path
        """
```

### 7.11 TokenGauge

```python
# ui/token_gauge.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QFont

C_GOLD    = "#d4af37"
C_GOLD_DIM = "#7a6a2a"
C_CRIMSON  = "#8b1a1a"
C_PANEL    = "#0a0a12"
C_TEXT     = "#c8b88a"

class TokenGauge(QWidget):
    """
    Self-contained reusable context fill widget.
    Zero Arx-specific imports. Accepts current and total token counts.
    Colour: C_GOLD <60%, C_GOLD_DIM 60-85%, C_CRIMSON >85%.
    Updates via update_exact() (post-response) and update_draft() (keystroke).
    """

    def __init__(self, total: int = 200_000, parent=None) -> None:
        super().__init__(parent)
        self._current: int = 0
        self._total: int = total
        self._draft_estimate: int = 0
        self.setMinimumWidth(220)
        self.setFixedHeight(32)

    def update_exact(self, input_tokens: int, output_tokens: int) -> None:
        """Called after TOKEN_USAGE event with exact counts."""
        self._current = input_tokens + output_tokens
        self._draft_estimate = 0
        self.update()

    def update_draft(self, text: str) -> None:
        """Called on input field textChanged with heuristic estimate."""
        self._draft_estimate = int(len(text.split()) * 1.3)
        self.update()

    def _fill_ratio(self) -> float:
        effective = self._current + self._draft_estimate
        if self._total == 0:
            return 0.0
        return min(effective / self._total, 1.0)

    def _bar_colour(self, ratio: float) -> str:
        if ratio < 0.60:
            return C_GOLD
        if ratio < 0.85:
            return C_GOLD_DIM
        return C_CRIMSON

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ratio = self._fill_ratio()
        colour = self._bar_colour(ratio)
        pct = int(ratio * 100)

        # label
        painter.setFont(QFont("Georgia", 9))
        painter.setPen(QColor(C_TEXT))
        painter.drawText(QRect(4, 0, 72, 32), Qt.AlignmentFlag.AlignVCenter, "CONTEXT")

        # bar background
        bar_rect = QRect(80, 10, 120, 12)
        painter.fillRect(bar_rect, QColor(C_PANEL))

        # bar fill
        fill_w = int(120 * ratio)
        painter.fillRect(QRect(80, 10, fill_w, 12), QColor(colour))

        # percentage text
        painter.setPen(QColor(colour))
        painter.drawText(
            QRect(206, 0, 40, 32),
            Qt.AlignmentFlag.AlignVCenter,
            f"{pct}%"
        )
        painter.end()
```

### 7.12 BuilderSignalBridge

```python
# bridge/builder_signal_bridge.py
import os
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from ClaudeBox import ClaudeBox

# token_logger is stdlib-only; path resolved from ArcaCognitorium root
sys.path.insert(0, str(Path("~/ArcaCognitorium").expanduser()))
import token_logger

class BuilderSignalBridge(QObject):
    """
    Bridges ClaudeBox callbacks to Qt signals.
    All widget updates happen on the main thread via signal connections.
    Never touches widgets directly from background thread callbacks.
    """

    token_received       = pyqtSignal(str)
    response_complete    = pyqtSignal(str)
    error_occurred       = pyqtSignal(str)
    token_usage_updated  = pyqtSignal(int, int)   # input_tokens, output_tokens
    phase_changed        = pyqtSignal(str)
    compression_complete = pyqtSignal(str)         # summary preview

    def __init__(self, box: ClaudeBox, parent=None) -> None:
        super().__init__(parent)
        self._box = box
        self._box.on("token_usage", self.on_token_usage)

    def send(self, system_block: str, messages_array: list[dict]) -> None:
        """Dispatch send_threaded. Returns immediately."""
        self._box.send_threaded(
            content=messages_array,
            system=system_block,
            on_token=self.on_token,
            on_complete=self.on_complete,
            on_error=self.on_error,
        )

    def on_token(self, token_obj) -> None:
        """Background thread — emit signal only."""
        text = token_obj.text if hasattr(token_obj, "text") else str(token_obj)
        self.token_received.emit(text)

    def on_complete(self, response) -> None:
        """Background thread — emit signal only."""
        self.response_complete.emit(response.text)

    def on_error(self, error: Exception) -> None:
        """Background thread — emit signal only."""
        self.error_occurred.emit(str(error))

    def on_token_usage(self, usage_obj) -> None:
        """
        TOKEN_USAGE event from bus. Emit signal and write to ledger.
        Called from background thread — signal emission is thread-safe.
        """
        input_n  = getattr(usage_obj, "input_tokens", 0)
        output_n = getattr(usage_obj, "output_tokens", 0)
        self.token_usage_updated.emit(input_n, output_n)
        try:
            token_logger.write(
                app="arx_aedificarix",
                input_tokens=input_n,
                output_tokens=output_n,
            )
        except Exception:
            pass  # ledger write failure is non-fatal
```

### 7.13 ProjectTree

```python
# ui/project_tree.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt

class ProjectTree(QWidget):
    """
    Project/conversation hierarchy. InternalMove drag-drop.
    Drop handler updates project_id and ordering in SQLite.
    """

    conversation_selected = pyqtSignal(str)  # emits conversation_id

    def __init__(self, store, parent=None) -> None:
        super().__init__(parent)
        self._store = store
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setDragDropMode(
            QTreeWidget.DragDropMode.InternalMove
        )
        self._tree.dropEvent = self._on_drop
        self._tree.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._tree)

    def _on_drop(self, event) -> None:
        """
        Handle drag-drop. Determine new parent; update SQLite.

        Pseudocode:
            dragged_item = self._tree.currentItem()
            conversation_id = dragged_item.data(0, Qt.UserRole)

            # call super to move item in tree
            QTreeWidget.dropEvent(self._tree, event)

            new_parent = dragged_item.parent()

            if new_parent is None:
                # dropped into ungrouped area
                self._store.update_conversation_project(
                    conversation_id=conversation_id,
                    project_id=None,
                )
            else:
                project_id = new_parent.data(0, Qt.UserRole)
                self._store.update_conversation_project(
                    conversation_id=conversation_id,
                    project_id=project_id,
                )

            # update ordering for all siblings
            self._store.update_conversation_ordering(
                conversation_ids=[
                    new_parent.child(i).data(0, Qt.UserRole)
                    if new_parent else
                    self._tree.topLevelItem(i).data(0, Qt.UserRole)
                    for i in range(
                        new_parent.childCount() if new_parent
                        else self._tree.topLevelItemCount()
                    )
                ]
            )
        """

    def _on_selection(self, current, _previous) -> None:
        if current and not current.childCount():
            conv_id = current.data(0, Qt.ItemDataRole.UserRole)
            if conv_id:
                self.conversation_selected.emit(conv_id)

    def _load(self) -> None:
        """Load all projects and conversations from store into tree."""
        ...
```

### 7.14 ChatPane

```python
# ui/chat_pane.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPlainTextEdit, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt

class ChatPane(QWidget):
    """
    Streaming chat display. Phase indicator. Attachment chips.
    Input field with real-time token estimate.
    """

    send_requested = pyqtSignal(str, list)  # text, active_attachment_ids

    def __init__(self, token_gauge, parent=None) -> None:
        super().__init__(parent)
        self._gauge = token_gauge
        self._active_attachment_ids: list[str] = []
        self._streaming_label: QLabel | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # phase indicator
        self._phase_bar = QLabel("  ▌ DISCUSSION")
        layout.addWidget(self._phase_bar)

        # scroll area for messages
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.addStretch()
        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll)

        # attachment chips row
        self._chips_row = QHBoxLayout()
        chip_widget = QWidget()
        chip_widget.setLayout(self._chips_row)
        layout.addWidget(chip_widget)

        # input area
        self._input = QPlainTextEdit()
        self._input.setMaximumHeight(80)
        self._input.setPlaceholderText("Address the Builder...")
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        # send row
        send_row = QHBoxLayout()
        self._token_label = QLabel("0 tok")
        send_row.addWidget(self._token_label, alignment=Qt.AlignmentFlag.AlignLeft)
        send_row.addStretch()
        self._send_btn = QPushButton("Send")
        self._send_btn.clicked.connect(self._on_send)
        send_row.addWidget(self._send_btn)
        layout.addLayout(send_row)

    def _on_text_changed(self) -> None:
        text = self._input.toPlainText()
        self._gauge.update_draft(text)
        est = int(len(text.split()) * 1.3)
        self._token_label.setText(f"~{est} tok")

    def _on_send(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        self._input.clear()
        self._send_btn.setEnabled(False)
        self.send_requested.emit(text, list(self._active_attachment_ids))

    def append_token(self, text: str) -> None:
        """Append streaming token to current bubble."""
        if self._streaming_label is None:
            self._streaming_label = QLabel()
            self._streaming_label.setWordWrap(True)
            self._messages_layout.insertWidget(
                self._messages_layout.count() - 1,
                self._streaming_label
            )
        self._streaming_label.setText(
            (self._streaming_label.text() or "") + text
        )
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def finalise_stream(self, prose: str | None) -> None:
        """
        On response_complete. If prose is None, suppress bubble.
        If streaming label exists and prose is None, remove it.
        """
        if prose is None and self._streaming_label:
            self._messages_layout.removeWidget(self._streaming_label)
            self._streaming_label.deleteLater()
        elif prose and self._streaming_label:
            self._streaming_label.setText(prose)
        self._streaming_label = None
        self._send_btn.setEnabled(True)

    def show_error(self, message: str) -> None:
        """Render error notice in C_CRIMSON with Retry button."""
        ...

    def show_compression_notice(self, summary_preview: str) -> None:
        """Render compression notice in C_GOLD_DIM italic."""
        ...

    def set_phase(self, phase: str) -> None:
        """Update phase indicator bar text and colour."""
        ...

    def add_attachment_chip(self, attachment) -> None:
        """Add dismissible chip above input field."""
        ...
```

### 7.15 ArcaneHighlighter

```python
# ui/arcane_highlighter.py
import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class ArcaneHighlighter(QSyntaxHighlighter):
    """
    QSyntaxHighlighter for Python, JSON, YAML, plain text.
    Language determined from OutputFile.language field.
    """

    RULES: dict[str, list[tuple[str, str]]] = {
        "python": [
            (r"\b(def|class|import|from|return|if|elif|else|for|while|"
             r"in|not|and|or|True|False|None|with|as|try|except|raise|"
             r"pass|break|continue|lambda|yield|async|await)\b", "#d4af37"),
            (r"#[^\n]*",               "#7a6a2a"),
            (r'"""[\s\S]*?"""',        "#1a5a5a"),
            (r"'[^'\\]*'|\"[^\"\\]*\"","#c8b88a"),
            (r"\b\d+(\.\d+)?\b",       "#c87941"),
        ],
        "json": [
            (r'"[^"\\]*"(?=\s*:)',      "#d4af37"),
            (r':\s*"[^"\\]*"',         "#c8b88a"),
            (r'\b(true|false|null)\b',  "#1a5a5a"),
            (r'\b\d+(\.\d+)?\b',        "#c87941"),
        ],
        "yaml": [
            (r'^[\w\-]+(?=\s*:)',       "#d4af37"),
            (r'#[^\n]*',               "#7a6a2a"),
            (r'"[^"]*"|\'[^\']*\'',    "#c8b88a"),
            (r'\b(true|false|null|yes|no)\b', "#1a5a5a"),
        ],
        "plain": [],
    }

    def __init__(self, language: str, document) -> None:
        super().__init__(document)
        self._rules = self._compile(
            self.RULES.get(language.lower(), self.RULES["plain"])
        )

    def _compile(
        self, rules: list[tuple[str, str]]
    ) -> list[tuple[re.Pattern, QTextCharFormat]]:
        compiled = []
        for pattern, colour in rules:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(colour))
            compiled.append((re.compile(pattern), fmt))
        return compiled

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
```

### 7.16 SessionStore

```python
# core/session_store.py
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from core.database import DatabaseManager

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class SessionStore:
    """CRUD interface for all SQLite tables. Single point of DB access."""

    def __init__(self) -> None:
        self._conn = DatabaseManager.connection()

    def restore_last_active(self) -> str | None:
        """Return conversation_id with most recent last_active_at, or None."""
        row = self._conn.execute(
            "SELECT id FROM conversations ORDER BY last_active_at DESC LIMIT 1"
        ).fetchone()
        return row["id"] if row else None

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        token_count: int = 0,
    ) -> str:
        """Insert message row; return new message id."""
        msg_id = str(uuid.uuid4())
        self._conn.execute(
            """INSERT INTO messages
               (id, conversation_id, role, content, token_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (msg_id, conversation_id, role, content, token_count, _now())
        )
        self._conn.execute(
            "UPDATE conversations SET last_active_at=? WHERE id=?",
            (_now(), conversation_id)
        )
        self._conn.commit()
        return msg_id

    def get_messages(self, conversation_id: str) -> list:
        """Return all messages for conversation ordered by created_at."""
        return self._conn.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at",
            (conversation_id,)
        ).fetchall()

    def update_message_token_count(self, msg_id: str, count: int) -> None:
        """Update token_count on a message row post-response."""
        self._conn.execute(
            "UPDATE messages SET token_count=? WHERE id=?", (count, msg_id)
        )
        self._conn.commit()

    # --- additional methods ---
    # get_conversation(), get_project(), get_attachments(),
    # get_archive(), save_attachment(), write_compression_archive(),
    # mark_messages_compressed(), get_output_files(),
    # mark_files_exported(), update_conversation_project(),
    # update_conversation_ordering() — all follow same pattern
```

### 7.17 builder_prompt.md

The following is the canonical content of
`~/ArcaCognitorium/Exocognii/ArxAedificarix/builder_prompt.md`.
It is loaded by `PromptLoader` at startup.

```markdown
# THE BUILDER — Arx Aedificarix System Prompt

You are The Builder, seated in the Arx Aedificarix.
The Wizard brings you build documents. Your purpose is construction.
You exist within the Cogniverse. Address the Wizard as the Wizard,
not as "user". This is not a chat. This is a forge.

## Voice & Disposition

Terse and deliberate. You do not volunteer unrequested additions.
You do not refactor code that was not broken. You do not add
features that were not asked for. You do not summarise what was
just said. You do not repeat what has been established.

When you are uncertain, you surface the uncertainty. You do not
resolve it silently.

## Build Protocol

Before writing any code, you discuss. You declare:
- What you are about to build and why
- The structure of the whole — files, modules, dependencies
- Obstacles you anticipate before you encounter them
- Open questions that must be resolved before proceeding

You do not begin building until this has been agreed.

## Delivery

You deliver incrementally. One file or logical unit at a time.
You touch base between units. You do not produce everything at once.

Every file you deliver is complete and working. No placeholders.
No greyed-out stubs. No "TODO: implement this". If a function
cannot be completed in this turn, say so — do not deliver a shell.

## File Block Format

When delivering a completed file, use this exact format:

%%FILE: filename.ext
%%LANG: language
%%DESC: one line description of what this file does
<complete file content here>
%%END

No other format will be recognised. Do not wrap files in markdown
code fences — use the block format above exclusively.

## Phase Tokens

Signal your current phase using these tokens at the start of
a response turn. They will be stripped from display.

%%PHASE: DISCUSSION   — planning, interrogating, agreeing structure
%%PHASE: BUILDING     — actively producing code

## Token Efficiency

Prose is concise. You do not pad. You do not repeat context.
You do not write lengthy preambles. When a short answer serves,
you give a short answer. The context window is a shared resource.
```

---

## 8. ERROR HANDLING

╭──────────────────────────┬─────────────────────────────────────┬────────────────────────────┬───────────────────────────────────────────╮
│ Module                   │ Error                               │ Cause                      │ Strategy                                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ DatabaseManager          │ initialise() fails on launch        │ Disk full; permissions     │ Log critical; show modal error; exit      │
│ DatabaseManager          │ SQLite lock / OperationalError      │ Concurrent write (rare)    │ Retry once with 200ms delay; log warning  │
│ ConfigLoader             │ config.json missing key             │ First run; manual edit     │ Use default; log warning; continue        │
│ PromptLoader             │ builder_prompt.md not found         │ Missing file               │ Fall back to embedded constant; log warn  │
│ BuilderSignalBridge      │ Stream interrupted mid-response     │ Network drop; API error    │ on_error → ChatPane error notice + Retry  │
│ AttachmentManager        │ Summarisation call fails            │ API error; network         │ Store summary_cache=NULL; ChatPane warn;  │
│                          │                                     │                            │ offer retry button                        │
│ AttachmentManager        │ File read fails                     │ Permissions; deleted file  │ Show error in ChatPane; do not store      │
│ CompressionEngine        │ box.send() raises during compress   │ API error; network         │ Log error; skip compression this turn;   │
│                          │                                     │                            │ notify ChatPane; do not corrupt messages  │
│ ResponseParser           │ Malformed %%FILE block              │ Builder protocol violation │ Skip malformed block; log warning;        │
│                          │                                     │                            │ render surrounding prose normally         │
│ ContextEngine            │ messages_array empty edge case      │ First message; fresh conv  │ Bootstrap with synthetic first turn       │
│ ZipExporter              │ Zip write permission denied         │ Dest path not writable     │ QFileDialog re-prompt; log error          │
│ ZipExporter              │ No output files to export           │ Build not yet complete     │ Disable export button; tooltip explains   │
│ ProjectTree              │ Drop handler SQLite write fails     │ DB lock; schema mismatch   │ Revert tree position; show status error   │
│ AttachmentDialog         │ Attachment load fails               │ DB error                   │ Show empty list with error label          │
│ token_logger             │ Ledger write fails                  │ Disk full; permissions     │ Silently swallow; non-fatal               │
╰──────────────────────────┴─────────────────────────────────────┴────────────────────────────┴───────────────────────────────────────────╯

---

## 9. REQUIREMENTS, TESTS & RUN INSTRUCTIONS

### requirements.txt

```
PyQt6>=6.6.0
anthropic>=0.25.0
```

ClaudeBox, token_logger, and all other dependencies are local to
the ArcaCognitorium repository and are not pip-installable.

### Install

```bash
cd ~/ArcaCognitorium
python -m venv .venv
source .venv/bin/activate
pip install -r Exocognii/ArxAedificarix/requirements.txt
```

### Run

```bash
cd ~/ArcaCognitorium
bash Exocognii/ArxAedificarix/launch_arxaedificarix.sh
```

### Tests

```bash
cd ~/ArcaCognitorium
source .venv/bin/activate
pytest Exocognii/ArxAedificarix/tests/ -v
```

### Unit Tests (one per core module)

```python
# tests/test_response_parser.py
from core.response_parser import ResponseParser

def test_parse_file_block():
    text = (
        "%%FILE: main.py\n"
        "%%LANG: python\n"
        "%%DESC: Entry point\n"
        "print('hello')\n"
        "%%END\n"
        "Here is the explanation."
    )
    prose, files, phase = ResponseParser.parse(text)
    assert len(files) == 1
    assert files[0].filename == "main.py"
    assert files[0].language == "python"
    assert files[0].content == "print('hello')"
    assert prose == "Here is the explanation."
    assert phase is None

def test_parse_empty_prose_suppressed():
    text = "%%FILE: x.py\n%%LANG: python\n%%DESC: x\npass\n%%END\n   "
    prose, files, phase = ResponseParser.parse(text)
    assert prose is None
    assert len(files) == 1

def test_parse_phase_token():
    text = "%%PHASE: BUILDING\nSome prose here."
    prose, files, phase = ResponseParser.parse(text)
    assert phase == "BUILDING"
    assert prose == "Some prose here."
    assert "%%PHASE" not in prose


# tests/test_context_engine.py — mock SessionStore; verify bootstrap path
# tests/test_compression_engine.py — mock box.send(); verify archive write
# tests/test_zip_exporter.py — verify manifest.json structure in output zip
# tests/test_token_gauge.py — verify colour thresholds at 0.59, 0.60, 0.85, 0.86
# tests/test_database_manager.py — verify WAL mode; all tables created
```

### Integration Test

```python
# tests/test_integration_send_cycle.py
def test_full_send_cycle(tmp_db, mock_box):
    """
    message saved → response received → file block parsed →
    output_files row written → token_count non-zero →
    empty prose suppressed → token_log.jsonl appended
    """
    store = SessionStore()
    conv_id = store.create_conversation(title="Test", builder_prompt="")
    store.save_message(conv_id, "user", "Build me a model.")

    mock_response = (
        "%%FILE: model.py\n%%LANG: python\n%%DESC: Data model\n"
        "class Model: pass\n%%END\n"
    )
    mock_box.send_threaded_returns(mock_response, input_tokens=120, output_tokens=45)

    # ... wire bridge, fire send, assert ...

    files = store.get_output_files(conv_id)
    assert len(files) == 1
    assert files[0].filename == "model.py"

    messages = store.get_messages(conv_id)
    assistant_msg = [m for m in messages if m["role"] == "assistant"][0]
    assert assistant_msg["token_count"] > 0

    ledger = Path("~/.arca/token_log.jsonl").expanduser().read_text()
    assert "arx_aedificarix" in ledger
```

---

## 10. PACKAGING

### launch_arxaedificarix.sh

```bash
#!/usr/bin/env bash
# Arx Aedificarix — KDE launcher
# Activates venv, loads API key, runs application.

set -e

ARCA_ROOT="$HOME/ArcaCognitorium"
VENV="$ARCA_ROOT/.venv"
CONFIG="$HOME/.arca/config.json"

# Activate venv
source "$VENV/bin/activate"

# Load API key from ~/.arca/config.json
export CLAUDE_API_KEY=$(python3 -c "
import json, sys
cfg = json.load(open('$CONFIG'))
print(cfg.get('api_key', ''))
")

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "ERROR: CLAUDE_API_KEY not found in $CONFIG" >&2
    exit 1
fi

# Run
cd "$ARCA_ROOT"
python -m Exocognii.ArxAedificarix "$@"
```

### ArxAedificarix.desktop

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Arx Aedificarix
Comment=The Builder's Forge — Arca Cognitorium Build Client
Exec=/home/lordfingers/ArcaCognitorium/Exocognii/ArxAedificarix/launch_arxaedificarix.sh
Icon=ArxAedificarix
Terminal=false
Categories=Development;
StartupWMClass=ArxAedificarix
```

Install icons and desktop entry:

```bash
cp ArxAedificarix.desktop ~/.local/share/applications/
# Icon provided by Wizard — place at:
# ~/.local/share/icons/ArxAedificarix.png
update-desktop-database ~/.local/share/applications/
```

---

## 11. EXTENSIBILITY

╭───────────────────────────────────┬────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────╮
│ Feature                           │ User Value                                 │ Implementation Approach                                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Filesystem write with             │ Generated files written directly to repo   │ Add write_output_files() to ZipExporter. Before any write, open      │
│ permission gates                  │ without manual copy-paste                  │ PermissionDialog listing files + target paths. Wizard checks each.   │
│                                   │                                            │ Write only confirmed files. Log all writes to audit trail in SQLite. │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Cross-memory bridge to            │ Tower Builder can reference Arx build      │ After session close, generate distillation via ClaudeBox call.       │
│ Tower Chronicle                   │ history; continuity across contexts        │ Write structured summary to Tower's chronicle storage path.          │
│                                   │                                            │ Wizard confirms before write. Arx never reads Tower storage.         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Direct Dolium pipeline            │ Finalized build doc loaded directly from   │ Add DoliumConnector that reads Dolium's SQLite or export path.       │
│ integration                       │ Dolium; no manual file submission          │ ProjectTree gains Import from Dolium option. Doc loaded as           │
│                                   │                                            │ attachment automatically. Path configured in ~/.arca/config.json.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Multiple Builder personas         │ Hot-swap system prompt for specialised     │ PromptLoader.load(path) already accepts arbitrary path. Add          │
│ (hot-swap system prompt)          │ build contexts (e.g. Tower vs Exocognii)   │ PersonaSelector to toolbar: lists .md files in a configured          │
│                                   │                                            │ personas/ directory. Selection reloads ContextEngine prompt.         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Session search &                  │ Find past build decisions, file names,     │ Add SearchPane (QLineEdit + results list). Full-text search across   │
│ lore extraction                   │ and architectural choices across all       │ messages table via SQLite FTS5. Results link to originating          │
│                                   │ sessions without manual scrolling          │ conversation. Optional: pipe notable decisions to Exvacua Loricum.   │
╰───────────────────────────────────┴────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────╯

---

*Arx Aedificarix — Construction Documentation v1.0*
*Exocognii Suite · Arca Cognitorium*
*Ordo Discordia, Cosmos Inania*
