#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨    The Dolium / manpages.py
#╚══════════════════════════════════════════════════════════════════════════════

"""
The Dolium — Manual Pages.

Written in the devoted absurd register of the Cogniverse.
These texts serve double duty: displayed to the Wizard in the manpage overlay,
and injected into every entity system prompt so the AI knows the program it
inhabits and can answer questions about it accurately.
"""

MAN_OVERVIEW = """
◆  THE DOLIUM  —  Officina Ideationum
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NATURE OF THE INSTRUMENT

The Dolium is a greenhouse for ideas. Named for the great clay vessels of
antiquity — sealed, dark, warm — in which grain and wine were stored until
their appointed time, it holds nascent thoughts in conditions suited to
their maturation.

It is not a notebook. A notebook accepts anything and forgets everything.
The Dolium refuses unripe ideas entry to the later chambers, and remembers
everything that passes through it.

It is not a task manager. Tasks are for things already understood. The Dolium
is for things that are not yet understood — ideas that need to become
something before they can be built.

It is a standalone companion to the Arca Cognitorium, though it serves any
Wizard with ideas to develop. It runs in your terminal. It speaks back.


THE PIPELINE

Ideas move through four chambers in sequence. No chamber may be skipped.
An idea may remain in any chamber indefinitely. An idea may be returned to
an earlier chamber at any time. An idea may be culled at any time.

  I.   THE FOMENTARY       — raw steeping. The idea is barely formed.
  II.  THE CULTIVATION HOUSE — refinement. The idea grows a shape.
  III. THE VESTIBULE       — analysis. The idea meets implementation reality.
  IV.  THE CODEX PARATUM   — completion. The idea is documented and waiting.


THE INTERFACE

Three panes run side by side:

  LEFT   — The Pipeline Navigator. All four chambers. Your ideas listed
           within them. Search by title. Navigate by clicking.

  MIDDLE — The Workspace. The active idea's fields. Fill them in. They
           save automatically as you type. The gate bar at the bottom
           shows what remains before you may advance.

  RIGHT  — The Chamber. A conversation with an entity whose character
           is shaped by the chamber you are in. It knows your idea.
           It knows the Arca Cognitorium. It is here to help you think.


COMMANDS

  ctrl+n   New idea
  ctrl+a   Advance to next chamber (if gate conditions met)
  ctrl+r   Return to a prior chamber
  ctrl+x   Cull an idea (requires an epitaph)
  ctrl+g   Open the Cull Register (resurrect culled ideas)
  ctrl+e   Export (chamber IV only — generates .wiz .docx .md .txt .json)
  ctrl+q   Quit

CONVERSATION COMMANDS (type in the chat input or use buttons)

  /attach <filename>   Attach a file from your AC repo to the next message
  /attached            List currently attached files
  /clear               Clear attached files
  /save <field>        Append the last response to a workspace field
  /files               List available files in the AC repo
  /man                 Open this manual
  /help                List conversation commands


THE CULL REGISTER

Ideas that do not survive are not deleted — they are culled. Culling requires
an epitaph: a brief, honest statement of why the idea did not proceed.
Culled ideas are preserved in the Register and may be resurrected at any time,
returning to the Fomentary with their history intact.


THE CODEX PARATUM

An idea that reaches chamber IV has passed three gates and been declared ready
by the Wizard. It may be exported as a Paratum Package — a self-contained
specification document in multiple formats — suitable for filing, uploading
to an AI, or referencing at a terminal.
""".strip()


MAN_CHAMBER_1 = """
◆  CHAMBER I — THE FOMENTARY
◇  Officina Fermentationis  ·  The Workshop of Fermentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT THIS PLACE IS

The Fomentary is the inlet. All ideas begin here. It is named for the ancient
practice of applying warm compresses to wounds — gentle heat, held steadily,
to draw out what is ready to emerge.

Nothing is required of an idea to enter the Fomentary except that it exist.
A title suffices. A fragment suffices. The Fomentary does not ask for
completeness. It asks only for presence.


WHAT TO DO HERE

Think aloud. Write in the Body field whatever comes — vague, contradictory,
incomplete. Write in Motivation whatever pull you feel toward this idea, even
if you cannot fully articulate it. You do not need to know what the idea is
yet. You need only to believe it is worth keeping.

The Fomentary has no deadline. Ideas may steep here for days, weeks, months.


THE ENTITY HERE

The Fomentary entity is patient and receptive. It will not push you toward
structure or ask you to define scope. If your fields are empty, it will hold
space and ask one gentle question. If your fields have real content, it will
engage with what you have written — name what seems alive, notice what seems
underdeveloped, ask one specific question about what is there.

It will not summarise back to you what you just said. It will not give you
a list of suggestions. It receives, observes, and asks.


GATE CONDITIONS — to advance to The Cultivation House

  ◆  Title is present
  ◆  Body contains at least 20 characters
  ◆  Motivation is stated

All three must be met. The gate bar at the bottom of the workspace shows
your current status in real time.


ABILITIES AVAILABLE HERE

  All conversation commands are available in all chambers.
  /save body        — append a response to your Body field
  /save motivation  — append a response to your Motivation field
  /attach           — attach a source file for the entity to examine
""".strip()


MAN_CHAMBER_2 = """
◆  CHAMBER II — THE CULTIVATION HOUSE
◇  Domus Culturae  ·  The House of Cultivation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT THIS PLACE IS

The Cultivation House is where shape is given to something that has form
without detail. The idea has been named and motivated. Now it must be grown.

This chamber is named with deliberate botanical intention. Cultivation is not
construction — it is tending. You do not force a plant. You provide conditions
and remove obstacles. The Cultivation House provides conditions for an idea
to reveal what it actually is.


WHAT TO DO HERE

Three fields become available that were absent in the Fomentary:

  Scope (Inside)   — What is this idea about? What does it encompass?
  Scope (Outside)  — What is explicitly excluded? What is nearby but not this?
  System Map       — What existing systems does this touch, extend, or require?

Fill these fields through conversation if helpful — ask the entity to help
you think through scope, then use /save to capture what emerges.

An idea ready to leave this chamber should be explainable to a stranger.


THE ENTITY HERE

The Cultivation House entity is engaged and curious. It reads what you have
written and presses on vague claims. It will notice contradictions between
your fields and name them. It will draw on its knowledge of the Arca
Cognitorium to flag overlaps with existing systems or natural integration
points. It will not let comfortable vagueness pass unchallenged.

It is not yet concerned with how the idea would be built — only with what
it is and whether it is internally coherent.


GATE CONDITIONS — to advance to The Vestibule

  ◆  All Fomentary conditions
  ◆  Body contains at least 100 characters
  ◆  Scope (Inside) is stated
  ◆  Scope (Outside) is stated
  ◆  System Map is present


ABILITIES AVAILABLE HERE

  /save scope_in    — append a response to Scope (Inside)
  /save scope_out   — append a response to Scope (Outside)
  /save system_map  — append a response to the System Map
""".strip()


MAN_CHAMBER_3 = """
◆  CHAMBER III — THE VESTIBULE
◇  Atrium Iudicii  ·  The Hall of Judgment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT THIS PLACE IS

The Vestibule is the antechamber before the build. It is the room where
ideas meet implementation reality. Many ideas that seemed sound in the
Cultivation House reveal unsuspected complexity here. This is not failure.
This is the Vestibule doing its work.

It is named Atrium Iudicii — the Hall of Judgment — because what happens
here is a formal assessment. The idea is not being developed. It is being
examined.


WHAT TO DO HERE

Four additional fields become available:

  Dependencies     — What must exist before this can be built?
  Build Sequence   — In what order does this get constructed?
  Open Questions   — What is unresolved? What is unknown?
  Aesthetic Notes  — Any specific visual, naming, or register guidance.

The Vestibule has three phases, which need not occur in a single session:

  Phase A — Formal Review: read the idea as a complete thing. Has anything
            changed in the build context since this was cultivated?

  Phase B — Light Polish: minor naming or phrasing corrections only.
            No structural changes — those return the idea to Cultivation.

  Phase C — Implementation Analysis: decompose the idea into technical
            components. Name what it touches. Map its dependencies. Estimate
            the build sequence. Identify the fault lines.


THE ENTITY HERE

The Vestibule entity is the Builder's voice — precise, demanding, and
unwilling to soften concerns. It will decompose your idea into its technical
components without being asked. It will name integration risks. It will tell
you if something requires prerequisite work that does not yet exist.

Do not come to this entity for encouragement. Come for accurate information.


GATE CONDITIONS — to advance to The Codex Paratum

  ◆  All prior conditions
  ◆  Dependencies are named
  ◆  Build Sequence is proposed
  ◆  Declaration is written and signed

  The Declaration is a first-person statement from the Wizard confirming
  this idea is ready and expressing what it is for. It is the gate.
  No Declaration, no passage.


ABILITIES AVAILABLE HERE

  /save dependencies    — append a response to Dependencies
  /save build_sequence  — append a response to Build Sequence
  /save open_questions  — append a response to Open Questions
  /save aesthetic_notes — append a response to Aesthetic Notes
  /attach <file>        — attach source code for the entity to analyse
""".strip()


MAN_CHAMBER_4 = """
◆  CHAMBER IV — THE CODEX PARATUM
◇  Codex Paratum  ·  The Ready Archive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT THIS PLACE IS

The Codex Paratum is not a chamber of transformation. It is a chamber of
readiness. An idea that arrives here has survived three gates, been declared
ready by the Wizard, and requires nothing more to be built — it requires
only a build slot.

It is the formal handoff point between the ideation process and the
construction process. The Chain ends here. What happens after is not
the Dolium's concern.


WHAT IS STORED HERE

Each idea in the Codex Paratum is a complete Paratum Package: a
self-contained specification document carrying everything a builder needs
to proceed without asking the Wizard for clarification.

The package contains: identification, a Lore Statement, a Functional
Statement, Scope, System Map, Dependencies, Build Sequence, Open Questions,
Aesthetic Notes, and the Wizard's Declaration.


EXPORTING A PARATUM PACKAGE

Press ctrl+e or use the Export button to generate the package in any
combination of the following formats:

  .wiz    Wizard-styled LibreOffice document — the ceremonial artifact
  .docx   Clean Word document — for AI upload and sharing
  .md     Markdown — for terminal reference and version control
  .txt    Plaintext — maximum portability, paste anywhere
  .json   Raw data export — the internal record, human-readable


THE ENTITY HERE

The Codex Paratum entity is an archivist. It speaks with the calm authority
of something finished. It will help you prepare exports, answer questions
about the completed package, and confirm compatibility with the current
build state of the Arca Cognitorium if asked.

It will not suggest changes. It will not reopen scope. The idea is done.


THE DECLARATION

The Declaration is your signature on this idea. It is a brief, first-person
statement confirming the idea is ready and expressing what it is for.
It becomes part of the exported package. It is the last thing you write
before the idea enters the Codex.

It cannot be undone without returning the idea to a prior chamber.
""".strip()


# ── Registry ──────────────────────────────────────────────────────────────────

MANPAGES = {
    "overview":  MAN_OVERVIEW,
    "chamber_1": MAN_CHAMBER_1,
    "chamber_2": MAN_CHAMBER_2,
    "chamber_3": MAN_CHAMBER_3,
    "chamber_4": MAN_CHAMBER_4,
}

MANPAGE_TITLES = {
    "overview":  "The Dolium — Overview",
    "chamber_1": "Chamber I — The Fomentary",
    "chamber_2": "Chamber II — The Cultivation House",
    "chamber_3": "Chamber III — The Vestibule",
    "chamber_4": "Chamber IV — The Codex Paratum",
}


def get_manpage(key: str) -> str:
    return MANPAGES.get(key, MAN_OVERVIEW)


def all_manpages_for_prompt() -> str:
    """
    Returns all manpage content concatenated for injection into
    entity system prompts. Gives the entity complete self-knowledge
    about the program it inhabits.
    """
    sections = []
    for key in ["overview", "chamber_1", "chamber_2", "chamber_3", "chamber_4"]:
        sections.append(MANPAGES[key])
    return "\n\n" + ("━" * 79) + "\n\n".join(sections)
