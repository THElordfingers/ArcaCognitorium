# CODEX PARATUM — Paratum Package
## The Dolium
*Luminarious · Arca Cognitorium · v1.0 · 2026-03-22*

---

## I. Identification

| Field | Value |
|---|---|
| Full Name | The Dolium |
| Working Name | The Dolium (final) |
| Version | v1.0 |
| Codex Entry Date | 2026-03-22 |
| Classification | Companion Application — Arca Cognitorium Ecosystem |
| Author | LordFingers (the Wizard) |
| Builder | The Builder (Claude) |

---

## II. The Lore Statement

Named for the great clay vessels of antiquity — sealed, dark, warm — in which grain and wine were stored until 
their appointed time, The Dolium is a greenhouse for ideas. It does not accept everything. It does not forget
anything. It imposes structure not as bureaucracy but as ceremony: the understanding that an idea which cannot be 
named, motivated, scoped, analysed, and declared ready is an idea that is not yet ready to be built.

The Dolium is a standalone companion to the Arca Cognitorium, inhabiting the same aesthetic register — the dark
 field, the aureate gold, the archaic Latin — while serving a distinct function: the maturation of thought before 
 it meets the chisel of implementation.

It has four chambers. Each chamber is a stage of growth. An idea that passes through all four has been 
transformed from a fragment of intuition into a documented, build-ready artifact. An idea that cannot make the 
passage has learned something about itself in the trying.

The Dolium does not rush. It is not a task manager. It is a place where ideas are kept until their time 
comes.

---

## III. The Functional Statement

The Dolium is a terminal user interface application built in Python 3 using the Textual framework.
 It implements a four-stage ideation pipeline in which ideas progress through defined chambers — Fomentary, 
 Cultivation House, Vestibule, Codex Paratum — each with gate conditions that must be met before advancement.
  Ideas are stored as JSON, auto-saved on every field change, and exportable from the final chamber as multi-format
   Paratum Packages.

Each chamber is served by a Claude API entity with a distinct persona, injected via ClaudeBox with a 
per-idea session. The entity receives the full current state of the idea on every message and the complete manpages
 of the application in its system prompt — giving it accurate self-knowledge of the program it inhabits and genuine
  awareness of what the Wizard has written.

The application runs standalone, requires no server, and persists all state to local JSON files in a `storage/`
 directory. It is launched with a single command from the project root.

---

## IV. Scope

### Inside

- Four-chamber pipeline: Fomentary, Cultivation House, Vestibule, Codex Paratum
- Per-idea field system with chamber-gated visibility
- Gate enforcement with real-time status display
- ClaudeBox-powered per-chamber entity with session management
- Full idea injection into every API message — entity sees all populated fields
- Manpage system: five pages in register, overlay UI, `/man` command, `ctrl+m` shortcut
- Self-knowledge injection: manpages embedded in every entity system prompt
- Slash command system: `/attach` `/attached` `/clear` `/save` `/files` `/man` `/help`
- Live AC context via `DOLIUM_CONTEXT_FILE` environment variable
- `update_context.py`: repo-reading context regeneration script in AC root
- Cull system with epitaph requirement and Cull Register with resurrection
- Multi-format export: `.wiz` `.docx` `.md` `.txt` `.json`
- Pipeline navigator with search, chamber headers, idea counts
- Workspace with auto-save on every field change
- Conversation history persisted per idea to disk

### Outside

- No multi-user support — single Wizard, single machine
- No cloud sync or remote access
- No cross-idea awareness in the entity — each conversation is idea-scoped
- Session persistence across restarts not implemented in v1
- No `.wiz` export without Node.js and `export_wiz.js`
- No streaming token-by-token display — responses arrive complete
- No idea tagging or filtering beyond title search

---

## V. System Map

### Repository Root

| File | Purpose |
|---|---|
| `main.py` | Entry point. Reads env vars. Launches DoliumApp. |
| `app.py` | DoliumApp (Textual App). Initialises ClaudeBox, store, context, screen. |
| `models.py` | Dataclasses: Idea, ChamberLog, CullRecord. Serialisation contract. |
| `store.py` | IdeaStore — sole filesystem interface. All JSON read/write. |
| `chambers.py` | Gate logic. Pure functions. GateResult dataclass. |
| `prompts.py` | Chamber system prompts. build_user_message(). set_context(). Self-knowledge injection. |
| `manpages.py` | Five manpage texts in register. all_manpages_for_prompt() for system injection. |
| `export.py` | ExportEngine — generates .wiz .docx .md .txt .json from Idea. |
| `dolium.tcss` | Full Textual CSS. AC palette. All widget styling. |

### ui/

| File | Purpose |
|---|---|
| `ui/layout.py` | ChainScreen — main screen. Three panes. All actions and message routing. |
| `ui/pipeline.py` | PipelineNav — left pane. Chamber sections. Idea entries. Search. |
| `ui/workspace.py` | IdeaWorkspace — middle pane. Fields. Auto-save. GateBar. |
| `ui/conversation.py` | ChainConversation — right pane. ClaudeBox wiring. Slash commands. |
| `ui/modals.py` | All modals: NewIdea, Advance, ReturnTo, Cull, Declaration, CullRegister, Export, Manpage. |

### Environment Variables

| Variable | Purpose |
|---|---|
| `CLAUDE_API_KEY` | API key for ClaudeBox. Required for conversation. |
| `DOLIUM_CONTEXT_FILE` | Path to CONTEXT.md in AC repo. Optional. |
| `DOLIUM_REPO_PATH` | Path to AC repo root. Required for /attach and /files. |
| `DOLIUM_STORAGE_DIR` | Override default storage/ directory. Optional. |

---

## VI. Dependencies

| Dependency | Status |
|---|---|
| Python 3.11+ | Required |
| textual | Required — `pip install textual` |
| python-docx | Required — `pip install python-docx` |
| anthropic | Required by ClaudeBox — `pip install anthropic` |
| ClaudeBox/ | Required — directory must be present in project root |
| CLAUDE_API_KEY | Required for conversation |
| Node.js | Optional — required for .wiz export only |
| docx (npm) | Optional — `npm install -g docx` |

---

## VII. Build Sequence

| Step | Deliverable |
|---|---|
| 1 | `models.py` — Idea, ChamberLog, CullRecord dataclasses |
| 2 | `store.py` — IdeaStore CRUD against the models |
| 3 | `chambers.py` — Four gate functions plus router |
| 4 | `prompts.py` — Chamber system prompts and build_user_message() |
| 5 | `dolium.tcss` — Full stylesheet |
| 6 | `ui/pipeline.py` — PipelineNav |
| 7 | `ui/workspace.py` — IdeaWorkspace with GateBar |
| 8 | `ui/conversation.py` — ChainConversation with ClaudeBox wiring |
| 9 | `ui/modals.py` — All seven modals |
| 10 | `ui/layout.py` — ChainScreen wiring all three panes |
| 11 | `export.py` — ExportEngine |
| 12 | `app.py` + `main.py` — Entry point |
| 13 | `manpages.py` — Five pages, /man command, system prompt injection |
| 14 | `update_context.py` — Context regeneration script for AC repo root |

---

## VIII. Open Questions

- **Session persistence**: ClaudeBox sessions are lost on app close. Display history persists but entity begins fresh. Fix designed, not implemented.
- **Cross-idea awareness**: entity has no knowledge of other ideas in the pipeline. Compact pipeline summary injection designed, deferred.
- **Streaming**: ClaudeBox delivers one token via on_token before on_complete fires. True streaming requires different event wiring.
- **.wiz export**: export_wiz.js script not yet written for The Dolium specifically. Export degrades gracefully without it.
- **Token cost of self-knowledge**: all five manpages injected per session creation (~2,000 additional tokens). Acceptable at current volume.

---

## IX. Aesthetic Notes

### Palette

| Token | Value | Usage |
|---|---|---|
| Void | `#0D0B0E` | Screen background |
| Umbra | `#161218` | Pane backgrounds |
| Aureate | `#C9A84C` | Primary gold — borders, active states |
| Parchment | `#D4C8A8` | Body text |
| Mist | `#5A6070` | Muted text, placeholders |
| Chamber I | `#A98FD4` | Fomentary violet |
| Chamber II | `#7EC8C8` | Cultivation teal |
| Chamber III | `#C87941` | Vestibule ember |
| Chamber IV | `#E8C96A` | Codex gold |

### Register

All in-app text uses the Cogniverse register: archaic Latin constructions, two-word names with bureaucratic authority, ceremonial tone for significant events. The application does not explain itself in plain language. It is inhabited, not operated.

---

## X. The Declaration

*The Dolium exists and functions. It was conceived as a greenhouse for ideas and built as one. It runs in the terminal, it speaks back, it holds ideas in conditions suited to their maturation, and it does not let them out until they are ready. The pipeline is sound. The gates are real. The entities know where they are and what they are for. The manpages are written in the correct register. The export formats are generated. The Cull Register preserves what did not survive. This idea has passed through its own instrument and emerged from it ready. I declare it complete.*

— LordFingers, the Wizard · 2026-03-22

---

*The Dolium — Codex Paratum Entry — v1.0*
