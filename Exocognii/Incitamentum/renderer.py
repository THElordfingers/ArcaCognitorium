"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████  ███████ ███    ██ ██████  ███████ ██████  ███████ ██████  ▍
🮈  ██   ██ ██      ████   ██ ██   ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ██████  █████   ██ ██  ██ ██   ██ █████   ██████  █████   ██████  ▍
🮈  ██   ██ ██      ██  ██ ██ ██   ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ██   ██ ███████ ██   ████ ██████  ███████ ██   ██ ███████ ██   ██ ▍
🮈                                                                    ▍
🮈                                                                    ▍
🮈                           Python Script                            ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

# =============================================================================
# INCITAMENTUM — renderer.py
# Version: 2.0
# Arca Cognitorium — All terminal output. No logic, only presentation.
# =============================================================================

import sys
import shutil
import textwrap
from typing import Iterator

# ── Palette ───────────────────────────────────────────────────────────────────
GOLD   = '\033[38;2;232;201;106m'
TEAL   = '\033[38;2;126;200;200m'
VIOLET = '\033[38;2;169;143;212m'
EMBER  = '\033[38;2;200;121;65m'
DIM    = '\033[38;2;140;123;92m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

WIDTH_MIN = 40


def _g(t: str) -> str: return f'{GOLD}{t}{RESET}'
def _t(t: str) -> str: return f'{TEAL}{t}{RESET}'
def _v(t: str) -> str: return f'{VIOLET}{t}{RESET}'
def _e(t: str) -> str: return f'{EMBER}{t}{RESET}'
def _d(t: str) -> str: return f'{DIM}{t}{RESET}'
def _b(t: str) -> str: return f'{BOLD}{t}{RESET}'


class Renderer:
    """All terminal output. Nothing else prints to stdout."""

    def __init__(self) -> None:
        self.width = max(shutil.get_terminal_size((100, 40)).columns, WIDTH_MIN)

    # ── Header ────────────────────────────────────────────────────────────────

    def header(self, cfg: dict) -> None:
        # 2-space indent + ║ + inner + ║  must equal self.width
        # so inner = self.width - 4  (2 indent + 2 border chars)
        inner = self.width - 4
        repo  = cfg.get('repo_url', '')
        print()
        print(_g('  ╔' + '═' * inner + '╗'))
        title = 'INCITAMENTUM  ·  PROMPT BUILDER'.center(inner)
        print(_g('  ║') + _b(_g(title)) + _g('║'))
        sub   = 'Arca Cognitorium  v2.0'.center(inner)
        print(_g('  ║') + _d(sub) + _g('║'))
        if repo:
            repo_display = repo[:inner].center(inner)
            print(_g('  ║') + _d(repo_display) + _g('║'))
        print(_g('  ╚' + '═' * inner + '╝'))
        print()

    # ── Menus ─────────────────────────────────────────────────────────────────

    def session_menu(self, sessions: dict) -> str:
        """
        Display session type menu plus config/history options.
        Returns the dict key ('1'–'6'), 'config', or 'history'.
        Loops until valid input.
        """
        valid = set(sessions.keys()) | {'7', '8'}
        print(f'  {_g("Select a session type:")}')
        print()
        for k, s in sessions.items():
            print(f'    {_e(k)}.  {_t(s["label"]):<14} {_d(s["description"])}')
        print()
        print(f'    {_e("7")}.  {_d("Configure        repository / preferences")}')
        print(f'    {_e("8")}.  {_d("History          browse recent prompts")}')
        print()
        while True:
            choice = self._ask('Select')
            if choice in valid:
                return choice if choice not in ('7', '8') else (
                    'config' if choice == '7' else 'history'
                )
            print(f'  {_d("  Enter a number from the list.")}')

    def config_menu(self, cfg: dict) -> str:
        """Display config sub-menu. Returns 'update', 'clear', or 'back'."""
        self.separator()
        print(f'\n  {_g("Repository Configuration")}')
        print(f'\n  Current: {_t(cfg.get("repo_url", "(not set)"))}')
        print(f'  Model:   {_t(cfg.get("model", "(not set)"))}')
        print()
        print(f'    {_e("1")}.  Update repository URL')
        print(f'    {_e("2")}.  Update model')
        print(f'    {_e("3")}.  Clear all config')
        print(f'    {_e("4")}.  Back')
        print()
        choice = self._ask('Select', '4')
        return {'1': 'update_repo', '2': 'update_model',
                '3': 'clear', '4': 'back'}.get(choice, 'back')

    # ── Interview ─────────────────────────────────────────────────────────────

    def interviewer_box_open(self, label: str = 'THE INTERVIEWER') -> None:
        w     = self.width - 4
        title = f'─ {label} '
        bar   = title + '─' * max(0, w - len(title))
        print()
        print(f'  {_v("┌" + bar + "┐")}')
        print(f'  {_v("│")}' + ' ' * w + _v('│'))

    def interviewer_box_close(self) -> None:
        w = self.width - 4
        print()
        print(f'  {_v("│")}' + ' ' * w + _v('│'))
        print(f'  {_v("└" + "─" * w + "┘")}')
        print()

    def stream_tokens(self, token_iter: Iterator[str]) -> str:
        """
        Consume token iterator, print each token immediately with soft wrapping.
        Returns full accumulated string.
        """
        accumulated: list[str] = []
        col = 0
        wrap_at = self.width - 6  # indent offset

        print(f'  {_v("│")}  ', end='', flush=True)

        for token in token_iter:
            accumulated.append(token)
            # Handle newlines in stream
            for char in token:
                if char == '\n':
                    print(f'\n  {_v("│")}  ', end='', flush=True)
                    col = 0
                else:
                    # Soft-wrap on spaces when approaching terminal edge
                    if char == ' ' and col >= wrap_at:
                        print(f'\n  {_v("│")}  ', end='', flush=True)
                        col = 0
                    print(char, end='', flush=True)
                    col += 1

        print()  # final newline after stream
        return ''.join(accumulated)

    def wizard_prompt(self) -> str:
        """Print the Wizard input prompt. Returns stripped input or empty string on EOF."""
        print()
        try:
            val = input(f'  {_t("▸")} {_b("You:")}  ')
            return val.strip()
        except EOFError:
            return ''

    # ── Output ────────────────────────────────────────────────────────────────

    def prompt_box(self, prompt: str) -> None:
        """Display the assembled prompt in a boxed panel."""
        w     = self.width - 4
        title = '─ ASSEMBLED PROMPT '
        bar   = title + '─' * max(0, w - len(title))
        print()
        print(f'  {_g("┌" + bar + "┐")}')
        print(f'  {_g("│")}')
        for line in prompt.splitlines():
            # Wrap long lines
            if len(line) > w - 2:
                wrapped = textwrap.wrap(line, width=w - 2) or ['']
                for wl in wrapped:
                    print(f'  {_g("│")}  {wl}')
            else:
                print(f'  {_g("│")}  {line}')
        print(f'  {_g("│")}')
        print(f'  {_g("└" + "─" * w + "┘")}')
        print()

    def exit_options(self) -> str:
        """
        Display post-prompt exit options. Returns 'copy', 'save', or 'done'.
        """
        print(
            f'  {_d("[c]")} {_t("Copy to clipboard")}   '
            f'{_d("[s]")} {_t("Save to file")}   '
            f'{_d("[Enter]")} {_t("Done")}'
        )
        print()
        try:
            val = input(f'  {_t("▸")} ').strip().lower()
        except EOFError:
            return 'done'
        if val == 'c':
            return 'copy'
        if val == 's':
            return 'save'
        return 'done'

    def history_display(self, history: list[dict]) -> None:
        """Display history entries in reverse chronological order."""
        self.separator()
        print(f'\n  {_g("Recent Prompts")}\n')
        if not history:
            print(f'  {_d("  No history yet.")}')
            print()
            return
        for i, entry in enumerate(reversed(history[-20:]), 1):
            ts    = entry.get('timestamp', '')[:16].replace('T', ' ')
            label = entry.get('session_label', '?')
            stat  = entry.get('status', 'complete')
            stat_col = _t(stat) if stat == 'complete' else _d(stat)
            print(f'  {_e(str(i).rjust(2))}.  {_t(label):<14} {_d(ts)}  {stat_col}')
            # Show first line of prompt as preview
            first_line = entry.get('prompt', '').splitlines()[0][:60] if entry.get('prompt') else ''
            if first_line:
                print(f'        {_d(first_line)}')
        print()

    # ── Utility ───────────────────────────────────────────────────────────────

    def separator(self) -> None:
        print(f'\n  {_d("─" * (self.width - 4))}\n')

    def print_error(self, msg: str) -> None:
        print(f'\n  {_e("✖")}  {msg}\n')

    def print_warning(self, msg: str) -> None:
        print(f'\n  {_d("⚠")}  {_d(msg)}\n')

    def print_ok(self, msg: str) -> None:
        print(f'  {_t("✓")}  {msg}')

    def print_cancelled(self) -> None:
        print(f'\n  {_d("Interview cancelled.")}')

    def print_outro(self) -> None:
        print()
        print(f'  {_d("Ordo Discordia, Cosmos Inania.")}')
        print()

    def _ask(self, prompt: str, default: str | None = None) -> str:
        """Internal input helper with optional default display."""
        hint = f' {_d("[" + default + "]")}' if default else ''
        try:
            val = input(f'  {_t("▸")} {prompt}{hint}: ').strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return default or ''
        return val if val else (default or '')
