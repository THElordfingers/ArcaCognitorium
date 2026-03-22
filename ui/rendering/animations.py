from __future__ import annotations
import time, random, math
from textual.app import App
from textual.worker import get_current_worker

PERF_BUDGET_MS = 16.0   # ~60fps threshold. Exceed = layer disabled.
GLYPH_INTERVAL = 7.0    # seconds between glyph field rotations
TEMP_INTERVAL  = 31.0   # seconds per color temperature sine cycle
PULSE_INTERVAL = 23.0   # seconds per background pulse cycle

from dataclasses import dataclass, field

@dataclass
class AnimationConfig:
    master_enabled: bool = False
    glyph_drift: bool = True
    color_temp_drift: bool = True
    background_pulse: bool = True
    event_effects: bool = True
    glyph_pool: list = field(default_factory=lambda: ['◆', '☉', '◇', '⛨', '✦', '◈', '⬡', '⬢'])

class AnimationController:
    """
    Manages all ambient and event-triggered animation workers.
    Instantiated once in app.__init__(). Holds reference to app.

    Threading model:
    - All workers launched via self.app.run_worker(fn, thread=True)
    - CSS variable updates sent via self.app.call_from_thread()
    - Workers check get_current_worker().is_cancelled before each sleep
    - Circuit breaker: if any worker frame exceeds PERF_BUDGET_MS,
      that layer is disabled and logged. Other layers continue.
    """

    def __init__(self, app: App, config: AnimationConfig) -> None:
        """Store app reference and config. Do not start workers here."""
        self.app = app
        self.config = config
        self._disabled_layers: set[str] = set()
        self._active_workers: list = []

    def start_idle(self) -> None:
        """Launch all enabled idle animation workers. Call from app.on_mount()."""
        if not self.config.master_enabled:
            return
        if self.config.glyph_drift and 'glyph_drift' not in self._disabled_layers:
            self._active_workers.append(
                self.app.run_worker(self._glyph_drift_worker, thread=True)
            )
        if self.config.color_temp_drift and 'color_temp' not in self._disabled_layers:
            self._active_workers.append(
                self.app.run_worker(self._color_temp_worker, thread=True)
            )
        if self.config.background_pulse and 'bg_pulse' not in self._disabled_layers:
            self._active_workers.append(
                self.app.run_worker(self._bg_pulse_worker, thread=True)
            )

    def stop_idle(self) -> None:
        """Cancel all idle workers. Call when streaming begins to free resources."""
        for w in self._active_workers:
            w.cancel()
        self._active_workers.clear()

    def resume_idle(self) -> None:
        """Restart idle workers after streaming completes."""
        self.start_idle()

    def fire_event(self, event_type: str,
                   entity_color: str | None = None) -> None:
        """
        Trigger a one-shot event animation. Runs as short-lived worker.
        Does not cancel idle workers.

        Supported event_type values:
          'entity_interrupt'     — pulse in entity_color from bubble edge inward
          'distillation'         — amber ripple through history pane border
          'chronicle_retrieve'   — shimmer on chronicle status indicator (800ms)
          'grimoire_inject'      — gold glyph pulse in title bar (600ms)
          'tome_inject'          — copper pulse on left pane project header
          'reflection_generated' — purple shimmer in status layer background
        """
        if not self.config.event_effects:
            return
        self.app.run_worker(
            lambda: self._event_worker(event_type, entity_color),
            thread=True
        )

    # ── Idle Workers ────────────────────────────────────────────────────

    def _glyph_drift_worker(self) -> None:
        """
        Every GLYPH_INTERVAL seconds, pick a random glyph from config.glyph_pool
        and push it to a random position in the background glyph field via
        app.call_from_thread(app.update_glyph_field, position, glyph).
        """
        worker = get_current_worker()
        while not worker.is_cancelled:
            t0 = time.monotonic()
            glyph = random.choice(self.config.glyph_pool)
            position = random.randint(0, 63)
            self.app.call_from_thread(self.app.update_glyph_field, position, glyph)
            elapsed_ms = (time.monotonic() - t0) * 1000
            if not self._check_perf('glyph_drift', elapsed_ms):
                return
            time.sleep(GLYPH_INTERVAL)

    def _color_temp_worker(self) -> None:
        """
        Continuously modulate --background-amber CSS variable on a sine wave.
        Full cycle period: TEMP_INTERVAL seconds.
        Amplitude: ±8 on the amber channel (R value of background color).

        """
        worker = get_current_worker()
        t_start = time.monotonic()
        while not worker.is_cancelled:
            t0 = time.monotonic()
            elapsed = t0 - t_start
            r_val = 13 + int(8 * math.sin(2 * math.pi * elapsed / TEMP_INTERVAL))
            new_bg = f'#{r_val:02X}0B0E'
            self.app.call_from_thread(self.app.set_css_variable, '--app-bg', new_bg)
            elapsed_ms = (time.monotonic() - t0) * 1000
            if not self._check_perf('color_temp', elapsed_ms):
                return
            time.sleep(0.1)


    def _bg_pulse_worker(self) -> None:
        """
        Single slow luminosity pulse on PULSE_INTERVAL cycle.
        Implemented as brief opacity change on the background sigil element.

        """
    def _bg_pulse_worker(self) -> None:
        worker = get_current_worker()
        t_start = time.monotonic()
        while not worker.is_cancelled:
            elapsed = time.monotonic() - t_start
            pulse = 0.5 + 0.5 * math.sin(2 * math.pi * elapsed / PULSE_INTERVAL)
            opacity = 0.06 + 0.04 * pulse
            self.app.call_from_thread(self.app.set_sigil_opacity, opacity)
            time.sleep(0.5)

    # ── Event Workers ───────────────────────────────────────────────────

    def _event_worker(self, event_type: str,
                      entity_color: str | None) -> None:
        """
        Dispatch to the correct one-shot effect based on event_type.
        Each effect applies a CSS class, waits for effect duration, removes class.


        distillation:
          apply 'distillation-ripple' class to history pane → sleep 1.2s → remove


        grimoire_inject / tome_inject / reflection_generated:
          apply named CSS class to target widget → sleep 0.6s → remove
        """
    def _event_worker(self, event_type: str, entity_color: str | None) -> None:
        if event_type == 'entity_interrupt' and entity_color:
            css_class = f'entity-pulse-{entity_color}'
            self.app.call_from_thread(self.app.query_one('#middle').add_class, css_class)
            time.sleep(0.8)
            self.app.call_from_thread(self.app.query_one('#middle').remove_class, css_class)

        elif event_type == 'distillation':
            self.app.call_from_thread(self.app.query_one('#right').add_class, 'distillation-ripple')
            time.sleep(1.2)
            self.app.call_from_thread(self.app.query_one('#right').remove_class, 'distillation-ripple')

        elif event_type == 'chronicle_retrieve':
            self.app.call_from_thread(self.app.status_layer.update_status, chronicle_retrieved=True)
            time.sleep(0.8)
            self.app.call_from_thread(self.app.status_layer.update_status, chronicle_retrieved=False)

        elif event_type in ('grimoire_inject', 'tome_inject', 'reflection_generated'):
            self.app.call_from_thread(self.app.status_layer.add_class, event_type)
            time.sleep(0.6)
            self.app.call_from_thread(self.app.status_layer.remove_class, event_type)

    # ── Circuit Breaker ─────────────────────────────────────────────────

    def _check_perf(self, layer_name: str, elapsed_ms: float) -> bool:
        """
        If elapsed_ms > PERF_BUDGET_MS:
          - Add layer_name to self._disabled_layers
          - Log warning via app.call_from_thread(logger.warning, ...)
          - Return False (caller should exit worker loop)
        Return True if layer should continue.
        """
        if elapsed_ms > PERF_BUDGET_MS:
            self._disabled_layers.add(layer_name)
            self.app.call_from_thread(
                self.app.log.warning,
                f'Animation layer {layer_name} exceeded perf budget ({elapsed_ms:.1f}ms). Disabled.'
            )
            return False
        return True
