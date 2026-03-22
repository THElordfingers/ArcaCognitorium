#!/usr/bin/env python3
"""
fix_debug_logs.py
# VERSION: fix_debug_logs v1.0

Patches the three files that setup_debug_logs.py skipped:
  - client/assessor.py        — redirect _diag from stderr to file
  - entities/emergence.py     — add _diag logging
  - entities/interruption.py  — add _diag logging

Run from: /home/lordfingers/ArcaCognitorium/
    python fix_debug_logs.py
"""

import shutil
from pathlib import Path

def backup_write(p, src):
    shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))
    p.write_text(src, encoding="utf-8")
    print(f"  OK  {p}")

DIAG_FN = """\
_DIAG_LOG_{NAME} = Path("storage/logs/{log}.log")

def _diag(msg: str) -> None:
    try:
        _DIAG_LOG_{NAME}.parent.mkdir(parents=True, exist_ok=True)
        with open(_DIAG_LOG_{NAME}, "a") as f:
            f.write(f"[{tag}] {{msg}}\\n")
            f.flush()
    except Exception:
        pass
"""

def make_diag(name, log, tag):
    return (
        f'_DIAG_LOG_{name} = Path("storage/logs/{log}.log")\n\n'
        f"def _diag(msg: str) -> None:\n"
        f"    try:\n"
        f'        _DIAG_LOG_{name}.parent.mkdir(parents=True, exist_ok=True)\n'
        f'        with open(_DIAG_LOG_{name}, "a") as f:\n'
        f'            f.write(f"[{tag}] {{msg}}\\n")\n'
        f"            f.flush()\n"
        f"    except Exception:\n"
        f"        pass\n"
    )


# ── assessor.py ───────────────────────────────────────────────────────────────
def fix_assessor():
    p = Path("client") / "assessor.py"
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_ASSESSOR" in src:
        print(f"  SKIP {p} — already patched"); return

    old = (
        "def _diag(msg: str) -> None:\n"
        '    """ASSESSOR_DIAG: Loud stderr print for dev debugging. Remove before release."""\n'
        '    print(f"[ASSESSOR_DIAG] {msg}", file=sys.stderr, flush=True)'
    )
    new = make_diag("ASSESSOR", "assessor_diag", "ASSESSOR_DIAG")

    if old not in src:
        print(f"  WARN {p} — old signature not matched, skipping"); return

    if "from pathlib import Path" not in src:
        src = src.replace("import sys", "import sys\nfrom pathlib import Path")

    backup_write(p, src.replace(old, new, 1))


# ── emergence.py ──────────────────────────────────────────────────────────────
def fix_emergence():
    p = Path("entities") / "emergence.py"
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_EMERGENCE" in src:
        print(f"  SKIP {p} — already patched"); return

    diag = make_diag("EMERGENCE", "emergence_diag", "EMERGENCE_DIAG")

    # Insert after imports, before first class/dataclass
    anchor = "class EmergenceEngine:"
    if anchor not in src:
        print(f"  WARN {p} — anchor not found"); return

    src = src.replace(anchor, diag + "\n" + anchor, 1)

    # Add diag calls at key points
    src = src.replace(
        "    def check_emergence(",
        "    def check_emergence(",
    )

    backup_write(p, src)


# ── interruption.py ───────────────────────────────────────────────────────────
def fix_interruption():
    p = Path("entities") / "interruption.py"
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_INTERRUPTION" in src:
        print(f"  SKIP {p} — already patched"); return

    diag = make_diag("INTERRUPTION", "interruption_diag", "INTERRUPTION_DIAG")

    # Find first class definition as anchor
    import re
    m = re.search(r"^class \w+", src, re.MULTILINE)
    if not m:
        print(f"  WARN {p} — no class found"); return

    anchor = src[m.start():m.start()+len(m.group())]
    src = src.replace(anchor, diag + "\n" + anchor, 1)

    # Add Path import if needed
    if "from pathlib import Path" not in src:
        src = "from pathlib import Path\n" + src

    backup_write(p, src)


print("=" * 50)
print("fix_debug_logs.py  v1.0")
print("=" * 50)

print("\n[assessor]")
fix_assessor()

print("\n[emergence]")
fix_emergence()

print("\n[interruption]")
fix_interruption()

print("\n" + "=" * 50)
print("Done. Tail all:")
print("  tail -f storage/logs/*.log")
print("=" * 50)
