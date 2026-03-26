# The Dolium
### The Dolium is a four-chamber ideation pipeline built in Python
### and PyQt6 under the Modus Arcanus design system. Ideas are
### created in the Fomentary and progress through the Cultivation
### House, the Vestibule, and the Codex Paratum — each with gate
### conditions, a distinct AI entity persona, and an ambient whisper
### system that observes the Wizard's writing in real time. The
### application connects to the Arca Cognitorium ecosystem via
### ClaudeBox and the live AC context file.

---

## Keyboard & Shortcut Reference

╭────────────────┬───────────────────────────────────────────────────╮
│ Key / Shortcut │ Action                                            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ctrl+n         │ Create a new idea                                 │
│ ctrl+a         │ Advance active idea to next chamber (if gate met) │
│ ctrl+r         │ Return active idea to a prior chamber             │
│ ctrl+x         │ Cull active idea (requires epitaph)               │
│ ctrl+g         │ Open the Cull Register                            │
│ ctrl+e         │ Export active idea (chamber IV only)              │
│ ctrl+m         │ Open the manual overlay                           │
│ ctrl+k         │ Open keyboard command palette                     │
│ ctrl+q         │ Quit                                              │
╰────────────────┴───────────────────────────────────────────────────╯

---

## Features

╭──────────────────────────────────┬─────────────────────────────────╮
│ Feature                          │ Status                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Four-chamber pipeline            │ Working                         │
│ Gate enforcement                 │ Working                         │
│ Workspace fields (gated)         │ Working                         │
│ Auto-save                        │ Working                         │
│ Ambient whisper system           │ Working                         │
│ Streaming token rendering        │ Working                         │
│ Pipeline navigator               │ Working                         │
│ Idea search                      │ Working                         │
│ ClaudeBox session management     │ Working                         │
│ Full idea injection per message  │ Working                         │
│ Entity self-knowledge (manpages) │ Working                         │
│ Live AC context injection        │ Working                         │
│ /attach — file injection         │ Working                         │
│ /save — append to field          │ Working                         │
│ /man — manual overlay            │ Working                         │
│ Cull system with epitaph         │ Working                         │
│ Cull Register with resurrection  │ Working                         │
│ Multi-format export              │ Partial — .wiz requires Node.js │
│ update_context.py                │ Working                         │
╰──────────────────────────────────┴─────────────────────────────────╯
---

## Usage Flowchart

```mermaid
flowchart TD
    Launch[python main.py] --> Nav[Pipeline panel loads]
    Nav --> Exists{Ideas exist?}
    Exists -- Yes --> Load[Click idea to load workspace]
    Exists -- No --> New[ctrl+n — New Idea dialog]
    New --> Title[Enter title — idea created in Fomentary]
    Title --> Load

    Load --> Write[Write in workspace fields]
    Write --> Whisper[After 1.5s — entity whispers in right panel]
    Write --> Chat[Send message to entity directly]
    Chat --> Save[/save field — append response to field]
    Write --> Gate{Gate conditions met?}
    Gate -- No --> Write
    Gate -- Yes --> Adv[ctrl+a — Advance dialog checklist]
    Adv --> IV{Chamber IV?}
    IV -- No --> Load
    IV -- Yes --> Declare[Write Declaration field]
    Declare --> Export[ctrl+e — Export dialog]
    Export --> Package[Files written to storage/exports/]

    Load --> Cull[ctrl+x — Cull dialog]
    Cull --> Epitaph[Enter epitaph]
    Epitaph --> Reg[Filed in Cull Register]
    Reg --> Res{Resurrect later?}
    Res -- Yes --> Fomentary[Returns to Fomentary]

    Load --> Return[ctrl+r — Return to prior chamber]
    Load --> Manual[ctrl+m — Manual overlay]
```

---

## Vision & Purpose

The Dolium exists because ideas arrive before they are ready, and without
structure they either dissolve or collide with build priorities they were never
prepared for. It imposes a four-stage pipeline — not as bureaucracy but as
ceremony — and places an AI entity in each chamber whose character matches the
work that chamber demands. The entity does not wait to be asked; it watches the
Wizard write and whispers observations in real time. The Dolium is not a note-
taker. It is a greenhouse.

---

## File & Folder Map

```
dolium/
├── main.py                — entry point
├── app.py                 — DoliumApp; global style; ClaudeBox init
├── models.py              — Idea, ChamberLog, CullRecord dataclasses
├── store.py               — IdeaStore; JSON persistence; in-memory cache
├── chambers.py            — GateEngine; pure gate functions; GateResult
├── prompts.py             — chamber + whisper system prompts;
│                            build_user_message(); set_context()
├── manpages.py            — five manpage texts; system prompt injection
├── export.py              — ExportEngine; .wiz .docx .md .txt .json
├── style.py               — Modus Arcanus palette; GLOBAL_STYLE;
│                            arcane_button(); gold_label(); dim_label()
├── workers.py             — AmbientWorker, ConversationWorker (QThread)
├── ClaudeBox/             — local ClaudeBox package
├── ui/
│   ├── __init__.py
│   ├── main_window.py     — DoliumWindow; QSplitter; panel composition
│   ├── pipeline_panel.py  — left panel; chamber tree; search
│   ├── workspace_panel.py — centre panel; fields; gate bar; debounce
│   ├── chamber_panel.py   — right panel; whisper stream; conversation
│   ├── dialogs.py         — all QDialog subclasses
│   └── widgets.py         — ArcaneField, WhisperBubble, ConvBubble,
│                            GateBar
└── storage/
    ├── ideas.json         — active idea store
    ├── culled.json        — Cull Register
    └── exports/           — generated Paratum Package files
```

---

## Features & Functions

### Four-Chamber Pipeline

The core structure. Ideas are created in chamber I and can only move forward by
meeting defined gate conditions. Each chamber has a distinct character, a set of
fields, and an AI entity whose persona matches the chamber's purpose.
Advancement is confirmed via a dialog showing a checklist of conditions as green
or red indicators. Ideas may be returned to any prior chamber at any time with a
note explaining the return.

### Workspace Fields

The centre panel renders all fields for the active idea. Fields are gated — they
only appear when the idea reaches the relevant chamber. Chamber I shows Title,
Tags, Body, Motivation. Chamber II adds Scope Inside, Scope Outside, System Map.
Chamber III adds Dependencies, Build Sequence, Open Questions, Aesthetic Notes.
Chamber IV adds Declaration. All fields save automatically on every keystroke.

### Ambient Whisper System

The most significant difference from v1. Every QTextEdit field in the workspace
is watched by a QTimer set to 1500ms. When the Wizard stops typing, an
AmbientWorker QThread fires — it calls ClaudeBox.send_threaded with a
specialised Whisper system prompt and the current field content. Tokens stream
back via on_token signals and appear word by word in the Whisper Stream section
of the right panel. The Wizard did not ask for it. The entity arrived because it
is present.

### Streaming Token Rendering

Both whispers and conversation responses stream word by word. AmbientWorker and
ConversationWorker are QThread subclasses that call ClaudeBox.send_threaded.
ClaudeBox must be configured with streaming.thread_mode: threaded in
claudebox.config.yaml — this fires on_token callbacks thread-safely from a
background thread. Each callback emits a token_received Qt signal, which the
chamber panel receives on the main thread and appends to the appropriate
QTextEdit.

### Gate Bar

The bottom of the workspace shows real-time gate status: a colour-coded
indicator (green = clear, amber = partial, red = blocked), an Advance button
enabled only when all conditions are met, a Return button, and a Cull button.
The gate bar re-evaluates on every field change without requiring a save action.

### Cull System

Any idea may be culled at any chamber. The Cull dialog requires a non-empty
epitaph — a brief, honest statement of why the idea did not proceed. The idea is
removed from the active pipeline and written to culled.json with its title,
epitaph, chamber at cull, and full body snapshot. The Cull Register (ctrl+g)
lists all culled ideas with their epitaphs and provides a Resurrect button per
row.

### Export System

Available only for chamber IV ideas. The Export dialog presents five format
checkboxes, all selected by default: .wiz (Wizard-styled LibreOffice document,
requires Node.js), .docx (clean Word document), .md (Markdown), .txt
(plaintext), .json (raw data). Files are written to storage/exports/ with a slug
derived from the idea title.

### Slash Commands

/attach <filename> searches the configured AC repo and prepends the file as a
fenced code block to the next message. /save <field> appends the last entity
response to the named workspace field. /man opens the manpage overlay. /files
lists available files in the AC repo. /help prints the command reference in the
conversation pane.

### Manpage Overlay

A tabbed modal accessible via ctrl+m or /man. Five pages: app overview and one
per chamber. Each page covers what the chamber is, what to do there, the
entity's character, gate conditions, and relevant /save fields. The same text is
injected into every entity system prompt, giving the entity complete self-
knowledge of the program it inhabits.

### Live AC Context

Entities are aware of the Arca Cognitorium architecture if DOLIUM_CONTEXT_FILE
is set. update_context.py in the AC repo root reads the codebase, calls the
Haiku model, and writes a 600-900 word architectural summary. The Dolium loads
this file at startup and replaces the static fallback context in every chamber
system prompt.

---

## Logic

### Architecture

Three QWidget panels compose DoliumWindow via a horizontal QSplitter:
PipelinePanel (left), WorkspacePanel (centre), ChamberPanel (right). All state
flows through app.py, which owns the ClaudeBox instance and IdeaStore. Panels
communicate via Qt signals: PipelinePanel emits idea_selected(str);
WorkspacePanel emits field_changed(field, text) and whisper_requested(field,
text, idea); ChamberPanel emits message_sent(str). app.py connects these signals
and routes state.

### API Wiring

ClaudeBox is initialised in app.py with CLAUDE_API_KEY. claudebox.config.yaml
must have streaming.thread_mode set to threaded — this is non-negotiable for
PyQt6. One ClaudeBox session is created per idea on first message via
create_session(session_id=idea.id, system_prompt=chamber_prompt). AmbientWorker
and ConversationWorker share this session so the entity's conversation history
includes both whispers and direct exchanges.

### Debounce and Whisper Lifecycle

WorkspacePanel holds a single QTimer (setSingleShot=True, interval=1500ms)
created in __init__ on the main thread. Every QTextEdit.textChanged signal calls
_on_field_changed(), which saves the idea and restarts the timer. After 1500ms
of silence, _on_debounce_fire checks whether a ConversationWorker is active
(self._conv_active flag). If not, it creates an AmbientWorker, connects its
token_received signal to ChamberPanel.on_whisper_token, and starts it. The
debounce timer does not restart while a conversation is in progress.

### Field Persistence

Every field change is written to disk immediately.
WorkspacePanel._on_field_changed() sets the Idea attribute in memory and calls
IdeaStore.update(idea), which writes the full ideas.json. The declared_at
timestamp is set automatically on the first non-empty save of the Declaration
field. There is no explicit save action.

---

## Input / Output & File Types

```
Input
  ├── Keyboard — user interaction via Qt events
  ├── storage/ideas.json — JSON — all active ideas, loaded at startup
  ├── storage/culled.json — JSON — Cull Register, loaded at startup
  ├── DOLIUM_CONTEXT_FILE — Markdown — live AC context, loaded at startup
  └── /attach <file> — any text file from DOLIUM_REPO_PATH

Output
  ├── storage/ideas.json — JSON — written on every idea mutation
  ├── storage/culled.json — JSON — written on cull and resurrection
  ├── storage/exports/<slug>.wiz — styled Word doc (requires Node.js)
  ├── storage/exports/<slug>.docx — clean Word document
  ├── storage/exports/<slug>.md — Markdown
  ├── storage/exports/<slug>.txt — plaintext
  └── storage/exports/<slug>.json — raw idea data

Configuration
  ├── CLAUDE_API_KEY — env var — Anthropic API key, required
  ├── DOLIUM_CONTEXT_FILE — env var — path to CONTEXT.md, optional
  ├── DOLIUM_REPO_PATH — env var — path to AC repo, optional
  ├── DOLIUM_STORAGE_DIR — env var — override storage/ path, optional
  └── ClaudeBox/claudebox.config.yaml — streaming.thread_mode: threaded
```
