# ARX AEDIFICARIX
### Expositio · v1.0 · Exocognii Suite · Arca Cognitorium · MMXXVI

---

## I. Identity

**Name & Version:** Arx Aedificarix v1.0

**Tagline:** The forge in which the Wizard's visions become code.

**Classification:** Desktop companion application — dedicated AI code
generation client. Part of the Exocognii Suite; not a standalone tool.

**Status:** Active development. Core build complete and operational.
Send pipeline, session persistence, file extraction, and export
confirmed working. Minor known issues under active resolution.

---

## II. Purpose

**Problem Statement:** Long-form code generation with an AI requires
sustained context. A general-purpose chat interface loses history,
forgets attached documents, provides no structured output management,
and gives no visibility into how full the context window is. When the
Wizard is commissioning a full application from The Builder, these
deficiencies compound: files get lost in prose, sessions cannot be
resumed, and there is no organised path from conversation to
deliverable package.

**Motivation:** The Dolium produces build documents. The build
documents need to become code. There was no dedicated place in the
Exocognii Suite for sustained, iterative construction work with
The Builder entity. The Arx was built to fill that gap — a workspace
designed for the specific workflow of document-grounded code
generation, where a session can last hours and produce dozens of
files.

**Intended Outcome:** The Wizard opens a conversation, attaches a
build document, and conducts a full construction session with The
Builder. Files accumulate in the output panel. When the session is
complete, the entire deliverable is exported as a zip package with
a manifest. The Arx persists every session to disk — conversations
can be resumed days later with full context intact.

**Anti-Purpose:** The Arx is not a general-purpose chat interface.
It is not a file editor. It is not a project management tool. It
does not run or test the code it generates. It does not replace the
Dolium's ideation pipeline — it begins where the Dolium ends.

---

## III. Audience

**Primary Users:** LordFingers — the Wizard. A single-user tool
built for the specific workflow of the Arca Cognitorium. The Arx
assumes familiarity with the Cogniverse, with ClaudeBox, and with
the Exocognii build chain.

**Secondary Users:** None. The Arx has no collaborative or
multi-user scope.

**Assumed Knowledge:** The user understands the Builder entity's
file block protocol (%%FILE / %%LANG / %%DESC / %%END), the phase
token system (%%PHASE), and the role of build documents in the
Cogniverse construction workflow.

**Out-of-Scope Audiences:** General AI chat users. Developers
outside the Cogniverse who are not familiar with the Exocognii
Suite. Anyone expecting a feature-complete IDE or code runner.

---

## IV. Design Philosophy

**Core Principles:**

- The forge does not close until the work is done. Sessions are
  persistent and resumable. Nothing is lost.
- Context is visible. The Wizard always knows how full the window
  is. Compression is automatic and non-destructive.
- Files are first-class citizens. Generated code is parsed,
  registered, previewed, and exported — not buried in chat history.
- Conservatism at the seams. The API payload is assembled fresh
  every send. No session state is assumed; it is always constructed
  from what is on disk.
- One tool, one job. The Arx builds. It does not ideate, does not
  manage projects, does not run code.

**Tradeoff Positions:**

- Persistence over simplicity. The SQLite schema is non-trivial
  because everything must survive a restart. This was the right
  call.
- Explicit assembly over ClaudeBox session magic. The
  ContextEngine assembles every payload from scratch. This is
  more work but means the payload is always exactly what the
  database says it should be.
- Flat directory over nested package. The Exocognii deployment
  pattern favours flat structures that a shell script can launch
  directly. The subpackages (core/, ui/, bridge/) exist for code
  organisation but are resolved via sys.path injection, not
  package hierarchy.

**Aesthetic Direction:** ModusArcanus throughout. Void background,
Aurum gold, Georgia serif. The Arx should feel like a craftsman's
bench — dark, purposeful, lit by gold. Every label carries weight.
No chrome, no decoration for its own sake.

**What This Philosophy Rejects:** Stateless interaction. Chat
interfaces that treat each message as independent. Interfaces that
hide context window status. Code delivery buried in markdown fences
rather than parsed and extracted.

---

## V. Technical Concept

**Mental Model:** The Arx is a three-layer machine. The core layer
is a persistent forge memory — a SQLite database recording every
conversation turn, every generated file, every attachment, every
compression event. The bridge layer translates between ClaudeBox's
event-driven async world and Qt's signal/slot world. The UI layer
renders the state of the forge and accepts the Wizard's commands.

**Core Abstractions:**

- Project — a named collection of conversations sharing
  instructions and project-scoped attachments.
- Conversation — a persistent session with The Builder. Has its
  own history, attachments, output files, and builder prompt.
- Message — a single turn (user or assistant) stored in SQLite.
  Compressed messages are replaced by their archive summary in
  the payload but never deleted from the database.
- OutputFile — a file block extracted from a Builder response.
  Exists in the output_files table and in the OutputPanel.
  Transitions from pending → ready → exported.
- Attachment — a file attached by the Wizard. Summarised via
  ClaudeBox on attach; summary injected into the system block
  on every send.
- CompressionArchive — a record of compressed turns and their
  summary. Originals preserved; summary substituted in payload.

**Data Flow Overview:** The Wizard sends a message. ContextEngine
reads the database and assembles a system_block (builder prompt +
project instructions + attachment summaries) and a messages_array
(all stored turns, compressed groups substituted with summaries).
BuilderSignalBridge loads this history into a ClaudeBox named
session via replace_history(), then dispatches send_threaded() with
the final user message as plain string content. Streaming tokens
arrive via box.on("token") and flow through Qt signals to ChatPane.
On response_complete, ResponseParser extracts %%FILE blocks and
%%PHASE tokens. Files are written to output_files and registered in
OutputPanel. The full response text is saved as an assistant message
in SQLite. TOKEN_USAGE fires once; TokenGauge updates; the ledger
is written.

**System Boundaries:** The Arx owns: its SQLite database, the UI,
the session assembly logic, and the output file registry. It
depends on: ClaudeBox for all API communication, the Anthropic API
for generation, PyQt6 for the interface, and venv-ARX for its
Python environment. It writes to the shared token ledger
(~/.arca/token_log.jsonl) but does not own it.

**Key Technical Decisions:**

- replace_history() session pattern over passing messages_array
  as content. The Anthropic API does not accept a list of message
  dicts as the content parameter; ClaudeBox expects a string or
  ContentBlock list. History is loaded into the ClaudeBox session
  manager; the final user turn is sent as a plain string.
- box.on("token") over send_threaded(on_token=...). ClaudeBox
  registers on_token via bus.once() internally, which fires only
  once. Persistent box.on() + box.off() in complete/error
  handlers guarantees full streaming.
- Atomic zip export via tmp-then-rename. Ensures dest_path only
  appears on successful completion; partial writes never produce
  a corrupt file.
- Dedicated comp_box for compression. A separate ClaudeBox
  instance is used for synchronous compression calls, preventing
  session contamination of the primary streaming box.

---

## VI. Functional Scope

**Core Capabilities:**

- Persistent multi-turn conversation with The Builder via
  ClaudeBox streaming.
- Project and conversation hierarchy with drag-drop organisation.
- %%FILE block extraction, output file registration, syntax-
  highlighted preview, and zip export.
- Conversation context management: attachment summarisation,
  system block assembly, automatic compression at threshold.
- Session persistence and restore across restarts.

**Supporting Capabilities:**

- TokenGauge with exact post-response and draft heuristic updates.
- ArcaneHighlighter for Python, JSON, YAML, Markdown, Bash.
- AttachmentDialog for re-injecting previously attached files.
- Phase indicator (DISCUSSION / BUILDING) driven by %%PHASE.
- Token ledger writes to ~/.arca/token_log.jsonl.
- Error display with retry path for API failures.

**Explicit Exclusions:**

- Does not run, test, or validate generated code.
- Does not read from or write to the Tower's memory systems.
- Does not communicate with Exvacua Loricum or Perpetuum
  Aedificare.
- Does not provide a multi-user or collaborative interface.
- Does not perform IdeaForge ideation — that is the Dolium.

**Future Scope:**

- Dolium pipeline integration: load finalised build doc directly
  from Dolium SQLite, no manual file submission.
- Persona hot-swap UI: PromptLoader + ContextEngine already wired;
  needs a selector surface.
- Direct filesystem write with permission gates (defined in build
  doc §11).
- Session search via SQLite FTS5.

---

## VII. Constraints & Context

**Technical Constraints:** PyQt6 exclusively — no PySide6. Python
3.11. Runs on Debian Trixie / KDE Plasma 6 / X11. Clipboard via
xclip only (X11; Qt clipboard as fallback). Dedicated venv-ARX.
ClaudeBox must be importable from ArcaCognitorium root (lowercase
package: `from claudebox import ClaudeBox`).

**External Dependencies:**

- Anthropic Claude API — all generation. Risk: API changes to
  message format require bridge updates.
- ClaudeBox — custom wrapper. Tightly coupled to its internal
  replace_history() and bus event API. Risk: ClaudeBox internals
  are not a stable public surface.
- PyQt6 — GUI. Stable; low risk.
- PyYAML — not a direct dependency of the Arx itself.

**Regulatory or Compliance Context:** None beyond the Anthropic API
terms of service governing API usage.

---

## VIII. Success Criteria

**Functional Success:**

- A conversation is opened, messages are sent and received with
  full streaming, Builder-produced files appear in OutputPanel,
  and a zip package exports cleanly.
- Sessions survive restart and restore last active conversation
  with full history intact.
- Compression triggers at threshold, compresses oldest turns,
  and continues the session without data loss.

**User Success:** The Wizard can conduct a full multi-hour
construction session, receive dozens of generated files, and
export the complete deliverable package without any manual copying
from chat history.

**Quality Benchmarks:** All six SQLite tables initialise on first
run. Token ledger entries are written per response. The UI remains
responsive during streaming (all API calls on background threads).

**Failure Conditions:** A conversation is lost on restart. A
generated file is not parsed from a valid %%FILE block. The context
window fills silently without compression triggering. Streaming
tokens do not appear incrementally (only on complete).

---

## IX. Glossary

**%%FILE block** — The Builder's file delivery format. A structured
block delimited by %%FILE, %%LANG, %%DESC header lines and %%END.
Parsed by ResponseParser; content written to output_files table.

**%%PHASE token** — A signal from The Builder indicating the current
mode: DISCUSSION (planning) or BUILDING (code generation). Drives
the phase indicator bar in ChatPane.

**Exloricum** — Not used in the Arx directly. Referenced here
because it appears in connected Cogniverse systems (Lore Corpus).

**ContextEngine** — The module that assembles the full API payload
(system_block + messages_array) for each send from the database
state. Never calls the API itself.

**BuilderSignalBridge** — The QObject seam between ClaudeBox's
event bus and Qt's signal/slot system. Translates background-thread
callbacks into main-thread-safe signal emissions.

**CompressionEngine** — Compresses the oldest N uncompressed
conversation turns via a synchronous ClaudeBox call on a worker
thread. Writes archive to SQLite; marks source messages compressed.

**Arx Aedificarix** — Latin/Cogniverse: *The Building Fortress*.
The forge. The place where construction happens.

---

## X. Revision Notes

**2026-04-03 — v1.0 initial build complete.**
Full build from ArxAedificarix_BUILD.md spec. All 19 modules
delivered. Core, bridge, and UI tiers complete. Send pipeline
operational after ClaudeBox replace_history() integration fix.
Import casing corrected (claudebox, not ClaudeBox). sys.path
injection added for flat-deployed subpackages.

---

*Arx Aedificarix — Expositio v1.0*
*Exocognii Suite · Arca Cognitorium*
*Ordo Discordia, Cosmos Inania*
