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

## NOTES

- Always include FILES IN SCOPE at ::INIT — even if "none"
- STATE can be changed mid-session: `STATE: ::THEORY`
- CONSTRAINTS protect adjacent systems — the most important field
- ::THEORY and ::LORE accept open-ended TASK descriptions
