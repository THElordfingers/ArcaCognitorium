"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████   █████  ████████ ██   ██        █████  ██    ██ ██████  ██ ████████ ▍
🮈  ██   ██ ██   ██    ██    ██   ██       ██   ██ ██    ██ ██   ██ ██    ██    ▍
🮈  ██████  ███████    ██    ███████ █████ ███████ ██    ██ ██   ██ ██    ██    ▍
🮈  ██      ██   ██    ██    ██   ██       ██   ██ ██    ██ ██   ██ ██    ██    ▍
🮈  ██      ██   ██    ██    ██   ██       ██   ██  ██████  ██████  ██    ██    ▍
🮈                                                                              ▍
🮈                                                                              ▍
🮈                                Python Script                                 ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃


ARCA COGNITORIUM — Path Audit & Correction Script
Version: 1.0

Pass 1: Report all path issues found.
Pass 2: Confirm and apply corrections.

Usage:
    python3 path_audit.py           # report only
    python3 path_audit.py --apply   # report then confirm and apply
    python3 path_audit.py --check   # dry run (alias for report only)
"""

import os
import re
import sys
import shutil
from pathlib import Path

# ── Palette ───────────────────────────────────────────────────────────────────
GOLD   = '\033[38;2;232;201;106m'
TEAL   = '\033[38;2;126;200;200m'
VIOLET = '\033[38;2;169;143;212m'
EMBER  = '\033[38;2;200;121;65m'
DIM    = '\033[38;2;140;123;92m'
RED    = '\033[38;2;200;80;80m'
GREEN  = '\033[38;2;100;200;120m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

def g(x): return f'{GOLD}{x}{RESET}'
def t(x): return f'{TEAL}{x}{RESET}'
def v(x): return f'{VIOLET}{x}{RESET}'
def e(x): return f'{EMBER}{x}{RESET}'
def d(x): return f'{DIM}{x}{RESET}'
def r(x): return f'{RED}{x}{RESET}'
def gr(x): return f'{GREEN}{x}{RESET}'
def b(x): return f'{BOLD}{x}{RESET}'

# ── Config ────────────────────────────────────────────────────────────────────
HOME         = str(Path.home())
PROJECT_ROOT = os.path.join(HOME, 'ArcaCognitorium')
TOOLS_ROOT   = os.path.join(PROJECT_ROOT, 'tools')
MACHINAE_ROOT = os.path.join(PROJECT_ROOT, 'machinae')

TOOLS = ['Dolium', 'Mythotex', 'Oculus', 'PromptBuilder', 'Vigilarum']

# Tools: old path patterns → new path
TOOL_REPLACEMENTS = []
for tool in TOOLS:
    old_tilde  = f'~/{tool}/'
    old_abs    = f'{HOME}/{tool}/'
    new_tilde  = f'~/ArcaCognitorium/tools/{tool}/'
    new_abs    = os.path.join(TOOLS_ROOT, tool) + '/'
    TOOL_REPLACEMENTS.append((old_tilde, new_tilde))
    TOOL_REPLACEMENTS.append((old_abs,   new_abs))

# Machinae: repo-internal .arca directory reference → home-level .arca
# Matches things like:
#   Path.home() / "ArcaCognitorium/.arca"
#   "ArcaCognitorium/.arca"
MACHINAE_CONFIG_PATTERN = re.compile(
    r'"ArcaCognitorium/\.arca"'
)
MACHINAE_CONFIG_REPLACEMENT = '".arca"'

MACHINAE_FILES = [
    'machina_circadiana.py',
    'machina_horologica.py',
    'machina_meteorologica.py',
    'machina_solaris.py',
    'machina_tidalis.py',
]

# ── Core ──────────────────────────────────────────────────────────────────────

class Finding:
    def __init__(self, filepath, lineno, original, replacement, match_text):
        self.filepath    = filepath
        self.lineno      = lineno
        self.original    = original
        self.replacement = replacement
        self.match_text  = match_text

    def display(self):
        rel = os.path.relpath(self.filepath, PROJECT_ROOT)
        print(f'  {t(rel)} {d("line")} {e(str(self.lineno))}')
        print(f'    {r("─")} {d(self.original.strip())}')
        print(f'    {gr("+")} {d(self.replacement.strip())}')
        print()


def audit_tools():
    findings = []
    for tool in TOOLS:
        tool_dir = os.path.join(TOOLS_ROOT, tool)
        if not os.path.isdir(tool_dir):
            print(f'  {d("  (skipping")} {e(tool)} {d("— directory not found)")}')
            continue
        for root, _, files in os.walk(tool_dir):
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                except Exception:
                    continue
                for i, line in enumerate(lines, 1):
                    for old, new in TOOL_REPLACEMENTS:
                        if old in line:
                            replacement_line = line.replace(old, new)
                            findings.append(Finding(fpath, i, line, replacement_line, old))
    return findings


def audit_machinae():
    findings = []
    for fname in MACHINAE_FILES:
        fpath = os.path.join(MACHINAE_ROOT, fname)
        if not os.path.isfile(fpath):
            print(f'  {d("  (skipping")} {e(fname)} {d("— file not found)")}')
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            match = MACHINAE_CONFIG_PATTERN.search(line)
            if match:
                matched_text = match.group(0)
                replacement_line = line[:match.start()] + MACHINAE_CONFIG_REPLACEMENT + line[match.end():]
                findings.append(Finding(fpath, i, line, replacement_line, matched_text))
    return findings


def apply_findings(findings):
    # Group by file
    by_file = {}
    for f in findings:
        by_file.setdefault(f.filepath, []).append(f)

    for fpath, file_findings in by_file.items():
        # Backup
        backup = fpath + '.bak'
        shutil.copy2(fpath, backup)

        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Apply by line number (1-indexed), sorted descending to preserve indices
        changes = {ff.lineno: ff.replacement for ff in file_findings}
        for lineno in sorted(changes.keys()):
            lines[lineno - 1] = changes[lineno]

        with open(fpath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        rel = os.path.relpath(fpath, PROJECT_ROOT)
        print(f'  {gr("✓")} {t(rel)} {d("— backup at")} {d(os.path.basename(backup))}')


# ── Main ──────────────────────────────────────────────────────────────────────

def header():
    print()
    print(g('  ╔══════════════════════════════════════════════════╗'))
    print(g('  ║') + b(g('     ARCA COGNITORIUM — PATH AUDIT v1.0           ')) + g('║'))
    print(g('  ╚══════════════════════════════════════════════════╝'))
    print()

def main():
    apply_mode = '--apply' in sys.argv

    header()

    # ── Tools audit ──
    print(v('  ── TOOLS PATH AUDIT (' + TOOLS_ROOT + ')'))
    print()
    tool_findings = audit_tools()

    if not tool_findings:
        print(f'  {gr("✓")} No stale tool paths found.\n')
    else:
        print(f'  {e(str(len(tool_findings)))} finding(s):\n')
        for f in tool_findings:
            f.display()

    # ── Machinae audit ──
    print(v('  ── MACHINAE CONFIG AUDIT (' + MACHINAE_ROOT + ')'))
    print()
    machinae_findings = audit_machinae()

    if not machinae_findings:
        print(f'  {gr("✓")} No stale config paths found.\n')
    else:
        print(f'  {e(str(len(machinae_findings)))} finding(s):\n')
        for f in machinae_findings:
            f.display()

    all_findings = tool_findings + machinae_findings

    if not all_findings:
        print(g('  All paths clean.'))
        print()
        return

    # ── Apply round ──
    if not apply_mode:
        print(d('  Run with --apply to apply corrections.'))
        print()
        return

    print(v('  ── APPLY CORRECTIONS'))
    print()
    try:
        confirm = input(f'  {GOLD}▸{RESET} Apply {e(str(len(all_findings)))} correction(s)? {DIM}(y/n){RESET}: ').strip().lower()
    except (KeyboardInterrupt, EOFError):
        print(f'\n  {d("Cancelled.")}')
        return

    if not confirm.startswith('y'):
        print(f'  {d("Aborted. No changes made.")}')
        print()
        return

    print()
    apply_findings(all_findings)
    print()
    print(gr('  ✓ Corrections applied. Backups written alongside originals.'))
    print(d('  Remove .bak files once you have verified the changes.'))
    print()


if __name__ == '__main__':
    main()
