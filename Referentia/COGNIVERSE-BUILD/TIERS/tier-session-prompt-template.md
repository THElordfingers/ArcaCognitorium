# TIER SESSION OPENER — TEMPLATE
*Fill in the brackets. Delete the notes in italics.*

---

```
::INIT

TIER: TIER 5 — AESTHETIC TRINITY
TARGET: Solidify Conceptually, Build, Integrate.
STATE: ::REVIEW ::BUILD

FILES IN SCOPE:
- ~/ArcaCognitorium/Referentia/COGNIVERSE-BUILD/cogniverse_handoff/aesthetic-trinity.txt
- Pairz will be added to the repo temporarily for this stage. ~/ArcaCognitorium/Pairz/
- A new extensions was added that should allow for the Builder to access the filesystem, and the repo
- *Fetch live init_urls.txt first, then pick relevant files*


CONTEXT:
The Aesthetic Trinity is a series of bureaus of the most exacting of the definition of the word.
They are the penultimate authority on their respective matters: One for a unified source of Color Themes,
One for an inarguable and durdgin source of document templates and form masters, and the last is a place
where the very heart of interaction is decided, the building and testing of UI interfaces. Together
they control the shape and form of every visible aspect in the Towers jurisdiction.


TASK:
Three Bureaus. Three visions. One ultimate goal. Many, many wires. so fucking many wires.
We start by getting the three individual offices through IdeaForge. The Color theme office
is to be carefully designed off the back of the Pairz application. Not a thematic rendition, but
taking its best concepts to better the bureaus own vision. While not everything they need to be connected
with is finished, built and online, the concepts are there, and these builds can at least have stubs
to refine and join later.

CONSTRAINTS:
Pairz is not to be redesigned, Nor is the Color bureau to be a direct imitation. It has it's own ends to meet,
and Pairz can provide some framework and ideas. 

KNOWN STATE:
Not fucking much except dreams at this point,
```

---

## NOTES ON EACH FIELD

**TIER / TARGET** — gives the Builder immediate orientation without reading the full
operation order. One line each.

**STATE** — declare it up front. `::BUILD` for known implementation work.
`::THEORY` if the component needs a design pass before code. `::AUDIT` if you
want to inspect live files before deciding anything.

**FILES IN SCOPE** — always include even if "none." For build sessions, fetch
`init_urls.txt` from the repo and paste the URLs for the specific component.Codexium Chromaticus — Sequentiae Umbrarum
The Builder cannot fetch GitHub directly — you paste, it reads.

**CONTEXT** — not a full brief. One paragraph maximum. The project instructions
and any loaded files carry the detail.

**TASK** — the most important field. Vague tasks produce vague sessions.
"Build X" is fine if there's a doc. "Continue from where we left off" is not.

**CONSTRAINTS** — protect adjacent systems. Name every file or component
that must not be touched even if the Builder notices something wrong with it.

**KNOWN STATE** — pre-empt the audit. If you know the current file has a bug,
say so. If a decision was made last session that the Builder might second-guess,
lock it here.

---

## EXAMPLE — BUILD SESSION

```
::INIT

TIER: Tier 2 — Dolium v2
TARGET: Build Dolium v2 — full application
STATE: ::BUILD

FILES IN SCOPE:
- https://raw.githubusercontent.com/THElordfingers/ArcaCognitorium/main/Exocognii/Dolium/dolium_v2_ideaforge.md

CONTEXT:
Dolium v1 (Textual) was abandoned — token consumption unacceptable,
workflow unsatisfactory. v2 is a full rebuild in PyQt6 with an ambient
whisper system observing field changes and responding after 1.5s debounce.
IdeaForge build doc exists in repo.

TASK:
Build Dolium v2 from the IdeaForge doc. Read the doc first and confirm
architecture before writing any code.

CONSTRAINTS:
Do not patch or reference v1 files. Do not alter ClaudeBox.
PyQt6 only — not PySide6. ModusArcanus_dux_tome.md governs visual design.

KNOWN STATE:
v1 exists at Exocognii/Dolium/ — ignore it entirely.
v2 has no files yet. Full build from scratch.
```

---

## EXAMPLE — THEORY SESSION

```
::INIT

TIER: Tier 4 — Memory Services
TARGET: Name two pending items from Schema v0.4
STATE: ::THEORY

FILES IN SCOPE:
- https://raw.githubusercontent.com/THElordfingers/ArcaCognitorium/main/Exocognii/Referentia/Exocognii-Memory-Schema_v0.4.md

CONTEXT:
Two names pending before memory service build can begin:
the shared Involucrum client library, and the collective suite name
for Exvacua Loricum + Perpetuum Aedificare + Praesidium as a system.

TASK:
Naming session. Wizard is sole naming authority — Builder suggests,
does not ratify. Bring options in the Nomenclatura Arcana register.

CONSTRAINTS:
Do not begin any build work. Do not name anything without Wizard confirmation.
Nomenclatura-convention-guide.md governs all suggestions.

KNOWN STATE:
Schema v0.4 is complete and final. Names are the only open item before build.
```

---

## EXAMPLE — AUDIT SESSION

```
::INIT

TIER: Tier 1 — Incitamentum path confirm
TARGET: Verify and patch Incitamentum directory path
STATE: ::AUDIT then ::BUILD

FILES IN SCOPE:
- https://raw.githubusercontent.com/THElordfingers/ArcaCognitorium/main/Exocognii/suite.manifest.json
- https://raw.githubusercontent.com/THElordfingers/ArcaCognitorium/main/suite.py

CONTEXT:
Incitamentum may be at tools/Incitamentum/ rather than Exocognii/Incitamentum/.
Needs verification and patch if wrong.

TASK:
Audit suite.manifest.json for Incitamentum path. If incorrect, produce
a patch script to move and update references. --check mode required.

CONSTRAINTS:
Do not alter any other tool paths. Do not touch ClaudeBox.

KNOWN STATE:
All other tools confirmed at Exocognii/{ToolName}/. Incitamentum origin
predates the Exocognii restructure — may have been missed.
```
