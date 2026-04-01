# IdeaForge Prompt System
## Production Documentation Protocol

> A complete system for transforming raw ideas into developer-ready build documentation through structured AI dialogue, iterative prompt refinement, and council-level quality review.

| Document Class | Version | Issued By | Status |
|---|---|---|---|
| Prompt Engineering System | 1.0 | AI Advancement Collective | Production Release |

---

## Table of Contents

1. [Philosophy & Design Principles](#1-philosophy--design-principles)
2. [System Overview](#2-system-overview)
3. [Phase 1 — Idea Intake & Q&A](#3-phase-1--idea-intake--qa)
4. [Phase 2 — Seed Prompt Construction](#4-phase-2--seed-prompt-construction)
5. [Phase 3 — Iterative Refinement (5 Cycles)](#5-phase-3--iterative-refinement-5-cycles)
6. [Council Review](#6-council-review-optional-but-recommended)
7. [The Master Prompt — Full Text](#7-the-master-prompt--full-text)
8. [Delivery Quality Gates](#8-delivery-quality-gates)
9. [Quick Reference — The 11 Required Sections](#9-quick-reference--the-11-required-sections)
10. [Common Failure Modes & Remedies](#10-common-failure-modes--remedies)
11. [Appendix — Glossary](#appendix--glossary)

---

## 1. Philosophy & Design Principles

This system was developed through direct observation of what separates a useful AI-generated build document from a deployment-ready one. The gap is almost never about the AI's knowledge — it is about the structure of the conversation that precedes the output.

Three principles govern this protocol:

**Principle 1 — Specificity compounds.**
Every concrete detail added to a prompt eliminates an entire class of vague output. Naming a serialization method, a widget library, or a color constant forces the AI to operate in a constrained, real-world space rather than a generalized one. Vague prompts produce vague documents.

**Principle 2 — Iteration is not failure, it is the method.**
No prompt produces a final-quality document on the first pass. This system treats iteration as the primary mechanism — not a fallback. Each cycle adds one layer of specificity based on concrete gap analysis. Five cycles of deliberate refinement consistently outperform one exhaustive prompt.

**Principle 3 — User-level simulation catches what architecture-level thinking misses.**
Technical review finds missing stubs. Simulated user testing finds missing experiences: the 30-second wait on first launch, the lost session on accidental close, the ambiguous error with no recovery path. Both modes of review are required in every iteration cycle.

---

## 2. System Overview

The IdeaForge system consists of four sequential phases. Each phase has defined inputs, outputs, and quality gates. Do not skip or abbreviate a phase — the value of later phases depends entirely on the quality of earlier ones.

| Phase | Name | Input | Output | Gate |
|---|---|---|---|---|
| 1 | Idea Intake & Q&A | Raw idea from user | Structured idea brief | All ambiguities resolved |
| 2 | Seed Prompt Construction | Idea brief | v1 prompt | Covers all 11 required sections |
| 3 | Iterative Refinement (×5) | Prompt vN + gap analysis + user sim | Final prompt + final doc | Council quality threshold met |
| 4 | Package Assembly | Final doc + metadata | Delivered package | Table of contents, no broken refs |

---

## 3. Phase 1 — Idea Intake & Q&A

Before any prompt is written, the idea must be stress-tested through structured dialogue. This phase is non-negotiable. Skipping it produces a document that answers the wrong questions with high precision.

### 3.1 Opening Statement

When the user presents an idea, the prompter responds with the following framing before asking any questions:

> Before we write the first prompt, I need to establish a clear picture of what we're building. I'm going to ask you a structured set of questions. Some may seem obvious — answer them anyway, because the answers constrain the AI's output in ways that prevent entire categories of revision work later.

### 3.2 Required Q&A Areas

The following question areas must be covered in Phase 1. They may be asked conversationally or as a structured list depending on the user's preference. Every area must yield a concrete answer before Phase 2 begins.

#### Area A — Platform & Environment

- What operating system and desktop environment is the primary target?
- What Python version is assumed? Is this negotiable?
- Are there any hard constraints on GUI framework (Qt, GTK, Electron, web-based)?
- Is this for personal use, team use, or public distribution?

#### Area B — Core Concept Clarity

- State the app's purpose in one sentence. What problem does it solve for whom?
- What does the user do first when they open it? Walk me through the core loop.
- What is the single most important feature? What would make the app useless if missing?
- What explicitly is out of scope for v1?

#### Area C — Technical Preferences

- Are there libraries, frameworks, or tools you already know you want to use?
- Are there libraries, frameworks, or tools you want to avoid?
- How do you want data to persist — local file, SQLite, cloud, none?
- Does the app need to run offline? Network access required?

#### Area D — User & UX Profile

- Who is the primary user? (skill level, context, frequency of use)
- What is the expected screen resolution or minimum window size?
- Are there strong aesthetic preferences? (dark theme, color palette, font)
- What does 'done' look like from a user's perspective after one session?

#### Area E — Scope & Novelty

- What makes this different from existing tools that do something similar?
- What is the most technically risky part of this idea?
- What are 2–3 features you'd love in v2 but are cutting from v1?
- Is there anything about this idea you're unsure how to implement?

### 3.3 Idea Brief Output

After Q&A is complete, the prompter produces a structured Idea Brief — a single-page summary that becomes the source of truth for all subsequent phases. It must include:

| Field | Content |
|---|---|
| App Name | Working title |
| One-Line Purpose | What it does and for whom |
| Platform | OS, Python version, GUI framework |
| Core Loop | The 3–5 step flow the user follows in every session |
| Key Features (v1) | Bullet list — must-haves only |
| Explicit Out of Scope | What is intentionally excluded |
| Technical Risks | The hardest parts to build correctly |
| Visual Identity | Theme, palette, font if specified |
| v2 Wishlist | Future features to inform extensibility section |
| Open Questions | Anything unresolved that may surface in iteration |

> ⚠ **NOTE:** The Idea Brief must be shown to the user and confirmed before Phase 2 begins. Disagreements at this stage cost 10 minutes. Disagreements discovered in cycle 3 cost hours.

---

## 4. Phase 2 — Seed Prompt Construction

The seed prompt is the v1 prompt. It is not expected to produce a final document. It is expected to produce a document that has the right shape and enough content to make gap analysis meaningful. A good seed prompt produces 70% of the final output correctly.

### 4.1 Seed Prompt Template

Use the following template, filling in the bracketed fields from the Idea Brief. Do not deviate from the section list — these 11 sections represent the minimum complete build document.

```
You are a senior software architect writing for a [EXPERIENCE_LEVEL] developer.
Produce complete, developer-ready construction documentation for
"[APP_NAME]" — a [PLATFORM] desktop application built with
[LANGUAGE_VERSION] + [GUI_FRAMEWORK].

[APP_NAME] is [ONE_LINE_PURPOSE].

[IF PIPELINE/STAGED ARCHITECTURE: Describe the core stages here,
one sentence each, in execution order.]

snake_case throughout. No filler. Every sentence carries information.
Write for a [EXPERIENCE_LEVEL] developer.

Sections:
1. Overview & Core Architecture (one paragraph + stage/component table)
2. Tech Stack — table: Tool | Version | Justification
3. Annotated Directory & File Tree
4. Module Breakdown — table: Module | Responsibility | Inputs | Outputs | Dependencies
5. ASCII UI Wireframe with full legend
6. Data Flow — 3 labeled paths: (a) happy path, (b) [DOMAIN_ERROR], (c) [SYSTEM_ERROR]
7. Code Stubs — all public classes/functions, type hints, docstrings
8. Error Handling — per-module table: Error | Cause | Strategy
9. requirements.txt + install/run/test commands + one pytest per core module
10. Packaging — .desktop file template + [PACKAGING_TOOL] guidance
11. Extensibility — 5 features: name | user value | implementation approach
```

### 4.2 Filling the Template

| Placeholder | How to Fill It |
|---|---|
| EXPERIENCE_LEVEL | mid-level / senior / junior — from Q&A Area D |
| APP_NAME | Working title from Idea Brief |
| PLATFORM | Linux / Windows / macOS — from Q&A Area A |
| LANGUAGE_VERSION + GUI_FRAMEWORK | e.g. Python 3.11 + PySide6 — from Q&A Area C |
| ONE_LINE_PURPOSE | Exact text from Idea Brief |
| DOMAIN_ERROR | Most likely user-facing error in the app's domain |
| SYSTEM_ERROR | Most likely system-level failure (network, disk, subprocess) |
| PACKAGING_TOOL | PyInstaller / Flatpak / AppImage — from Q&A Area D |

> ✓ **TIP:** Write the two error path labels (DOMAIN_ERROR, SYSTEM_ERROR) before writing the rest of the prompt. They force you to think about what can go wrong, which sharpens the architecture description above them.

---

## 5. Phase 3 — Iterative Refinement (5 Cycles)

Five refinement cycles are the minimum for a production-quality document. Each cycle follows an identical four-step sequence. Skipping steps within a cycle accumulates debt that forces extra cycles later.

### 5.1 The Four-Step Cycle

| Step | Action | Output |
|---|---|---|
| 1. Simulate AI Response | Mentally or actually run the current prompt. Summarize what it produces, not just what it says it produces. | Response summary — what exists, what is vague, what is absent |
| 2. Architecture Gap Analysis | Compare the response against the Completeness Framework (Section 5.3). Note every gap by section number. | Numbered gap list |
| 3. User-Level Simulation | Imagine a developer sitting down with the document to build the app. Where do they stop? What question do they have that the document doesn't answer? | User friction points — 3 to 5 minimum |
| 4. Prompt Revision | Add one targeted instruction per gap. Do not add more than the gaps require. Trim any instruction that became redundant. | Prompt vN+1 |

### 5.2 Cycle Focus Areas

Each of the five cycles tends to surface a different class of problem. Use this as a reference — gaps may appear in different cycles on different projects.

| Cycle | Typical Gaps Found | Prompt Lever to Apply |
|---|---|---|
| 1 | Wrong shape — sections present but shallow; architecture not reflected in modules | Specify pipeline stages, module responsibilities, architectural constraints explicitly |
| 2 | Missing novel features; UI wireframe single-panel; data flow linear only | Require multi-panel wireframe, 3-path data flow, domain-specific novel feature in extensibility |
| 3 | No code stubs; no dependency versions; no sandboxing/isolation strategy | Require stubs with type hints + docstrings; add rationale column to tech stack; specify execution model |
| 4 | No session persistence; no threading model; blocking calls on main thread; UX gaps | Add session manager, Worker pattern, startup sequence, user onboarding experience |
| 5 | Token efficiency; redundant instructions; missing integration tests; packaging incomplete | Trim prompt, add integration test scaffold, specify packaging flags, confirm all TypedDicts |

### 5.3 Completeness Framework

After each simulated AI response, check every item in this framework. Any unchecked item is a gap to address in the next cycle's prompt revision.

#### Architecture
- [ ] Core pipeline/stage architecture explicitly named and sequenced
- [ ] Each stage's inputs and outputs specified
- [ ] Execution model specified (subprocess isolation, threading, async)
- [ ] Data persistence strategy specified (SQLite, JSON, none)
- [ ] Security/sandboxing approach documented or explicitly deferred

#### Module Layer
- [ ] Every module has a clear single responsibility
- [ ] Module table includes: Responsibility, Inputs, Outputs, Dependencies
- [ ] No module performs work that belongs to another module
- [ ] All cross-cutting concerns (logging, config, session) are in dedicated modules

#### UI Layer
- [ ] Wireframe shows ALL interactive elements
- [ ] Every element in the wireframe has a legend entry
- [ ] Layout is implementable in the specified framework (no aspirational widgets)
- [ ] Keyboard shortcuts listed if app is described as keyboard-centric

#### Data Flow
- [ ] Happy path covers the complete end-to-end loop
- [ ] Error path 2 covers the most likely user-facing failure
- [ ] Error path 3 covers the most likely system-level failure
- [ ] Each path shows where errors are caught and how they surface to the user

#### Code Stubs
- [ ] All public classes present
- [ ] All public methods present with type hints and one-line docstrings
- [ ] Naming convention consistent throughout (snake_case specified and enforced)
- [ ] Critical/complex methods have pseudocode or implementation notes, not just docstrings

#### Error Handling
- [ ] Every module has its own error handling subsection
- [ ] Each error specifies: type, cause, strategy
- [ ] No error handling just says 'log and continue' without specifying what continues
- [ ] Startup failure paths are documented (app cannot start → what does user see?)

#### Testing
- [ ] requirements.txt content shown explicitly
- [ ] Install, run, and test commands all present
- [ ] At least one unit test per core module
- [ ] At least one integration test covering the critical path end-to-end

#### Packaging
- [ ] .desktop file template shown verbatim
- [ ] Packaging command shown with all relevant flags
- [ ] Runtime asset path resolution documented (sys._MEIPASS pattern or equivalent)

#### Extensibility
- [ ] All features have: name, user value, implementation approach
- [ ] At least one feature is technically novel — not just 'add more settings'
- [ ] Extensibility features don't contradict the v1 architecture

### 5.4 User Simulation Protocol

In every cycle, after architecture gap analysis, perform a user-level simulation. Adopt the perspective of a mid-level developer who has just received the document and is about to write their first line of code. Answer these questions:

1. What is the first file I create, and what goes in it?
2. Where do I get stuck first? Which module stub is too vague to implement?
3. What happens when I run the app for the first time? Is the experience documented?
4. What happens when the first thing that can go wrong, goes wrong?
5. Is there any feature described that I don't know how to implement from the document alone?

Each "yes" answer to question 5, or "I get stuck" answer to questions 1–4, is a gap. Add it to the next cycle's revision.

### 5.5 Prompt Efficiency Rules

As cycles progress, the prompt grows. These rules prevent it from becoming unwieldy:

- Remove any instruction that the AI is now consistently following correctly.
- Consolidate related instructions into a single sentence with a colon-separated list.
- Use reference markers when architecture decisions are stable — don't repeat them verbatim.
- Never add an instruction without removing or condensing something else of equal length.
- The final prompt (v5) should be longer than v1 but shorter than v3 at its peak — the middle cycles are exploratory, the final is refined.

---

## 6. Council Review (Optional but Recommended)

After cycle 5 produces a candidate final document, a council review pass applies experienced architectural judgment before the document is delivered. This step is optional for small projects but strongly recommended for anything that will be handed to a developer team.

### 6.1 Council Review Scope

The council reviewer reads the document as an experienced senior engineer, not as a validator of a checklist. They look for:

- Architectural decisions that are technically correct but practically problematic
- Implicit assumptions the document makes that a developer could miss
- Sections that describe something without specifying how to implement it
- Any place where the document claims something is 'sandboxed' or 'secure' without implementing it
- Features deferred to v2 that should be in v1, and v1 features that should be deferred

### 6.2 Council Review Output

| Section | Contents | Required |
|---|---|---|
| What to Keep | Explicit affirmation of sound architecture and good decisions | Yes |
| Foundational Reconsiderations | Architectural changes that affect the whole codebase | Yes |
| Tactical Revisions | Specific implementation gaps — can be addressed in parallel | Yes |
| Priority Order | Numbered sequence telling the developer what to resolve first | Recommended |

> ⚠ **NOTE:** If a council review surfaces a Foundational Reconsideration, run one additional prompt cycle incorporating the revision before delivering the final document. Do not deliver a document that you know has an architectural flaw.

---

## 7. The Master Prompt — Full Text

This is the distilled master prompt, ready to use as a starting point for any new project. Fill in all bracketed fields from the Idea Brief before use.

> ⚠ **When to use this prompt:** Use this as your FINAL cycle prompt after 4 prior iterations have refined the architecture. Do not use this as your first prompt — it will overwhelm an underdeveloped idea brief and produce a document that is technically detailed but conceptually wrong.

```
You are a senior software architect writing for a [EXPERIENCE_LEVEL] Linux developer.
Produce the final, complete, developer-ready build document for "[APP_NAME]" —
a [VISUAL_IDENTITY] [PLATFORM] desktop application built with [STACK].

[APP_NAME] is [ONE_LINE_PURPOSE].

[ARCHITECTURE BLOCK — describe pipeline stages, components, or layers explicitly.
 One sentence per stage. Include the key architectural decisions from revision cycles:
 execution model, persistence strategy, threading approach, sandboxing stance.]

Enforce all of the following — do not omit or summarize any:

[ARCHITECTURAL CONSTRAINTS — list each resolved architectural decision as a
 one-line constraint. Example:
  - Execution model: subprocess writes RunResult JSON envelope
  - Threading: all blocking ops use Worker(QRunnable) + WorkerSignals pattern
  - Editor: QPlainTextEdit + PythonHighlighter, no QScintilla
  - Layout: QSplitter with PipelineDivider widgets, animated arrows deferred to v2]

Begin with a Table of Contents listing all sections and subsections.

Sections — include every item, fully specified:

1. Overview & Architecture
   - One paragraph summary
   - Stage/component table: Name | Role (one line each)
   - Keyboard shortcuts table (if app is keyboard-driven)

2. Tech Stack — table: Tool | Version | Justification

3. Directory Tree & Database Schema
   - Full annotated file tree
   - CREATE TABLE statements for all tables

4. Module Breakdown
   - Table: Module | Stage | Responsibility | Inputs | Outputs | Dependencies

5. UI Wireframe
   - ASCII multi-panel layout, all interactive elements visible
   - Full legend — every element explained
   - QSS rules for any styled custom widget

6. Data Flow — 3 labeled paths:
   - (a) Successful/happy path — end to end
   - (b) [DOMAIN_ERROR_PATH]
   - (c) [SYSTEM_ERROR_PATH + user cancellation if applicable]

7. Code Stubs
   - All public classes and functions
   - snake_case, type hints, one-line docstrings
   - Critical functions: full pseudocode or implementation notes
   - Include: [LIST CRITICAL STUBS FROM REVISION CYCLES]
   - Include full text of any runner/template scripts

8. Error Handling — per-module table: Error | Cause | Strategy
   - Include startup failure paths
   - Include offline/network failure paths

9. Setup & Testing
   - requirements.txt (full content)
   - Install, run, test commands
   - One unit test per core module
   - Integration test scaffold covering the critical path

10. Packaging
    - .desktop file template (verbatim)
    - [PACKAGING_TOOL] command with all flags
    - Runtime asset path resolution pattern

11. v[X] Planned Feature — [FEATURE NAME] (if applicable)
    - Architecture note for a near-future feature

12. Extensibility — 6 features:
    - Name | User Value | Implementation Approach
    - Must include: [FEATURES SURFACED IN Q&A v2 WISHLIST]

snake_case. No filler. Every sentence carries information.
```

---

## 8. Delivery Quality Gates

Before delivering the final document package, verify every gate in this checklist. A document that fails any gate is not ready to deliver.

### 8.1 Document Completeness
- [ ] Table of Contents present and accurate
- [ ] All 11 required sections present (12 if planned feature section applies)
- [ ] No section contains the word 'TBD', 'TODO', or 'to be determined'
- [ ] No section says a component 'handles' something without specifying how

### 8.2 Technical Soundness
- [ ] Every architectural decision is implementable with the specified tech stack
- [ ] No blocking calls remain on the main UI thread without documented mitigation
- [ ] No security claim is made without an implementation specified
- [ ] The wireframe is implementable in the specified GUI framework without custom engine work
- [ ] The packaging command includes all assets the application needs at runtime

### 8.3 Developer Usability
- [ ] A mid-level developer can identify the first file to create and what to put in it
- [ ] The most complex function has pseudocode or detailed implementation notes
- [ ] All database schemas are shown as explicit CREATE TABLE statements
- [ ] The startup sequence is documented as an ordered list of steps
- [ ] All error states visible to the user have a specified recovery path

### 8.4 Package Contents
- [ ] Final prompt (v5 or later) included
- [ ] Revision document included if council review was performed
- [ ] Idea Brief included
- [ ] All documents formatted and legible

---

## 9. Quick Reference — The 11 Required Sections

Every build document produced by this system must contain these sections. A document missing any section is incomplete by definition.

| # | Section | Minimum Content |
|---|---|---|
| 1 | Overview & Architecture | One paragraph + component/stage table |
| 2 | Tech Stack | Tool, version, and justification for every dependency |
| 3 | Directory Tree + DB Schema | Full annotated file tree + CREATE TABLE statements |
| 4 | Module Breakdown | Responsibility, inputs, outputs, dependencies per module |
| 5 | UI Wireframe | ASCII layout + complete legend |
| 6 | Data Flow | Three labeled paths including at least one error path |
| 7 | Code Stubs | All public interfaces with type hints + docstrings |
| 8 | Error Handling | Per-module error table with cause and strategy |
| 9 | Setup & Testing | requirements.txt + commands + unit and integration tests |
| 10 | Packaging | .desktop file + packaging command with flags |
| 11 | Extensibility | 5–6 features with name, user value, implementation approach |

---

## 10. Common Failure Modes & Remedies

| Failure Mode | Symptom | Remedy |
|---|---|---|
| Architecture not constrained early | Document describes a generic app with the right name | Add explicit architectural constraints block in cycle 2 |
| Wireframe single-panel | All UI in one box; no stage separation visible | Require multi-panel ASCII wireframe with panel headers in cycle 2 |
| Vague 'sandboxed' claim | Document says exec() runs 'in a sandboxed namespace' | Require specification of actual sandbox mechanism or honest deferral |
| Blocking calls on main thread | pip install, file I/O called directly — UI would freeze | Require Worker/QRunnable pattern for all blocking operations |
| Pickle-only serialization | Subprocess return values break for third-party objects | Require serialization hierarchy: json → pickle_b64 → repr |
| Missing startup sequence | App appears but developer doesn't know what happens first | Require ordered startup sequence as a dedicated subsection |
| No integration tests | Unit tests pass but pipeline never tested end-to-end | Require at least one integration test in the test scaffold |
| Extensibility too generic | Features like 'add more settings' or 'improve performance' | Require user value statement and concrete implementation approach per feature |
| Prompt grows without pruning | v4 prompt is 3× longer than v1 with no gain in quality | Apply efficiency rules: remove redundant instructions after each cycle |

---

## Appendix — Glossary

| Term | Definition |
|---|---|
| Idea Brief | The structured one-page summary produced at the end of Phase 1 Q&A |
| Seed Prompt | The v1 prompt — intentionally incomplete, designed to produce a reviewable first draft |
| Completeness Framework | The checklist of 30+ items used to identify gaps in each simulated AI response |
| Gap Analysis | Step 2 of each cycle — comparing simulated response against the Completeness Framework |
| User Simulation | Step 3 of each cycle — adopting a developer's perspective to find experience-level gaps |
| Council Review | A senior architectural review of the candidate final document before delivery |
| Foundational Reconsideration | An architectural flaw that, if not fixed, makes implementation unreliable |
| RunResult Envelope | The JSON contract between a subprocess and the main process — a pattern for structured output capture |
| Worker Pattern | QRunnable + WorkerSignals — the Qt-idiomatic way to run blocking operations off the main thread |
| Tiered Venv | A persistent base virtual environment plus per-session overlay environments — balances startup speed and isolation |

---

*IdeaForge Prompt System v1.0 · AI Advancement Collective · Production Release*
