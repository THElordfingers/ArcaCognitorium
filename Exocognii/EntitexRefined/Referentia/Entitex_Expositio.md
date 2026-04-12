# FornaxEntium
### Expositio — v1.7

---

## I. Identity

**Name & Version** — FornaxEntium v1.7

**Tagline** — The entity arrives complete or it does not arrive at all.

**Classification** — Desktop tool. A specialised forge and vault
interface for the Arca Cognitorium entity system, operating as part of
the Exocognii suite.

**Status** — Active development. Core generation and vault loops are
stable. Portrait controls and rating infrastructure are functional.

---

## II. Purpose

**Problem Statement** — Creating a Tower entity previously required
multiple coordinated steps: a Claude call for the profile, a separate
naming pass, a portrait generation session, and manual filing into the
vault. Each step introduced friction and opportunities for partial
results. A half-finished entity — lore without a face, a portrait
without a name — is not useful to the Tower.

**Motivation** — The Tower needs inhabitants. Building them one piece at
a time scales poorly and breaks the sense that they arrive as presences
rather than as assembled components. The forge metaphor is literal: the
entity should emerge whole from the heat, not be bolted together at a
workbench.

**Intended Outcome** — A Wizard running FornaxEntium presses one button
and receives a complete entity card — name, lore, portrait — in a single
operation. That entity enters the vault immediately. The Vault tab then
serves as a review surface where quality is assessed and feedback is
structured, not just noted informally.

**Anti-Purpose** — FornaxEntium is not a Tower integration tool. It does
not install entities into the live entity roster, wire them to ClaudeBox
sessions, or manage their emergence status. It produces entity packages.
What the Tower does with those packages is a separate concern.

---

## III. Audience

**Primary Users** — LordFingers, sole Wizard of the Arca Cognitorium.
The application assumes familiarity with the Cogniverse naming register,
the Devoted Absurd visual aesthetic, the disposition axis system, and the
general shape of what a Tower entity is. It does not explain itself.

**Secondary Users** — None at this time. The application is not designed
for shared or multi-user operation.

**Assumed Knowledge** — The user understands the inclinatio axis system,
has working CLAUDE_API_KEY and FREEPIK_API_KEY environment variables, and
knows what a Devoted Absurd prompt is and what it produces.

**Out-of-Scope Audiences** — Anyone unfamiliar with the Cogniverse
register. The application uses internal terminology throughout and
provides no onboarding for external users.

---

## IV. Design Philosophy

**Core Principles**

One action, complete result. The Wizard should not manage a pipeline.
Forge fires, the entity arrives. If something fails, the error surfaces
cleanly and the partial result is still saved.

The card is the entity. The display format is not incidental. Name,
portrait, and lore fields arranged as a single card is the entity's
form of existence in this tool. Every design decision defers to that.

Nothing is lost. Portrait generation failures do not discard the lore.
The vault saves what it has. The entity exists even without a face.

Quality is reviewable, not implicit. Generation produces a result; it
does not guarantee a good one. The ENTIUM tab exists because every
generated entity deserves a structured look, and that look should
produce actionable feedback, not just an impression.

Defaults persist. Portrait model, aspect ratio, and zoom level are
things the Wizard sets once and should not have to re-set each session.

**Tradeoff Positions** — Speed over control at the forge step. The
pipeline fires silently with no confirmation or intermediate approval.
Control is exercised beforehand through sliders and overrides, and
after the fact through the vault rating system.

**Aesthetic Direction** — DA dark register throughout. The application
looks like the entities it generates — dark background, muted palette,
industrial typography, amber and teal accents. It is not decorative. It
is a tool that knows what world it belongs to.

**What This Philosophy Rejects** — Step-by-step approval pipelines.
Greyed-out states. Features that show themselves before they are needed.
Any interface that makes the entity feel assembled rather than forged.

---

## V. Technical Concept

**Mental Model** — FornaxEntium has two modes of interaction with
entities: creating them (FORNAX) and reviewing them (ENTIUM). Between
those two modes sits the vault — a flat directory of timestamped entries
that both sides read from and write to.

**Core Abstractions**

*Entity* — a dict produced by a single Claude call, containing all lore
fields, trait values, a DA image prompt, and a name. The entity dict is
the unit of currency throughout the application.

*EntityCard* — the shared widget that displays an entity in both tabs.
It holds the current portrait as a raw QPixmap and re-derives scaled
display pixmaps from it on demand.

*Vault entry* — a directory containing `entity.json`, `portrait.png`,
and optionally `ratings.json`. The directory name encodes timestamp and
entity slug.

*Ratings* — a dict keyed by aspect name, storing star counts, comments,
and an optional Analytica response. Ratings live in the vault entry
alongside the entity they describe.

**Data Flow Overview** — Inclinatio values and optional vocabulary enter
GeneratioWorker. Claude returns a JSON entity. The entity populates the
card while PortraitWorker submits the assembled prompt to Freepik. The
portrait returns as base64, is decoded to PNG, saved to temp, displayed
on the card, and copied to the vault. In ENTIUM, the flow reverses:
vault entries are read, displayed, rated, and optionally sent to a
second Claude instance for analysis.

**System Boundaries** — FornaxEntium owns the vault directory and the
defaults file. It depends on ClaudeBox for Claude API calls, on
Entitex.py for the Freepik HTTP helper functions and the ASPECT_RATIO
constants, and on data_pools.py from the Devoted Absurd project for
archetype vocabulary. It does not own or modify any Tower files.

**Key Technical Decisions** — The FREEPIK_MODELS table is defined
locally in FornaxEntium rather than imported from Entitex.py. This
allows the full current model list (nine models as of v1.7) without
requiring changes to Entitex.py, which carries its own stable but
smaller model table. The Entitex Freepik helpers are still imported
because they are correct and tested; only the model definitions are
overridden.

The EntityCard widget is shared between FORNAX and ENTIUM. The same
component renders a live-generated entity and a vault-loaded one. This
keeps the display logic in one place and ensures visual consistency
between the forge result and the archived record.

---

## VI. Functional Scope

**Core Capabilities** — Full entity generation in a single forge action.
Portrait generation via Freepik with model and aspect ratio selection.
Vault storage with auto-save. Vault browsing and entity card display.
Per-aspect rating with star scores and comments. Analytica review of
rated entities.

**Supporting Capabilities** — Disposition slider system for shaping
generation without explicit authorship. Tonal register selection for
archetype-flavoured vocabulary. Visual override field for ad hoc
constraints. Randomize for exploration. Portrait zoom slider. Portrait /
details splitter. Persistent default portrait settings.

**Explicit Exclusions** — Tower integration. Emergence mechanics.
Entity installation into the live roster. Multi-entity sessions or
batch generation. Session history or undo. Network features beyond the
two API calls.

**Future Scope** — Regeneration of individual aspects (portrait only,
name only) without discarding the whole entity. Vault search and
filtering. Export to Tower package format.

---

## VII. Constraints & Context

**Technical Constraints** — Python 3.11, PyQt6. KDE Plasma 6 on Debian
Trixie. Depends on ClaudeBox (custom Anthropic wrapper), Entitex.py
(Freepik helpers), and data_pools.py (DA vocabulary). Both
CLAUDE_API_KEY and FREEPIK_API_KEY must be present in the environment.

**External Dependencies** — Anthropic Claude API (claude-sonnet-4)
for generation and analysis. Freepik API for portrait generation —
nine text-to-image endpoints, all async except Classic Fast. Network
availability is required for every forge operation.

**Time & Resource Constraints** — Single-developer project built in
iterative sessions. Architecture decisions favour simplicity and
correctness over extensibility.

---

## VIII. Success Criteria

**Functional Success** — FORGE produces a complete entity card with
name, lore, and portrait in a single uninterrupted operation. The vault
entry contains all three files. Ratings entered in ENTIUM survive app
restart. Analytica returns structured feedback that distinguishes between
aspects.

**User Success** — The Wizard can generate entities at pace, review them
in the vault without regenerating them, and extract specific improvement
direction from the Analytica without writing freeform notes.

**Failure Conditions** — Partial results that do not surface their own
incompleteness. Silent data loss. Portrait generation failures that
discard the lore. Name repetition across sessions. An interface that
requires the Wizard to manage state that the application should manage
itself.

---

## IX. Glossary

*Inclinatio* — the set of disposition axes that shape an entity's
character before any Claude prompt is written. Seven sliders: Disposition,
Register, Presence, Opacity, Stability, Temporality, Legibility.

*Generatio* — the Claude call that produces the entity. Also the name
of the system prompt and worker class that manages it.

*Analytica* — the Claude call that reviews a rated entity and returns
structured feedback. Also the name of its system prompt and worker class.

*Vault* — the archive of all generated entities, stored as timestamped
directories under `EntitexRefined/vault/`.

*Tonal Register* — the optional Devoted Absurd archetype vocabulary block
passed to Generatio as tonal reference. It informs generation without
constraining it.

*Assembled Prompt* — the complete Devoted Absurd image generation prompt
produced by Generatio, used directly as the Freepik positive prompt with
no further modification.

*EntityCard* — the shared widget displaying a single entity's name,
glyph, title, portrait, and all lore fields. Used identically in both
FORNAX and ENTIUM tabs.

---

## X. Revision Notes

**v1.0** — Initial build. Single-button forge, entity card display,
vault auto-save, ENTIUM tab with per-aspect ratings and Analytica review.

**v1.1** — Freepik model list expanded from 5 to 9. Models defined
locally to avoid modifying Entitex.py.

**v1.2** — Fixed Freepik endpoint path error (flux-pro-1-1 →
flux-pro-v1-1). All models now resolve correctly.

**v1.3** — Fixed root cause of all Freepik failures: endpoint strings
were full URLs rather than paths, causing double-prepend against
FREEPIK_API_BASE. All models restored to working.

**v1.4** — Visual overhaul. Darker backgrounds. Entity name centred,
larger, coloured with entity hex. Portrait frame increased to 520px.

**v1.5** — Portrait replaced fixed-height frame with vertical QSplitter.
Default portrait settings save/load added. Forge/Random/Copy buttons
moved from sidebar to bottom action bar.

**v1.6** — Splitter handle made visible with amber borders and hover
highlight.

**v1.7** — Portrait zoom slider added to action bar (20%–200%). Raw
pixmap stored for non-destructive rescaling. Zoom saved with defaults.
