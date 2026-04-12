# NUNTIUS — nuntius_registry.py
# v1.0
"""Consumer registry. Loaded from Configuus at startup. Immutable post-load."""

from __future__ import annotations

import logging
from typing import List

from .nuntius_config import ConsumerConfig, NuntiusConfig

logger = logging.getLogger(__name__)


class ConsumerRegistry:
    """Holds the immutable consumer list loaded from Configuus at startup."""

    def __init__(self, config: NuntiusConfig) -> None:
        """Populate consumer list from config. Immutable after construction."""
        self._consumers: List[ConsumerConfig] = []
        self._load(config)

    def _load(self, config: NuntiusConfig) -> None:
        """Parse config.consumers into internal list. Called once at init."""
        for entry in config.consumers:
            self._consumers.append(entry)
        logger.info(
            "ConsumerRegistry loaded %d consumer(s): %s",
            len(self._consumers),
            [c.name for c in self._consumers],
        )

    @property
    def consumers(self) -> List[ConsumerConfig]:
        """Return the immutable consumer list."""
        return list(self._consumers)
