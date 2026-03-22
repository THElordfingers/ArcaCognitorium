#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / main.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

import os
import sys

from app import DoliumApp


def main() -> None:
    if not os.environ.get("CLAUDE_API_KEY"):
        print(
            "[dolium] Warning: CLAUDE_API_KEY not set. "
            "Conversation will use the stub — pipeline fully functional.",
            file=sys.stderr,
        )
    DoliumApp().run()


if __name__ == "__main__":
    main()
