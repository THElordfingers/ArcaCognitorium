
from __future__ import annotations
from dataclasses import dataclass, replace
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style
from ui.state import StatusState


class StatusLayer(Widget):
    """
    Bottom status bar. Always visible. Never requires navigation.
    Renders the machine's current operational state as a single Rich Text row.
    App pushes state changes — widget never pulls.
    """

    DEFAULT_CSS = '''
    StatusLayer {
        height: 1;
        background: #0D0B0E;
        border-top: solid #2A2535;
        padding: 0 1;
    }
    '''

    state: reactive[StatusState] = reactive(StatusState, layout=True)

    def update_status(self, **kwargs) -> None:
        """Update one or more StatusState fields. Triggers reactive re-render.
        Usage: app.status_layer.update_status(model_id='gpt-4o', context_pct=72)
        """
        self.state = replace(self.state, **kwargs)

    def render(self) -> Text:
        """
        Assemble status bar as Rich Text row.
        Layout (left to right):
          ◆ [model_id]  │  [entity_name]  │  [memory_icons]  │  [context_bar]  │  [P_count]

        Implementation notes:
        - model_id: pale color (#D4C8A8)
        - entity_name: rendered in entity_color hex
        - 🔮 grimoire icon: gold if grimoire_active, mist if not
        - ✦ chronicle icon: shimmer amber if chronicle_retrieved, mist if not
        - context bar: 8 segments (▓ filled / ░ empty)
          · grey (#5A6070) below 75%
          · amber (#C68B2A) at 75–89%
          · copper (#AD6F3B) at 90%+
        - P[n] distillation count: shown only if distillation_count > 0
        - streaming: model indicator pulses (append '…' to model_id) while streaming=True
        """
        s = self.state
        t = Text()

        # Model indicator
        model_label = s.model_id + ('…' if s.streaming else '')
        t.append('◆ ', style=Style(color='#'+C_RULE))
        t.append(model_label, style=Style(color='#D4C8A8'))
        t.append('  │  ', style=Style(color='#2A2535'))

        # Entity name in its jewel tone
        t.append(s.entity_name, style=Style(color='#'+s.entity_color, bold=True))
        t.append('  │  ', style=Style(color='#2A2535'))

        # Memory indicators
        grimoire_color = '#C9A84C' if s.grimoire_active else '#5A6070'
        chronicle_color = '#C68B2A' if s.chronicle_retrieved else '#5A6070'
        t.append('🔮 ', style=Style(color=grimoire_color))
        t.append('✦ ', style=Style(color=chronicle_color))
        if s.tome_active:
            t.append('📜 ', style=Style(color='#AD6F3B'))
        t.append(' │  ', style=Style(color='#2A2535'))

        # Context fill bar
        filled = round(s.context_pct / 100 * 8)
        if s.context_pct >= 90:
            bar_color = '#AD6F3B'  # copper
        elif s.context_pct >= 75:
            bar_color = '#C68B2A'  # amber
        else:
            bar_color = '#5A6070'  # mist
        bar = '▓' * filled + '░' * (8 - filled)
        t.append(bar, style=Style(color=bar_color))
        t.append(f'  {s.context_pct}%', style=Style(color=bar_color))

        # Distillation count
        if s.distillation_count > 0:
            t.append(f'  │  P{s.distillation_count}', style=Style(color='#C68B2A'))

        # Project name
        if s.project_name:
            t.append(f'  │  {s.project_name}', style=Style(color='#5A6070'))

        return t

C_RULE = 'C9A84C'  # module-level constant for rule color
