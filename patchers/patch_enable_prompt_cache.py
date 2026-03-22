#!/usr/bin/env python3
"""
patch_enable_prompt_cache.py
─────────────────────────────────────────────────────────────────────────────
Enables Anthropic prompt caching in the ArcaCognitorium-local
claudebox.config.yaml. The canonical source at ~/Anthropic/Claudebox/
is left completely untouched.

Usage:
  python patch_enable_prompt_cache.py
─────────────────────────────────────────────────────────────────────────────
"""

import sys
import re
import shutil
from pathlib import Path
from datetime import datetime


TARGET = Path.home() / "ArcaCognitorium" / "claudebox" / "claudebox.config.yaml"


def patch(p: Path) -> None:
    if not p.exists():
        print(f"[ERROR] Not found: {p}")
        print("        Check that ClaudeBox is dropped into ~/ArcaCognitorium/ClaudeBox/")
        sys.exit(1)

    text = p.read_text(encoding="utf-8")

    match = re.search(r"^(\s*cache_control\s*:\s*)(false|true)", text, re.MULTILINE)
    if not match:
        print(f"[ERROR] Could not find 'cache_control:' key in {p}")
        print("        Has the file been modified from its original structure?")
        sys.exit(1)

    if match.group(2) == "true":
        print(f"[OK] Prompt caching already enabled in {p}. Nothing to do.")
        return

    backup = p.with_suffix(f".yaml.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(p, backup)
    print(f"[BACKUP]  {backup}")

    patched = text[:match.start(2)] + "true" + text[match.end(2):]
    p.write_text(patched, encoding="utf-8")

    print(f"[PATCHED] {p}")
    print()
    print("  system.cache_control: false  →  true")
    print()
    print("  Entity system prompts will be cached on first call.")
    print("  Subsequent turns within ~5 min cost ~10% of normal input token price.")
    print("  Restart the tower for the change to take effect.")


if __name__ == "__main__":
    print(f"[TARGET] {TARGET}")
    patch(TARGET)
