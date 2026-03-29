# INCITAMENTUM PROMPT BUILDER v2.0
## Build Document — Arca Cognitorium Companion Tool

| Field | Value |
|---|---|
| App | INCITAMENTUM PROMPT BUILDER |
| Version | 2.0 |
| Document Class | Build Specification |
| Status | Ready for Construction |

---

## Table of Contents

1. [Overview & Architecture](#1-overview--architecture)
2. [Tech Stack](#2-tech-stack)
3. [Directory Tree](#3-directory-tree)
4. [Module Breakdown](#4-module-breakdown)
5. [ASCII UI / Interaction Wireframe](#5-ascii-ui--interaction-wireframe)
6. [Data Flow](#6-data-flow)
7. [Code Stubs](#7-code-stubs)
8. [Error Handling](#8-error-handling)
9. [Setup & Testing](#9-setup--testing)
10. [Extensibility](#10-extensibility)

---

## 1. Overview & Architecture

INCITAMENTUM v2.0 replaces the static template interpolation of v1.x with a live AI-conducted interview. The Wizard launches the tool, selects a session type, and is interviewed by a ClaudeBox-powered AI Interviewer that streams its questions and synthesis in real time. The conversation concludes with a fully assembled Builder session prompt, which the Wizard can copy or save.

The architecture is a three-stage linear pipeline with a persistent state layer underneath.

| Stage | Name | Responsibility |
|---|---|---|
| 1 | Boot & Config | Load `~/.arca/config.json`, display header, present session type menu |
| 2 | Interview Loop | Multi-turn streaming conversation with the AI Interviewer via ClaudeBox `box.stream()` |
| 3 | Prompt Assembly & Output | AI synthesises the final prompt; Wizard chooses file / clipboard / stdout exits |

---

## 2. Tech Stack

| Tool | Version | Justification |
|---|---|---|
| Python | 3.10+ | Runtime — no negotiation |
| ClaudeBox | local canonical | All AI calls — `from claudebox import ClaudeBox`; env `CLAUDE_API_KEY` |
| `claude-sonnet-4-5` | latest | Interviewer model — balance of speed and quality for interactive streaming |
| `json` | stdlib | Config and history persistence |
| `subprocess` | stdlib | xclip clipboard integration |
| `os`, `sys`, `pathlib` | stdlib | Config paths, exit handling |
| `textwrap` | stdlib | Terminal-width-aware output wrapping |
| `shutil` | stdlib | Terminal width detection |

No external dependencies beyond ClaudeBox and its own requirements.

---

## 3. Directory Tree

```
prompt_builder/
├── prompt_builder.py          — entry point, main() loop
├── interviewer.py             — AI interview engine, ClaudeBox session management
├── config.py                  — config load/save, history read/write
├── renderer.py                — all terminal output, ANSI palette, header, streaming display
├── session_types.py           — session type definitions and system prompt fragments
├── output.py                  — final prompt display, file write, clipboard
└── prompt_builder_DOC.md      — application doc (post-build)

~/.arca/
├── config.json                — repo URL, model preference, display settings
└── history.json               — last N completed prompts with metadata
```

---

## 4. Module Breakdown

| Module | Responsibility | Inputs | Outputs | Dependencies |
|---|---|---|---|---|
| `prompt_builder.py` | Entry point, top-level loop, menu dispatch | argv, stdin | side effects | all modules |
| `interviewer.py` | ClaudeBox session lifecycle, multi-turn stream loop, final prompt extraction | session_type, config, user stdin | assembled prompt string | ClaudeBox, session_types, renderer |
| `config.py` | Load/save config.json and history.json; provide defaults | filesystem | config dict, history list | json, pathlib |
| `renderer.py` | All styled terminal output — header, prompts, streaming tokens, separators | strings, token generator | stdout | shutil, textwrap |
| `session_types.py` | Session type registry — labels, descriptions, system prompt fragments | — | dict of session type definitions | — |
| `output.py` | Final prompt display, file write, xclip copy | prompt string | files, clipboard, stdout | subprocess, pathlib |

---

## 5. ASCII UI / Interaction Wireframe

```
┌──────────────────────────────────────────────────────────────────────┐
│         INCITAMENTUM PROMPT BUILDER  ·  Arca Cognitorium v2.0       │
│         Repo: https://raw.githubusercontent.com/...                  │
└──────────────────────────────────────────────────────────────────────┘

  Select a session type:

    1.  ::INIT        Session open with live files
    2.  ::THEORY      Architectural — design and conceptualization
    3.  ::LORE        Narrative — cosmology, naming, world-building
    4.  ::AUDIT       Assessment — read-only review
    5.  ::BUILD       Implementation — active construction
    6.  ::REVIEW      Validation at a build seam
    7.  Configure     Repository / preferences
    8.  History       Browse recent prompts

  ▸ Select:  _

──────────────────────────────────────────────────────────────────────

  [After selection — Interview begins]

  ┌─ THE INTERVIEWER ────────────────────────────────────────────────┐
  │                                                                  │
  │  You've opened a ::BUILD session. Before I can construct your   │
  │  prompt, I need to understand the scope. What component or      │
  │  system are you building today?                                  │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

  ▸ You:  _

  [Wizard types. Streamed AI response follows. Loop continues until
   the Interviewer signals readiness to assemble.]

──────────────────────────────────────────────────────────────────────

  ┌─ ASSEMBLED PROMPT ───────────────────────────────────────────────┐
  │                                                                  │
  │  ::BUILD                                                         │
  │                                                                  │
  │  Repository: https://raw.githubusercontent.com/...              │
  │  Files in scope: ui/layout.py, ui/components/rune_column.py     │
  │                                                                  │
  │  Focus: Implement the RuneColumn widget as a composable         │
  │  Textual component. Single-purpose. No layout assumptions.      │
  │                                                                  │
  │  Constraints: Must not touch existing LayoutManager. ...        │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

  [c] Copy to clipboard    [s] Save to file    [Enter] Done

──────────────────────────────────────────────────────────────────────
```

**Legend:**

| Element | Meaning |
|---|---|
| `┌─ THE INTERVIEWER ─┐` | Boxed AI response panel |
| `▸ You:` | Wizard input prompt |
| `┌─ ASSEMBLED PROMPT ─┐` | Final output panel |
| `[c] [s] [Enter]` | Exit action keys |
| Streaming tokens | AI response printed character by character via `box.stream()` |

---

## 6. Data Flow

### Path A — Happy Path (complete interview → assembled prompt)

```
main()
  └─ load_config()                        # ~/.arca/config.json
  └─ display_menu()                       # session type selection
  └─ Interviewer.run(session_type)
       └─ build_system_prompt(type)       # from session_types.py
       └─ box = ClaudeBox(system=...)     # one box per interview session
       └─ loop:
            ├─ box.stream(user_input)     # sync generator
            ├─ renderer.stream_tokens()   # print tokens as they arrive
            ├─ accumulate full_response   # join token stream
            ├─ check for PROMPT_READY     # sentinel in AI response
            └─ if not ready: continue
       └─ extract_prompt(full_response)   # strip boilerplate, return prompt block
  └─ output.display_prompt(prompt)        # boxed display
  └─ output.handle_exits(prompt)          # [c] / [s] / Enter
  └─ save_to_history(prompt, session_type)  # ~/.arca/history.json
```

### Path B — User abandons mid-interview (Ctrl+C)

```
KeyboardInterrupt caught in Interviewer.run()
  └─ renderer.print_cancelled()
  └─ offer: [s] Save partial transcript  /  [Enter] Discard
  └─ if save: write partial to history with status="abandoned"
  └─ clean exit — no crash, no traceback
```

### Path C — ClaudeBox / API failure

```
box.stream() raises exception
  └─ caught in Interviewer._stream_turn()
  └─ renderer.print_error(e)              # "The Interviewer fell silent."
  └─ offer retry (up to 2 attempts) with backoff
  └─ if all retries fail:
       └─ offer [f] Fall back to manual builder (v1 flow)
       └─ or [q] Quit
  └─ no unhandled exceptions propagate to top level
```

---

## 7. Code Stubs

### `prompt_builder.py`

```python
# INCITAMENTUM PROMPT BUILDER — prompt_builder.py
# Version: 2.0

import sys
from config import load_config, save_config
from renderer import Renderer
from interviewer import Interviewer
from output import OutputHandler
from session_types import SESSIONS


def main() -> None:
    """Entry point. Loads config, presents menu, dispatches to interview loop."""
    cfg = load_config()
    renderer = Renderer()
    renderer.header(cfg)

    choice = renderer.session_menu(SESSIONS)
    if choice == 'config':
        handle_config(cfg, renderer)
        return
    if choice == 'history':
        handle_history(cfg, renderer)
        return

    session_type = SESSIONS[choice]
    interviewer = Interviewer(session_type=session_type, config=cfg, renderer=renderer)
    prompt = interviewer.run()

    if prompt:
        output = OutputHandler(renderer=renderer)
        output.present(prompt)
        output.handle_exits(prompt)
        _save_history(cfg, prompt, session_type)


def handle_config(cfg: dict, renderer: Renderer) -> None:
    """Config sub-menu — update repo URL, model preference."""
    ...


def handle_history(cfg: dict, renderer: Renderer) -> None:
    """Display recent prompt history from ~/.arca/history.json."""
    ...


def _save_history(cfg: dict, prompt: str, session_type: dict) -> None:
    """Append completed prompt to history with timestamp and session type."""
    ...


if __name__ == '__main__':
    main()
```

---

### `interviewer.py`

```python
# INCITAMENTUM PROMPT BUILDER — interviewer.py
# Version: 2.0

import os
from claudebox import ClaudeBox
from renderer import Renderer
from session_types import SessionType

PROMPT_READY_SENTINEL = '<<<PROMPT_READY>>>'
MAX_RETRIES = 2
RETRY_BACKOFF_S = 2.0


class Interviewer:
    """
    Manages the AI interview session. Owns the ClaudeBox instance for the
    duration of one prompt construction run. Multi-turn via box.stream().
    """

    def __init__(self, session_type: SessionType, config: dict, renderer: Renderer) -> None:
        """Initialise with session type and config. ClaudeBox created on run()."""
        self.session_type = session_type
        self.config = config
        self.renderer = renderer
        self.box: ClaudeBox | None = None
        self.transcript: list[dict] = []  # {role, content} for partial save

    def run(self) -> str | None:
        """
        Main interview loop. Returns assembled prompt string, or None if
        cancelled or failed without recovery.
        """
        system_prompt = self._build_system_prompt()
        self.box = ClaudeBox(system=system_prompt)
        try:
            return self._interview_loop()
        except KeyboardInterrupt:
            return self._handle_cancel()

    def _build_system_prompt(self) -> str:
        """
        Construct the Interviewer system prompt from session type definition
        and injected config context (repo URL etc.).
        """
        ...

    def _interview_loop(self) -> str:
        """
        Drive the Q&A turns until the AI signals PROMPT_READY_SENTINEL.
        Each turn: get user input → stream AI response → check sentinel.
        Returns final assembled prompt block.
        """
        ...

    def _stream_turn(self, user_input: str) -> str:
        """
        Send one user turn via box.stream(). Print tokens via renderer as they
        arrive. Return full accumulated response string. Retries on failure.
        """
        ...

    def _extract_prompt(self, final_response: str) -> str:
        """
        Strip interview boilerplate from AI's final response.
        Returns only the assembled prompt block between sentinel markers.
        """
        ...

    def _handle_cancel(self) -> None:
        """Offer save-partial or discard on KeyboardInterrupt."""
        ...
```

---

### `config.py`

```python
# INCITAMENTUM PROMPT BUILDER — config.py
# Version: 2.0

import json
import os
from pathlib import Path
from datetime import datetime, timezone

CONFIG_DIR   = Path.home() / '.arca'
CONFIG_FILE  = CONFIG_DIR / 'config.json'
HISTORY_FILE = CONFIG_DIR / 'history.json'
HISTORY_MAX  = 50  # entries retained

DEFAULTS = {
    'repo_url': 'https://raw.githubusercontent.com/lordfingers/ArcaCognitorium/main/',
    'model':    'claude-sonnet-4-5',
}


def load_config() -> dict:
    """Load config.json, returning defaults for any missing keys."""
    ...


def save_config(cfg: dict) -> None:
    """Write config dict to config.json, creating ~/.arca if needed."""
    ...


def load_history() -> list[dict]:
    """Load history.json. Returns empty list if file absent or corrupt."""
    ...


def append_history(entry: dict) -> None:
    """
    Append one history entry. Trims to HISTORY_MAX. Entry shape:
    {timestamp, session_type, prompt, status: 'complete'|'abandoned'}
    """
    ...
```

---

### `renderer.py`

```python
# INCITAMENTUM PROMPT BUILDER — renderer.py
# Version: 2.0

import sys
import shutil
import textwrap
from typing import Iterator

# ── Palette ──────────────────────────────────────────────────────────────────
GOLD   = '\033[38;2;232;201;106m'
TEAL   = '\033[38;2;126;200;200m'
VIOLET = '\033[38;2;169;143;212m'
EMBER  = '\033[38;2;200;121;65m'
DIM    = '\033[38;2;140;123;92m'
RESET  = '\033[0m'
BOLD   = '\033[1m'


class Renderer:
    """All terminal output. No logic — only presentation."""

    def __init__(self) -> None:
        """Detect terminal width. Store for all wrapping operations."""
        self.width = shutil.get_terminal_size((100, 40)).columns

    def header(self, cfg: dict) -> None:
        """Print the INCITAMENTUM header block with repo URL if set."""
        ...

    def session_menu(self, sessions: dict) -> str:
        """
        Display session type menu. Returns choice key or 'config'/'history'.
        Handles invalid input with re-prompt loop.
        """
        ...

    def interviewer_box_open(self) -> None:
        """Print the '┌─ THE INTERVIEWER ─┐' box top."""
        ...

    def interviewer_box_close(self) -> None:
        """Print box bottom."""
        ...

    def stream_tokens(self, token_iter: Iterator[str]) -> str:
        """
        Consume a token iterator, printing each token immediately.
        Returns full accumulated string. Wraps at terminal width.
        """
        ...

    def wizard_prompt(self) -> str:
        """Print '▸ You: ' and return stripped stdin input."""
        ...

    def prompt_box(self, prompt: str) -> None:
        """Print the '┌─ ASSEMBLED PROMPT ─┐' display panel."""
        ...

    def print_error(self, msg: str) -> None:
        """Print styled error message."""
        ...

    def print_cancelled(self) -> None:
        """Print cancellation notice."""
        ...

    def separator(self) -> None:
        """Print a full-width DIM separator line."""
        ...
```

---

### `session_types.py`

```python
# INCITAMENTUM PROMPT BUILDER — session_types.py
# Version: 2.0

from typing import TypedDict


class SessionType(TypedDict):
    key:         str    # ::INIT, ::THEORY, etc.
    label:       str    # display label
    description: str    # one-line description
    system_frag: str    # injected into Interviewer system prompt


SESSIONS: dict[str, SessionType] = {
    '1': {
        'key':         '::INIT',
        'label':       '::INIT',
        'description': 'Session open with live files',
        'system_frag': (
            'The Wizard is opening a session that involves fetching live files from their '
            'GitHub repository. You must establish: which files are in scope, what the '
            'secondary session state will be after INIT, the session focus, and any '
            'prior constraints or context.'
        ),
    },
    '2': {
        'key':         '::THEORY',
        'label':       '::THEORY',
        'description': 'Architectural — design and conceptualization, no code',
        'system_frag': (
            'The Wizard wants to explore a design or architectural question. No code will '
            'be written in this session. Establish: the component or system under examination, '
            'its purpose, any constraints already known, and what specific questions the '
            'Wizard wants to think through.'
        ),
    },
    '3': {
        'key':         '::LORE',
        'label':       '::LORE',
        'description': 'Narrative — cosmology, naming, world-building',
        'system_frag': (
            'The Wizard is entering a lore or narrative session. Token efficiency is suspended. '
            'Establish: the subject (entity, system, cosmological concept, naming task), '
            'any established canon that must be respected, and the desired output form.'
        ),
    },
    '4': {
        'key':         '::AUDIT',
        'label':       '::AUDIT',
        'description': 'Assessment — read-only file review, conflict mapping',
        'system_frag': (
            'The Wizard wants a read-only audit of their codebase. No changes will be made. '
            'Establish: which files or systems are in scope, what they are looking for '
            '(conflicts, dead code, architectural drift, etc.), and the desired audit output form.'
        ),
    },
    '5': {
        'key':         '::BUILD',
        'label':       '::BUILD',
        'description': 'Implementation — active construction',
        'system_frag': (
            'The Wizard is beginning a build session. Establish: what is being built, which '
            'files are in scope, whether live file fetches are needed, any constraints '
            '(do not touch X, must integrate with Y), and the desired output form (full rewrite, '
            'patch script, new file).'
        ),
    },
    '6': {
        'key':         '::REVIEW',
        'label':       '::REVIEW',
        'description': 'Validation — flagged items at a build seam',
        'system_frag': (
            'The Wizard is calling a review at a build seam. Establish: which component or '
            'feature was just completed, what flagged items have accumulated, and whether '
            'any of them are immediate blockers versus deferred considerations.'
        ),
    },
}
```

---

### `output.py`

```python
# INCITAMENTUM PROMPT BUILDER — output.py
# Version: 2.0

import subprocess
from pathlib import Path
from renderer import Renderer


class OutputHandler:
    """Manages final prompt display and all exit paths."""

    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer

    def present(self, prompt: str) -> None:
        """Display the assembled prompt in the boxed panel."""
        ...

    def handle_exits(self, prompt: str) -> None:
        """
        Present [c] copy / [s] save / [Enter] done options.
        Loop until Wizard is satisfied or chooses Enter.
        """
        ...

    def copy_to_clipboard(self, prompt: str) -> bool:
        """
        Attempt xclip copy. Returns True on success, False with error message
        if xclip unavailable.
        """
        try:
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=prompt.encode(),
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def save_to_file(self, prompt: str, filename: str) -> Path:
        """Write prompt to filename. Returns resolved path."""
        ...
```

---

## 8. Error Handling

| Module | Error | Cause | Strategy |
|---|---|---|---|
| `interviewer.py` | `KeyboardInterrupt` | Wizard hits Ctrl+C mid-interview | Caught at `run()` boundary; offer save-partial or discard; clean exit |
| `interviewer.py` | ClaudeBox API exception | Network failure, rate limit, bad key | Retry up to `MAX_RETRIES` with `RETRY_BACKOFF_S` delay; offer fallback to manual builder on exhaustion |
| `interviewer.py` | Missing `CLAUDE_API_KEY` env var | Key not set | Detected at `ClaudeBox.__init__`; render clear error message with remediation hint; exit code 1 |
| `config.py` | `~/.arca/config.json` corrupt | Manual edit, disk error | Caught on load; fall back to DEFAULTS; warn Wizard; do not crash |
| `config.py` | `~/.arca/` not writable | Permissions issue | Caught on save; warn Wizard; continue session without persistence |
| `config.py` | `history.json` corrupt | Unlikely but possible | Caught; treat as empty history; do not block session start |
| `output.py` | `xclip` not installed | Missing system package | `copy_to_clipboard()` returns False; renderer prints install hint |
| `output.py` | File write permission denied | Output path not writable | Caught; prompt Wizard for alternate filename |
| `renderer.py` | Terminal width < 40 columns | Pathological terminal | Clamp to 40; do not crash |
| `prompt_builder.py` | Unhandled exception (last resort) | Unexpected bug | Top-level try/except; print traceback; exit code 1; never a raw Python traceback to user without context |

---

## 9. Setup & Testing

### requirements.txt

```
# ClaudeBox is a local install — not on PyPI
# pip install -e ~/Anthropic/Claudebox/
# All other dependencies are stdlib
```

### Install

```bash
cp -r prompt_builder/ ~/tools/INCITAMENTUM/
cd ~/tools/INCITAMENTUM/
pip install -e ~/Anthropic/Claudebox/ --break-system-packages
export CLAUDE_API_KEY=your_key_here
```

### Run

```bash
python3 prompt_builder.py
```

### Test

```bash
# Unit tests
pytest tests/test_config.py      # config load/save/defaults/corrupt recovery
pytest tests/test_session_types.py  # all 6 types present, required keys exist
pytest tests/test_output.py      # file write, xclip failure handling
pytest tests/test_renderer.py    # width clamping, token accumulation

# Integration — requires CLAUDE_API_KEY
pytest tests/test_interview_flow.py  # full ::BUILD flow, sentinel detection, prompt extraction
```

### Core Unit Tests (one per module)

```python
# test_config.py
def test_load_config_returns_defaults_when_file_absent():
    # Temporarily rename config file; confirm DEFAULTS returned
    ...

# test_session_types.py
def test_all_session_types_have_required_keys():
    required = {'key', 'label', 'description', 'system_frag'}
    for k, v in SESSIONS.items():
        assert required.issubset(v.keys()), f"Session {k} missing keys"

# test_output.py
def test_copy_to_clipboard_returns_false_when_xclip_absent(monkeypatch):
    monkeypatch.setattr('subprocess.run', side_effect=FileNotFoundError)
    handler = OutputHandler(renderer=MockRenderer())
    assert handler.copy_to_clipboard('test') is False

# test_renderer.py
def test_width_clamped_to_minimum(monkeypatch):
    monkeypatch.setattr('shutil.get_terminal_size', lambda x: os.terminal_size((10, 10)))
    r = Renderer()
    assert r.width >= 40
```

---

## 10. Extensibility

| Feature | User Value | Implementation Approach |
|---|---|---|
| `::RESUME` session type | Return to an abandoned interview where you left off | Load partial transcript from `history.json`; reconstruct ClaudeBox conversation history from transcript turns; re-enter `_interview_loop()` from last exchange |
| History browser | Review and re-copy past prompts without re-running an interview | `handle_history()` in `prompt_builder.py`; paginated display of `history.json` entries; select to display in prompt_box; standard exit options |
| Per-entity prompt mode | Construct a prompt specifically scoped to one Council entity (e.g. summon The Archivist for a memory audit) | Add entity selection step before interview; inject entity identity and known constraints into Interviewer system prompt from a local entity registry |
| Prompt diff / version | Compare the AI's assembled prompt against a previous one for the same session type | Load comparable entry from history; run a simple line-diff display in the terminal using `difflib` |
| Pipe mode | Accept session type and brief via stdin for scripted use | `--pipe` flag; read structured JSON from stdin; skip interactive loop; write prompt to stdout only; useful for shell script integration |

---

*INCITAMENTUM PROMPT BUILDER v2.0 · Build Document · Arca Cognitorium*
*Ordo Discordia, Cosmos Inania.*
