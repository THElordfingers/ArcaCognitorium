"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████  ██████   ██████  ███    ███ ██████  ████████    ██████  ██    ██ ██ ██      ██████  ███████ ██████  ▍
🮈  ██   ██ ██   ██ ██    ██ ████  ████ ██   ██    ██       ██   ██ ██    ██ ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ██████  ██████  ██    ██ ██ ████ ██ ██████     ██ █████ ██████  ██    ██ ██ ██      ██   ██ █████   ██████  ▍
🮈  ██      ██   ██ ██    ██ ██  ██  ██ ██         ██       ██   ██ ██    ██ ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ██      ██   ██  ██████  ██      ██ ██         ██       ██████   ██████  ██ ███████ ██████  ███████ ██   ██ ▍
🮈                                                                                                              ▍
🮈                                                                                                              ▍
🮈                                                Python Script                                                 ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

# =============================================================================
# INCITAMENTUM — prompt_builder.py
# Version: 2.0
# Arca Cognitorium — Entry point. Main loop, menu dispatch, config, history.
#
# Run: python3 prompt_builder.py
# Requires: CLAUDE_API_KEY env var
# Config:   ~/.arca/config.json
# History:  ~/.arca/history.json
# =============================================================================

import sys
import os

from config        import load_config, save_config, append_history, load_history, make_history_entry
from renderer      import Renderer
from interviewer   import Interviewer
from output        import OutputHandler
from session_types import SESSIONS


# ── API key guard ─────────────────────────────────────────────────────────────

def _check_api_key(renderer: Renderer) -> bool:
    """Warn and return False if CLAUDE_API_KEY is not set."""
    if not os.environ.get('CLAUDE_API_KEY'):
        renderer.print_error(
            'CLAUDE_API_KEY is not set. Export it before running:\n'
            '  export CLAUDE_API_KEY=your_key_here'
        )
        return False
    return True


# ── Config sub-menu ───────────────────────────────────────────────────────────

def handle_config(cfg: dict, renderer: Renderer) -> None:
    """Config sub-menu — update repo URL, model, or clear config."""
    while True:
        action = renderer.config_menu(cfg)

        if action == 'update_repo':
            url = renderer._ask(
                'New repository base URL',
                cfg.get('repo_url', ''),
            )
            if url:
                cfg['repo_url'] = url
                if save_config(cfg):
                    renderer.print_ok('Saved.')
                else:
                    renderer.print_error('Could not write to ~/.arca/config.json.')

        elif action == 'update_model':
            model = renderer._ask('Model identifier', cfg.get('model', 'claude-sonnet-4-5'))
            if model:
                cfg['model'] = model
                if save_config(cfg):
                    renderer.print_ok('Saved.')
                else:
                    renderer.print_error('Could not write config.')

        elif action == 'clear':
            confirm = renderer._ask('Clear all config? (yes/no)', 'no')
            if confirm.lower() in ('yes', 'y'):
                save_config({})
                cfg.clear()
                cfg.update(load_config())
                renderer.print_ok('Config cleared. Defaults restored.')

        else:  # back
            break


# ── History sub-menu ──────────────────────────────────────────────────────────

def handle_history(renderer: Renderer) -> None:
    """Display history and optionally show a full entry."""
    history = load_history()
    renderer.history_display(history)

    if not history:
        return

    choice = renderer._ask(
        'Enter entry number to view prompt, or Enter to go back',
        '',
    )
    if not choice:
        return

    try:
        idx = int(choice) - 1
        # history_display shows reversed list, so mirror that
        entry = list(reversed(history[-20:]))[idx]
        renderer.prompt_box(entry.get('prompt', '(empty)'))
        output = OutputHandler(renderer=renderer)
        output.handle_exits(entry.get('prompt', ''))
    except (ValueError, IndexError):
        renderer.print_warning('Invalid selection.')


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    cfg      = load_config()
    renderer = Renderer()

    renderer.header(cfg)

    if not _check_api_key(renderer):
        sys.exit(1)

    try:
        choice = renderer.session_menu(SESSIONS)
    except KeyboardInterrupt:
        print()
        renderer.print_outro()
        return

    if choice == 'config':
        handle_config(cfg, renderer)
        renderer.print_outro()
        return

    if choice == 'history':
        handle_history(renderer)
        renderer.print_outro()
        return

    # ── Interview ─────────────────────────────────────────────────────────────
    session_type = SESSIONS[choice]
    interviewer  = Interviewer(
        session_type = session_type,
        config       = cfg,
        renderer     = renderer,
    )

    prompt = interviewer.run()

    if not prompt:
        # Cancelled or failed — save partial transcript to history if it exists
        partial = interviewer.partial_transcript
        if partial:
            partial_text = '\n'.join(
                f'[{t["role"].upper()}] {t["content"]}' for t in partial
            )
            append_history(make_history_entry(
                session_key   = session_type['key'],
                session_label = session_type['label'],
                prompt        = partial_text,
                status        = 'abandoned',
            ))
        renderer.print_outro()
        return

    # ── Output ────────────────────────────────────────────────────────────────
    output = OutputHandler(renderer=renderer)
    output.present(prompt)
    output.handle_exits(prompt)

    append_history(make_history_entry(
        session_key   = session_type['key'],
        session_label = session_type['label'],
        prompt        = prompt,
        status        = 'complete',
    ))

    renderer.separator()
    renderer.print_outro()


if __name__ == '__main__':
    main()
