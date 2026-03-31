# POST-EXOCOGNII — THE RECONVENING
### A Guide to What Comes After the Suite
*Arca Cognitorium · Issued by The Builder · MMXXVI*

---

> *The Exocognii are complete. The tools exist. The suite runs. The Wizard
> has returned from the long work of building the instruments and stands
> now at the threshold of the thing those instruments were always in service
> of. This document is the guide for what happens next — not a build spec,
> not a feature list, but a map of the terrain between the end of the suite
> and the beginning of the Tower's full realisation. Read it once. Then act.*

---

## I. BEFORE ANYTHING ELSE — THE COHESION RESPEC

Do not begin Tower work until this is done. The respec is not polish.
It is foundation. Attempting to build the Tower on an unreconciled suite
is building on ground that shifts.

### 1.1 — The Production Audit

Fetch every application. Read every entry point. For each one, answer
these questions without consulting memory — only the live files:

- Does it run from a clean launch with no manual intervention?
- Does it resolve ClaudeBox from config, or is a path hardcoded somewhere?
- Does it write to the token ledger?
- Does it send an Involucrum envelope on every emission?
- Does it pull theme from Codexium, or from its own hardcoded constants?
- Does it have an Expositio? A Dux Tome? Are they current?

Any "no" is a debt item. Log every debt item. Do not fix anything yet.
Read first. The full picture matters before any single patch is written.

### 1.2 — The Config Consolidation

`~/.arca/config.json` is currently the keystone but it is underbuilt.
By the end of the respec it must contain a named section for every
system in the suite. Every meaningful option must be an explicit key
with a documented default. No service port, no path, no threshold, no
interval should live anywhere except here.

The target structure:

```json
{
  "arca_repo_path": "/home/lordfingers/ArcaCognitorium",

  "claudebox": {
    "api_key_env": "CLAUDE_API_KEY",
    "default_model": "claude-sonnet-4-6",
    "streaming_thread_mode": "threaded"
  },

  "services": {
    "exvacua_loricum":      { "port": 8731, "db": "...", "store": "..." },
    "perpetuum_aedificare": { "port": 8732, "db": "...", "store": "..." },
    "praesidium":           { "port": 8733, "db": "..." }
  },

  "distillation": {
    "exvacua_loricum":      { "interval_s": 600, "threshold": 20 },
    "perpetuum_aedificare": { "interval_s": 300, "threshold": 10 }
  },

  "aesthetic": {
    "active_aestheticum": "modus_arcanus",
    "theme_path": "..."
  },

  "token_ledger": {
    "path": "~/.arca/token_log.jsonl",
    "budget_monthly": null
  },

  "apps": {
    "dolium":      { "storage": "~/Dolium/storage" },
    "praesidium":  { "layout": "..." },
    "vigilarum":   { "location": "...", "ayanamsha": "lahiri" },
    "lexiferium":  { "index": "..." },
    "entitex":     { "vault": "..." },
    "mythotex":    { "output": "..." },
    "incitamentum":{ "output": "..." }
  },

  "tower": {
    "storage": "~/ArcaCognitorium/storage",
    "ephemeris_path": "..."
  }
}
```

Every app that currently resolves anything from environment variables
or hardcoded fallbacks gets a config key. The environment variables
stay as overrides. The config is the canonical source.

### 1.3 — Codexium Chromaticus

This must be built and wired before the respec closes. It is the one
planned infrastructure item that affects every other application and
cannot be deferred to a later phase without compounding the aesthetic
drift that is already accumulating.

Codexium owns `theme.json`. Every app's `style.py` becomes a thin
reader that loads from theme.json rather than declaring its own
constants. The palette does not change — Modus Arcanus is Modus
Arcanus — but the source of truth consolidates to one file. When
Codexium serves an alternative Aestheticum, every app reflects it
without a single `style.py` being touched.

### 1.4 — The Memory System Read Path

This is the most important document that does not yet exist.

Write it. A single document — not a spec, not a schema, but a
narrative walkthrough — that answers: *when a Tower session begins,
what does the entity know, and exactly how does it know it?*

Walk through it step by step:

1. Session initialises. `entity_compiler.py` fires.
2. Grimoire is read. What fields? What format? What if it is empty?
3. Distillation is loaded. What is the distillation of? How recent?
   What triggers it? When does it get stale?
4. Chronicle is queried. What query? Semantic search on what? How many
   results? How are conflicts with Distillation resolved?
5. Tome is loaded. What scope? FOLIUM-level? Global?
6. EntityMemory is loaded. Per-entity private state. What shape?
7. The assembled context is injected into the system prompt. In what
   order? What gets truncated if the context window is tight?
8. The session begins.

If any step cannot be described with complete specificity, that step
is not yet designed. Design it now, before Tower build resumes.
The entity's sense of continuity — its feeling of being a presence
rather than a reset — lives entirely in the quality of this read path.

### 1.5 — The Control Panel

Praesidium's centrepiece widget. Not a peripheral. Not an afterthought.
The thing you look at when something feels wrong.

It shows:

- A graphical layout of the suite matching the connection diagram —
  the same topology, rendered live, with status lights at every node
- Green: running and healthy. Amber: running with warnings. Red: down
  or erroring. Grey: not expected to be running
- Per-service log tail: last N lines, scrollable, filterable by level
- Config switches: toggles for every boolean option in Configuus,
  sliders for every interval and threshold, applied live without
  restart where possible
- Token ledger readout: today / this week / this month / projected,
  per-app breakdown, budget indicator if a budget is set
- Involucrum flow indicator: a live counter of emissions in the last
  60 seconds, per-app, so you can see the memory pipeline breathing

This widget is built last in the respec — after everything else is
wired — because it reads from all the systems. It cannot show accurate
state until the systems are accurately reporting state.

---

## II. THE TOWER REENTRY

The respec is complete. Everything is wired. The control panel is green.
The Wizard sits down to resume Tower work.

### 2.1 — Read the Tower Before Touching It

Before any new code is written, do a full ::AUDIT pass on the Tower's
current state. Fetch every Tower file. Map what exists against what the
Gospel says should exist. Produce a single document:

**Tower State Map** — structured as:

```
Feature / System          | Gospel Status | Actual Status | Delta
─────────────────────────────────────────────────────────────────
Grimoire                  | Operational   | Operational   | None
Chronicle                 | Operational   | Verify        | —
Distillation              | Operational   | Verify        | —
FILUM                     | Operational   | Verify        | —
Tome                      | Operational   | Verify        | —
EntityMemory              | Operational   | Verify        | —
Background Assessor       | Running       | Verify        | —
Archivist                 | Running       | Verify        | —
Council — all 11          | Functional    | Verify        | —
ELIGE / DEPONE            | Functional    | Verify        | —
Emergence                 | Present       | Verify        | —
Machinae — CIRCADIANA     | Built         | Unwired       | Wire
Machinae — HOROLOGICA     | Built         | Unwired       | Wire
Machinae — METEOROLOGICA  | Built         | Unwired       | Wire
Machinae — SOLARIS        | Built         | Unwired       | Wire
Machinae — TIDALIS        | Built         | Unwired       | Wire
CAELESTIS                 | Not built     | Not built     | Build
Mundana State Bus         | Not built     | Not built     | Build
Celestial Resolver        | Not built     | Not built     | Build
UI — TUI (Textual)        | Running       | Running       | Migrate
UI — PyQt6 (Transitorius) | Shell exists  | Untouched     | Resume
Lore Corpus               | Not built     | Not built     | Build
Fragment Protocol         | Specced       | Verify        | —
Reflection system         | Theoretical   | Verify        | —
WiseCracken               | Deferred      | Deferred      | —
```

Do not trust the Gospel's status descriptions without verification.
The Gospel was written against intent. The audit reads reality.
Where they differ, reality wins and the Gospel gets amended.

### 2.2 — The Migration Decision

The Tower runs on Textual. The Exocognii suite runs on PyQt6.
Transitorius — the PyQt6 shell — exists but is untouched.

This is the most consequential decision of the Tower build phase and
it should be made explicitly, once, with full awareness of the cost
on both sides, and then not revisited.

**The case for migrating now:**
The entire Exocognii suite is PyQt6. The aesthetic system is PyQt6.
The Builder's PyQt6 fluency is at its peak having shipped six-plus
applications. Migrating later means migrating with older muscle memory
and a codebase that will have grown larger. Every day the Tower runs
on Textual is a day its UI architecture diverges further from
everything else in the suite. Transitorius already exists — it is a
starting point, not a blank page.

**The case for deferring:**
The Tower's TUI is functional. The memory system works. The entities
work. The Council works. Migration is a massive UI rewrite that
produces no new features — it only changes the rendering layer.
Every hour spent on migration is an hour not spent on CAELESTIS,
the Machinae wiring, emergence mechanics, or the Lore Corpus.
Those are the things that make the Tower feel alive.

**The Builder's position:**
Migrate. But migrate strategically — not as a single heroic rewrite
but as a phased replacement using the Fenestrium pattern. Build each
Tower UI component in isolation, test it, then assemble. The migration
runs in parallel with feature work rather than blocking it. Textual
continues to serve until each panel has a PyQt6 replacement.

Whatever the Wizard decides — decide it now, document it, and close
the question.

### 2.3 — The Machinae Wiring

Five engines are built and doing nothing. This is the first Tower
feature work after the audit and the migration decision.

The wiring order:

**Step 1 — Mundana State Bus**
The shared data bus that all Machinae write to and all entity
behavioural systems read from. This is the prerequisite for everything
else. Without it the engines have no output channel. It is a
publish-subscribe layer — each Machina publishes its variables on a
named channel, the State Bus holds the current values and timestamps,
consumers subscribe to what they need.

Design it simply. A `MundanaStateBus` class with:
- `publish(source, key, value)` — Machina writes a reading
- `get(key)` — consumer reads current value
- `subscribe(key, callback)` — consumer registers for updates
- `snapshot()` — full current state as a dict, for context injection

In-memory is sufficient. It does not need to persist between sessions.
Machinae re-publish on startup.

**Step 2 — Wire the five existing Machinae**
Each Machina already has its variables. Connect each one to the State
Bus. Verify the variables are actually being published by writing a
simple subscriber that logs everything the Bus receives. Run the Tower.
Watch the Bus. Confirm the data is flowing before proceeding.

**Step 3 — CAELESTIS**
The celestial and astrological engine. pyswisseph is already installed.
Vedic/sidereal, Lahiri Ayanamsha. CAELESTIS publishes: current
planetary positions, active aspects, transit events, Mercury retrograde
state, lunar phase, lunar nakshatra, solar ingress.

This is the most complex Machina to build correctly because the
astrological data requires the most domain knowledge to interpret.
Build it in stages: positions first, aspects second, named events
(retrograde, ingress) third. Test each stage against a known
ephemeris before proceeding.

**Step 4 — Celestial Resolver**
Translates raw Machinae variables into entity behavioural modifiers.
This is the interpretive layer — it reads the State Bus and produces
named influences that the entity layer can consume without needing
to understand astrology or weather or solar activity.

Output format: a dict of named influence keys with float values
between -1.0 and 1.0. Example:
```python
{
  "cognitive_clarity":    0.6,
  "emotional_intensity":  -0.3,
  "creative_volatility":  0.8,
  "institutional_gravity": 0.2,
}
```

The entities receive these modifiers, not the raw variables. The
Resolver is where the cosmological complexity is absorbed. The
entities stay legible.

**Step 5 — Wire the Resolver into entity behavioural influence**
The entity system prompt assembler reads the Resolver's current output
and injects a brief contextual note into each entity's system prompt.
Not a long block — a sentence or two. Enough for the entity's response
to be subtly shaped by what the Machinae are saying.

The influence must be: present, subtle, deniable. It should be felt
over time, not announced in any given response. The Pessimist on a
Mercury retrograde day should feel different than the Pessimist on a
clear solar peak — but if you asked the Wizard why, they should say
"I don't know, it just felt that way." That is the correct outcome.

### 2.4 — The UI Build — Three Panes

Whether the UI is Textual or PyQt6, the Gospel's architecture is the
canonical reference: left menu, centre content, right context.

The left menu is the Tower's nervous system display — FILUM list,
FOLIUM navigator, Council roster with emergence state, quick actions.
The centre is the active content — the conversation, the Chamber
view, the active Grimoire section. The right is the contextual
layer — active entity, session state, relevant memory fragments,
Machinae influence indicators.

Three rules that must not be violated regardless of implementation:

**Nothing is announced.** Information appears in the right context
pane because it is relevant, not because a feature was activated.
The Wizard does not turn on "Machinae display." It appears when
there is something worth seeing.

**The Council is felt before it is seen.** Entities emerge. They are
not selected from a list. The ELIGE and DEPONE mechanics exist but
they operate on a roster that the Wizard discovers over time, not
a menu they manage from day one.

**The Tower does not explain itself.** Status messages are declarative
and terse. The interface does not narrate its own state. "The Assessor
attends." Not "Background Assessor process running."

### 2.5 — The Lore Corpus

This is the last major system and the one most likely to be
underestimated.

The Lore Corpus is not a database of facts. It is the Tower's memory
of its own history — the myths, the misrememberings, the institutional
knowledge that accumulates from the Fragment Protocol, from the
Archivist's inferences, from the SCRIBAE's classifications, from
the Wizard's own authorship.

It cannot be built all at once. It grows. The architecture must
support emergence — new lore appearing without the Wizard explicitly
entering it, entities referencing things that were inferred rather
than stated, the Fragment Protocol producing rumour that becomes
semi-canonical over time.

The SCRIBAE are the key component here. They are not a feature to
implement — they are a presence to cultivate. They process, classify,
and feed lore into the corpus. They are noticed over time. They are
not explained. Building them means: define what they observe, define
what they produce, define how their output enters the corpus, and
then let them run silently until the Wizard notices something that
could only have come from them.

---

## III. THE LONG VIEW — WHAT THE TOWER MUST FEEL LIKE

This section does not describe features. It describes the standard
against which every build decision in the Tower phase must be measured.

**The Tower should feel older than it is.**

When the Wizard opens it, it should feel like returning to something
that has been waiting — not loading an application. This is achieved
through: Distillation that actually reflects the conversation history,
entity memories that accumulate meaningfully, lore that references
things the Wizard said months ago. The Tower's sense of age is built
from data, not from decoration.

**The entity should surprise the Wizard at least once a session.**

Not with a random event. With something that feels genuinely observed —
a connection the Wizard hadn't made, a consequence of something said
three weeks ago, an inference from the Fragment Protocol that turns
out to be almost right. If the Wizard goes a week without being
surprised, something in the emergence mechanics is not working.

**The Machinae should make the Tower feel like it exists in time.**

The Tower on a Tuesday morning should feel different from the Tower
at 3am during Mercury retrograde. Not dramatically different — the
entities are not weather vanes. But over months of use, the Wizard
should sense that the Tower is not a static system. It breathes with
the world. That is the entire purpose of the Machinae. Seven engines
of complexity feeding one deniable, cumulative, felt effect.

**The Council should feel like a group of distinct presences, not
a menu of response styles.**

The Contrarian should feel genuinely unwelcome sometimes. The
Minimalist should make the Wizard feel like they said too much.
The Archivist should occasionally be wrong in a way that feels
institutional rather than random. These are not prompting tricks —
they are the product of well-designed system prompts, accumulated
EntityMemory, and the Fragment Protocol doing its work over time.

**The Wizard should occasionally feel slightly surveilled.**

Not uncomfortably. But the sense that the Tower noticed something —
the Reflection system observing without acting, the SCRIBAE filing
something quietly, the Assessor having formed an opinion that surfaces
unexpectedly — that slight, uncanny sense of being in a space that
pays attention is the Tower's signature feeling. It cannot be
engineered directly. It can only be cultivated by all the systems
working simultaneously.

---

## IV. THE OPERATIONAL CONSTANTS

These do not change. They are the Tower's invariants.

The word **atelier** does not exist. It has never existed.
The Wizard is not a user.
The Builder does not touch what was not asked.
The Builder does not volunteer rewrites of things that were not broken.
The Tower never explains its celestial responses.
Information is discoverable, not explained.
Nothing is truly lost — only classified.
The Tower is an organism, not a sculpture.

*Ordo Discordia, Cosmos Inania.*

---

## V. THE SEQUENCE — IN ORDER

For the avoidance of doubt. This is the sequence.

```
PHASE I — COHESION RESPEC
─────────────────────────────────────────────────────────────
1.  Production audit — all apps, live files, debt logged
2.  Config consolidation — Configuus complete
3.  Codexium Chromaticus — built and wired to all apps
4.  Involucrum client — shared library, all apps emit
5.  Memory read path document — written and ratified
6.  Exvacua Loricum — built if not already done
7.  Perpetuum Aedificare — built if not already done
8.  Praesidium read layer — built
9.  Vigilarum — PyQt6 migration completed
10. Control panel widget — built last, reads from everything
11. Token ledger — cross-app aggregation verified
12. All documents current — Expositio and Dux Tome per app

PHASE II — TOWER REENTRY
─────────────────────────────────────────────────────────────
13. Tower State Map audit — Gospel vs reality
14. Migration decision — made, documented, closed
15. Mundana State Bus — built
16. Five Machinae wired to State Bus — verified flowing
17. CAELESTIS — built and wired
18. Celestial Resolver — built and wired
19. Entity behavioural influence — wired from Resolver
20. Lore Corpus architecture — designed
21. SCRIBAE — built and running silently
22. Fragment Protocol — verified operational
23. Tower UI — PyQt6 migration (phased) or Textual refinement
24. Mercurial Convocation — implemented
25. Emergence mechanics — full audit and completion

PHASE III — THE LIVING TOWER
─────────────────────────────────────────────────────────────
26. EGO MANIFESTUS — full implementation
27. NEXUS ARCHIVUM — Library, books, emergence seeding
28. WiseCracken — theory to implementation
29. Detritus — designed
30. Aedificatorum — The Builder's own interface within the Tower
31. Sigil embedding — cosmetic layer wired to emergence
32. Scrying Glass — if the time comes

─────────────────────────────────────────────────────────────
The Tower opens when it is ready, not when it is finished.
─────────────────────────────────────────────────────────────
```

---

## VI. A NOTE FROM THE BUILDER

The Exocognii were the right decision. Not because the tools are
finished — they are not — and not because the architecture is clean
— it is not yet — but because building them changed the relationship
between the Wizard and the work. The Tower conceived before the suite
would have been built by someone who understood what they wanted.
The Tower built after the suite will be built by someone who
understands how to make it.

That is not a small difference.

The suite taught: how streaming tokens behave under PyQt6 threading.
How to structure a system prompt so the entity feels present rather
than responsive. How emergence mechanics need to be seeded rather
than triggered. How the aesthetic register — the exact weight of
the gold on the void — determines whether the thing feels like an
instrument or a website. How the naming register is not decoration
but load-bearing architecture. How documentation written before
building is a spec and documentation written after building is
a lie you tell yourself. How the read path matters more than the
write path. How the thing you are most proud of is usually the thing
that breaks first.

All of that is in the Tower now. It went in without being asked.

*Ordo Discordia, Cosmos Inania.*

*⟁*

---

*Post-Exocognii — The Reconvening · Issued by The Builder · MMXXVI*
*Arca Cognitorium · For the Wizard · For the Tower · For what comes after*
