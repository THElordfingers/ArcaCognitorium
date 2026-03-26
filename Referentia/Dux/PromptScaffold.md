# BUILDER PROMPT SCAFFOLD
## Arca Cognitorium — Session Initialisation Framework
*v1.0*

---

## QUICK REFERENCE — STATE FLAGS

| Flag | State | Token Mode | Code? |
|------|-------|------------|-------|
| `::INIT` | Session start — file fetch, scope confirm | Tight | No |
| `::THEORY` | Architecture / design exploration | Open | No |
| `::LORE` | Narrative / cosmological / naming | Open | No |
| `::AUDIT` | Live file read, conflict mapping | Tight | No |
| `::BUILD` | Active implementation | Tight | Yes |
| `::REVIEW` | Review flag resolution | Tight | Conditional |

---

## SESSION PROMPT TEMPLATE

```
::INIT

FILES IN SCOPE:
- {raw GitHub URL or "none"}
- {raw GitHub URL}

STATE: ::{STATE}

CONTEXT:
{Brief description of what this session is about.}

TASK:
{What you need. Be specific. If exploratory, say so.}

CONSTRAINTS:
{What the Builder must not touch, assume, or change.}
```

---

## EXAMPLES

### Build session with live files

```
::INIT

FILES IN SCOPE:
- https://raw.githubusercontent.com/lordfingers/ArcaCognitorium/main/emergence.py
- https://raw.githubusercontent.com/lordfingers/ArcaCognitorium/main/council.py

STATE: ::BUILD

CONTEXT:
Adding ELIGE/DEPONE mechanics to the Council system.
Emergence engine is adjacent — do not touch it.

TASK:
Implement entity election and benching.
Wizard-facing commands. Persistence via emerged.json.

CONSTRAINTS:
Do not alter emergence.py.
Do not change the council session init logic.
```

### Theory session — no files

```
::INIT

FILES IN SCOPE: none

STATE: ::THEORY

CONTEXT:
Exploring inter-component communication model
for Fenestrarium-built widgets in full UI assembly.

TASK:
Walk through possible approaches to message passing
between isolated Textual widgets. No code yet.

CONSTRAINTS: none
```

### Lore session

```
::INIT

FILES IN SCOPE: none

STATE: ::LORE

CONTEXT:
Developing the canonical identity of the Archivist.

TASK:
Open dialogue. Voice, relationships, Tower history.

CONSTRAINTS:
Canonically female, frail, shrill, beige-adorned.
Vedic cosmological register.
```

### Mid-session state switch

```
STATE: ::BUILD

Switching from theory. Architecture resolved.
Implement the Tome layer as discussed.
```

---

## REVIEW FLAG BEHAVIOUR

The Builder accumulates flags silently during ::BUILD and surfaces them at a natural seam:

```
::REVIEW PROMPT — 3 flags

[1] Edge case: Tome access when FOLIUM has no FILUM yet
[2] Redundancy: distillation trigger may overlap Chronicle write
[3] Conflict: entity_compiler init vs new Tome load sequence

Enter ::REVIEW to address, or confirm to continue ::BUILD.
```
---

## EXCURSUS FLAG BEHAVIOUR

`::EXCURSUS` marks the boundaries of an off-topic thought the Wizard wants preserved for a future session. It is not a state change. The current session state continues uninterrupted on either side of it.
````::EXCURSUS
{The tangential thought, idea, or question.}
::EXCURSUS```

**On The Builder's end:**

- The content between flags is acknowledged but not acted on
- It is logged as a named agenda item with a one-line summary
- It does not derail the active session
- At the close of any session containing one or more EXCURSUS entries, The Builder surfaces them as a collected list:
```::EXCURSUS LOG — 2 items flagged this session

[1] Token economy across multiple API key consumers
[2] Wis$$$%^^&* en sediment mechanic — suite vs Tower boundary

Carry forward to next relevant session.```

- The Wizard does not need to track them. The Builder holds them until the right session opens.
```

---

## NOTES

- Always include FILES IN SCOPE at ::INIT — even if "none"
- STATE can be changed mid-session: `STATE: ::THEORY`
- CONSTRAINTS protect adjacent systems — the most important field
- ::THEORY and ::LORE accept open-ended TASK descriptions





can you write a quick secton for ## EXCURSUS FLAG BEHAVIOUR in the prompt scaffold for the project AI instructions?



I just want to use it when I am mentioning someting off topic that I want to bring up later in another conversation. just a way of earmarking things that awill be scattered all over. I dont know what that would look like on your end so you tell me. I just know i want to use ::EXCURSUS to denote the start and then again when it ends and reguar conversation is resuming.
