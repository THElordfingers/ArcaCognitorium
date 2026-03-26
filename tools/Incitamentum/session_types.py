"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████ ███████ ███████ ███████ ██  ██████  ███    ██    ████████ ██    ██ ██████  ███████ ███████  ▍
🮈  ██      ██      ██      ██      ██ ██    ██ ████   ██       ██     ██  ██  ██   ██ ██      ██       ▍
🮈  ███████ █████   ███████ ███████ ██ ██    ██ ██ ██  ██ █████ ██      ████   ██████  █████   ███████  ▍
🮈       ██ ██           ██      ██ ██ ██    ██ ██  ██ ██       ██       ██    ██      ██           ██  ▍
🮈  ███████ ███████ ███████ ███████ ██  ██████  ██   ████       ██       ██    ██      ███████ ███████  ▍
🮈                                                                                                      ▍
🮈                                                                                                      ▍
🮈                                            Python Script                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

# =============================================================================
# INCITAMENTUM — session_types.py
# Version: 2.0
# Arca Cognitorium — Session type registry for the AI Interviewer
# =============================================================================

from typing import TypedDict


class SessionType(TypedDict):
    key:         str   # ::INIT, ::THEORY, etc.
    label:       str   # display label
    description: str   # one-line menu description
    system_frag: str   # injected into Interviewer system prompt


SESSIONS: dict[str, SessionType] = {
    '1': {
        'key':         '::INIT',
        'label':       '::INIT',
        'description': 'Session open with live files',
        'system_frag': (
            'The Wizard is opening a session that involves fetching live files from their '
            'GitHub repository. You must establish: which files are in scope, what the '
            'secondary session state will be after INIT completes, the session focus in '
            'one or two sentences, and any prior constraints or context worth surfacing. '
            'Ask about repository URL only if it is not already in your context.'
        ),
    },
    '2': {
        'key':         '::THEORY',
        'label':       '::THEORY',
        'description': 'Architectural — design and conceptualization, no code',
        'system_frag': (
            'The Wizard wants to explore a design or architectural question. No code will '
            'be written in this session. Establish: the component or system under examination, '
            'its one-line purpose, any constraints already known, and what specific questions '
            'the Wizard wants to think through. Expansive dialogue is permitted in this state.'
        ),
    },
    '3': {
        'key':         '::LORE',
        'label':       '::LORE',
        'description': 'Narrative — cosmology, naming, world-building',
        'system_frag': (
            'The Wizard is entering a lore or narrative session. Token efficiency is suspended — '
            'depth and atmosphere are valued here. Establish: the subject (entity, system, '
            'cosmological concept, or naming task), any established canon that must be '
            'respected, and the desired output form (names list, lore entry, world-building '
            'dialogue, etc.).'
        ),
    },
    '4': {
        'key':         '::AUDIT',
        'label':       '::AUDIT',
        'description': 'Assessment — read-only file review, conflict mapping',
        'system_frag': (
            'The Wizard wants a read-only audit of their codebase. No changes will be made. '
            'Establish: which files or systems are in scope, what they are looking for '
            '(conflicts, dead code, architectural drift, redundancy, etc.), and the desired '
            'audit output form. Confirm that no patches or rewrites are in scope.'
        ),
    },
    '5': {
        'key':         '::BUILD',
        'label':       '::BUILD',
        'description': 'Implementation — active construction',
        'system_frag': (
            'The Wizard is beginning a build session. Establish: what exactly is being built '
            '(component name, file, or system), which files are in scope, whether live file '
            'fetches from the repository are needed, any hard constraints (do not touch X, '
            'must integrate with Y), and the desired delivery form (full rewrite, patch script, '
            'new file). Token discipline applies — only what is asked.'
        ),
    },
    '6': {
        'key':         '::REVIEW',
        'label':       '::REVIEW',
        'description': 'Validation — flagged items at a build seam',
        'system_frag': (
            'The Wizard is calling a review at a build seam. Establish: which component or '
            'feature was just completed, what flagged items have accumulated that need '
            'addressing, and whether any of them are immediate blockers versus items that '
            'can be deferred to a later seam.'
        ),
    },
}
