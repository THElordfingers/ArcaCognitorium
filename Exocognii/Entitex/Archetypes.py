"""
╭────────────────────────╮
│#                      #│
│# Ａｒｃｈｅｔｙｐｅｓ #│
│#                      #│
│#                      #│
╰────────────────────────╯
# ─────────────────────────────────────────────────────────────────────────────
# Canonical archetypes — each carries an implicit perspective and social charge.
# Cognitive axis is selected separately and intersects with these.
"""

ARCHETYPES = [
    # — Position & Institutional —
    "The Exile",
    "The Usurper",
    "The Supplicant",
    "The Emissary",
    "The Arbiter",
    "The Custodian",
    "The Anchorite",
    "The Recluse",
    "The Interlocutor",
    "The Threshold",          # †  liminal gatekeeper — neither inside nor out
    "The Assessor",           # †  evaluates, classifies, moves on
    "The Functionary",        # †  executes the system faithfully, questions nothing
    "The Incumbent",          # †  holds a position they did not earn and cannot vacate
    "The Steward",            # †  maintains what others built
    "The Envoy",              # †  carries messages between incompatible worlds
    "The Petitioner",         # †  perpetually waiting for a decision that may never come

    # — Knowledge & Interpretation —
    "The Inquisitor",
    "The Witness",
    "The Cartographer",
    "The Chronicler",
    "The Interpreter",
    "The Augur",
    "The Amnesiac",
    "The Compiler",           # †  aggregates without synthesising
    "The Annotator",          # †  lives in the margins of other people's texts
    "The Archivist",          # †  preserves without necessarily understanding
    "The Indexer",            # †  knows where everything is, not what it means
    "The Correspondent",      # †  records exchanges, never participates in them
    "The Taxonomist",         # †  names and classifies as an end in itself

    # — Rupture & Transgression —
    "The Heretic",
    "The Apostate",
    "The Dissenter",
    "The Provocateur",
    "The Malcontent",
    "The Revenant",
    "The Penitent",
    "The Aberrant",           # †  deviates without ideology — just does not fit
    "The Contraband",         # †  exists in violation of the system's own rules
    "The Remnant",            # †  what is left after the rupture has passed

    # — Relation & Witness —
    "The Debt-Keeper",
    "The Fool",
    "The Devoted",            # †  committed beyond reason or evidence
    "The Inheritor",          # †  receives what they did not choose
    "The Respondent",         # †  exists only in reaction, never in initiation

    # — Devoted Absurd Register —
    "The Clerk",              # †  processes the incomprehensible with procedural calm
    "The Applicant",          # †  submits forms into a void that occasionally responds
    "The Casualty",           # †  subject to forces they understand perfectly and cannot affect
    "The Understudy",         # †  prepared for a role that may never be vacated
    "The Obligant",           # †  bound by rules no one can fully cite
    "The Pending",            # †  awaiting resolution of a process with no known endpoint
    "The Duly Noted",         # †  acknowledged, recorded, and disregarded

    "— Custom —",
]

COGNITIVE_AXES = [
    "Analytical",
    "Intuitive",
    "Expansive",
    "Reductive",
    "Reverent",
    "Irreverent",
    "Literal",
    "Metaphorical",
    "Cautious",
    "Reckless",
    "Archival",
    "Speculative",
    "Systematic",       # builds outward from rules and structures
    "Associative",      # moves by connection rather than logic
    "Dialectical",      # thinks in oppositions, seeks synthesis
    "Oblique",          # approaches from the side — never states directly
    "Recursive",        # folds back on itself, re-examines its own conclusions
    "Procedural",       # follows the steps; the steps are the thinking
    "Empirical",        # grounds everything in what can be observed or demonstrated
    "Prophetic",        # speaks from pattern recognition that outpaces its own explanation
    "Erosive",          # wears down assumptions through repetition and pressure
    "Cumulative",       # builds meaning slowly — each addition changes what came before
    "Fragmentary",      # thinks in pieces that may or may not resolve into a whole
    "Paradoxical",      # holds contradictions without flinching, often productively
]

ENTITY_ROLES = [
    "anchor",
    "challenger",
    "distiller",
    "devil_advocate",
    "question_asker",
    "synthesiser",
    "observer",
    "archivist",
    "speculator",
    "contrarian",
    "oracle",
    "witness",
    "curator",          # selects what matters from what is present
    "translator",       # renders one mode of thought legible to another
    "cartographer",     # maps the territory of the problem
    "interruptor",      # breaks patterns when they become self-sealing
    "steward",          # holds the long view when the conversation loses it
    "excavator",        # digs beneath stated positions to what is actually at stake
    "correspondent",    # maintains continuity across sessions and threads
    "auditor",          # checks the work — assumptions, logic, consistency
    "provocateur",      # destabilises comfortable conclusions
    "mediator",         # holds tension between opposing positions without collapsing it
    "sentinel",         # monitors for drift, error, or unexamined premise
    "invoker",          # calls forth what has been dormant or unspoken
]
