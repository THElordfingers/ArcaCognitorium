#!/usr/bin/env python3
"""
setup_debug_logs.py
# VERSION: setup_debug_logs v1.0

Sets up file-based debug logging for all background systems.
Each system writes to its own log in storage/logs/.

Logs created:
  storage/logs/assessor_diag.log    — Assessor observation cycles
  storage/logs/archivist_diag.log   — Archivist chronicle cycles
  storage/logs/emergence_diag.log   — Entity emergence signals
  storage/logs/interruption_diag.log — Entity interruption checks
  storage/logs/router_diag.log      — Model routing decisions
  storage/logs/council_diag.log     — Council state changes

Tail any of them in a separate terminal:
  tail -f storage/logs/assessor_diag.log
  tail -f storage/logs/archivist_diag.log
  tail -f storage/logs/emergence_diag.log
  tail -f storage/logs/interruption_diag.log
  tail -f storage/logs/router_diag.log
  tail -f storage/logs/council_diag.log

Or tail all at once:
  tail -f storage/logs/*.log

Run from: /home/lordfingers/ArcaCognitorium/
    python setup_debug_logs.py
"""

import shutil, re
from pathlib import Path

LOGS = Path("storage/logs")


def backup_write(p: Path, src: str) -> None:
    bak = p.with_suffix(p.suffix + ".bak")
    shutil.copy2(p, bak)
    p.write_text(src, encoding="utf-8")
    print(f"  OK  {p}")


def add_diag(src: str, log_name: str, after_line: str) -> str:
    """Add a _diag function writing to a named log file, after a given line."""
    diag_fn = (
        f"\n_DIAG_LOG_{log_name.upper()} = Path(\"storage/logs/{log_name}.log\")\n\n"
        f"def _diag(msg: str) -> None:\n"
        f"    try:\n"
        f"        _DIAG_LOG_{log_name.upper()}.parent.mkdir(parents=True, exist_ok=True)\n"
        f"        with open(_DIAG_LOG_{log_name.upper()}, \"a\") as f:\n"
        f"            f.write(f\"[{log_name.upper()}] {{msg}}\\n\")\n"
        f"            f.flush()\n"
        f"    except Exception:\n"
        f"        pass\n"
    )
    if after_line in src and "_DIAG_LOG" not in src:
        return src.replace(after_line, after_line + diag_fn, 1)
    return src


# ── assessor_chronicler.py ────────────────────────────────────────────────────

def patch_assessor():
    p = Path("client") / "assessor.py"
    if not p.exists():
        print(f"  NOT FOUND: {p}"); return
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_ASSESSOR" in src:
        print(f"  SKIP {p} — already patched"); return

    # Replace existing stderr _diag with file-based one
    old = (
        "def _diag(msg: str) -> None:\n"
        "    \"\"\"ASSESSOR_DIAG: Loud stderr print for dev debugging. Remove before release.\"\"\"\n"
        "    print(f\"[ASSESSOR_DIAG] {msg}\", file=sys.stderr, flush=True)"
    )
    new = (
        "_DIAG_LOG_ASSESSOR = Path(\"storage/logs/assessor_diag.log\")\n\n"
        "def _diag(msg: str) -> None:\n"
        "    \"\"\"ASSESSOR_DIAG: File logging for dev debugging.\"\"\"\n"
        "    try:\n"
        "        _DIAG_LOG_ASSESSOR.parent.mkdir(parents=True, exist_ok=True)\n"
        "        with open(_DIAG_LOG_ASSESSOR, \"a\") as f:\n"
        "            f.write(f\"[ASSESSOR_DIAG] {msg}\\n\")\n"
        "            f.flush()\n"
        "    except Exception:\n"
        "        pass"
    )
    if old in src:
        if "from pathlib import Path" not in src:
            src = src.replace("import sys", "import sys\nfrom pathlib import Path")
        backup_write(p, src.replace(old, new, 1))
    else:
        print(f"  SKIP {p} — _diag signature changed, check manually")


# ── archivist_chronicler.py ───────────────────────────────────────────────────

def patch_archivist():
    p = Path("client") / "archivist_chronicler.py"
    if not p.exists():
        print(f"  NOT FOUND: {p}"); return
    src = p.read_text(encoding="utf-8")

    if "from pathlib import Path" not in src:
        src = src.replace("import json", "import json\nfrom pathlib import Path")

    anchor = "log = logging.getLogger(__name__)"
    if anchor not in src:
        print(f"  SKIP {p} — anchor not found"); return
    if "_DIAG_LOG_ARCHIVIST" in src:
        print(f"  SKIP {p} — already patched"); return

    diag_block = (
        "\n_DIAG_LOG_ARCHIVIST = Path(\"storage/logs/archivist_diag.log\")\n\n"
        "def _diag(msg: str) -> None:\n"
        "    try:\n"
        "        _DIAG_LOG_ARCHIVIST.parent.mkdir(parents=True, exist_ok=True)\n"
        "        with open(_DIAG_LOG_ARCHIVIST, \"a\") as f:\n"
        "            f.write(f\"[ARCHIVIST_DIAG] {msg}\\n\")\n"
        "            f.flush()\n"
        "    except Exception:\n"
        "        pass\n"
    )
    src = src.replace(anchor, anchor + diag_block, 1)

    # Inject _diag calls into tick()
    src = src.replace(
        "        self._turn_counter += 1\n\n"
        "        if self._interval <= 0",
        "        self._turn_counter += 1\n"
        "        _diag(f\"Tick {self._turn_counter} — interval={self._interval} — messages={len(thread_messages)}\")\n\n"
        "        if self._interval <= 0",
    )

    # Inject into _run_cycle
    src = src.replace(
        "        archivist = self._get_archivist()\n"
        "        messages = self._build_messages(thread_messages)",
        "        _diag(\"Firing archivist cycle...\")\n"
        "        archivist = self._get_archivist()\n"
        "        _diag(f\"Compiled: {archivist.display_name}\")\n"
        "        messages = self._build_messages(thread_messages)\n"
        "        _diag(f\"Messages: {len(messages)} items\")",
    )

    src = src.replace(
        "        raw_response = \"\".join(gen).strip()\n\n"
        "        entries = self._parse_response(raw_response)",
        "        raw_response = \"\".join(gen).strip()\n"
        "        _diag(f\"Response: {len(raw_response)} chars — {raw_response[:150]}\")\n\n"
        "        entries = self._parse_response(raw_response)",
    )

    src = src.replace(
        "        return ArchivistResult(written=written, fired=True)",
        "        _diag(f\"Done. Written: {written}\")\n"
        "        return ArchivistResult(written=written, fired=True)",
    )

    backup_write(p, src)


# ── emergence.py ──────────────────────────────────────────────────────────────

def patch_emergence():
    p = Path("entities") / "emergence.py"
    if not p.exists():
        print(f"  NOT FOUND: {p}"); return
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_EMERGENCE" in src:
        print(f"  SKIP {p} — already patched"); return

    if "from pathlib import Path" not in src:
        src = "from pathlib import Path\n" + src

    anchor = "import logging"
    if anchor not in src:
        print(f"  SKIP {p} — anchor not found"); return

    diag_block = (
        "\n_DIAG_LOG_EMERGENCE = Path(\"storage/logs/emergence_diag.log\")\n\n"
        "def _diag(msg: str) -> None:\n"
        "    try:\n"
        "        _DIAG_LOG_EMERGENCE.parent.mkdir(parents=True, exist_ok=True)\n"
        "        with open(_DIAG_LOG_EMERGENCE, \"a\") as f:\n"
        "            f.write(f\"[EMERGENCE_DIAG] {msg}\\n\")\n"
        "            f.flush()\n"
        "    except Exception:\n"
        "        pass\n"
    )
    src = src.replace(anchor, anchor + diag_block, 1)
    backup_write(p, src)


# ── interruption.py ───────────────────────────────────────────────────────────

def patch_interruption():
    p = Path("entities") / "interruption.py"
    if not p.exists():
        print(f"  NOT FOUND: {p}"); return
    src = p.read_text(encoding="utf-8")
    if "_DIAG_LOG_INTERRUPTION" in src:
        print(f"  SKIP {p} — already patched"); return

    if "from pathlib import Path" not in src:
        src = "from pathlib import Path\n" + src

    anchor = "import logging"
    if anchor not in src:
        print(f"  SKIP {p} — anchor not found"); return

    diag_block = (
        "\n_DIAG_LOG_INTERRUPTION = Path(\"storage/logs/interruption_diag.log\")\n\n"
        "def _diag(msg: str) -> None:\n"
        "    try:\n"
        "        _DIAG_LOG_INTERRUPTION.parent.mkdir(parents=True, exist_ok=True)\n"
        "        with open(_DIAG_LOG_INTERRUPTION, \"a\") as f:\n"
        "            f.write(f\"[INTERRUPTION_DIAG] {msg}\\n\")\n"
        "            f.flush()\n"
        "    except Exception:\n"
        "        pass\n"
    )
    src = src.replace(anchor, anchor + diag_block, 1)
    backup_write(p, src)


# ── Create log dir and clear stale logs ───────────────────────────────────────

def setup_log_dir():
    LOGS.mkdir(parents=True, exist_ok=True)
    for name in ["assessor_diag", "archivist_diag", "emergence_diag",
                 "interruption_diag", "router_diag", "council_diag"]:
        f = LOGS / f"{name}.log"
        if not f.exists():
            f.touch()
    print(f"  OK  {LOGS}/ — log files ready")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("setup_debug_logs.py  v1.0")
    print("=" * 55)

    print("\n[log dir]")
    setup_log_dir()

    print("\n[assessor]")
    patch_assessor()

    print("\n[archivist]")
    patch_archivist()

    print("\n[emergence]")
    patch_emergence()

    print("\n[interruption]")
    patch_interruption()

    print("\n" + "=" * 55)
    print("Done. Tail all logs at once:")
    print("  tail -f storage/logs/*.log")
    print("\nOr individually:")
    print("  tail -f storage/logs/assessor_diag.log")
    print("  tail -f storage/logs/archivist_diag.log")
    print("  tail -f storage/logs/emergence_diag.log")
    print("  tail -f storage/logs/interruption_diag.log")
    print("=" * 55)


if __name__ == "__main__":
    main()
