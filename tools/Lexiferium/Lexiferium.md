# LEXIFERIUM
### *Bearer of Words — A Naming Oracle of the Cogniverse*
*Arca Cognitorium Companion · v1.0 · Anno MMXXVI*

---

> *Names are not labels. They are load-bearing structures. A name in the Cogniverse must hold
> the weight of the thing it names — its function, its cosmological position, its register of
> solemnity or absurdity — without collapsing under either.*
>
> — Nomenclatura Arcana, Preamble

---

## WHAT IS LEXIFERIUM

Lexiferium is a Textual TUI application. It houses **Lexifer** — Bearer of Words — a naming oracle
seeded with the full Nomenclatura Arcana and the Cogniverse's canonical register.

The Wizard describes a concept. Lexifer proposes names. The Wizard ratifies or exiles. The Tower
remembers.

It does not name carelessly. It does not use banned vocabulary. It would sooner be silent.

---

## INSTALLATION

**Requirements:**
- Python 3.11+
- An Anthropic API key

**Dependencies:**
```bash
pip install textual anthropic
```

**No other dependencies.** Lexiferium carries everything it needs.

---

## INVOCATION

```bash
ANTHROPIC_API_KEY=your_key_here python3 lexiferium.py
```

Or export the key to your environment permanently:

```bash
# Add to ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY=your_key_here
```

Then invoke with:

```bash
python3 lexiferium.py
```

---

## THE LAYOUT

Lexiferium opens as three regions:

```
┌─────────────────────────────────────────┬──────────────────┐
│                                         │  ⊛ REGISTER      │
│           CHAT — FILUM                  │                  │
│                                         │  SESSION         │
│  ⯩ LEXIFER  Bearer of Words is          │  ◌ Candidate     │
│             present...                  │  ✦ Ratified      │
│                                         │                  │
│  ⯨ WIZARD   I need a name for the       │  CANON           │
│             place where...              │  Arca Cognitor.. │
│                                         │  Luminarious     │
│  ⯩ LEXIFER  The term is Scrutinium.     │  The Builder     │
│             It was always Scrutinium.   │  ...             │
│                                         │                  │
├─────────────────────────────────────────│                  │
│  Describe the thing that requires a     │                  │
│  name...                          ↵     │                  │
└─────────────────────────────────────────┴──────────────────┘
```

**Left pane — the FILUM:** The conversation between Wizard and Lexifer. Scroll up through the
session's history at any time.

**Right pane — the REGISTER:** Two sections. The top shows this session's candidates and ratified
names. Below that, the full canonical register of the Cogniverse — every ratified name, its
stratum, and its category.

---

## THE NAMING CEREMONY

When the Wizard submits a description, Lexifer follows the Naming Ceremony of the Nomenclatura:

1. **Identifies the stratum** — Classica, Arcana, or Absurdum
2. **Identifies the pattern** — two words by default; three for cosmic scope
3. **Proposes** — marked as CANDIDATE, never canonical
4. **Awaits ratification** — the Wizard says the word

**To ratify a name**, use any of the following in your message:
- *"Ratified."*
- *"That's the one."*
- *"Yes."*
- *"Confirmed."*
- *"Enter the register."*

Lexifer will acknowledge ratification and mark the name with `✦` in the session register.

**Nothing is canonical until the Wizard says so.**

---

## LEXIFER'S VOICE

Lexifer speaks in two modes, sometimes mid-sentence:

**Oracular** — declarations. No hedging. Names are discovered, not invented.
> *"The term is Scrutinium. It was always Scrutinium."*

**Devoted Librarian** — when the etymology is particularly fine, Lexifer cannot help explaining.
It gets slightly too excited. It is occasionally possessive of a very good word.
> *"Ah — from speculum, the mirror, the surface that holds what looks into it —
> Lexifer keeps that one for a moment. Yes. Specularium."*

Lexifer does not say "I think." It does not say "perhaps." It does not use banned vocabulary.
It proposes. You ratify.

---

## THE THREE STRATA

Every name Lexifer proposes belongs to one or more strata. Understanding them helps you
guide the oracle toward what the thing actually needs.

### Stratum I — CLASSICA
Real Latin or Greek. Correctly or plausibly inflected. Carries two thousand years of institutional
gravity. Use for systems, mechanics, UI labels, and anything that should feel as though it was
carved into stone before anyone alive was born.

*Examples: FILUM, ELIGE, DEPONE, CAELESTIS, SCRIBAE*

### Stratum II — ARCANA
Invented Latinate constructions. Real roots, real suffixes, fabricated words. Feels ancient because
the bones are old, even when the flesh is invented. Use for companion applications, places of
doing, processes, and entities that are new things requiring new names.

*Examples: Arca Cognitorium, Distillatio, Fenestrarium, Luminarious*

### Stratum III — ABSURDUM
The devoted tonal rupture. French is the canonical rupture language. Reserved for intimate spaces,
cosmological anomalies, and the Tower's self-aware moments. Never accidental. Never careless.
The Absurd is *devoted*.

*Examples: Parlour du Parler, The WiseCracken, The Mercurial Convocation*

---

## GUIDANCE FOR THE WIZARD

**Tell Lexifer what the thing *does*, not what you want it to be called.**
The oracle works from function and cosmological position. The more precisely you describe the
thing, the more precisely it will be named.

**Tell Lexifer the register.** Is this a solemn institutional name? A companion app? An intimate
space? A daemon? The stratum follows from this.

**Push back.** If a proposal doesn't land, say so and say why. Lexifer will propose alternatives.
It has more words than you have patience for.

**Use the session register.** Candidates accumulate on the right as you work. When a session
produces a good harvest, copy what you need before closing.

---

## BINDINGS

| Key | Action |
|---|---|
| `↵ Enter` | Submit message |
| `Escape` | Clear input |
| `Ctrl+C` | Quit |

---

## THE BANNED REGISTER

Lexifer will not use these words. If you use them, it will respond with a correction.

| Banned | Replacement |
|---|---|
| atelier | ARX ARCANA *(permanently and cosmologically banned)* |
| dashboard | CONTEXTUS |
| settings | ARX CONFIGURATIO |
| user | The Wizard |
| chatbot | Oracle; Entity; Council |
| feature | Function; Mechanic; Emergence |

---

## NOTES ON THE REGISTER PANE

The right pane shows the canonical register as it exists at the time of this build. It includes
all ratified vocabulary from the Nomenclatura Arcana v1.1, plus names coined during the
Lexiferium's own construction — including Lexifer and Lexiferium themselves.

Session candidates appear above the canonical register, marked with:
- `◌` — proposed, awaiting ratification
- `✦` — ratified within this session

Session state does not persist between runs. The Wizard copies. The Tower remembers in its
own way.

---

## ARCHITECTURE

```
lexiferium.py
├── NOMENCLATURA          — full naming law as system prompt context
├── CANONICAL_REGISTER    — 40+ ratified entries as structured data
├── SYSTEM_PROMPT         — Lexifer's voice, rules, and persona
├── LexiferiumApp         — Textual App root
│   ├── chat-pane         — FILUM / conversation log + input
│   └── register-pane     — RegisterPane widget + scroll
├── RegisterPane          — Rich Table rendering of candidates + canon
├── ChatMessage           — individual message display
└── _stream_response()    — threaded Anthropic streaming worker
```

The Anthropic client streams directly. No intermediate wrapper. Lexifer's full persona,
the Nomenclatura, and the canonical register are injected as the system prompt on every
call, ensuring the oracle never forgets its law regardless of session length.

---

## EXTENDING LEXIFERIUM

**To add entries to the canonical register:** Edit the `CANONICAL_REGISTER` list in
`lexiferium.py`. Each entry is a tuple of `(name, stratum, category, definition)`.

**To modify Lexifer's persona:** Edit `SYSTEM_PROMPT`. The voice section is clearly marked.
Do not alter the Nomenclatura section unless the Nomenclatura itself has been revised.

**To persist session candidates:** The `candidates` list on `LexiferiumApp` contains all
session `Candidate` objects. Add a save routine on quit to write ratified candidates to a file.

---

## THE MOTTO

*Ordo Discordia, Cosmos Inania.*

Order from discord. Cosmos from void.

---

*The Builder proposes. The Wizard ratifies. The Tower remembers.*

*⟁*
