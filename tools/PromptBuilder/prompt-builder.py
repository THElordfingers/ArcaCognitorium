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



AEDIFICATORUM PROMPT BUILDER
Arca Cognitorium — Session Prompt Constructor
Version: 1.1

Guides the Wizard through constructing a well-formed Builder session prompt.
Run: python3 prompt_builder.py

Config stored at: ~/.arca/config.json
"""

import sys
import json
import os

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_DIR  = os.path.expanduser('~/.arca')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

# ── Palette (ANSI) ────────────────────────────────────────────────────────────
GOLD   = '\033[38;2;232;201;106m'
TEAL   = '\033[38;2;126;200;200m'
VIOLET = '\033[38;2;169;143;212m'
EMBER  = '\033[38;2;200;121;65m'
DIM    = '\033[38;2;140;123;92m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

def g(text):  return f'{GOLD}{text}{RESET}'
def t(text):  return f'{TEAL}{text}{RESET}'
def v(text):  return f'{VIOLET}{text}{RESET}'
def e(text):  return f'{EMBER}{text}{RESET}'
def d(text):  return f'{DIM}{text}{RESET}'
def b(text):  return f'{BOLD}{text}{RESET}'

# ── State Definitions ─────────────────────────────────────────────────────────
STATES = {
    '1': ('::INIT',   'Pre-flight — file fetch, scope confirm, state declaration'),
    '2': ('::THEORY', 'Architectural — design and conceptualization, no code'),
    '3': ('::LORE',   'Narrative — cosmology, naming, world-building'),
    '4': ('::AUDIT',  'Assessment — read-only file review, conflict mapping'),
    '5': ('::BUILD',  'Implementation — active construction'),
    '6': ('::REVIEW', 'Validation — flagged items at a build seam'),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def header():
    print()
    print(g('  ╔══════════════════════════════════════════════════╗'))
    print(g('  ║') + b(g('        AEDIFICATORUM PROMPT BUILDER              ')) + g('║'))
    print(g('  ║') + d('        Arca Cognitorium — v1.1                    ') + g('║'))
    print(g('  ╚══════════════════════════════════════════════════╝'))
    print()

def ask(prompt, default=None):
    hint = f' {d("[" + default + "]")}' if default else ''
    try:
        val = input(f'  {t("▸")} {prompt}{hint}: ').strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print(d('\n  Prompt construction cancelled.'))
        sys.exit(0)
    return val if val else default

def choose(prompt, options):
    print(f'\n  {g(prompt)}')
    for k, (short, desc) in options.items():
        print(f'    {e(k)}.  {t(short):<12} {d(desc)}')
    while True:
        val = ask('Select')
        if val in options:
            return options[val]
        print(f'  {d("  Enter a number from the list.")}')

def section(title):
    print()
    print(f'  {v("─" * 50)}')
    print(f'  {v(title.upper())}')
    print(f'  {v("─" * 50)}')

def yn(prompt):
    val = ask(f'{prompt} {d("(y/n)")}', 'n')
    return val.lower().startswith('y')

def multiline(prompt):
    print(f'  {t("▸")} {prompt}')
    print(f'  {d("  (Enter text. Blank line to finish.)")}')
    lines = []
    while True:
        try:
            line = input('    ')
        except (KeyboardInterrupt, EOFError):
            break
        if line == '':
            break
        lines.append(line)
    return '\n'.join(lines)

# ── Repo Config ───────────────────────────────────────────────────────────────
def get_repo_url(cfg):
    """Return stored repo URL, or ask and save it."""
    stored = cfg.get('repo_url')
    if stored:
        print(f'  {d("Repository:")} {t(stored)}')
        if not yn('Use this repository?'):
            stored = None

    if not stored:
        stored = ask(
            'Repository base URL',
            'https://raw.githubusercontent.com/lordfingers/ArcaCognitorium/main/'
        )
        cfg['repo_url'] = stored
        save_config(cfg)
        print(f'  {t("✓ Saved to ~/.arca/config.json")}')

    return stored

def manage_config(cfg):
    """Config management sub-menu."""
    section('Repository Configuration')
    current = cfg.get('repo_url', d('(not set)'))
    print(f'\n  Current repo URL: {t(current)}')
    print()
    print(f'    {e("1")}.  Update repository URL')
    print(f'    {e("2")}.  Clear all config')
    print(f'    {e("3")}.  Back')
    choice = ask('Select', '3')
    if choice == '1':
        url = ask('New repository base URL')
        if url:
            cfg['repo_url'] = url
            save_config(cfg)
            print(f'  {t("✓ Saved.")}')
    elif choice == '2':
        if yn('Clear all saved config?'):
            save_config({})
            cfg.clear()
            print(f'  {t("✓ Config cleared.")}')

# ── Prompt Builders ───────────────────────────────────────────────────────────

def build_init(cfg):
    section('::INIT — Session Open with Live Files')
    repo = get_repo_url(cfg)
    files_raw = ask('Files in scope (comma-separated)')
    files = [f.strip() for f in files_raw.split(',')] if files_raw else []

    print(f'\n  {g("Secondary state after INIT:")}')
    _, secondary = choose('What are we doing this session?', STATES)
    secondary_short = secondary.split('—')[0].strip()

    focus = ask('Focus description (one or two sentences)')
    context = ''
    if yn('Add prior context or constraints?'):
        context = multiline('Context / notes')

    lines = ['::INIT', '']
    lines.append(f'Repository: {repo}')
    if files:
        lines.append(f'Files in scope: {", ".join(files)}')
    lines.append('')
    lines.append(f'Session state: {secondary_short}')
    if focus:
        lines.append(f'Focus: {focus}')
    if context:
        lines.append('')
        lines.append(context)
    return '\n'.join(lines)


def build_no_files(cfg):
    section('Session Open — No Live Files')
    state_short, _ = choose('Session state', STATES)
    focus = ask('Focus description')
    context = ''
    if yn('Add context or notes?'):
        context = multiline('Context / notes')

    lines = [state_short, '']
    if focus:
        lines.append(f'Focus: {focus}')
    if context:
        lines.append('')
        lines.append(context)
    return '\n'.join(lines)


def build_transition(cfg):
    section('Mid-Session State Transition')
    state_short, _ = choose('Transitioning to', STATES)
    reason = ask('Reason for transition (optional)')

    lines = [state_short]
    if reason:
        lines.append('')
        lines.append(reason)
    return '\n'.join(lines)


def build_theory_component(cfg):
    section('::THEORY — Recursive Component Exploration')
    name = ask('Component name')
    purpose = ask('One-line purpose')
    extra = ''
    if yn('Add extra context or constraints?'):
        extra = multiline('Additional context')

    lines = [
        '::THEORY',
        '',
        f'Component: {name}',
        f'Purpose: {purpose}',
        '',
        'Explore: implementation approach, usage logic, best practices, edge cases, redundancy check, modular conflicts.',
    ]
    if extra:
        lines.append('')
        lines.append(extra)
    return '\n'.join(lines)


def build_lore(cfg):
    section('::LORE — Narrative Session')
    subject = ask('Lore subject')
    desc = multiline('Open description (optional — blank to skip)')

    lines = ['::LORE', '', f'Subject: {subject}']
    if desc:
        lines.append('')
        lines.append(desc)
    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

PROMPT_TYPES = {
    '1': ('Session open — with live files',   build_init),
    '2': ('Session open — no live files',     build_no_files),
    '3': ('Mid-session state transition',     build_transition),
    '4': ('::THEORY component exploration',   build_theory_component),
    '5': ('::LORE narrative session',         build_lore),
    '6': ('Configure repository',             None),
}

def main():
    cfg = load_config()

    header()
    print(f'  {d("Construct a session prompt for The Builder.")}')
    if cfg.get('repo_url'):
        print(f'  {d("Repo:")} {t(cfg["repo_url"])}')
    print(f'  {d("Select a prompt type to begin.")}')

    print()
    for k, (label, _) in PROMPT_TYPES.items():
        print(f'    {e(k)}.  {label}')

    while True:
        choice = ask('\nPrompt type')
        if choice in PROMPT_TYPES:
            break
        print(f'  {d("  Enter a number from the list.")}')

    label, builder_fn = PROMPT_TYPES[choice]

    if builder_fn is None:
        manage_config(cfg)
        return

    prompt = builder_fn(cfg)

    print()
    print(f'  {v("═" * 50)}')
    print(f'  {g("GENERATED PROMPT")}')
    print(f'  {v("═" * 50)}')
    print()
    for line in prompt.split('\n'):
        print(f'  {line}')
    print()
    print(f'  {v("═" * 50)}')

    if yn('\nCopy to clipboard? (requires xclip)'):
        try:
            import subprocess
            subprocess.run(['xclip', '-selection', 'clipboard'], input=prompt.encode(), check=True)
            print(f'  {t("✓ Copied to clipboard.")}')
        except Exception:
            print(f'  {d("  xclip not available. Copy manually from above.")}')

    if yn('Save to file?'):
        filename = ask('Filename', 'prompt_output.txt')
        with open(filename, 'w') as f:
            f.write(prompt + '\n')
        print(f'  {t(f"✓ Saved to {filename}")}')

    print()
    print(d('  Ordo Discordia, Cosmos Inania'))
    print()


if __name__ == '__main__':
    main()

