"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████  ██    ██ ████████ ██████  ██    ██ ████████ ▍
🮈 ██    ██ ██    ██    ██    ██   ██ ██    ██    ██    ▍
🮈 ██    ██ ██    ██    ██    ██████  ██    ██    ██    ▍
🮈 ██    ██ ██    ██    ██    ██      ██    ██    ██    ▍
🮈  ██████   ██████     ██    ██       ██████     ██    ▍
🮈                                                      ▍
🮈                                                      ▍
🮈                    Python Script                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

# =============================================================================
# INCITAMENTUM — output.py
# Version: 2.0
# Arca Cognitorium — Final prompt display and all exit paths.
# =============================================================================

import subprocess
from pathlib import Path
from renderer import Renderer


class OutputHandler:
    """Manages final prompt display and all exit paths."""

    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer

    def present(self, prompt: str) -> None:
        """Display the assembled prompt in the boxed panel."""
        self.renderer.prompt_box(prompt)

    def handle_exits(self, prompt: str) -> None:
        """
        Loop through exit options until Wizard chooses Done.
        [c] copy  [s] save  [Enter] done
        """
        while True:
            choice = self.renderer.exit_options()

            if choice == 'copy':
                if self.copy_to_clipboard(prompt):
                    self.renderer.print_ok('Copied to clipboard.')
                else:
                    self.renderer.print_error(
                        'xclip not available. Install with: sudo apt install xclip'
                    )

            elif choice == 'save':
                filename = self.renderer._ask('Save to filename', 'prompt_output.txt')
                if filename:
                    saved = self.save_to_file(prompt, filename)
                    if saved:
                        self.renderer.print_ok(f'Saved to {saved}')
                    else:
                        self.renderer.print_error(f'Could not write to {filename}. Check permissions.')

            else:  # done / Enter
                break

    def copy_to_clipboard(self, prompt: str) -> bool:
        """Attempt xclip copy. Returns True on success."""
        try:
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=prompt.encode(),
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def save_to_file(self, prompt: str, filename: str) -> Path | None:
        """Write prompt to filename. Returns resolved Path on success, None on failure."""
        try:
            path = Path(filename).expanduser().resolve()
            path.write_text(prompt + '\n', encoding='utf-8')
            return path
        except OSError:
            return None
