#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/client/clipboard.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import base64
import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple


def _copy_osc52(text: str) -> None:
    data = base64.b64encode(text.encode("utf-8", errors="replace")).decode("ascii")
    seq = f"\x1b]52;c;{data}\x07"
    sys.stdout.write(seq)
    sys.stdout.flush()


def copy_to_clipboard(text: str) -> Tuple[bool, str]:
    """
    Best-effort clipboard copy.

    Order:
      1) wl-copy (Wayland)
      2) xclip (X11)
      3) xsel (X11)
      4) OSC52 (terminal clipboard escape)

    Returns: (ok, method_or_error)
    """
    text = text or ""

    # Wayland
    if shutil.which("wl-copy"):
        try:
            subprocess.run(
                ["wl-copy"],
                input=text.encode("utf-8", errors="replace"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, "wl-copy"
        except Exception as e:
            return False, f"wl-copy failed: {e}"

    # X11
    if shutil.which("xclip"):
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-in"],
                input=text.encode("utf-8", errors="replace"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, "xclip"
        except Exception as e:
            return False, f"xclip failed: {e}"

    if shutil.which("xsel"):
        try:
            subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text.encode("utf-8", errors="replace"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, "xsel"
        except Exception as e:
            return False, f"xsel failed: {e}"

    # OSC52 fallback (may be blocked by terminal config/policy)
    try:
        _copy_osc52(text)
        return True, "osc52"
    except Exception as e:
        return False, f"osc52 failed: {e}"
