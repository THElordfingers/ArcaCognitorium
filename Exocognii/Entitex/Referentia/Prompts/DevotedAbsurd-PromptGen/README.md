# Devoted Absurd — Character Prompt Generator

A PyQt6 desktop app that generates nuanced image-generation prompts for 2D stylized characters, with Claude running silently in the background to refine, score, and learn from every generation.

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Run
python main.py
```

---

## Architecture

```
main.py          — PyQt6 UI, all windows and panels
data_pools.py    — Character archetypes, trait pools, prompt assembly, weighted generation
claude_worker.py — Background Claude API calls (threaded, non-blocking)
learning.py      — JSON history, scoring, weight nudging, stats
```

History and learning data is saved to:
```
~/.devoted_absurd/history.json
```

---

## Character Archetypes

| Key               | Description                          |
|-------------------|--------------------------------------|
| bureaucrat        | Officials, inspectors, clerks        |
| street            | Civilians, regulars, eccentrics      |
| criminal          | Underworld, fixers, fences           |
| military          | Veterans, contractors, ex-soldiers   |
| scifi             | Dystopian roles, corporate zones     |
| retro_futurist    | Alternate history, analogue-punk     |
| fantasy_grounded  | No magic glows — gritty civic roles  |

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
Each archetype needs: `label`, `palette_hint`, `style_flex`, `roles`, `personalities`, `garments`, `props`, `details`.

The style DNA in `assemble_prompt()` is always appended — it cannot be overridden per archetype, only the palette and flex hints vary.
