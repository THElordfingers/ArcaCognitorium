# PRAESIDIUM
### Expositio — v1.4 · Exocognii Suite · Arca Cognitorium · ＭＭＸＸＶＩ

---

## I. Identity

**Name:** PRAESIDIUM  
**Version:** 1.4  
**Tagline:** The ambient command centre of the Arca Cognitorium workflow — always
present, always watching, never in the way.  
**Classification:** Persistent ambient desktop application — PyQt6, secondary
monitor, free-floating widget canvas.  
**Status:** Active development. Phases 1–3 complete and functional. Phase 4
(INGENIUM pipeline, remaining dockables) pending.

---

## II. Purpose

### Problem Statement

The Wizard works across a constellation of tools — the Tower, the Exocognii
suite, git repositories, lore files, entity packages — with no unified surface
to observe their state or act on common operations. Switching context to perform
a git commit, check a token count, or look up a lore entry costs attention that
belongs to the work itself.

### Motivation

A secondary monitor is wasted as a mirror or a blank. PRAESIDIUM reclaims it as
a living instrument panel — a surface that aggregates the state of the entire
Arca Cognitorium workflow into a single ambient view, where actions are one
gesture away and no window management is required.

### Intended Outcome

The Wizard operates with their primary monitor fully devoted to the work at
hand. PRAESIDIUM runs on the secondary monitor as a persistent peripheral
awareness layer: git status is visible at a glance, commits happen without
switching context, Claude is available for instant query, token costs are
tracked across every tool, and lore is searchable without opening a separate
application.

### Anti-Purpose

PRAESIDIUM is not the Tower. It does not host entities, run sessions, or
manage the Council. It is not a file manager, a terminal, or a project
management platform. It does not attempt to replace any tool in the Exocognii
suite — it surfaces and acts on their state.

---

## III. Audience

### Primary Users

The Wizard (LordFingers) — sole operator of the Arca Cognitorium. Technically
fluent, multi-project, late-night working style with fragmented thought
patterns. Expects the tool to infer scope, stay out of the way, and be reliable
without demanding attention.

### Secondary Users

None currently. The architecture is single-instance and single-user. Future
consideration: read-only observation surface for collaborators.

### Assumed Knowledge

Comfort with PyQt6 desktop application conventions. Familiarity with git
operations at the command-line level. Awareness of the Exocognii suite
architecture and ClaudeBox integration patterns.

### Out-of-Scope Audiences

Developers unfamiliar with the Arca Cognitorium project. Non-technical users.
Anyone expecting a conventional desktop application with standard UX patterns.

---

## IV. Design Philosophy

### Core Principles

**Ambient over intrusive.** PRAESIDIUM lives on the periphery. It never demands
attention — it rewards it. Information is present when the Wizard looks, not
pushed when the Wizard is working.

**Composable over monolithic.** Every piece of functionality is a widget. The
canvas is a composition surface. No feature is baked into the shell that
belongs in a widget.

**Persistence without ceremony.** Layout, state, preferences, and content
survive every restart without the Wizard doing anything. The application should
be indistinguishable from one that was never closed.

**Workflow pain relief first.** Build order is determined by what causes the
most friction in the daily workflow, not by architectural elegance or feature
completeness.

**Arcane register throughout.** The visual and naming language follows
ModusArcanus and Nomenclatura Arcana. The tool is an instrument of the
Cogniverse, not a productivity dashboard.

### Tradeoff Positions

Stability over features — when a feature risks breaking existing behaviour, it
is deferred. The widget canvas must always open cleanly.

Persistence over freshness — layout.json is the canonical source of truth for
widget state. Live data from Exocognii services enriches but does not replace
it.

Local-first over service-first — every widget that can function without the
Exocognii FastAPI service does so, with graceful degradation when the service
is available.

### Aesthetic Direction

ModusArcanus in full. Void backgrounds, Aurum accents, Parchment body text.
Georgia serif throughout. The interface reads as something bound in leather and
illuminated by candlelight, rendered in pixels. No rounded corners, no
drop shadows, no animations that serve aesthetics over function — except the
blind collapse, which earns its place.

### What This Philosophy Rejects

Notification systems, modal dialogs, tooltips that block, auto-saving that
might corrupt, widgets that phone home, features that assume connectivity,
and any visual language that could be mistaken for a productivity SaaS product.

---

## V. Technical Concept

### Mental Model

PRAESIDIUM is a canvas. Widgets are instruments placed on that canvas. Each
instrument has one job. The canvas remembers where every instrument was left.
The shell is infrastructure — it exists to host, wire, and persist. The
intelligence lives in the widgets.

### Core Abstractions

**ArcaneWidget** — the base class for every widget. Handles drag, resize, lock,
animated collapse, font scaling, status signalling, and visibility persistence.
All widgets inherit from it; none bypass it.

**LayoutManager** — the memory of the canvas. Reads and writes layout.json,
restores widget geometry on launch, debounces saves to 500ms after last change,
exposes save_as_default() for snapshotting preferred arrangements.

**WidgetRegistry** — the factory. Maps class names to module paths, dispatches
construction with appropriate arguments. New widgets register here.

**Configuus** — the configuration layer. Reads ~/.arca/config.json, creates
defaults on first run, exposes typed accessors for all inter-tool paths and
service endpoints.

**token_logger** — the shared ledger. A stdlib-only module at
~/.arca/token_logger.py that any tool in the Exocognii suite can import to
append usage records to ~/.arca/token_log.jsonl. The TokenTracker widget
watches this file live.

### Data Flow Overview

On launch: `run.py` → `Configuus` → `WidgetRegistry` → `LayoutManager.load()`
→ widget instances positioned on canvas → signals wired → event loop running.

On widget interaction: user action → widget signal → layout_manager records
geometry → debounced save to layout.json.

On git operation: GitWidget → subprocess (Popen) → live stdout stream → output
panel → layout_manager records nothing (content is transient).

On Claude query: ChatWidget input → ClaudeBox send_threaded → background thread
→ _Relay pyqtSignal → main thread text append → on_complete → token_logger
append → TokenTracker file watcher fires → display updates.

### System Boundaries

PRAESIDIUM owns: the canvas, all widget logic, layout persistence, token
logging for its own chat widget.

PRAESIDIUM depends on: ClaudeBox (at arca_repo_path/claudebox/), git (system),
~/.arca/config.json, Exocognii FastAPI service (optional, graceful degradation),
~/.arca/token_log.jsonl (shared with Tower, Dolium, other tools).

### Key Technical Decisions

**Absolute positioning over Qt layouts.** Free-floating widgets with
drag/resize require absolute positioning. Qt's layout managers would fight
user repositioning. The canvas is a bare QWidget; widgets are children with
manually managed geometry.

**setParent() must not be called after move/resize.** Qt resets geometry on
reparent. Widgets are constructed with the canvas as parent — this is the only
safe moment. _load_widgets() does not call setParent().

**bus.on() not bus.once() for ClaudeBox streaming.** send_threaded() registers
on_token with bus.once() internally — it fires exactly once. ChatWidget registers
its own persistent handler via box.on("token", handler) before calling
send_threaded(), deregistering via box.off() in on_complete.

**QFileSystemWatcher for token tracking.** Rather than signal-chaining from
the chat widget to the tracker, the tracker watches the log file directly. This
enables cross-app tracking — Tower, Dolium, and any future tool can append to
the same file and the tracker updates automatically.

**QThread for long git operations.** commit/push/pull/fetch use QThread with
Popen line-by-line stdout reading. The UI stays responsive; output streams live
into the output panel. subprocess.run() is only used for fast read operations
(status, branch, log).

---

## VI. Functional Scope

### Core Capabilities

Git workflow management — branch display, status, staged/unstaged detection,
commit with file picker, push, pull, fetch, live streaming output, lock
detection and auto-clear.

Claude conversation — streaming chat with ClaudeBox, project-aware system
prompt injection, context selector (Tower / Praesidium / General), token
forwarding, session persistence within a run.

Token tracking — cross-app ledger via file watcher, session and daily totals,
per-app breakdown, cost estimation, progress bars.

Widget canvas — free-floating, draggable, resizable, lockable, persistently
arranged widgets on an ambient secondary-monitor surface.

### Supporting Capabilities

Todo board (tabbed, multi-list, persistent), App Launcher (configurable),
Style Reference (Chromata Arcana palette), Status Legend (aggregated widget
status), Display Panel (universal renderer — plain/markdown/diff/image, file
drop), Diff Viewer (git modes + two-file drop), Repo Activity (commit feed +
file watcher), Quick File Drop (ingest zone with clipboard and display routing),
Referentia Aggregator (local file search + Exocognii service search), Art
Widget (image viewer, fit/fill/actual/zoom, SVG), Glyph Browser (Unicode sheet
browser with Glyptorum integration, click-to-copy).

### Explicit Exclusions

Entity management (Entitex), lore generation (Mythotex), prompt construction
(Incitamentum), celestial tracking (Vigilarum), naming oracle (Lexiferium).
These are Exocognii tools that PRAESIDIUM may surface state from, but does not
replicate.

### Future Scope

Multiple canvases (virtual desktop switching for widget layouts). INGENIUM
widget idea pipeline. Exocognii FastAPI service integration (build node status,
drift flags, lore node search). Perpetuum Aedificare / Exvacua Loricum read
surfaces. ArtWidget gallery mode.

---

## VII. Constraints & Context

### Technical Constraints

PyQt6 exclusively — PySide6 mixing causes hard crashes. Debian Trixie, KDE
Plasma 6, X11. Python 3.11. No async in the Qt main thread — threading via
QThread and daemon threads only. Clipboard via xclip (X11 only) with Qt
fallback.

### External Dependencies

ClaudeBox — canonical at ~/ArcaCognitorium/claudebox/. CLAUDE_API_KEY
environment variable. git (system). xclip (system). PyQt6, PyQt6-Qt6Svg (for
ArtWidget SVG support). Optional: httpx (Referentia Aggregator service mode).

### Resource Constraints

Single developer. Build sessions are context-window-bounded. Features are
built in priority order determined by immediate workflow pain, not architectural
completeness.

---

## VIII. Success Criteria

### Functional Success

PRAESIDIUM opens on the secondary monitor without crashing, restores all
widgets to their last positions, polls the repo automatically, and is ready
for a git commit or Claude query within three seconds of launch.

### User Success

The Wizard completes a commit-and-push cycle without touching a terminal.
The Wizard queries Claude about the codebase and receives a streaming response
without leaving the primary monitor context. Token costs are visible at a
glance across all tools.

### Quality Benchmarks

Widget layout survives restart. No geometry resets on relaunch. Lock state
persists. git operations stream output live with no UI freeze. Token tracker
updates within one second of any tool completing a Claude response.

### Failure Conditions

The application crashes on launch. Widget positions reset on every restart.
git operations freeze the UI. The token tracker shows stale data. ClaudeBox
fails silently without surfacing an error to the user.

---

## IX. Glossary

**ArcaneWidget** — the base class all PRAESIDIUM widgets inherit from. Provides
the standard chrome: header bar, drag, resize, lock, animated collapse, font
scaling, status dot.

**Canvas** — the bare QWidget that fills the space between the top bar and
status bar. Widgets are parented to it and positioned absolutely.

**Chromata Arcana** — the ModusArcanus colour palette. Void, Aurum, Parchment,
Umbra, Sanguis, Viridis.

**Configuus** — the configuration loader. Reads ~/.arca/config.json.

**layout.json** — the canonical record of widget positions, sizes, visibility,
lock state, and font size. Written atomically on every geometry change.

**layout_default.json** — the user-saved default layout. Written by ⊙ SAVE
DEFAULT. Loaded as fallback when layout.json is absent or corrupt.

**LayoutManager** — the persistence layer. Owns layout.json and layout_default.json.

**token_log.jsonl** — the shared cross-app token usage ledger at
~/.arca/token_log.jsonl. Append-only, one JSON object per line.

**token_logger** — the shared stdlib module at ~/.arca/token_logger.py.
Imported by any Exocognii tool to append usage records.

**WidgetRegistry** — the factory. Maps class names to modules, dispatches
construction.

---

## X. Revision Notes

**v1.0** — Phase 1: application shell, ArcaneWidget base, GitWidget, default
layout, LayoutManager. Initial build.

**v1.1** — Phase 2: ChatWidget (ClaudeBox streaming), TokenTracker, TodoBoard,
AppLauncher, StyleReference, StatusLegend. ADD WIDGET picker. Cross-widget
signal wiring.

**v1.2** — Phase 2.5: Git widget streaming output (QThread/Popen), pre-commit
file picker, lock detection. Token ledger cross-app architecture (token_logger,
QFileSystemWatcher). Widget lock, visibility persistence, animated blind
collapse, per-widget font resize, SAVE DEFAULT.

**v1.3** — Phase 3: DisplayPanel, DiffViewer, RepoActivity, QuickFileDrop,
ReferentiaAggregator. Registry and picker expanded.

**v1.4** — Phase 3.5: TodoBoard v2 (tabbed multi-list), ArtWidget, GlyphBrowser.
widget_base v1.3 (animated blind, font resize integrated). Geometry restore
bug fixed (setParent() ordering). Stale layout entry accumulation noted,
cleanup deferred.

---

*PRAESIDIUM · Expositio · v1.4 · Vigilia Perpetua · Arca Cognitorium · ＭＭＸＸＶＩ*
