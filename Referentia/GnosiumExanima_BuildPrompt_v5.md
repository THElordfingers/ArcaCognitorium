# GNOSIUM EXANIMA — IdeaForge Phase 2+3 Build Prompt
### v5 — Refined (5 Cycles)
*Arca Cognitorium — Exocognii Suite*

---

## Refinement Log

╭─────────────────────────────────────────────────────────────────╮
│  CYCLE 1 — Structural Gaps                                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  · Missing startup sequence — what loads in what order           │
│  · No empty-vault state — what does the Wizard see with no       │
│    entity packages?                                              │
│  · No session management UI — how are sessions listed,           │
│    switched, titled, deleted?                                    │
│  · Configuus integration unspecified — service URLs, repo path   │
│  · Window geometry persistence missing                           │
╰─────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────╮
│  CYCLE 2 — User Simulation Gaps                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  · Wizard addresses specific entity by name in Chamber — how?    │
│  · Multi-entity response rendering — name prefix, colour?        │
│  · Token warning UX — what does the Wizard see and do?           │
│  · Mode switch mid-conversation — ClaudeBox rebuild mechanics    │
│  · Portrait display sizing and layout unspecified                │
╰─────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────╮
│  CYCLE 3 — Composite Prompt Specificity                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  · Exact composite prompt structure needed — preamble format,    │
│    entity section delimiters, response format instruction         │
│  · Distillation mechanics — what triggers it, what model call,   │
│    where stored, how re-seeded                                   │
│  · Mundana message format and what GNOSIUM does with the data    │
╰─────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────╮
│  CYCLE 4 — Error Path Hardening                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  · Malformed entity package (missing role.yaml) — skip or warn?  │
│  · ClaudeBox streaming failure mid-response — partial display?   │
│  · Token budget threshold scope — system prompt only, or         │
│    system prompt + history?                                      │
│  · NUNTIUS POST failure — silent or logged?                      │
│  · SQLite write failure — conversation lost?                     │
╰─────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────╮
│  CYCLE 5 — Final Polish                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  · All module names concrete and final                           │
│  · All paths absolute                                            │
│  · All config keys named                                         │
│  · Redundancy removed from prompt body                           │
│  · Extensibility section sharpened with implementation notes      │
╰─────────────────────────────────────────────────────────────────╯

---

## Refined Prompt

```
You are a senior software architect writing for a senior developer
working within the Arca Cognitorium ecosystem. Produce complete,
developer-ready construction documentation for "GNOSIUM EXANIMA" —
a Debian Trixie / KDE Plasma 6 desktop application built with
Python 3.11 + PyQt6.

GNOSIUM EXANIMA is a standalone overseer chat interface for
conversing with Tower entities, testing entity packages, and
maintaining ambient awareness across the Exocognii suite. It runs
independently — not embedded in the Tower, not paired in-process
with PRAESIDIUM, not responsible for code generation (that is Arx
Aedificarix), not responsible for entity creation (that is ENTITEX).

It lives at ~/ArcaCognitorium/Exocognii/GnosiumExanima/.
Venv: venv-GNOSIUM.

════════════════════════════════════════════════════════════════
 ARCHITECTURE
════════════════════════════════════════════════════════════════

Two conversation modes:

  CHAMBER — shared thread, multiple active entities. Single
  ClaudeBox instance with composite system prompt. All active
  entities see the same context. Personality-driven self-selection
  determines which entities respond — no round-robin, no per-entity
  API call. One API call per Wizard message. Claude reads the room
  based on each entity's role.yaml and traits.yaml and voices
  whoever has something to say. Could be one entity, could be
  several, could be none until the Wizard prompts one by name.

  The Wizard can address a specific entity by prefixing their name:
  "Contrarian, what do you think?" — the composite prompt instructs
  the model to prioritise the named entity in that case while
  allowing others to contribute if relevant.

  SOLO — single entity, private thread. One ClaudeBox instance, one
  entity's system prompt. Isolated conversation history.

Both modes maintain independent session threads. Switching from
Chamber to Solo does not destroy the Chamber thread. Switching back
reloads it. Each mode switch rebuilds the ClaudeBox instance with
the appropriate system prompt and reloads history via
replace_history().

════════════════════════════════════════════════════════════════
 STARTUP SEQUENCE
════════════════════════════════════════════════════════════════

On launch, in order:

  1. Read ~/.arca/config.json (Configuus) for:
       arca_repo_path   — ClaudeBox import path
       service URLs     — Exvacua Loricum, Perpetuum Aedificare,
                          Praesidium endpoints
  2. sys.path.insert for ClaudeBox import
  3. Initialise SQLite store at
       Exocognii/GnosiumExanima/storage/gnosium.db
     Run CREATE TABLE IF NOT EXISTS for all tables
  4. Scan ENTITEX vault at
       Exocognii/Entitex/vault/
     Each subdirectory is an entity package. Validate: must contain
     role.yaml and traits.yaml at minimum. Packages missing either
     are skipped with a warning logged to stderr — not shown in UI
     unless zero valid packages found.
  5. Restore last window geometry from
       Exocognii/GnosiumExanima/storage/window_state.json
  6. Restore last session if one exists — reload mode, active
     entities, conversation history
  7. Attempt Mundana State Bus connection (non-blocking). If
     unavailable, status strip shows disconnected — app functions
     fully without it.
  8. UI ready.

Empty vault state: if zero valid entity packages found, show a
centred message in the conversation area: "No entity packages found
in vault. Use ENTITEX to generate entity packages." Entity panel
is empty but visible. All other UI functional.

════════════════════════════════════════════════════════════════
 ENTITY SYSTEM
════════════════════════════════════════════════════════════════

Entities load from ENTITEX vault at:
  ~/ArcaCognitorium/Exocognii/Entitex/vault/{entity_id}/

Each entity package contains:
  role.yaml    — purpose, domain, behavioural directives
  traits.yaml  — personality, temperament, communication style
  lore.yaml    — backstory, relationships, canonical position
                 (optional — entity functions without it)
  portrait.png — entity portrait image (optional — show placeholder
                 silhouette if missing)

Entity panel (left side of window):
  - Scrollable list of all valid entity packages from vault
  - Each entry: portrait thumbnail (48x48), entity name, toggle
    checkbox (Chamber mode) or radio button (Solo mode)
  - Active entities highlighted with C_GOLD border on portrait
  - Panel header shows current mode: "CHAMBER" or "SOLO"
  - Mode switch control at top of panel

Toggling an entity on/off in Chamber mode:
  1. Rebuild composite system prompt from all currently active
     entities
  2. Destroy current ClaudeBox instance
  3. Create new ClaudeBox with updated system prompt
  4. Reload conversation history via replace_history()
  5. Token budget check — warn if composite system prompt exceeds
     threshold

Tower memory seed: on entity load, read Tower entity memory at
  ~/ArcaCognitorium/storage/entities/{entity_id}/memory.json
if it exists. Include as context block in that entity's system
prompt section. Read-only — GNOSIUM never writes to this path.

════════════════════════════════════════════════════════════════
 COMPOSITE SYSTEM PROMPT STRUCTURE
════════════════════════════════════════════════════════════════

Chamber mode composite prompt, assembled in this order:

  ┌─────────────────────────────────────────────────────────┐
  │  PREAMBLE                                               │
  │  You are operating in the GNOSIUM EXANIMA chamber.      │
  │  Multiple entities are present. For each response,      │
  │  speak as whichever entity or entities have something    │
  │  relevant to contribute. Prefix each entity's speech    │
  │  with their name in square brackets, e.g.:              │
  │  [The Contrarian] I disagree because...                 │
  │  [The Socratic] But have you considered...              │
  │                                                         │
  │  If the Wizard addresses an entity by name, that        │
  │  entity responds first. Others may follow if relevant.  │
  │  If no entity has a strong opinion, say so briefly.     │
  │  Do not force participation.                            │
  ├─────────────────────────────────────────────────────────┤
  │  ENTITY BLOCK: {entity_name}                            │
  │  --- role.yaml content ---                              │
  │  --- traits.yaml content ---                            │
  │  --- Tower memory seed (if exists) ---                  │
  │  (repeated per active entity)                           │
  ├─────────────────────────────────────────────────────────┤
  │  CONTEXT BLOCK (optional)                               │
  │  Ambient Mundana state summary if connected.            │
  │  Injected only if state has changed since last send.    │
  └─────────────────────────────────────────────────────────┘

Solo mode: preamble simplified to "You are {entity_name}",
followed by that entity's role.yaml + traits.yaml + Tower
memory seed. No multi-entity prefix instruction.

════════════════════════════════════════════════════════════════
 CONVERSATION RENDERING
════════════════════════════════════════════════════════════════

Chat area (centre of window):
  - Wizard messages: right-aligned, C_GOLD text on dark bubble
  - Entity responses: left-aligned, C_TEAL text on dark bubble
  - In Chamber mode, entity name prefix rendered in C_CRIMSON
    bold before the entity's text within the bubble
  - Streaming: tokens append in real-time to the current
    response bubble
  - Scroll-to-bottom on new message. Manual scroll-up pauses
    auto-scroll until the Wizard scrolls back to bottom.
  - Timestamps shown on hover, not inline

════════════════════════════════════════════════════════════════
 SESSION MANAGEMENT
════════════════════════════════════════════════════════════════

Session list (accessible via panel or menu):
  - Shows all sessions with title, mode, date, entity count
  - Sessions auto-titled from first Wizard message (first 60
    chars). Editable by Wizard.
  - Create new session: resets conversation, preserves current
    entity selection and mode
  - Switch session: saves current, loads selected, rebuilds
    ClaudeBox with that session's entity set and history
  - Delete session: confirm dialog, then hard delete from SQLite

One active session per mode at any time. "New Session" creates a
new one for the current mode. Prior sessions remain in the list.

════════════════════════════════════════════════════════════════
 MEMORY & DISTILLATION
════════════════════════════════════════════════════════════════

SQLite store: Exocognii/GnosiumExanima/storage/gnosium.db

Tables:

  sessions
    id              TEXT PRIMARY KEY  — UUID
    mode            TEXT NOT NULL     — 'chamber' or 'solo'
    title           TEXT
    created_at      TEXT NOT NULL     — ISO 8601
    updated_at      TEXT NOT NULL     — ISO 8601
    active_entities TEXT NOT NULL     — JSON array of entity_ids
    is_current      INTEGER DEFAULT 0

  messages
    id              TEXT PRIMARY KEY  — UUID
    session_id      TEXT NOT NULL     — FK to sessions
    role            TEXT NOT NULL     — 'wizard' or 'entity'
    entity_id       TEXT              — null for wizard messages
    content         TEXT NOT NULL
    timestamp       TEXT NOT NULL     — ISO 8601

  distillations
    id              TEXT PRIMARY KEY  — UUID
    session_id      TEXT NOT NULL     — FK to sessions
    summary         TEXT NOT NULL     — compressed context
    message_range   TEXT NOT NULL     — JSON: {from_id, to_id}
    created_at      TEXT NOT NULL     — ISO 8601
    token_estimate  INTEGER           — approx tokens in summary

  entity_state
    entity_id       TEXT PRIMARY KEY
    last_loaded_at  TEXT
    notes           TEXT              — freeform, future use

Distillation trigger: when a session's message count exceeds a
configurable threshold (default: 40 messages, key:
gnosium.distillation_threshold in Configuus). On trigger:

  1. Take the oldest N messages not yet distilled (where N is
     the count above threshold)
  2. Send to ClaudeBox with a distillation system prompt:
     "Compress the following conversation into a dense context
     summary preserving all decisions, opinions, unresolved
     questions, and entity positions. Maximum 800 tokens."
  3. Store result in distillations table
  4. On next session reload, seed ClaudeBox with:
     all distillations (chronological) + last 20 raw messages

This is a separate ClaudeBox call — not the conversation instance.
Use a lightweight model config if ClaudeBox supports it.

════════════════════════════════════════════════════════════════
 TOKEN BUDGET
════════════════════════════════════════════════════════════════

System prompt token threshold: configurable, default 4000 tokens.
Key: gnosium.system_prompt_token_threshold in Configuus.

This measures the composite system prompt only — not conversation
history. Rough estimation: len(prompt_text) / 3.5.

When exceeded:
  - Yellow warning bar appears below the entity panel:
    "System prompt: ~{n} tokens ({entity_count} entities active)"
  - Does NOT block sending. The Wizard decides.
  - Warning clears when entities are toggled off below threshold.

Token logging: every ClaudeBox response logs to
~/.arca/token_log.jsonl:
  { app: "gnosium_exanima", timestamp, input_tokens, output_tokens,
    session_id, mode }
Delta writes only — baseline tracking per session to avoid
double-counting.

════════════════════════════════════════════════════════════════
 CLAUDEBOX WIRING — NON-NEGOTIABLE
════════════════════════════════════════════════════════════════

Import:
  sys.path.insert(0, str(Path.home() / 'ArcaCognitorium'))
  from ClaudeBox import ClaudeBox

Construction:
  ClaudeBox(
      api_key=os.environ.get('CLAUDE_API_KEY'),
      system_prompt=composite_prompt
  )

Streaming pattern:
  box.on("token", on_token_received)    # before every send
  # ... in on_complete and on_error handlers:
  box.off()

  NEVER use bus.once() — fires only once, causes truncation.

History reload:
  box._conversation.replace_history(session_id, history_list)
  # history_list = list of {role, content} dicts
  # Then pass only the new user message as string to
  # send_threaded()

ClaudeBox instance lifecycle:
  - Created on app start (or first entity toggle)
  - Destroyed and recreated on:
      entity toggle (Chamber)
      entity switch (Solo)
      mode switch (Chamber ↔ Solo)
      session switch
  - Never reused across prompt changes — always fresh instance

════════════════════════════════════════════════════════════════
 EXOCOGNII CONNECTIVITY
════════════════════════════════════════════════════════════════

NUNTIUS (write path):
  Import: from nuntius import emit
  On conversational events (wizard message sent, entity response
  received, session created, session closed), call:
    emit(Involucrum(
        source_app="gnosium_exanima",
        source_version=__version__,
        timestamp=now_iso(),
        hint="conversation" | "session_lifecycle",
        body=event_description
    ))
  Fire-and-forget dual POST to Exvacua Loricum (8731) and
  Perpetuum Aedificare (8732). Failure is silent — logged to
  stderr, never shown to Wizard, never blocks conversation.

Cognosis (read path — on-demand):
  Wizard or entity can invoke queries. Accessed via menu or
  future command syntax. Not ambient polling.
  - Exvacua Loricum: GET /lore/search?q={term}
  - Perpetuum Aedificare: GET /build/nodi, GET /build/recent
  - Praesidium: GET /search, GET /status
  Service URLs from Configuus. If service unreachable: show
  inline error in conversation area styled as system message
  (not entity speech). Do not retry automatically.

Mundana State Bus (ambient read):
  Connect on startup via Unix socket. Subscribe to:
    mundana.app_status
    mundana.token_ledger
    mundana.caelestis
  Data displayed in status strip at bottom of window.
  If disconnected: status strip shows "Mundana: disconnected".
  Reconnect on configurable interval (default 30s). Clean
  unsubscribe on app close. No leaked socket connections.

════════════════════════════════════════════════════════════════
 UI LAYOUT
════════════════════════════════════════════════════════════════

Three-region layout:

  ┌──────────────┬──────────────────────────────────────────┐
  │              │                                          │
  │  ENTITY      │  CONVERSATION AREA                       │
  │  PANEL       │                                          │
  │              │  - Streaming chat bubbles                │
  │  - Mode      │  - Wizard right, entities left           │
  │    switch    │  - Entity name prefix in Chamber         │
  │  - Entity    │                                          │
  │    list      │                                          │
  │    w/toggle  │                                          │
  │  - Portraits │                                          │
  │              │                                          │
  │              ├──────────────────────────────────────────┤
  │              │  INPUT BAR                               │
  │              │  Text input + Send button                │
  ├──────────────┼──────────────────────────────────────────┤
  │  TOKEN WARN  │  STATUS STRIP                            │
  │  (if active) │  Mundana state · service status · tokens │
  └──────────────┴──────────────────────────────────────────┘

  Menu bar: Session (New, Switch, Delete, Export) · View ·
  Connectivity (Cognosis queries) · About

Minimum window size: 900x600.
Window geometry saved on close, restored on launch.
Entity panel width: 220px fixed. Conversation area fills
remaining space.

════════════════════════════════════════════════════════════════
 PYQT6 CONSTRAINTS
════════════════════════════════════════════════════════════════

- QKeySequence and QShortcut are in QtGui, not QtWidgets/QtCore
- QDropEvent.pos() removed — use event.position().toPoint()
- QSplitter ignores min/max on QScrollArea children
- No PySide6 mixing — PyQt6 exclusively
- Token constants (C_GOLD, C_CRIMSON, C_TEAL) from ModusArcanus
  module — never hardcode hex values
- ModusArcanus design system: near-black void background (#0A0A0F
  or nearest constant), Aurum gold accents, Georgia serif body
- All blocking operations (ClaudeBox calls, SQLite writes, HTTP
  requests) run off the main thread via QThread or QRunnable

════════════════════════════════════════════════════════════════
 KDE DEPLOYMENT
════════════════════════════════════════════════════════════════

launch_gnosium.sh:
  #!/bin/bash
  cd /home/lordfingers/ArcaCognitorium
  source venv-GNOSIUM/bin/activate
  PYTHONPATH=. python3 -m GnosiumExanima

Icon: ~/.local/share/icons/gnosium_exanima.png
Desktop file: ~/.local/share/applications/gnosium_exanima.desktop

Never run as: python3 __main__.py from inside the package
directory — breaks relative imports.

════════════════════════════════════════════════════════════════
 EXPLICIT OUT OF SCOPE
════════════════════════════════════════════════════════════════

- Emergence mechanics, celestial entity influence, SCRIBAE,
  Fragment Protocol
- Lore engine integration, Library, Compendium
- PRAESIDIUM in-process pairing (Maniacum Omnifex is conceptual)
- Entity creation or editing (ENTITEX)
- Code output or build doc ingestion (Arx Aedificarix)
- The word "atelier" does not exist in the Cogniverse

════════════════════════════════════════════════════════════════

snake_case throughout. No filler. Every sentence carries
information. Write for a senior developer building within an
established ecosystem with existing conventions.

Sections:
1.  Overview & Core Architecture
      One paragraph + component table.
2.  Tech Stack
      Table: Tool | Version | Justification
3.  Annotated Directory & File Tree + DB Schema
      Full file tree. CREATE TABLE statements for all tables.
4.  Module Breakdown
      Table: Module | Responsibility | Inputs | Outputs |
      Dependencies
5.  ASCII UI Wireframe
      Full wireframe with complete legend. Must show both
      Chamber and Solo mode states.
6.  Data Flow — 3 labeled paths:
      (a) Happy path: Wizard sends message in Chamber mode,
          composite prompt built, entities respond, response
          rendered with name prefixes, message persisted,
          NUNTIUS emits
      (b) Entity toggle mid-session: entity toggled on,
          composite prompt rebuilt, ClaudeBox destroyed and
          recreated, history reloaded, token budget checked
      (c) Cognosis query failure: Wizard invokes lore search,
          Exvacua Loricum unreachable, inline system message
          displayed, no retry, conversation continues
7.  Code Stubs
      All public classes and functions. Type hints. Docstrings.
      Pseudocode for: composite prompt builder, distillation
      trigger, ClaudeBox lifecycle manager, entity vault
      scanner.
8.  Error Handling
      Per-module table: Error | Cause | Strategy.
      Must cover: malformed entity package, ClaudeBox stream
      failure mid-response, SQLite write failure, NUNTIUS POST
      failure, Mundana disconnect, empty vault, token budget
      exceeded.
9.  Setup & Testing
      requirements.txt content shown explicitly.
      Install, run, and test commands.
      One pytest per core module. One integration test: full
      message send/receive/persist cycle.
10. Packaging
      .desktop file template shown verbatim.
      launch_gnosium.sh shown verbatim.
11. Extensibility — 5 features:
      name | user value | implementation approach.
      Must include: Celestial Resolver integration, Fragment
      Protocol, distillation auto-trigger.

All tables use box-drawing characters — no pipe tables.
80-character line width for all prose.
```

---

## Idea Brief Reference

╭──────────────────────────┬──────────────────────────────────────╮
│  Field                   │  Content                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  App Name                │  GNOSIUM EXANIMA                     │
│  One-Line Purpose        │  Standalone overseer chat for Tower  │
│                          │  entity interaction, testing, and    │
│                          │  Exocognii awareness                 │
│  Platform                │  Debian Trixie, Python 3.11, PyQt6   │
│  Core Loop               │  Launch → Select mode → Toggle       │
│                          │  entities → Converse → Session saves  │
│  Explicit Out of Scope   │  Emergence, celestial influence,     │
│                          │  lore engine, PRAESIDIUM pairing,    │
│                          │  code generation, entity creation    │
│  Technical Risks         │  Composite prompt token budget,      │
│                          │  mode-switch session continuity,     │
│                          │  Mundana subscription lifecycle      │
│  Visual Identity         │  ModusArcanus — void, gold, Georgia  │
│  v2 Wishlist             │  Celestial Resolver, Fragment        │
│                          │  Protocol, distillation auto-trigger │
│                          │  celestial.yaml entity awareness     │
╰──────────────────────────┴──────────────────────────────────────╯

---

*Phase 2+3 — Build Prompt v5 — GNOSIUM EXANIMA*
*5 refinement cycles complete.*
*Ready for Dolium ingestion or direct execution.*
