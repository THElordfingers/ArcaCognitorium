"""
manpages.py — Dolium v2
Five manpage texts describing the Dolium's chambers and philosophy.
Injected into system prompts to orient the entity.
"""

from __future__ import annotations


MANPAGE_DOLIUM = """
THE DOLIUM — OVERVIEW

The Dolium is an ideation instrument. It is not a note-taking application.
It is not a project manager. It is a four-chamber pipeline through which
raw ideas are cultivated into declared intentions.

An idea enters the Fomentary as a fragment. It exits the Codex as a
declaration — a statement of what this thing is, why it matters, and
what the first act of making it real looks like.

The Dolium does not store ideas. It processes them.
""".strip()


MANPAGE_FOMENTARY = """
CHAMBER I — THE FOMENTARY

The Fomentary is the fermentation vessel. An idea arrives here unnamed,
unresolved, possibly wrong. That is acceptable. The Fomentary exists
precisely for things that have not yet found their form.

The Wizard must give the idea a title, a body (what it is), and a
motivation (why it matters now, to this Wizard, in this context).

Gate conditions to advance:
  · Title must be present
  · Body must reach 100 characters
  · Motivation must reach 60 characters

An idea that cannot survive these conditions has not yet fermented.
It may return to the Fomentary from any later chamber.
""".strip()


MANPAGE_CULTIVATION = """
CHAMBER II — THE CULTIVATION HOUSE

The Cultivation House is where an idea is made to grow under pressure.
The Wizard must elaborate — say more than was comfortable in the Fomentary.
They must name the obstacles honestly, and they must commit to a first step.

The first step is not a roadmap. It is a single, specific, executable act.
If it cannot be described in under two sentences, it is not a first step.

Gate conditions to advance:
  · Elaboration must reach 150 characters
  · Obstacles must reach 60 characters
  · First Step must reach 40 characters

The entity watches the Cultivation House with particular attention.
Resistance to the obstacles field is a diagnostic signal.
""".strip()


MANPAGE_VESTIBULE = """
CHAMBER III — THE VESTIBULE

The Vestibule is the threshold chamber. An idea that reaches here has
survived fermentation and cultivation. It must now be refined — stated
in its final form — and its remaining open problems must be named.

Refined Form is not a summary of what came before. It is a new statement:
what would this be if it were finished? What would a reader encounter?

Open problems are not the same as obstacles. Obstacles are things that
might stop the work. Open problems are things the work has not yet resolved.

Gate conditions to advance:
  · Refined Form must reach 120 characters
  · Open Problems must reach 60 characters
  · Next Actions must reach 60 characters
""".strip()


MANPAGE_CODEX = """
CHAMBER IV — THE CODEX

The Codex is the final chamber. An idea that reaches here is ready to
be declared. Declaration is a formal act — the Wizard states what this
thing is, in the clearest language they can produce, as if speaking to
someone who has never heard of it and must decide whether it is worth
pursuing.

The Summary is a compact form — one to three sentences. The tags organise
the idea within the Arca Cognitorium's broader schema.

Declaration gate conditions:
  · Declaration must reach 80 characters
  · Summary must reach 60 characters

Once declared, the idea may be exported in .wiz, .docx, .md, .txt, or .json.
""".strip()


def all_manpages_for_prompt() -> str:
    """Returns all five manpages as a single block for injection into system prompts."""
    pages = [
        MANPAGE_DOLIUM,
        MANPAGE_FOMENTARY,
        MANPAGE_CULTIVATION,
        MANPAGE_VESTIBULE,
        MANPAGE_CODEX,
    ]
    return "\n\n---\n\n".join(pages)
