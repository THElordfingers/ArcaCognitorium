# Auctoritas Spectralis — compositio.py
# v1.0.0
"""Signal orchestration for the Compositio pipeline.

Connects: ForgePanel → derivatio → scrutinium → auto_render → preview.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from .derivatio import derive_tokens, hex_to_oklab
from .scrutinium import (
    build_contrast_matrix, audit_passes,
    simulate_all_tokens,
)
from .constants import DEFAULT_BG, DEFAULT_FG


class Compositio(QObject):
    """Orchestrates the derivation/audit/render pipeline."""

    tokens_derived = pyqtSignal(dict, dict, list)     # tokens, oklab, clipped
    audit_complete = pyqtSignal(list, dict)            # matrix, audit_summary
    palette_ready = pyqtSignal(dict)                   # tokens (for auto_render)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_tokens = {}
        self._current_oklab = {}
        self._current_clipped = []
        self._current_matrix = []
        self._current_audit = {}
        self._current_bg = DEFAULT_BG
        self._current_fg = DEFAULT_FG
        self._vision_mode = ''

    def on_palette_changed(self, bg_hex: str, fg_hex: str):
        """Called when the Wizard adjusts BG or FG."""
        self._current_bg = bg_hex
        self._current_fg = fg_hex
        self._run_pipeline()

    def on_vision_mode_changed(self, mode: str):
        """Called when vision simulation mode changes."""
        self._vision_mode = mode
        self._run_pipeline()

    def _run_pipeline(self):
        """Full pipeline: derive → audit → emit."""
        result = derive_tokens(self._current_bg, self._current_fg)
        self._current_tokens = result['tokens']
        self._current_oklab = result['oklab']
        self._current_clipped = result['clipped']

        # Apply vision sim if active
        display_tokens = self._current_tokens
        if self._vision_mode:
            display_tokens = simulate_all_tokens(
                self._current_tokens, self._vision_mode
            )

        # Audit on the actual (non-simulated) tokens
        self._current_matrix = build_contrast_matrix(self._current_tokens)
        self._current_audit = audit_passes(self._current_matrix)

        # Emit signals
        self.tokens_derived.emit(
            display_tokens, self._current_oklab, self._current_clipped
        )
        self.audit_complete.emit(self._current_matrix, self._current_audit)
        self.palette_ready.emit(display_tokens)

    def get_current_tokens(self) -> dict:
        return dict(self._current_tokens)

    def get_current_oklab(self) -> dict:
        return dict(self._current_oklab)

    def get_current_audit(self) -> dict:
        return dict(self._current_audit)

    def get_current_matrix(self) -> list[dict]:
        return list(self._current_matrix)

    def get_base_pair(self) -> tuple[str, str]:
        return self._current_bg, self._current_fg

    def get_base_pair_dict(self) -> dict:
        bg_l, bg_a, bg_b = hex_to_oklab(self._current_bg)
        fg_l, fg_a, fg_b = hex_to_oklab(self._current_fg)
        return {
            'bg_hex': self._current_bg,
            'bg_oklab': {'l': bg_l, 'a': bg_a, 'b': bg_b},
            'fg_hex': self._current_fg,
            'fg_oklab': {'l': fg_l, 'a': fg_a, 'b': fg_b},
        }
