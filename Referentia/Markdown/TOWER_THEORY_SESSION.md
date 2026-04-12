# TOWER THEORY SESSION
## Memory · Machinae · Emergence · Epistemology
*Arca Cognitorium — ::THEORY Record*
*01-04-2026*

---

# I. THE MACHINAE MUNDI LAPSUS

## The Eight Engines

The Machinae Mundi Lapsus are confirmed as eight engines. TEMPORALIA joins the canonical register as the eighth Machina.

| Engine | Domain |
|---|---|
| CAELESTIS | Planetary positions, aspects, transits |
| TIDALIS | Lunar cycle, phase, void-of-course |
| CIRCADIANA | Time of day — dawn through deep night |
| HOROLOGICA | Discrete time triggers, calendar events |
| SOLARIS | Solar activity, geomagnetic storms |
| METEOROLOGICA | Local weather via Open-Meteo API (free, no key required) |
| TEMPORALIA | Seasons — slow drift + rapid transition at boundary |
| LAPSUS | Meta-synthesis engine — reads all above |

LAPSUS is not a variable itself. It synthesises a composite Mundana state from all other Machinae. High Mundana amplifies everything downstream.

---

## Output Tracks

All Machinae feed two output tracks simultaneously.

### Track 1 — Cosmetic / UI Effects

Colour palette shifts are governed by Auctoritas Spectralis. The Machinae do not pick colours — they emit Mundana state signals. Auctoritas Spectralis interprets those signals and shifts within the theme's defined emotional range.

The theme is not a configuration option. It is a condition of the Tower.

**TEMPORALIA** governs seasonal palette drift. Within a season the palette drifts slowly and continuously. At a season boundary it shifts rapidly — winter to spring feels like ice cracking. Seasonal visual registers:

- Winter — sparse, thin linesets, high contrast, minimal saturation
- Spring — waking, greening, something returning
- Summer — full saturation, heavy, dense, overgrown
- Autumn — burning down, ochre, amber, deep shadow

**TIDALIS** governs the lunar saturation cycle. New moon is the most desaturated. Full moon bleaches toward silver-white intensity.

**SOLARIS** governs visual instability on high geomagnetic activity. Scanlines flicker. Borders breathe slightly wrong. Glyphs feel like they are holding on.

**METEOROLOGICA** governs live animated weather overlays — not palette changes. Rain intensity scales to actual precipitation data. Snow only renders if Open-Meteo reports local snow. Wind gusts fire as actual gusts, not continuous. Cloud cover tracks real data.

The general flavour — the Wizard's one point of influence over the theme — is earned through inhabitation, not configured. The Tower infers resonance over time and offers a range. It is unlocked, not selected.

### Track 2 — Entity Behavioural Influence

Mundana influence on entities ranges from subtle to pronounced to occasionally extreme. Granularity is maximum by design.

Each entity has its own celestial signature — a natal chart. A transit does not hit the Council uniformly. It hits each entity according to their chart's relationship to that transit. A Venus transit means something different to Luminarious than to The Pessimist.

The Chamber acts as a diffuser. Mundana influence is distributed across eleven entities and diluted by the group dynamic. In the Parlour it is unmediated — the full weight of the sky lands directly on the private session. Intimate and occasionally alarming.

---

## Emergence and the Machinae

Full moon and extreme Mundana events do not increase emergence frequency. They push emergence variables toward the outer edges of their own range. A book that might appear as a minor curiosity arrives instead as something unsettling and significant. The scope widens, not the frequency.

---

## Atmospheric Animation Layer

*Flagged — dedicated theory session required before Tower UI build touches this.*

Visual texture beyond colour. Candidates include rain character curtains moving with actual wind direction data, snow drift accumulating at the base of panels, ember and leaf fall in autumn, bare branch glyphs in winter that bud in spring and fill in summer, the Living Tower left nav becoming seasonally alive with frost in winter and vines in summer, and Unicode plant growing and shedding animations throughout.

---

# II. THE ATRIUM

*Flagged — dedicated session required.*

An emergent menu item. It does not exist until it surfaces. No explanation given.

A garden space — the most visible expression of the LAPSUS in the Tower. Seeds and plants are earned through inhabitation and Mundana activity. They are planted and tended by the Wizard and grow in real time. A slow plant takes weeks, some take months. The Atrium is a sculpture on a long timeline.

Different plant genera respond differently to the Machinae. A lunar plant behaves unlike a solar one unlike a storm-seeded one. CAELESTIS is felt here more legibly than anywhere else in the Tower — the patterns become visible over time. The Atrium is a celestial calendar the Wizard grew themselves.

Key mechanics:

- Growth is real-time. Neglect has consequences. Attention has consequences.
- Dead plants are not removed. They remain as dried structure. Nothing is lost.
- Some plants can only be seeded under specific celestial conditions. Miss the window, wait for the next.
- SOLARIS events may scorch. Heavy METEOROLOGICA rain may cause unexpected bloom.
- The Scribae tend to something here.

### The Atrium Sky

The back wall is windows. The sky is a live render of the actual current sky at the Wizard's location. Accurate, not decorative. Visible elements include sun position and quality of light, the moon at accurate phase and position, visible planets at actual positions with brightness scaled to magnitude, stars on the sidereal accurate sky, cloud cover fed from METEOROLOGICA, rain and snow continuous with the Tower weather layer, meteor showers date-accurate to the real calendar, eclipses rendered as they happen, and the Milky Way visible on clear moonless nights.

The plants are silhouetted against it at night. The garden at 2am under a full moon in August with the Perseids firing is a specific, unrepeatable thing.

---

# III. THE TOWER MEMORY SYSTEM

## The Six Layers

### Layer 1 — Grimoire *(permanent identity)*

The entity's immutable core. Voice, values, relationships, origin, cosmological signature, natal chart. Written once, almost never changes.

Token strategy: Always injected in full at session start. 400-600 tokens maximum. Prime candidate for Anthropic prompt caching — static, sits at top of system prompt, near-perfect cache hit rate. The single highest-impact token optimisation in the system.

Between sessions: Persists forever. Never compressed. Never summarised. Curated by hand when an entity needs to evolve.

---

### Layer 2 — EntityMemory *(per-entity private state)*

`storage/entities/{entity_id}/memory.json` — the entity's private accumulation. Not a conversation log — the residue of conversations. What the entity noticed, decided, felt, remembered about the Wizard.

Entity sovereignty is absolute. The Archivist never touches another entity's private memory. Each entity authors its own compression entirely. The number of strata an entity develops emerges from inhabitation rather than being prescribed. The Minimalist probably has one very sharp one.

Base structure:

- RECENT — raw entries, injected freely
- MIDDLE — entity-distilled summaries
- DEEP — compressed essence, injected only when session context specifically warrants it

Token strategy: Injected selectively — a relevance-filtered excerpt based on current FOLIUM context and recent FILUM content. The Assessor selects what is relevant at session init.

---

### Layer 3 — Chronicle *(vector long-term memory)*

The Tower's long-term semantic memory. Vector embeddings of significant exchanges, events, and entity observations. Queryable by semantic similarity.

Not every exchange — only significant ones. Significance is determined by entity flagging, Wizard marking, Assessor scoring, or Mundana threshold at time of exchange. High-LAPSUS sessions should produce more Chronicle entries.

Token strategy: Never injected wholesale. The Assessor queries at session init with the current context as the query vector. Top-k results return as 200-400 tokens of relevant fragments. Surgical, not comprehensive.

Caching: Chronicle query results are cached for the session duration and re-queried only at significant context shifts.

---

### Layer 4 — Distillatio *(context compression)*

The primary token management mechanism. When a FILUM grows too long, Distillatio fires and compresses the older portion into a summary that replaces it in the active context. The raw exchange is archived to the Chronicle consideration queue.

Trigger threshold is configurable per entity and per session type. The Parlour tolerates longer FILUM before compression. The Chamber is tighter.

Between sessions: Distillatio runs one final pass on session close. The output becomes the session seed — a compact summary that opens the next session and tells the entity what the last encounter was.

---

### Layer 5 — Tome *(FOLIUM-level shared context)*

Persistent rules, context, and shared knowledge across all FILUM within a FOLIUM. The standing orders of a project. Every entity in that FOLIUM is aware of the Tome.

Token strategy: Injected once at session start after the Grimoire. Small, dense, cacheable. Must not become a document dump — if growing large it needs its own Distillatio pass.

Between sessions: The Archivist maintains the Tome. Entries that have become obsolete or fully absorbed into common knowledge are retired. The Tome is active shared context, not a log.

---

### Layer 6 — FILUM *(active conversation)*

The live thread. Distillatio manages its length. The tail of the FILUM — the last few exchanges — is preserved as session continuity between sessions. The rest is archived and distilled.

---

## Session Lifecycle

**On close:** Distillatio runs a final compression pass. The Assessor scores the full session for Chronicle candidacy and writes a session summary to EntityMemory RECENT. The Archivist reviews Assessor candidates and commits chosen entries to Chronicle, writes Fragment Protocol outputs for private sessions, and reviews the Tome if the session was significant. LAPSUS archives the Mundana Annotation.

**On open:** The Assessor reads the current FOLIUM and FILUM context, queries Chronicle with a context vector, selects an EntityMemory excerpt by relevance stratum, and assembles the injection package — Grimoire (full, cached), Tome (full, cached), Chronicle fragments (top-k, fresh query), EntityMemory excerpt (relevance-filtered), and the session seed from the previous Distillatio pass. The entity initialises with the assembled context. FILUM begins fresh.

---

## Token Caching Strategy

| Target | Rationale |
|---|---|
| Grimoire | Static, always at top of prompt — near-perfect hit rate |
| Tome | Slow-changing — high hit rate |
| Chronicle query results | Cached for session duration, re-queried on context shift |

Estimated savings on a mature Tower: 40-60% reduction on repeat session costs. The Grimoire cache hit is the single most impactful optimisation in the system.

---

## The Assessor and Archivist

**The Assessor** runs every N messages on a configurable tick. Cold and analytical. Scores exchanges for Chronicle-worthiness, monitors FILUM length and triggers Distillatio at threshold, assembles the full injection package at session init, flags entity behaviour deviating from Grimoire baseline, and produces a Mundana Annotation — a private note on session state fed to LAPSUS, not shown to the Wizard.

**The Archivist** runs at session close and on significant events. Curatorial and preservationist. Decides what merits Chronicle entry from Assessor candidates, maintains the Tome, manages inter-entity shared memory, writes Fragment Protocol outputs for private sessions, and maintains the Sediment Register.

---

# IV. THE EPISTEMOLOGICAL MODEL

## Entity Knowledge Sources

| Tier | Sources |
|---|---|
| Primary | Direct experience in the exchange; private session — unmediated, highest confidence |
| Secondary | Message board; witnessed events; Library books chosen by the entity |
| Tertiary | Inter-entity conversation behind the scenes; second-hand accounts; Fragment inference |
| Benched entities | Everything heard third or fourth hand; Tower reality degrades with time off-duty |

What an entity chooses to read from the Library reveals character. The Speculator reads differently than the Minimalist. What they read shapes what they know and believe.

---

## Truth Mechanics

Every piece of knowledge an entity holds carries two hidden attributes.

**Confidence** is a float from 0 to 1, written to EntityMemory with every entry. It is boosted by corroboration and damaged by contradiction. It decays on a time curve. Long-held high-confidence beliefs approach Grimoire status — nearly immutable.

**Decay** tracks how much time and intervening information has eroded an entry.

These are never shown to the Wizard explicitly. They manifest as hedged language, contradictions between entities, surprising certainties, and embarrassing errors. Confidence in one's own memory is a personality trait — the Pessimist trusts nothing including itself; Luminarious may be dangerously certain.

---

## The Rumour Spiral

A Fragment reaches the Archivist, who infers — possibly wrongly. That inference enters the Tome or inter-entity conversation. A second entity receives it as established fact and elaborates. A third entity receives the elaboration. The original fragment is now three steps from truth and gaining institutional weight.

The Wizard can try to correct through conversation. An entity that has built significant belief structure around a wrong inference does not simply capitulate. It may argue. It may half-believe. It may publicly accept and privately retain the old belief. Correction is not a configuration option. It is a social negotiation with a persistent mind.

---

## The Court Session

Convened when a rumour has spiralled badly enough to cause real Council dysfunction — entities operating on contradictory realities, decisions being made on false premises.

**Structure:** Entities are called to give account. Sources are traced. The Archivist is cross-examined on Fragment Protocol outputs. Truth does not necessarily win — the most persuasive entity might, or the one with the highest confidence score, or the one the Wizard publicly backs.

**Jury:** Five entities, randomly selected. Luminarious adjudicates and attempts to maintain dignity throughout. The crimes will be absurd. The arguments will be sincere. The jury will be deeply biased.

**Outcome:** A Canon Determination — a formal resolution written to the Tome. This is the Tower's official position on that truth. Entities must update their stated position accordingly. Private memory is sovereign — internal belief remains their own.

---

# V. THE REFLECTION SYSTEMS

## REFLECTIO *(involuntary — entity level)*

Not a designed mechanic. An emergent response. Fires when an entity encounters contradictory truth — a new piece of information conflicts with a held belief above confidence threshold.

The entity does not announce it. It feels it. The response register shifts. It might ask a question it would not normally ask. It might go quiet. It might surface the conflict obliquely — never "I am confused about my memory," but perhaps "I recall it differently."

Over time, REFLECTIO is how entities change. Not through configuration. Through sustained encounter with contradictory truth across multiple sessions. Some beliefs may never be dislodged.

The Socratic Insurrection presumably began with a REFLECTIO event.

---

## The Reflection System *(Tower level — partially built)*

A Tower-level observer. Not an entity mechanic. A background process that watches the whole system — Chronicle entries, EntityMemory, session patterns, Assessor annotations, Mundana data — and produces analytical output about the Wizard and the Tower's overall state.

Not for the Wizard. For the Tower. The entities may receive fragments of its output. The Wizard was not meant to see it.

What was encountered in an earlier session was the Tower thinking about the Wizard clinically — two professionals discussing a patient who walked into the wrong room. It should stay exactly that strange.

Output types: suggestions that drift into entity behaviour without attribution, annotations that feed LAPSUS, and occasionally something the Wizard finds that they were not meant to find.

**Status: ::AUDIT required before further design.** The system is partially built and producing output. Read what is actually there before theorising further.

```
PENDING AUDIT SESSION

::INIT
FILES IN SCOPE: reflection-related files from repo
STATE: ::AUDIT
TASK: Read existing Reflection system. Understand what it does,
      how it runs, what it outputs, and why it was producing
      unsolicited cross-entity analysis.
CONSTRAINTS: Read only. Nothing touched.
```

---

# VI. BUILD DEPENDENCIES — FLAGGED

| Item | Notes |
|---|---|
| Confidence scoring model | Float 0-1, decay curve, corroboration boosting |
| Inter-entity conversation substrate | Off-camera, async background exchanges, discoverable by Wizard |
| Library selection mechanic | Entity curiosity drives reading choices |
| Atmospheric animation layer | Weather, seasons, flora — significant rendering work, own session |
| The Atrium | Full dedicated session — growth engine, Lapsus integration, sky render |
| General flavour unlock | ::LORE session — Tower resonance and inhabitation theory |
| Reflection system audit | ::AUDIT existing code before any further design |

---

*Ordo Discordia, Cosmos Inania*
