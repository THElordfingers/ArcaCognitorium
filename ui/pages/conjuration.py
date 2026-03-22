#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/ui/pages/conjuration.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import yaml
from pathlib import Path
from textual.app import ComposeResult, App
from textual.screen import Screen
from textual.widgets import Label, Switch, Input, Select, Button, Static
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.message import Message


CONFIG_PATH = Path('config.yaml')


class ConjurationPage(Screen):
    """
    The Conjuration Chamber — all configuration controls.
    Sections mirror config.yaml structure with lore names.
    Changes write to config.yaml immediately on widget change event.
    Non-restart settings apply in real-time via app message passing.
    """

    class ConfigChanged(Message):
        """Posted to app when config.yaml is updated."""
        def __init__(self, section: str, key: str, value) -> None:
            super().__init__()
            self.section = section
            self.key = key
            self.value = value

    SECTIONS = [
        ('The Aether',      'api'),
        ('The Vessels',     'memory'),
        ('The Oracle',      'routing'),
        ('The Awakening',   'boot'),
        ('The Vestments',   'conjuration'),
        ('The Emanations',  'animations'),
        ('The Sanctum',     'layout'),
        ('The Conclave',    'entities'),
    ]

    def compose(self) -> ComposeResult:
        yield Label('◆  CONJURATION CHAMBER  ◆', id='conjure-title')
        with ScrollableContainer():
            for section_name, config_key in self.SECTIONS:
                yield self._build_section(section_name, config_key)
        yield Button('◀  BACK', id='conjure-back')

    def _build_section(self, name: str, key: str) -> Vertical:
        cfg = self._load_config()
        section_data = cfg.get(key, {})

        block = Vertical(classes='conjure-section')
        block.mount(Label(f'◆ {name.upper()}', classes='conjure-section-header'))

        if not isinstance(section_data, dict):
            block.mount(Static(f'({key}: no editable keys)', classes='conjure-empty'))
            return block

        for k, v in section_data.items():
            row = Horizontal(classes='conjure-row')
            row.mount(Label(k, classes='conjure-key'))

            widget_id = f'cfg__{key}__{k}'

            if isinstance(v, bool):
                widget = Switch(value=v, id=widget_id)
            elif isinstance(v, int):
                widget = Input(value=str(v), id=widget_id, type='integer')
            elif isinstance(v, list):
                widget = Input(value=', '.join(str(i) for i in v), id=widget_id)
            else:
                widget = Input(value=str(v) if v is not None else '', id=widget_id)

            row.mount(widget)
            block.mount(row)

        return block

    def on_switch_changed(self, event: Switch.Changed) -> None:
        widget_id = event.switch.id or ''
        if not widget_id.startswith('cfg__'):
            return
        _, section, key = widget_id.split('__', 2)
        self._write_config(section, key, event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        widget_id = event.input.id or ''
        if not widget_id.startswith('cfg__'):
            return
        _, section, key = widget_id.split('__', 2)

        # Coerce type to match original config value
        cfg = self._load_config()
        original = cfg.get(section, {}).get(key)
        value = event.value

        if isinstance(original, bool):
            value = value.lower() in ('true', '1', 'yes')
        elif isinstance(original, int):
            try:
                value = int(value)
            except ValueError:
                return
        elif isinstance(original, list):
            value = [v.strip() for v in value.split(',')]

        self._write_config(section, key, value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'conjure-back':
            self.app.pop_screen()

    def _write_config(self, section: str, key: str, value) -> None:
        try:
            cfg = self._load_config()
            if section not in cfg:
                cfg[section] = {}
            cfg[section][key] = value

            tmp = CONFIG_PATH.with_suffix('.yaml.tmp')
            tmp.write_text(yaml.dump(cfg, default_flow_style=False, allow_unicode=True))
            tmp.rename(CONFIG_PATH)

            self.post_message(self.ConfigChanged(section, key, value))
        except Exception as e:
            self.app.log.error(f'Conjuration write failed: {e}')

    def _load_config(self) -> dict:
        try:
            return yaml.safe_load(CONFIG_PATH.read_text()) or {}
        except Exception:
            return {}
