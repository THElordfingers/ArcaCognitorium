# ─────────────────────────────────────────────────────────────────────────────
# mundana_channels.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
Canonical channel manifest for the Mundana State Bus.

All channel names are lowercase, dot-separated, following the pattern
mundana.{engine_or_domain}.  Unknown channel names raise BusChannelError.
New channels require Wizard ratification before being added here.
"""
from typing import Final


class BusChannelError(Exception):
    """Raised when an unknown channel name is used in publish or subscribe."""


# ── Canonical channel manifest ────────────────────────────────────────────────
CHANNELS: Final[dict[str, str]] = {
    "mundana.caelestis":      "CAELESTIS celestial engine tick",
    "mundana.resolver":       "Celestial Resolver behavioural output",
    "mundana.circadiana":     "CIRCADIANA circadian phase",
    "mundana.horologica":     "HOROLOGICA system time tick",
    "mundana.meteorologica":  "METEOROLOGICA weather state",
    "mundana.solaris":        "SOLARIS solar data",
    "mundana.tidalis":        "TIDALIS tidal state",
    "mundana.lapsus":         "LAPSUS meta-engine drift state",
    "mundana.token_ledger":   "Token usage ledger (all apps)",
    "mundana.app_status":     "App heartbeat / status",
    "mundana.bus_control":    "Bus internal control (shutdown broadcast)",
}


def validate_channel(name: str) -> str:
    """Return name if valid, raise BusChannelError otherwise."""
    if name not in CHANNELS:
        raise BusChannelError(
            f"Channel '{name}' is not in the manifest. "
            f"Known channels: {list(CHANNELS)}"
        )
    return name
