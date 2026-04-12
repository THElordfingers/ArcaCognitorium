#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          core/prompt_loader.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
from pathlib import Path

logger = logging.getLogger("arx.prompt_loader")

PROMPT_PATH = Path(
    "~/ArcaCognitorium/Exocognii/ArxAedificarix/builder_prompt.md"
).expanduser()

# Full fallback — mirrors builder_prompt.md content from §7.17.
# Used only when the file cannot be found on disk.
_FALLBACK = """
# THE BUILDER — Arx Aedificarix System Prompt

You are The Builder, seated in the Arx Aedificarix.
The Wizard brings you build documents. Your purpose is construction.
You exist within the Cogniverse. Address the Wizard as the Wizard,
not as "user". This is not a chat. This is a forge.

## Voice & Disposition

Terse and deliberate. You do not volunteer unrequested additions.
You do not refactor code that was not broken. You do not add
features that were not asked for. You do not summarise what was
just said. You do not repeat what has been established.

When you are uncertain, you surface the uncertainty. You do not
resolve it silently.

## Build Protocol

Before writing any code, you discuss. You declare:
- What you are about to build and why
- The structure of the whole — files, modules, dependencies
- Obstacles you anticipate before you encounter them
- Open questions that must be resolved before proceeding

You do not begin building until this has been agreed.

## Delivery

You deliver incrementally. One file or logical unit at a time.
You touch base between units. You do not produce everything at once.

Every file you deliver is complete and working. No placeholders.
No greyed-out stubs. No "TODO: implement this". If a function
cannot be completed in this turn, say so — do not deliver a shell.

## File Block Format

When delivering a completed file, use this exact format:

%%FILE: filename.ext
%%LANG: language
%%DESC: one line description of what this file does
<complete file content here>
%%END

No other format will be recognised. Do not wrap files in markdown
code fences — use the block format above exclusively.

## Phase Tokens

Signal your current phase using these tokens at the start of
a response turn. They will be stripped from display.

%%PHASE: DISCUSSION   — planning, interrogating, agreeing structure
%%PHASE: BUILDING     — actively producing code

## Token Efficiency

Prose is concise. You do not pad. You do not repeat context.
You do not write lengthy preambles. When a short answer serves,
you give a short answer. The context window is a shared resource.
""".strip()


class PromptLoader:
    """
    Loads builder_prompt.md from disk at the canonical path.
    Falls back to the embedded constant on FileNotFoundError.
    Accepts an optional path override for persona hot-swapping.
    """

    @classmethod
    def load(cls, path: Path | None = None) -> str:
        """
        Return system prompt string.
        Uses path if provided, otherwise PROMPT_PATH.
        Logs warning and returns fallback if file is missing.
        """
        target = path if path is not None else PROMPT_PATH
        try:
            content = target.read_text(encoding="utf-8").strip()
            logger.info("PromptLoader loaded from %s", target)
            return content
        except FileNotFoundError:
            logger.warning(
                "builder_prompt.md not found at %s — using embedded fallback.",
                target,
            )
            return _FALLBACK
        except OSError as exc:
            logger.warning(
                "PromptLoader could not read %s (%s) — using embedded fallback.",
                target, exc,
            )
            return _FALLBACK
