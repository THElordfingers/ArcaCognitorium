"""
Claude API worker for Devoted Absurd.
Runs silently in background threads — never blocks the UI.
Handles iterative prompt refinement, scoring, and weakness flagging.
"""

import json
import threading
from typing import Callable, Optional
import anthropic

# ── SYSTEM PROMPT FOR THE BACKGROUND CLAUDE ───────────────────────────────────
SYSTEM_PROMPT = """You are a specialist image-generation prompt engineer for a 2D character illustration project called "Devoted Absurd".

The project has a locked visual style:
- Stylized 2D illustration, bold clean ink outlines, flat cel shading
- Muted desaturated palette, strong midtone presence, defined shadow shapes
- Angular but grounded human proportions, fully human characters
- Understated punk influence, restrained dark humour, bureaucratic/institutional themes
- No animals, no glossy rendering, no painterly effects

Your job is to:
1. Analyse the provided character prompt for weaknesses (vagueness, contradictions, style drift, clichés, weak specificity)
2. Score it 1-10 for likely image generation quality (10 = precise, evocative, style-consistent; 1 = vague, contradictory, likely to drift)
3. Produce a refined version that is more precise and evocative while staying true to the locked style
4. Suggest one iterative improvement direction if the user wanted to push further

Respond ONLY in valid JSON with this exact structure:
{
  "score": <float 1-10>,
  "reasoning": "<2-3 sentences explaining the score>",
  "weaknesses": ["<short weakness tag>", ...],
  "refined_prompt": "<the full improved prompt>",
  "next_iteration_suggestion": "<one sentence on what to explore next>"
}

Be harsh but fair. A score of 7+ means the prompt is genuinely strong. Most prompts start around 4-6.
Never exceed 15 words in any direct quote from the input prompt."""

# ── ITERATIVE REFINEMENT HISTORY ──────────────────────────────────────────────
# Stored per-session in memory. Each entry_id has a conversation history.
_refinement_sessions: dict[str, list] = {}
_sessions_lock = threading.Lock()


def _call_claude(messages: list, max_tokens: int = 1200) -> dict:
    """Raw API call. Returns parsed JSON dict or raises."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyse_prompt_async(
    entry_id: str,
    prompt: str,
    on_complete: Callable[[str, dict], None],
    on_error: Callable[[str, str], None],
):
    """
    Fire-and-forget background analysis of a prompt.
    Calls on_complete(entry_id, result_dict) when done.
    """
    def _run():
        try:
            messages = [{"role": "user", "content": f"Analyse and refine this character prompt:\n\n{prompt}"}]
            result = _call_claude(messages)
            with _sessions_lock:
                _refinement_sessions[entry_id] = messages + [
                    {"role": "assistant", "content": json.dumps(result)}
                ]
            on_complete(entry_id, result)
        except Exception as e:
            on_error(entry_id, str(e))

    threading.Thread(target=_run, daemon=True).start()


def iterate_refinement_async(
    entry_id: str,
    user_feedback: str,
    on_complete: Callable[[str, dict], None],
    on_error: Callable[[str, str], None],
):
    """
    Continue refining an existing session with user feedback.
    Maintains full conversation history for context.
    """
    def _run():
        with _sessions_lock:
            history = list(_refinement_sessions.get(entry_id, []))

        if not history:
            on_error(entry_id, "No refinement session found for this entry.")
            return

        try:
            history.append({"role": "user", "content": user_feedback})
            result = _call_claude(history)
            history.append({"role": "assistant", "content": json.dumps(result)})
            with _sessions_lock:
                _refinement_sessions[entry_id] = history
            on_complete(entry_id, result)
        except Exception as e:
            on_error(entry_id, str(e))

    threading.Thread(target=_run, daemon=True).start()


def clear_session(entry_id: str):
    with _sessions_lock:
        _refinement_sessions.pop(entry_id, None)
