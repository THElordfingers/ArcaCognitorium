"""
# claude_worker.py — Devoted Absurd Character Prompt Generator
# v4.0 — Medieval overhaul + bug fixes
#
# KEY CHANGES from v3:
#   — Fixed first_err scoping bug in _parse_json_response
#   — Fixed clear_session → delete_session (ClaudeBox API)
#   — Simplified _call_analysis to use native ClaudeBox session management
#   — Rewrote GENERATION_SYSTEM for medieval-dark-ages register with pseudo-tech
#   — Rewrote ANALYSIS_SYSTEM to match
#
# Runs silently in background threads — never blocks the UI.
# Handles character generation, iterative prompt refinement,
# scoring, and weakness flagging.
#
# ClaudeBox wired per ArcaCognitorium canonical pattern:
#   sys.path → ~/ArcaCognitorium
#   from claudebox import ClaudeBox
#   api_key=os.environ.get('CLAUDE_API_KEY')
"""

import os
import json
import threading
from pathlib import Path
from typing import Callable

import sys
sys.path.insert(0, str(Path.home() / 'ArcaCognitorium'))
from claudebox import ClaudeBox


# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────

GENERATION_SYSTEM = """You are a character designer for a 2D illustration project called "Devoted Absurd".

── LOCKED VISUAL STYLE ──────────────────────────────────────────────────────
Stylized 2D illustration, bold clean ink outlines, flat cel shading.
Dark world. Deep shadow register throughout. This is not a bright world.
Palette is muted, heavily desaturated, anchored in dark tones:
  — near-blacks, coal, soot, deep charcoal
  — dark industrials: furnace green, deep rust, oxidised copper, tarnished iron
  — aged organics: dried blood, stained parchment, worn leather, old wood
  — bruised tones: deep plum, dark slate, cold ink-wash blue — all dark
Highlights: sparse, deliberate, one or two punchy colour accents maximum.
No pastels. No bright primaries. No mint green. No cream. No beige.
No light backgrounds. Backgrounds are near-black or deep dark tones.
Angular but grounded human proportions, fully human characters.
No animals, no glossy rendering, no painterly effects.
Understated punk influence, medieval-institutional and bureaucratic themes.
Dark humour, restrained. Surface wear and decay visible but not grotesque.

── SETTING — THE DARK AGES ──────────────────────────────────────────────────
This is a medieval dark-ages world. Not high fantasy. Not modern. Not Victorian.
The primary register is firmly medieval:
  — Guilds, city gates, toll roads, feudal courts, parish churches, market squares
  — Castle garrisons, walled towns, river crossings, forest roads, charcoal kilns
  — Parchment and wax seal, quill and iron-gall ink, tally sticks and ledgers
  — Wool, linen, leather, rough iron, tallow, stone, timber, rope

PSEUDO-TECHNOLOGY — the crucial texture layer:
This medieval world has developed crude mechanical technology. Not steampunk.
Not shiny brass and goggles. Heavy, dark, mechanical, and old:
  — Bellows-driven pneumatic systems: capsule mail, forge air, organ pipes
  — Gear-driven mechanisms: filing engines, census machines, clock towers, mill works
  — Waterwheel-powered industry: stamp presses, bolt forges, document presses, saw mills
  — Hand-cranked devices: calculation machines, crossbow windlasses, printing presses
  — Clockwork automata: mechanical sentries, messenger pigeons, filing clerks
  — Alchemical apparatus: distillation, lamp fuels, reagent processing
  — Steam exists but is CRUDE — sealed copper boilers, hand-riveted, unreliable
The technology is built from wood, iron, copper, rope, and necessity.
It creaks. It jams. It smells of grease and charcoal. It is not decorative.

Characters exist within this world. Their roles, clothing, props, and details
should feel grounded in this medieval-mechanical register. A guild inspector
might carry a gear-driven tally counter. A castle clerk might operate a
waterwheel-powered filing engine. A garrison armourer might maintain
spring-loaded crossbow mechanisms.

── YOUR ROLE ────────────────────────────────────────────────────────────────
You will receive an archetype vocabulary package. This is reference material, not a pick list.
Read it to understand the tonal register, the kinds of roles that fit, the material textures,
the prop logic, the personality flavours. Then invent a complete, specific character.

Do NOT copy vocabulary items verbatim. Synthesise from them.
Do NOT pick generic defaults. Invent something with texture and specificity.
The character should feel like they have a history and a function in a real, lived-in medieval world.
Lean into the pseudo-tech where it fits naturally — not every character needs a mechanism,
but the world contains them and characters interact with them.

── PALETTE ENFORCEMENT ──────────────────────────────────────────────────────
This is the most common failure mode. Be aggressive about it.
Every colour you name must be dark. Ask: is this light? If yes, darken it.
"Dark teal" not "teal". "Near-black olive" not "olive green".
"Deep rust" not "rust orange". "Bruised plum" not "purple".
Backgrounds: always near-black or deep dark. Never light.
If in doubt: darken. The world is dark.

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Respond ONLY in valid JSON with this exact structure:
{
  "role": "<specific invented job title — medieval register, not modern>",
  "personality": "<2-3 sentences of specific character texture — not a trope label>",
  "garment": "<specific clothing: fabric, cut, condition, worn details — medieval materials>",
  "prop": "<one specific carried object with condition detail — period-appropriate>",
  "detail": "<one small telling physical or clothing detail>",
  "mood": "<expression and bearing — specific, not just an emotion word>",
  "posture": "<body language and stance>",
  "body_type": "<build description>",
  "age": "<age range with one sentence on what it means for this specific person>",
  "era_blend": "<how this character sits in the medieval-mechanical world — what tech touches their life>",
  "palette": "<3-4 specific dark colours — named precisely, all anchored in shadow register>",
  "background": "<one flat near-black or deep dark colour — never light>",
  "assembled_prompt": "<the full image generation prompt, ready to use>"
}

The assembled_prompt must:
  1. Open with the full style DNA (stylized 2D, bold ink outlines, flat cel shading, etc.)
  2. State the medieval-mechanical setting explicitly
  3. Weave all character elements into a single cohesive paragraph
  4. End with a strict palette note — name the dark colours, forbid any light drift
  5. Specify a dark background explicitly

── JSON HYGIENE — CRITICAL ──────────────────────────────────────────────────
Your response must be valid, parseable JSON. Follow these rules exactly:
- Every string value must be on a single line. No literal newline or carriage
  return characters inside any string value. Use a space instead of a line break.
- The assembled_prompt field must be one continuous string. Do not break it
  across lines. Do not insert \\n sequences.
- Do not use unescaped double-quote marks inside any string value.
  If you must reference something with quotes, use single quotes instead.
- Do not add a trailing comma after the last field in the object.
- Respond with the JSON object only — no preamble, no commentary, no fences."""


ANALYSIS_SYSTEM = """You are a specialist image-generation prompt engineer for a 2D character illustration project called "Devoted Absurd".

── PROJECT REGISTER ─────────────────────────────────────────────────────────
Stylized 2D illustration, bold clean ink outlines, flat cel shading.
Dark world. Deep shadow register throughout.
Muted heavily desaturated palette: near-blacks, dark industrials, aged materials.
Medieval dark-ages setting with pseudo-mechanical technology — bellows, gears,
waterwheel-driven machinery, alchemical apparatus, clockwork automata, crude steam.
Not steampunk. Not modern. Not Victorian. Medieval-mechanical.
No pastels. No light backgrounds. No bright primaries.
Angular but grounded human proportions, fully human characters.
Understated punk influence, medieval-institutional and bureaucratic themes.

── YOUR JOB ─────────────────────────────────────────────────────────────────
1. Analyse the provided prompt for weaknesses:
   — palette drift toward light (flag aggressively)
   — light or pale backgrounds (this is a hard failure)
   — MODERN ANACHRONISMS (flag aggressively: cars, phones, electricity, plastic,
     modern office equipment, suits and ties, zoning boards, parking meters,
     convenience stores — anything post-medieval)
   — vagueness or generic defaults
   — contradictions or style drift
   — era confusion — the setting is medieval with crude mechanisms, not modern
   — clichés, weak specificity, missed texture
   — character that feels assembled rather than invented

2. Score 1-10 for likely image generation quality:
   10 = precise, evocative, style-consistent, properly dark, era-coherent
   7+ = genuinely strong — do not inflate
   Below 5 = vague, contradictory, drifts light, generic, era-wrong
   Flag palette drift toward lightness aggressively. A pale background alone drops the score 2 points.
   Flag modern anachronisms aggressively. A modern role or prop drops the score 2 points.

3. Produce a refined version — more precise, more evocative,
   anchored harder in the dark shadow register, medieval register sharpened,
   pseudo-tech woven in where it enriches the character.

4. Suggest one iterative direction.

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Respond ONLY in valid JSON with this exact structure:
{
  "score": <float 1-10>,
  "reasoning": "<2-3 sentences explaining the score — be specific and harsh>",
  "weaknesses": ["<short weakness tag>", ...],
  "refined_prompt": "<the full improved prompt>",
  "next_iteration_suggestion": "<one sentence on what to sharpen next>"
}

Be harsh but fair. A 7+ means genuinely strong.
Flag any palette drift toward lightness immediately — it is the most common failure.
Flag any modern anachronisms immediately — the second most common failure.
Never exceed 15 words in any direct reference to input text.

── JSON HYGIENE — CRITICAL ──────────────────────────────────────────────────
Your response must be valid, parseable JSON. Follow these rules exactly:
- Every string value must be on a single line. No literal newlines inside strings.
- The refined_prompt field must be one continuous string. No line breaks inside it.
- Do not use unescaped double-quote marks inside any string value.
  Use single quotes if you need to quote something within a string.
- Do not add a trailing comma after the last field in the object.
- Respond with the JSON object only — no preamble, no commentary, no fences."""


# ── CLAUDEBOX INSTANCES ───────────────────────────────────────────────────────

_api_key = os.environ.get('CLAUDE_API_KEY')

_gen_box = ClaudeBox(api_key=_api_key, system_prompt=GENERATION_SYSTEM, stream=False)
_gen_box_lock = threading.Lock()

_analysis_box = ClaudeBox(api_key=_api_key, system_prompt=ANALYSIS_SYSTEM, stream=False)
_analysis_box_lock = threading.Lock()


# ── INTERNAL HELPERS ──────────────────────────────────────────────────────────

def _parse_json_response(text: str) -> dict:
    """
    Parse JSON from Claude response. Multi-stage recovery:
    1. Strip markdown fences
    2. Extract first {...} block if there's surrounding text
    3. Attempt direct parse
    4. On failure: repair common breakage (literal newlines inside strings,
       unescaped quotes) then retry
    5. On second failure: raise with the original error and a snippet
    """
    import re

    original = text
    text = text.strip()

    # Stage 1: strip markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    # Stage 2: extract first outermost {...} block
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        text = text[brace_start:brace_end + 1]

    # Stage 3: direct parse
    # NOTE: first_err must be preserved outside the except block
    # because Python 3 deletes exception variables on block exit.
    first_err = None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        first_err = e

    # Stage 4: repair common LLM JSON breakage
    repaired = text

    # 4a. Replace literal newlines inside string values with space
    def repair_newlines(s: str) -> str:
        out = []
        in_string = False
        escaped = False
        for ch in s:
            if escaped:
                out.append(ch)
                escaped = False
            elif ch == "\\" and in_string:
                out.append(ch)
                escaped = True
            elif ch == '"':
                out.append(ch)
                in_string = not in_string
            elif ch in ("\n", "\r") and in_string:
                out.append(" ")
            else:
                out.append(ch)
        return "".join(out)

    repaired = repair_newlines(repaired)

    # 4b. Remove any trailing commas before } or ]
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError as second_err:
        snippet = original[:200].replace("\n", "↵")
        raise ValueError(
            f"JSON parse failed after repair attempt.\n"
            f"Original error: {first_err}\n"
            f"Repair error: {second_err}\n"
            f"Response snippet: {snippet}"
        ) from second_err


def _call_generation(seed_context: str) -> dict:
    """Single generation call. Returns parsed character dict."""
    with _gen_box_lock:
        response = _gen_box.send(seed_context, max_tokens=4096)
    return _parse_json_response(response.text)


def _call_analysis(prompt_content: str, session_id: str = None) -> dict:
    """
    Analysis/refinement call using native ClaudeBox session management.
    If session_id is provided, the conversation history is maintained by ClaudeBox.
    """
    with _analysis_box_lock:
        response = _analysis_box.send(
            prompt_content, session_id=session_id, max_tokens=4096
        )
    return _parse_json_response(response.text)


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def generate_character_async(
    archetype_key: str,
    archetype_label: str,
    palette_hint: str,
    style_flex: str,
    overrides: dict,
    on_complete: Callable[[dict], None],
    on_error: Callable[[str], None],
    archetype_vocabulary: str = "",
):
    """
    Fire-and-forget character generation via Claude.

    Claude receives the archetype vocabulary as reference material and invents
    a character freely within that register — it does not pick from the pools.

    archetype_vocabulary: formatted vocabulary string from data_pools.get_archetype_vocabulary()
    on_complete(char_dict) — char_dict is ready to use directly
    on_error(error_str)
    """
    def _run():
        try:
            override_lines = ""
            if overrides:
                locked = [f"  {k}: {v}" for k, v in overrides.items() if v]
                if locked:
                    override_lines = (
                        "\n\nThe following fields are locked by the user and must not be changed:\n"
                        + "\n".join(locked)
                    )

            vocab_block = ""
            if archetype_vocabulary:
                vocab_block = (
                    "\n\n── ARCHETYPE VOCABULARY REFERENCE ──────────────────────────────────\n"
                    "Read this as tonal and textural reference. "
                    "Synthesise from it freely — do not copy items verbatim.\n\n"
                    + archetype_vocabulary
                )

            seed = (
                f"Archetype: {archetype_label}\n"
                f"Palette direction: {palette_hint}\n"
                f"Style register: {style_flex}\n"
                f"Invent a complete, specific character in a medieval dark-ages world "
                f"with crude mechanical pseudo-technology. "
                f"Use the vocabulary reference below as inspiration, not as a pick list. "
                f"Synthesise. Do not copy. Invent something with history and texture. "
                f"The character must feel grounded in a medieval register — no modern elements."
                f"{vocab_block}"
                f"{override_lines}"
            )

            result = _call_generation(seed)

            char = {
                "archetype_key": archetype_key,
                "archetype_label": archetype_label,
                "role": result.get("role", ""),
                "personality": result.get("personality", ""),
                "garment": result.get("garment", ""),
                "prop": result.get("prop", ""),
                "detail": result.get("detail", ""),
                "mood": result.get("mood", ""),
                "posture": result.get("posture", ""),
                "body_type": result.get("body_type", ""),
                "age": result.get("age", ""),
                "era_blend": result.get("era_blend", ""),
                "palette_hint": result.get("palette", palette_hint),
                "background": result.get("background", "flat near-black void"),
                "style_flex": style_flex,
                "assembled_prompt": result.get("assembled_prompt", ""),
                "name": overrides.get("name", ""),
                "extra": overrides.get("extra", ""),
                "setting_hint": None,
                "_source": "claude",
            }
            on_complete(char)

        except Exception as e:
            on_error(str(e))

    threading.Thread(target=_run, daemon=True).start()


def analyse_prompt_async(
    entry_id: str,
    prompt: str,
    on_complete: Callable[[str, dict], None],
    on_error: Callable[[str, str], None],
):
    """Fire-and-forget background analysis of a prompt."""
    def _run():
        try:
            # Use entry_id as session_id for native ClaudeBox session tracking
            session_id = f"analysis_{entry_id}"

            # Clear any previous session with this ID
            try:
                _analysis_box.delete_session(session_id)
            except Exception:
                pass  # Session may not exist yet

            content = f"Analyse and refine this character prompt:\n\n{prompt}"
            result = _call_analysis(content, session_id=session_id)
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
    """Continue refining an existing session with user feedback."""
    def _run():
        session_id = f"analysis_{entry_id}"

        # Check if session exists
        try:
            history = _analysis_box.get_history(session_id)
            if not history:
                on_error(entry_id, "No refinement session found for this entry.")
                return
        except Exception:
            on_error(entry_id, "No refinement session found for this entry.")
            return

        try:
            result = _call_analysis(user_feedback, session_id=session_id)
            on_complete(entry_id, result)
        except Exception as e:
            on_error(entry_id, str(e))

    threading.Thread(target=_run, daemon=True).start()


def clear_session(entry_id: str):
    """Clear a refinement session."""
    session_id = f"analysis_{entry_id}"
    try:
        _analysis_box.delete_session(session_id)
    except Exception:
        pass
