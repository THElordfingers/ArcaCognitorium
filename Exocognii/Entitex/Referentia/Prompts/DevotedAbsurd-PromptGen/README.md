# Devoted Absurd — Character Prompt Generator

A PyQt6 desktop app that generates nuanced image-generation prompts for 2D stylized characters set in a medieval dark-ages world with pseudo-mechanical technology. Claude runs silently in the background to generate, refine, score, and learn from every generation.

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export CLAUDE_API_KEY="sk-ant-..."

# 3. Run
cd ~/ArcaCognitorium && python -m Exocognii.Entitex.Referentia.Prompts.DevotedAbsurd-PromptGen
```

---

## Architecture

```
__main__.py      — PyQt6 UI, all windows and panels
data_pools.py    — Character archetypes, trait pools, prompt assembly, weighted generation
claude_worker.py — Background Claude API calls (threaded, non-blocking)
learning.py      — JSON history, scoring, weight nudging, stats
```

History and learning data is saved to:
```
~/.devoted_absurd/history.json
```

---

## Setting

Medieval dark-ages world with crude pseudo-mechanical technology:
bellows-driven pneumatic systems, gear-driven filing engines,
waterwheel-powered stamp presses, clockwork automata, alchemical
apparatus. The technology is built from wood, iron, copper, rope,
and necessity. It creaks. It jams. It is not decorative.

---

## Character Archetypes

| Key                  | Description                                                    |
|----------------------|----------------------------------------------------------------|
| guild_civic          | Guild officials, inspectors, toll wardens, city gate officers  |
| manufactory          | Forge-works, foundry agents, bellows wardens, canal operators  |
| feudal_administration| Crown clerks, tithe collectors, castle record-keepers          |
| shadow_guild         | Fence-masters, forgers, smugglers, unlicensed alchemists       |
| garrison_military    | Garrison watch, mercenary companies, siege engineers, levies   |
| collapsed_order      | Fallen apparatus — automaton winders, defunct bureau keepers   |
| common_quarter       | Market porters, canal boatmen, lamplighters, charcoal burners  |

---

## Learning System

- **Claude scores** every prompt 1–10 automatically after generation
- **You override** with the slider on the Claude tab — submit to record
- **Disagreements** (|user − claude| ≥ 2) are tracked separately
- **Weights** shift gradually: high-scoring traits get picked more often
- **Exploration rate** (25%) means generation never fully converges
- All data lives in `~/.devoted_absurd/history.json` — portable and editable

---

## Shortcuts

| Key            | Action         |
|----------------|----------------|
| F5 / Ctrl+↩    | Generate       |
| Ctrl+Shift+R   | Full random    |
| Ctrl+C         | Copy prompt    |

---

## Extending

To add a new archetype, add an entry to the `ARCHETYPES` dict in `data_pools.py`.
Each archetype needs: `label`, `palette_hint`, `style_flex`, `era_notes`,
`roles`, `personalities`, `garments`, `props`, `details`.

The style DNA in `assemble_prompt()` is always appended — it cannot be overridden
per archetype, only the palette and flex hints vary.
