from __future__ import annotations
from dataclasses import dataclass

@dataclass
class StatusState:
    model_id: str = '—'
    entity_name: str = 'LUMINARIOUS'
    entity_color: str = 'C9A84C'
    grimoire_active: bool = False
    chronicle_retrieved: bool = False
    tome_active: bool = False
    context_pct: int = 0
    distillation_count: int = 0
    project_name: str | None = None
    streaming: bool = False
    reflection_pending: bool = False


@dataclass
class BubbleMessage:
    """All data needed to render a single conversation bubble."""
    speaker_id: str          # 'wizard' | 'luminarious' | entity_id
    display_name: str        # 'WIZARD' | 'LUMINARIOUS' | 'THE CONTRARIAN'
    content: str             # Full message text (may be partial during streaming)
    model_id: str            # Model that handled this turn
    timestamp: str           # ISO format
    color_hex: str           # Speaker color — Wizard uses pale, others use entity color
    is_entity: bool = False  # True if an Entity interruption
    uninvited: bool = False  # True if Entity arrived without /summon
    token_count: int = 0
    chronicle_hit: bool = False  # True if Chronicle retrieval occurred this turn    
