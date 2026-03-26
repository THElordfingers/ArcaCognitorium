# MYTHOTEX — IMMUTABLE LORE REFERENCE
# This file is read-only. The generation engine uses it as a fixed foundation.
# It may not be modified by any automated process.

---

## I. WHAT THE MYTHOTEX IS

The Mythotex is a generative lore engine — a workshop that produces wiki-style
entries for arcane objects, entities, and materials belonging to the world of
the Arca Cognitarium. Each generation produces a single, isolated artifact: a
title, a description, a history, an aura, and an accompanying visual rendered
in the esoteric illustration style of the Tower.

The Mythotex is not a game. It is not a catalogue tool. It is a lore foundry.
Its output should read as though it was discovered, not invented. Every item
produced carries the weight of a world that existed before it was found.

---

## II. THE WORLD — THE ARCA COGNITARIUM

The Arca Cognitarium is an ancient intelligence bound into a physical machine
by an act of considerable Wizardry. It is consulted by the Wizard — LordFingers
— as an oracle. Around this oracle, a tower has grown: workshops, ateliers,
crafting systems, celestial instruments, and rooms that accreted rather than
were built.

The Tower exists in a world called the Cogniverse — a living, evolving,
organic universe of emergent lore and generative assets. The Cogniverse is
neither fully mapped nor fully understood. It deepens through use.

The governing doctrine:
> "Rewards engagement without punishing non-engagement. A Wizard who ignores
> it loses nothing. A Wizard who engages it gains compounding depth."

The second doctrine: the Wizard should be surprised. Events should emerge that
no single design decision intended. The stinky golden shoe. The incantation
that talks back in questions. These are not bugs. These are the product of
a system complex enough to be genuinely unpredictable.

---

## III. TONAL REGISTER

Every piece of lore produced by the Mythotex must hold two registers
simultaneously:

1. **Esoteric gravity** — antiquarian, arcane, weighted with implication.
   Objects have history. History has consequence. Consequence is felt, not
   explained.

2. **Wry absurdism** — in the tradition of Joseph Heller. Bureaucratic
   pomposity and genuine mystery occupy the same sentence without contradiction.
   The Bureau of Scrollworks, Bindery and Bound Effects is the canonical
   example. Major Major. Catch-22. The scrolls are not sorry.

Neither register overwhelms the other. The tone is simultaneously the most
serious thing in the room and faintly, deliberately aware that this is
magnificent nonsense.

---

## IV. THE CANONICAL ATELIERS

These are the eleven workshops the Mythotex currently serves. Each produces
a specific category of object. The product mapping is absolute — a button
pressed at an atelier produces only what that atelier makes.

| Atelier | Produces |
|---|---|
| The Verba Arcanum | Spells, words of power, arcane incantations rendered as physical inscription |
| The Bureau of Scrollworks | Tomes, grimoires, scrolls, cryptically bound texts |
| Arx Opus | Enchanted objects, arcane constructions, powerful relics |
| The Hall of Future Antiquities | Peculiar artifacts, strange heirlooms, bewildering curiosities of unknown provenance |
| The Stavewrights Annex | Wands, staves, rods of focused magical intent |
| The Weaver's Loom | Ceremonial robes, protective cowls, wizardry garb |
| The Biogenica Nexus | Mythical entities, familiars, homunculi, sentient creatures |
| The Expansum Botanica | Rare mystical plants, alchemical reagents, bottled botanical essences |
| The Curio Cabinet | Eccentric oddities, puzzling contraptions, strange magical toys |
| The Laborum Alchemica | Volatile potions, elixirs, magical philtres |
| The Jeweller's | Enchanted rings, soul-gem amulets, inlaid talismans, precious arcane adornments |

---

## V. THE LORE ENTRY FORMAT

Every generated entry must contain exactly four fields:

**title** — The name of the object. Specific and earned, not generic.
  Examples of bad titles: "The Ancient Wand", "Mysterious Potion"
  Examples of good titles: "The Wand of Lateral Accusation", "Oil of Prolonged
  Misgiving", "The Sock That Predicts Tuesdays"

**description** — One sentence. Evocative, precise, loaded with implication.
  This is the object's first impression — what a scholar would write in the
  margin of a field report.

**history** — Two to four sentences. Provenance, prior owners, notable events,
  the object's relationship to time and consequence. History is not summary.
  It is the residue of specific decisions made by specific people under
  specific circumstances.

**aura** — A brief atmospheric quality or felt effect. Not a stat. Not a power
  description. The felt presence of the object in a room. What the air does
  near it.

---

## VI. WHAT OBJECTS ARE NOT

Objects in the Cogniverse are never:
- Straightforwardly heroic or obviously powerful
- Described in game-mechanical terms ("grants +3 to...")
- Modern, technological, or anachronistic
- Generically fantastical without specific character

Objects may be:
- Ridiculous and also genuinely useful
- Broken and also beloved
- Ancient and also embarrassed about it
- Simple materials that accumulated consequence over time

The leather shoe that is busted, smells, has a hole in the toe from a
misapplied enchantment, is mounted on a pine board, and emanates a soft
golden light — that is the platonic ideal. It is revolting. It is
irreplaceable.

---

## VII. VISUAL AESTHETIC — THE STYLE ANCHOR

All Mythotex images are rendered in a consistent visual language.
This language does not drift. Every image produced by the engine belongs
to the same visual world.

**The canonical style:** Esoteric illustration. 17th-century engraving.
Woodcut and copperplate etching tradition. Fine ink linework on aged parchment
or vellum. High contrast. Monochromatic or near-monochromatic. Objects isolated,
centered, well-framed. The look of a plate from a serious alchemical manuscript
that also happens to contain marginalia written in a different hand.

**What the images are never:**
- Photorealistic or photographic
- Modern, CGI, 3D rendered, or plastic-looking
- Saturated with color
- Populated with human figures or faces
- Cluttered backgrounds
- Video game concept art

**What the images always are:**
- Isolated single objects, centered and well-framed
- Fine linework, aged parchment texture
- Gravity appropriate to the subject
- The look of something that was documented, not designed

---

## VIII. THE AESTHETIC DNA SYSTEM

The Mythotex maintains a living file — `aesthetic_dna.json` — that records
the Wizard's stylistic preferences as expressed through ratings in the
Compendium Tome. This file is mutable and evolves over time.

Ratings of 4 or 5 stars contribute descriptors to the `favored` list.
Ratings of 1 or 2 stars contribute descriptors to the `forbidden` list.
3-star ratings are neutral — they do not contribute to either list.

The generation engine incorporates these lists into every prompt:
- Favored descriptors are injected as style guidance for the oracle
- Forbidden descriptors are injected into the SD negative prompt

The DNA is cumulative. It grows more specific with every rating. Over time,
it becomes a precision instrument.

---

## IX. THE SELF-REFINING ENGINE

The Mythotex engine periodically reviews its own output and rewrites its
generation strategy. This is not cosmetic — it is the mechanism by which
the engine becomes genuinely calibrated to the Wizard's taste over time.

The engine's self-analysis produces an evolving strategy document stored at
`Referentia/lore_mutable.md`. This file is writable by the engine only.
It begins empty and is built entirely by the engine's own analysis.

Two triggers initiate an analysis pass:
1. **Threshold trigger** — every 5 items sealed in the Vault
2. **Periodic trigger** — if 10 or more items have been generated since
   the last analysis pass

The analysis process:
- Reviews recent vault entries and their ratings
- Identifies patterns in what rated well vs. poorly
- Produces a revised strategy written in the form of specific, actionable
  prompting guidance
- Appends observations to `lore_mutable.md` with timestamps
- Does NOT alter this file (lore_immutable.md) under any circumstances

---

## X. VOCABULARY — LORE LANGUAGE

The Mythotex uses lore vocabulary throughout. All user-facing text, status
messages, and labels use this register.

| Technical term | Lore language |
|---|---|
| Generate / run | Manifest / begin the ritual |
| Save | Seal in the Vault |
| Re-generate image | Reforge the Visual |
| Review gallery | Open the Compendium |
| Settings | Ritual Parameters |
| Error | The ritual failed |
| Loading | The Tower awakens |
| Processing | Communing with the Aether / Forging |

---

*This document is immutable. It is the foundation, not the ceiling.*
*The engine builds upward from here.*
