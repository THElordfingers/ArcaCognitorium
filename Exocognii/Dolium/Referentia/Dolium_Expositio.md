# THE DOLIUM v2
### Expositio · Arca Cognitorium · Exocognii Suite · MMXXVI

---

## I. IDENTITY

╭──────────────────────┬──────────────────────────────────────────────╮
│  Name                │  The Dolium v2                               │
├──────────────────────┼──────────────────────────────────────────────┤
│  Version             │  2.0                                         │
├──────────────────────┼──────────────────────────────────────────────┤
│  Classification      │  Ideation instrument · Pipeline application  │
├──────────────────────┼──────────────────────────────────────────────┤
│  Status              │  Complete · Ready for deployment             │
├──────────────────────┼──────────────────────────────────────────────┤
│  Thesis              │  A four-chamber vessel through which raw     │
│                      │  ideas are fermented into declared           │
│                      │  intentions — in the presence of an entity   │
│                      │  that watches without being asked.           │
╰──────────────────────┴──────────────────────────────────────────────╯

---

## II. PURPOSE

### Problem Statement

Ideas do not fail because they are bad. They fail because they are
abandoned in the space between having them and doing something with
them. That space has no structure, no pressure, no witness. The idea
is had, noted somewhere, and forgotten. Or it is acted on too quickly,
before it has been tested against itself, before the motivation has
been named, before the obstacles have been admitted.

The v1 Dolium addressed the structural problem — a pipeline, chambers,
gates — but failed at the experiential one. The workspace felt like a
form. Fields to fill. Boxes to satisfy. The entity was present only
when summoned. The result was a productive-feeling application that
nobody wanted to inhabit.

### Motivation

The redesign began from a single observation: an idea being worked
deserves a witness, not just a container. The entity should be present
the way a thinking companion is present — noticing things you haven't
said, arriving with observations you didn't ask for, making the space
feel occupied rather than empty. The pipeline structure was sound. The
soul of the thing needed to be rebuilt from the ground up.

### Intended Outcome

An idea that passes through the Dolium has been named, tested under
pressure, refined into its final form, and declared. The Wizard who
declared it knows what it is, why it matters, what stands in its way,
and what the first act of making it real looks like. That is the
deliverable. Not a note. Not a document. A declared intention with
everything required to act on it already worked out.

### Anti-Purpose

The Dolium is not a general note-taking application. It is not a task
manager. It is not a brainstorming surface or a mind map or a knowledge
base. Ideas that are not ready to be processed do not belong here — the
Fomentary exists for early-stage material, but even that requires the
Wizard to name the thing and say why it matters. Fragments belong
elsewhere until they are ready to become ideas.

---

## III. AUDIENCE

### Primary Users

The Wizard — sole inhabitant of the Arca Cognitorium. Someone who
generates more ideas than can be acted on, who needs a system that
applies pressure rather than merely storage, and who works best when
accompanied rather than alone. Comfortable with structured tools that
have opinions about process.

### Assumed Knowledge

Familiarity with the Arca Cognitorium's register and cosmology. Basic
fluency with PyQt6 desktop applications. Understanding that the entity
is not a chatbot — it is a presence with a particular character and a
particular relationship to the work.

### Out-of-Scope Audiences

Teams. Collaborative workflows. Anyone looking for a frictionless
capture tool. The Dolium applies pressure deliberately. It is not
suitable for users who want to add ideas without committing to the
process of developing them.

---

## IV. DESIGN PHILOSOPHY

### Core Principles

**Presence over response.** The entity does not wait to be asked. It
observes, notices, and arrives with a whisper when the Wizard has been
writing long enough to have said something worth observing. This is the
architectural centre of v2. Everything else is in service of it.

**Structure that earns its keep.** The four chambers and their gates
are not bureaucracy. Each threshold marks a genuine change in the
nature of the work — fermentation, pressure-testing, refinement,
declaration. The gates are calibrated to the minimum evidence that the
work has actually happened, not to perform rigor.

**Inhabitation over interaction.** The Dolium should feel like a place
you go to do a kind of work, not a tool you pick up and put down. The
aesthetic, the entity's voice, the persistence of conversation and
whisper history — these are all in service of making it feel occupied.

**Nothing is lost.** Culled ideas are not deleted. They are classified.
The cull register preserves everything. An idea that is wrong now may
be right later. The Dolium is not a judge.

### Tradeoff Positions

Pressure over comfort. The gates require real content — not token
minimums for their own sake, but thresholds that cannot be satisfied
by a sentence. This will frustrate anyone who wants to advance quickly.
That frustration is the point.

Ambient over explicit. The whisper system fires unprompted. It cannot
be turned off per field. The entity's observations are not always
welcome. This is also the point.

### Aesthetic Direction

Modus Arcanus throughout. Dark gold on void. Georgia serif. An
instrument that looks like it was designed rather than assembled. The
right panel carries the entity's voice — whispers in italic dim gold
above the conversation line, conversation in parchment below. The
separation is visual and tonal. Whispers are observations. Conversation
is dialogue. They are different things.

### What This Philosophy Rejects

Encouragement. The entity does not affirm effort or celebrate progress.
It notices things about the idea. Cheerfulness is architecturally
banned. Gamification. Streak tracking. The Dolium has no interest in
your consistency, only in whether the idea has been properly worked.

---

## V. TECHNICAL CONCEPT

### Mental Model

A fermentation vessel with four chambers. Material enters the first
chamber as raw, unnamed, unresolved. It passes through successive
chambers under increasing pressure — elaboration, refinement,
declaration — and exits as a structured intention ready to be acted on.
The entity inhabits the vessel. It does not control the pipeline. It
observes it.

### Core Abstractions

**Idea** — the primary domain object. A title, four chambers' worth of
fields, a conversation history, a chamber log, and a culled flag. Flows
through the pipeline. Never truly deleted.

**Chamber** — a stage in the pipeline with a defined set of fields and
a gate condition. The gate is a pure function: given an Idea, it returns
passed or failed with a list of what remains unmet.

**GateResult** — the output of gate evaluation. Passed boolean plus a
list of human-readable failure descriptions. The UI renders this
directly — the gate bar and the AdvanceDialog both consume it.

**AmbientWorker** — the debounced whisper thread. Fires after 1500ms of
typing inactivity on any field with sufficient content. Creates a new
ClaudeBox call per fire. Shares the idea's session with
ConversationWorker so the entity's conversation context is unified.

**IdeaStore** — JSON persistence with in-memory cache. Single source of
truth. Corruption-resistant with automatic backup on malformed data.

### Data Flow

The Wizard types in a field. The field emits a change signal. The
WorkspacePanel updates the Idea in memory, persists via IdeaStore,
re-evaluates the gate, and resets a 1500ms QTimer. When the timer
fires — if the field has enough content and no conversation is active
— an AmbientWorker is created, fires a ClaudeBox call with the field
text and idea context, and streams the response into the whisper
section of the ChamberPanel. On explicit message send, a
ConversationWorker fires on the same session, streams into the
conversation section, and persists the turn to the Idea's conversation
history.

### System Boundaries

The Dolium owns: idea persistence, gate logic, entity session
management per idea, export generation. It does not own: the ClaudeBox
API wrapper (imported from the ArcaCognitorium repo via config path),
theme or aesthetic definitions beyond its own style.py, or any
cross-suite state. Integration points for Praesidium pipeline state
feed and shared knowledge center are architecturally identified but
not yet wired — they are waiting on infrastructure that does not yet
exist.

### Key Technical Decisions

QTimer debounce lives on the main thread and never moves. Only its
timeout signal crosses into the worker thread. This is non-negotiable
for PyQt6 stability.

AmbientWorker and ConversationWorker share a single ClaudeBox session
per idea. The entity's whispers and its conversation are one continuous
context. A `_conv_active` flag on ChamberPanel prevents collision —
whispers are suppressed while a conversation turn is in flight.

Session ID equals Idea ID. One session per idea, persisted across
launches via conversation history replay on load.

---

## VI. FUNCTIONAL SCOPE

### Core Capabilities

Four-chamber ideation pipeline with gated advancement. Per-chamber
field sets with character-minimum gate conditions. Ambient whisper
system — entity observes field changes and generates unprompted
observations after typing inactivity. Direct conversation with the
chamber entity via shared session. Idea persistence with cull and
resurrect mechanics. Export to `.md .txt .json .docx .wiz`.

### Supporting Capabilities

Pipeline panel with chamber tree, idea list, and search. Advance,
return-to-earlier-chamber, and cull dialogs with gate result display.
Cull register with resurrection. Per-chamber conversation history
replay on idea load. Status bar with current idea and chamber context.

### Explicit Exclusions

Cross-idea awareness in entity context. Whisper rate limiting beyond
the `_conv_active` flag. Session summarization or token budget
management. Integration with Praesidium, shared knowledge center, or
memory pipelines — these are deferred pending infrastructure.
Multi-Wizard support. Cloud sync of any kind.

### Future Scope

Token-aware session management — summary compression of old turns at
a configurable threshold. Praesidium pipeline state injection into
entity context. Shared knowledge center context block in
`build_user_message()`. Theme resolution from a central aesthetic
pipeline rather than local constants.

---

## VII. CONSTRAINTS & CONTEXT

╭──────────────────────┬──────────────────────────────────────────────╮
│  Platform            │  Debian Trixie · KDE Plasma 6 · X11          │
├──────────────────────┼──────────────────────────────────────────────┤
│  Language            │  Python 3.11+                                │
├──────────────────────┼──────────────────────────────────────────────┤
│  Framework           │  PyQt6 6.6+                                  │
├──────────────────────┼──────────────────────────────────────────────┤
│  API                 │  CLAUDE_API_KEY via ClaudeBox                │
├──────────────────────┼──────────────────────────────────────────────┤
│  Config              │  ~/.arca/config.json · arca_repo_path key    │
├──────────────────────┼──────────────────────────────────────────────┤
│  Storage             │  DOLIUM_STORAGE env var or                   │
│                      │  ~/Dolium/storage/ default                   │
├──────────────────────┼──────────────────────────────────────────────┤
│  Dependencies        │  python-docx (optional · .docx export)       │
│                      │  Node.js + docx npm (optional · .wiz export) │
╰──────────────────────┴──────────────────────────────────────────────╯

ClaudeBox is never copied into the Dolium directory. It is imported
from the ArcaCognitorium repo path resolved at runtime from config.
If ClaudeBox is unavailable the pipeline functions normally — only
the entity is absent.

---

## VIII. SUCCESS CRITERIA

### Functional Success

An idea can be created, developed through all four chambers, declared,
and exported without error. Gate conditions correctly block advancement
until met. The entity whispers within 1500ms of typing inactivity on
fields with sufficient content. Conversation history survives app
restart. Culled ideas can be resurrected.

### User Success

The Wizard works an idea through to declaration and the resulting
export contains everything needed to act on it. The entity's whispers
surface something about the idea that was not explicitly stated.
The experience feels inhabited rather than procedural.

### Quality Benchmarks

74 unit and integration tests passing across models, store, and gate
logic. No blocking calls on the main thread. ClaudeBox unavailability
degrades gracefully — app runs without entity presence. JSON corruption
creates a backup and starts clean rather than crashing.

### Failure Conditions

The app has failed its purpose if the Wizard fills fields mechanically
to satisfy gates without the content actually representing genuine
work. The gates are a minimum floor, not a guarantee. The entity's
whispers are the diagnostic — if they stop arriving because the fields
are technically satisfied but thin, something is wrong with how the
app is being used, not with the app.

---

## IX. GLOSSARY

╭─────────────────────────┬─────────────────────────────────────────────╮
│  The Fomentary          │  Chamber I. Fermentation vessel for raw,    │
│                         │  unnamed, unresolved ideas.                 │
├─────────────────────────┼─────────────────────────────────────────────┤
│  The Cultivation House  │  Chamber II. Pressure and elaboration.      │
│                         │  Obstacles named. First step committed.     │
├─────────────────────────┼─────────────────────────────────────────────┤
│  The Vestibule          │  Chamber III. Refinement and threshold.     │
│                         │  Idea stated in its final form.             │
├─────────────────────────┼─────────────────────────────────────────────┤
│  The Codex              │  Chamber IV. Declaration. The idea is       │
│                         │  complete or it is not declared.            │
├─────────────────────────┼─────────────────────────────────────────────┤
│  GateResult             │  Output of gate evaluation. Passed boolean  │
│                         │  plus list of unmet conditions.             │
├─────────────────────────┼─────────────────────────────────────────────┤
│  AmbientWorker          │  Debounced whisper thread. Fires after      │
│                         │  1500ms typing inactivity.                  │
├─────────────────────────┼─────────────────────────────────────────────┤
│  Whisper                │  Unprompted entity observation. Appears in  │
│                         │  the right panel, italic, without being     │
│                         │  asked. Not conversation. Not advice.       │
├─────────────────────────┼─────────────────────────────────────────────┤
│  Declaration            │  The act of marking an idea complete from   │
│                         │  the Codex. Triggers export. Irreversible   │
│                         │  in intent if not in data.                  │
├─────────────────────────┼─────────────────────────────────────────────┤
│  Cull                   │  Removal of an idea from the active         │
│                         │  pipeline. Never permanent. The cull        │
│                         │  register preserves all culled ideas.       │
╰─────────────────────────┴─────────────────────────────────────────────╯

---

## X. REVISION NOTES

╭──────────────────┬──────────────────────────────────────────────────╮
│  2026-03-27      │  v2.0 — Complete redesign from Textual to        │
│                  │  PyQt6. Ambient whisper system introduced.        │
│                  │  Three-panel layout. Modus Arcanus applied        │
│                  │  throughout. 74 tests passing.                    │
│                  │  v1 (Textual) retired.                            │
╰──────────────────┴──────────────────────────────────────────────────╯

---

*Expositio · The Dolium v2 · Arca Cognitorium · MMXXVI*
