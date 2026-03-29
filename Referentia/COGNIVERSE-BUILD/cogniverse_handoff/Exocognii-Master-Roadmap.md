# EXOCOGNII MASTER ROADMAP
*Arca Cognitorium v1.1 · Build Sequencing Document*


# PHASE 0 — FOUNDATION
Complete before any new application build begins. These are prerequisite infrastructure decisions.


## 0.1  Memory Systems Architecture Session
Session type: ::THEORY — no build, design only
Dedicated session covering LORICA FORNAX schema, Build Memory schema, shared log routing substrate, ClaudeBox session data as token tracker feed, and how PRAESIDIUM connects to both. Output: architecture decision document for both memory systems.


### Prompt for this session:
::INIT
FILES IN SCOPE: none
STATE: ::THEORY
CONTEXT:
Designing two memory systems for the Exocognii suite:
LORICA FORNAX (lore canon) and Build Memory (project/session).
Both will expose a local FastAPI. Apps write logs to flat files.
Memory systems read logs and distill. PRAESIDIUM queries both.

TASK:
Design the schema, API surface, distillation cadence, and
log routing architecture for both systems. Interview style.
One domain at a time. No code yet.

CONSTRAINTS:
ClaudeBox lives in ArcaCognitorium main repo — no copies.
All apps import from ~/.arca/config.json for the repo path.


## 0.2  ClaudeBox Centralisation
Task type: ::BUILD — single patch
Audit all existing apps (Dolium, Vigilarum, Mythotex, Oculus) and confirm they import ClaudeBox from the canonical path in the ArcaCognitorium repo rather than carrying local copies. Update any that do not.
Reference: ~/.arca/config.json stores the repo root path.


### Prompt for this session:
::INIT
FILES IN SCOPE:
- [fetch each app's main.py or app.py]
STATE: ::AUDIT then ::BUILD
CONTEXT:
ClaudeBox must live only in ArcaCognitorium/claudebox/.
All Exocognii apps must import from the canonical path.
TASK:
Audit imports in each tool. Patch any that carry local copies.
CONSTRAINTS:
Do not alter ClaudeBox itself.


# PHASE 1 — PRAESIDIUM
The ambient command centre. Lives on the third monitor. Always open. Built in PySide6.


## 1.1  Run PRAESIDIUM Idea Brief through Dolium
When Dolium is ready — or use the Idea Brief directly with the Aedificatorium
The PRAESIDIUM Idea Brief is included in this package. Feed it through the four-stage Dolium pipeline to produce a full build document, then pass to the Aedificatorium. If Dolium is not yet ready, use the Idea Brief directly with the IdeaForge seed prompt.


### IdeaForge seed prompt (use if Dolium unavailable):
You are a senior software architect writing for a mid-level developer.
Produce complete developer-ready construction documentation for
PRAESIDIUM — a PySide6 desktop application built with Python 3.11.

PRAESIDIUM is a persistent ambient command centre for the Arca
Cognitorium workflow, running on a dedicated 1849x779px monitor.
It provides: default widget layout (movable/resizable), dockable
optional widgets, a universal Display Panel system, a Status Legend
aggregator, and a manual Widget Idea Pipeline (INGENIUM).

Core default widgets: Git Widget, Project Status/Repo Activity Feed,
App Launcher, Chat (Claude/project-aware), Style Reference,
Token Tracker with graphs, TODO/Notice Board, Status Legend.

Dockable widgets: Display Panel (multi-instance, universal renderer),
Referentia Aggregator, Build Pipeline Status, Diff Viewer,
Prompt History, Active Model Display, Quick File Drop, Export Hub,
Relationship Map, Clipboard History, Keyboard Shortcut Reference,
Repo Activity Feed (by date), Screenshot/Annotation.

snake_case throughout. No filler. Every sentence carries information.

Sections: [standard 11-section IdeaForge format]


## 1.2  Build PRAESIDIUM — Phase 1 (Default Layout + Git Widget)
Priority: immediate workflow pain relief
Build the application shell, default widget layout, and Git widget first. This delivers the most immediate value — the git operations alone justify the build.


## 1.3  Build PRAESIDIUM — Phase 2 (Remaining Default Widgets)
Token Tracker, App Launcher, Style Reference, TODO, Status Legend, Chat integration.


## 1.4  Build PRAESIDIUM — Phase 3 (Dockable Widget System)
Display Panel system, Referentia Aggregator, Repo Activity Feed, Diff Viewer, Quick File Drop.


## 1.5  Build PRAESIDIUM — Phase 4 (INGENIUM + Remaining Dockables)
Widget Idea Pipeline, Prompt History, Export Hub, Relationship Map, remaining dockables.


# PHASE 2 — LORICA FORNAX (LORE ENGINE)
The canonical lore substrate. Standalone app with local FastAPI. Three-pane interface.


## 2.1  Run LORICA FORNAX Idea Brief through Dolium / IdeaForge
The LORICA FORNAX Idea Brief is included in this package. Follow the same process as PRAESIDIUM.


### IdeaForge seed prompt:
You are a senior software architect writing for a mid-level developer.
Produce complete developer-ready construction documentation for
LORICA FORNAX — a PySide6 desktop application built with Python 3.11,
with a local FastAPI service layer.

LORICA FORNAX is a lore canon engine for the Arca Cognitorium.
It ingests raw documents (JSON conversation exports, .md, .txt),
parses them for lore-relevant segments, refines each into a
structured LORIDEX entry (categorised, headered, datestamped),
maintains a ratified canon database, and exposes a query API
for other Exocognii apps to access canonical lore.

Three-pane UI: Left=raw document tree + LORIFICARE trigger,
Centre=interactive canon chat, Right=LORIDEX display + canon tree.

snake_case throughout. No filler. Every sentence carries information.

Sections: [standard 11-section IdeaForge format]


## 2.2  Build LORICA FORNAX — Core
Ingestion pipeline, LORIFICARE parser, LORIDEX schema, canon database, three-pane UI.


## 2.3  Build LORICA FORNAX — API Layer
FastAPI service. Endpoints: query canon, get LORIDEX entry, list categories, search.


# PHASE 3 — BUILD MEMORY SYSTEM
Project/session memory. Separate from lore. Tracks builds, git activity, app usage, session summaries. Requires dedicated ::THEORY session (see Phase 0.1).


## 3.1  Build Memory — Core Service
Log ingestion, distillation engine, FastAPI query layer.


## 3.2  Wire PRAESIDIUM to Build Memory
Project Status widget, Repo Activity Feed, and Chat all query Build Memory.


# PHASE 4 — WIRE EXISTING EXOCOGNII APPS
Connect existing apps to the memory systems.


| App | Writes to | Reads from | Priority |
| --- | --- | --- | --- |
| Dolium | Build Memory (pipeline state, docs produced) | — | High |
| Mythotex | Build Memory (generation log) | LORICA FORNAX (lore context) | High |
| Lexiferium | LORICA FORNAX (vocabulary) | LORICA FORNAX (canon vocab) | Medium |
| Vigilarum | Build Memory (session log) | — | Low |
| Oculus | Build Memory (debug logs) | — | Low |
| Fenestrium | Build Memory (output files) | — | Low |


# PHASE 5 — REMAINING EXOCOGNII BUILDS
New apps to build once the infrastructure is stable.


| App | Purpose | Dependencies | Status |
| --- | --- | --- | --- |
| Aedificatorium | Build docs → implementable files. Chat interface with doc ingestion. | ClaudeBox, Build Memory | To Build |
| Incitamentum | Prompt builder chat interface. | ClaudeBox | To Build |
| Lexiferium | Vocabulary register + compendium. Suggests canon vocabulary. | ClaudeBox, LORICA FORNAX | To Build |
| GLYPTORUM | Glyph drawing/browsing app. Replace terminal text file workflow. | — | Needs streamlining |
| Dolium | Idea → build doc pipeline. Four-stage chat. | ClaudeBox, Build Memory | Needs overhaul |


# ONGOING


| Item | Description |
| --- | --- |
| Git hygiene | Commit after every meaningful build seam. Use PRAESIDIUM Git Widget once built. |
| Snapshot cadence | Snapshot before destructive patches, before major new feature work, at phase completions. |
| Lore deep dive | Dedicated session to parse old conversations for lore corpus. Feed into LORICA FORNAX once built. |
| Dolium overhaul | Redesign pipeline stages before next use. Revisit IdeaForge system integration. |
| init_urls.txt | Update raw GitHub URLs to v1.1-living-tower branch after any Referentia restructure. |
