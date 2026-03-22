#!/usr/bin/env python3
"""
MACHINA CIRCADIANA
════════════════════════════════════════════════════════════════════════════════
Arca Cognitorium — Circadian Rhythm Engine

Models circadian rhythms for each Council entity and a generic human baseline.
Each entity has a unique rhythm profile reflecting their personality.
No external dependencies — pure math and a clock.

Usage:
    from machinae.machina_circadiana import MachinaCircadiana

    circ = MachinaCircadiana()
    circ.update()

    circ.entities["archivist"].position    # 0.0-1.0 current rhythm position
    circ.entities["archivist"].peak        # True if currently at or near peak
    circ.entities["archivist"].phase_name  # "rising" / "peak" / "falling" / "trough"
    circ.human.alertness                   # 0.0-1.0 generic human alertness
    circ.human.phase_name                  # "sleep" / "rising" / "alert" / "trough" / "evening"
    circ.conditions.most_active            # entity name currently at highest position
    circ.conditions.least_active           # entity name currently at lowest position
    circ.triggers.poll()                   # ["archivist_peak", "speculator_rising", ...]

Daemon mode:
    python3 MachinaCircadiana.py             # writes ~/ArcaCognitorium/.arca/circadian_state.json
    python3 MachinaCircadiana.py --watch     # live terminal display
    python3 MachinaCircadiana.py --once      # single write and exit

════════════════════════════════════════════════════════════════════════════════
ENTITY RHYTHM PROFILES
════════════════════════════════════════════════════════════════════════════════

Each entity has a custom circadian curve defined by one or more peaks across
the 24-hour cycle. Peaks are modeled as Gaussian curves summed together,
producing a smooth waveform unique to each entity's nature.

Archivist      — nocturnal scholar. Peaks 22:00-02:00. Secondary at 05:00.
Assessor       — liminal hours. Peaks at dawn (06:00) and dusk (18:00).
Contrarian     — counter-rhythmic. Peaks in the post-lunch trough (14:00).
Luminarious    — solar. Follows the sun. Peak at solar noon (13:00).
Minimalist     — flattest of all. Gentle morning preference (08:00). Consistent.
Pessimist      — late afternoon existential hour (16:00). Dark night spike (03:00).
Socratic       — morning inquiry (08:00) and late night recursion (01:00).
Speculator     — narrow midnight spike (00:00) and early afternoon (13:30).
Systems Thinker— long sustained working-day peak (09:00-16:00).
Toolsmith      — morning build hours (08:00-13:00). Disengages at evening.

════════════════════════════════════════════════════════════════════════════════
"""

import math
import json
import time
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

VERSION   = "1.0.0"
ARCA_DIR  = Path.home() / ".arca"
STATE_PATH = ARCA_DIR / "machina_circadiana.json"

# ─────────────────────────────────────────────────────────────────────────────
# CURVE MATH
# ─────────────────────────────────────────────────────────────────────────────

def gaussian(x: float, mu: float, sigma: float) -> float:
    """
    Standard Gaussian bell curve.
    x and mu in hours (0-24). Returns 0.0-1.0.
    Handles wrap-around for midnight-crossing peaks.
    """
    # Compute shortest distance on circular 24h clock
    diff = (x - mu + 12) % 24 - 12
    return math.exp(-0.5 * (diff / sigma) ** 2)


def build_curve(peaks: list, hour: float) -> float:
    """
    Build a composite rhythm value from multiple Gaussian peaks.
    peaks: list of (mu_hour, sigma, weight)
    Returns normalised 0.0-1.0.
    """
    total  = sum(weight * gaussian(hour, mu, sigma)
                 for mu, sigma, weight in peaks)
    max_possible = sum(weight for _, _, weight in peaks)
    return min(1.0, total / max_possible) if max_possible > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# ENTITY PROFILES
# ─────────────────────────────────────────────────────────────────────────────
#
# Format: list of (peak_hour, sigma, weight)
# sigma controls width — small = narrow spike, large = broad shoulder
# weight controls relative height of each peak
#
ENTITY_PROFILES = {
    "archivist": {
        "description": "Nocturnal scholar. Peaks late night, secondary at pre-dawn.",
        "peaks": [
            (23.0, 2.0, 1.0),   # Primary: late night
            ( 0.5, 1.5, 0.9),   # Midnight sustained
            ( 5.0, 1.2, 0.6),   # Pre-dawn secondary
        ],
        "baseline": 0.25,
    },
    "assessor": {
        "description": "Liminal hours. Peaks at dawn and dusk thresholds.",
        "peaks": [
            ( 6.0, 1.5, 1.0),   # Dawn
            (18.5, 1.5, 0.95),  # Dusk
            (12.0, 2.0, 0.4),   # Noon plateau (minor)
        ],
        "baseline": 0.30,
    },
    "contrarian": {
        "description": "Counter-rhythmic. Peaks when others trough.",
        "peaks": [
            (14.5, 1.8, 1.0),   # Post-lunch drag — contrarian's moment
            ( 3.5, 1.5, 0.7),   # Deep night counter-spike
            (20.0, 1.2, 0.5),   # Late evening disagreement hour
        ],
        "baseline": 0.40,       # Never fully quiet
    },
    "luminarious": {
        "description": "Solar. Genuinely follows the sun. Absent at night.",
        "peaks": [
            (13.0, 3.5, 1.0),   # Solar noon — broad, sustained
            (10.0, 2.0, 0.7),   # Morning rise
            (16.0, 2.0, 0.6),   # Afternoon hold
        ],
        "baseline": 0.10,       # Truly quiet at night
    },
    "minimalist": {
        "description": "Flattest rhythm. Gentle morning preference. Consistent.",
        "peaks": [
            ( 8.0, 3.0, 1.0),   # Morning clarity — broad, not dramatic
            (14.0, 4.0, 0.8),   # Sustained through day
        ],
        "baseline": 0.55,       # High floor — always somewhat present
    },
    "pessimist": {
        "description": "Late afternoon existential hour. Dark night spike.",
        "peaks": [
            (16.0, 2.0, 1.0),   # The 4pm dread
            ( 3.0, 1.2, 0.75),  # Dark night of the soul
            (10.0, 1.5, 0.4),   # Morning doubt (minor)
        ],
        "baseline": 0.25,
    },
    "socratic": {
        "description": "Morning inquiry and late night recursion. Two distinct peaks.",
        "peaks": [
            ( 8.0, 1.8, 1.0),   # Morning questions — probing, energetic
            ( 1.0, 1.5, 0.9),   # Late night recursion — deep, circular
            (11.0, 1.5, 0.5),   # Pre-lunch secondary
        ],
        "baseline": 0.25,
    },
    "speculator": {
        "description": "Irregular. Narrow spikes, low baseline. Hard to predict.",
        "peaks": [
            ( 0.0, 1.0, 1.0),   # Midnight — sharp spike
            (13.5, 1.2, 0.85),  # Early afternoon flash
            (22.0, 1.0, 0.6),   # Pre-midnight build
        ],
        "baseline": 0.15,       # Very low baseline — mostly quiet
    },
    "systems_thinker": {
        "description": "Long sustained working-day peak. Needs time to build models.",
        "peaks": [
            (12.0, 4.5, 1.0),   # Broad sustained centre of day
            ( 9.5, 2.0, 0.8),   # Morning ramp
            (15.5, 2.0, 0.75),  # Afternoon hold
        ],
        "baseline": 0.20,
    },
    "toolsmith": {
        "description": "Morning build hours. Disengages as evening approaches.",
        "peaks": [
            ( 9.0, 2.0, 1.0),   # Core build hour
            (11.5, 2.0, 0.85),  # Pre-lunch productive
            (14.0, 1.5, 0.5),   # Early afternoon fade
        ],
        "baseline": 0.15,
    },
}

# Generic human alertness curve (two-process model approximation)
HUMAN_PEAKS = [
    (10.0, 2.5, 1.0),   # Morning peak
    (21.0, 2.0, 0.8),   # Evening second wind
]
HUMAN_BASELINE = 0.20

# Phase thresholds
PEAK_THRESHOLD   = 0.75
TROUGH_THRESHOLD = 0.30

# ─────────────────────────────────────────────────────────────────────────────
# STATE OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class EntityRhythm:
    """
    Current circadian state of a single entity.
    position: 0.0 (trough) → 1.0 (peak)
    """
    def __init__(self, name: str):
        self.name        = name
        self.position    = 0.5
        self.position_1h = 0.5   # position one hour from now (trajectory)
        self.phase_name  = "rising"
        self.peak        = False
        self.trough      = False
        self.rising      = False
        self.falling     = False
        self.description = ENTITY_PROFILES[name]["description"]

    def update(self, hour: float):
        profile  = ENTITY_PROFILES[self.name]
        peaks    = profile["peaks"]
        baseline = profile["baseline"]

        raw  = build_curve(peaks, hour)
        raw1 = build_curve(peaks, (hour + 1.0) % 24)

        # Apply baseline floor
        self.position    = round(baseline + (1.0 - baseline) * raw,  4)
        self.position_1h = round(baseline + (1.0 - baseline) * raw1, 4)

        self.peak   = self.position >= PEAK_THRESHOLD
        self.trough = self.position <= TROUGH_THRESHOLD
        self.rising = self.position_1h > self.position + 0.02
        self.falling= self.position_1h < self.position - 0.02

        if   self.peak:    self.phase_name = "peak"
        elif self.trough:  self.phase_name = "trough"
        elif self.rising:  self.phase_name = "rising"
        elif self.falling: self.phase_name = "falling"
        else:              self.phase_name = "stable"

    def to_dict(self):
        return {
            "name":        self.name,
            "position":    self.position,
            "position_1h": self.position_1h,
            "phase_name":  self.phase_name,
            "peak":        self.peak,
            "trough":      self.trough,
            "rising":      self.rising,
            "falling":     self.falling,
            "description": self.description,
        }


class HumanRhythm:
    """
    Generic human circadian baseline.
    Does not model a specific individual — approximates typical alertness.
    Tower uses this to contextualise the session.
    """
    def __init__(self):
        self.alertness   = 0.5
        self.alertness_1h= 0.5
        self.phase_name  = "alert"
        self.sleep_likely= False
        self.peak        = False

    def update(self, hour: float):
        raw  = build_curve(HUMAN_PEAKS, hour)
        raw1 = build_curve(HUMAN_PEAKS, (hour + 1.0) % 24)
        self.alertness    = round(HUMAN_BASELINE + (1.0 - HUMAN_BASELINE) * raw,  4)
        self.alertness_1h = round(HUMAN_BASELINE + (1.0 - HUMAN_BASELINE) * raw1, 4)
        self.sleep_likely = hour >= 23.0 or hour <= 5.0
        self.peak         = self.alertness >= PEAK_THRESHOLD

        if   hour >= 23.0 or hour <= 5.5: self.phase_name = "sleep"
        elif hour <= 8.5:                  self.phase_name = "rising"
        elif self.alertness >= 0.65:       self.phase_name = "alert"
        elif hour >= 13.0 and hour <= 15.0:self.phase_name = "trough"
        else:                              self.phase_name = "evening"

    def to_dict(self):
        return {
            "alertness":    self.alertness,
            "alertness_1h": self.alertness_1h,
            "phase_name":   self.phase_name,
            "sleep_likely": self.sleep_likely,
            "peak":         self.peak,
        }


class CircadianConditions:
    """Derived conditions across all entities."""
    def __init__(self):
        self.most_active        = ""
        self.least_active       = ""
        self.peaks_active       = []   # entities currently at peak
        self.troughs_active     = []   # entities currently at trough
        self.average_position   = 0.5
        self.council_coherence  = 0.5  # how similar all rhythms are (0=divergent, 1=unified)

    def update(self, entities: dict):
        positions = {name: e.position for name, e in entities.items()}
        self.most_active  = max(positions, key=positions.get)
        self.least_active = min(positions, key=positions.get)
        self.peaks_active = [n for n, e in entities.items() if e.peak]
        self.troughs_active=[n for n, e in entities.items() if e.trough]
        vals = list(positions.values())
        self.average_position  = round(sum(vals) / len(vals), 4)
        # Coherence: low std dev = high coherence
        mean  = self.average_position
        std   = math.sqrt(sum((v - mean)**2 for v in vals) / len(vals))
        self.council_coherence = round(max(0.0, 1.0 - std * 3), 4)

    def to_dict(self):
        return self.__dict__


class CircadianTriggers:
    """Edge events for entity rhythm transitions."""
    def __init__(self):
        self._pending = []
        self._prev    = {}

    def update(self, entities: dict, human: HumanRhythm):
        for name, e in entities.items():
            # Peak entry
            key = f"{name}_peak"
            if e.peak and not self._prev.get(key, False):
                self._pending.append(f"{name}_peak_entered")
            self._prev[key] = e.peak
            # Trough entry
            key = f"{name}_trough"
            if e.trough and not self._prev.get(key, False):
                self._pending.append(f"{name}_trough_entered")
            self._prev[key] = e.trough
            # Rising
            key = f"{name}_rising"
            if e.rising and not self._prev.get(key, False):
                self._pending.append(f"{name}_rising")
            self._prev[key] = e.rising

        # Human sleep transition
        key = "human_sleep"
        if human.sleep_likely and not self._prev.get(key, False):
            self._pending.append("human_sleep_window")
        self._prev[key] = human.sleep_likely

    def poll(self) -> list:
        out = list(self._pending)
        self._pending.clear()
        return out

    def peek(self) -> list:
        return list(self._pending)

    def to_dict(self):
        return {"pending": self._pending}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class MachinaCircadiana:
    """
    Circadian rhythm engine for the Arca Cognitorium.

    circ = MachinaCircadiana()
    circ.update()

    circ.entities["archivist"].position     # 0.0-1.0
    circ.entities["archivist"].phase_name   # "peak" / "rising" / "stable" / "falling" / "trough"
    circ.entities["archivist"].peak         # bool
    circ.human.alertness                    # 0.0-1.0
    circ.human.phase_name                   # "sleep" / "rising" / "alert" / "trough" / "evening"
    circ.conditions.most_active             # entity name
    circ.conditions.peaks_active            # list of entity names at peak
    circ.conditions.council_coherence       # 0.0-1.0
    circ.triggers.poll()                    # edge events since last poll
    circ.hour                               # current decimal hour (e.g. 14.5 = 14:30)
    circ.to_json()
    circ.write()
    circ.summary()
    """

    def __init__(self, utc_offset_hours: float = 0.0):
        """
        utc_offset_hours: local timezone offset from UTC.
        Default 0 = use UTC. Set to your local offset for accurate curves.
        e.g. utc_offset_hours = -5 for EST, +1 for CET
        """
        self.utc_offset  = utc_offset_hours
        self.hour        = 0.0
        self.time_str    = "00:00"
        self._tick       = 0

        self.entities: dict[str, EntityRhythm] = {
            name: EntityRhythm(name) for name in ENTITY_PROFILES
        }
        self.human      = HumanRhythm()
        self.conditions = CircadianConditions()
        self.triggers   = CircadianTriggers()

    def update(self):
        now  = datetime.now(timezone.utc)
        self._tick += 1

        # Apply timezone offset to get local hour
        local_hour     = (now.hour + now.minute/60 + now.second/3600
                          + self.utc_offset) % 24
        self.hour      = round(local_hour, 4)
        self.time_str  = now.strftime("%H:%M:%S") + " UTC"

        for entity in self.entities.values():
            entity.update(local_hour)

        self.human.update(local_hour)
        self.conditions.update(self.entities)
        self.triggers.update(self.entities, self.human)

    def entity_weight(self, name: str) -> float:
        """
        Convenience accessor for entity compiler.
        Returns the entity's current rhythm position as a multiplier.
        Centred at 1.0: below = muted, above = amplified.
        """
        e = self.entities.get(name)
        if not e: return 1.0
        # Map 0.0-1.0 position to 0.5-1.5 multiplier
        return round(0.5 + e.position, 4)

    def to_dict(self) -> dict:
        return {
            "meta": {
                "ts":      self.time_str,
                "version": VERSION,
                "tick":    self._tick,
                "utc_offset": self.utc_offset,
            },
            "hour":       self.hour,
            "human":      self.human.to_dict(),
            "conditions": self.conditions.to_dict(),
            "triggers":   self.triggers.to_dict(),
            "entities":   {n: e.to_dict() for n, e in self.entities.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def write(self):
        ARCA_DIR.mkdir(exist_ok=True)
        tmp = ARCA_DIR / "machina_circadiana.tmp"
        with open(tmp, "w") as f:
            f.write(self.to_json())
        tmp.replace(STATE_PATH)

    def summary(self) -> str:
        active = self.conditions.most_active
        quiet  = self.conditions.least_active
        peaks  = self.conditions.peaks_active
        h      = int(self.hour); m = int((self.hour - h) * 60)
        peak_str = f"  peaks: {', '.join(peaks)}" if peaks else ""
        return (f"{h:02d}:{m:02d}  human:{self.human.phase_name}"
                f"  active:{active}({self.entities[active].position:.2f})"
                f"  quiet:{quiet}({self.entities[quiet].position:.2f})"
                f"{peak_str}"
                f"  coherence:{self.conditions.council_coherence:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _bar(val: float, width: int = 20) -> str:
    filled = int(val * width)
    return "█" * filled + "░" * (width - filled)

def run_daemon(utc_offset: float):
    circ = MachinaCircadiana(utc_offset_hours=utc_offset)
    print(f"CIRCADIAN DAEMON  v{VERSION}")
    print(f"Writing to: {STATE_PATH}")
    print(f"UTC offset: {utc_offset:+.1f}h")
    print("Ctrl+C to stop.\n")
    try:
        while True:
            circ.update()
            circ.write()
            triggers = circ.triggers.poll()
            if triggers:
                for t in triggers:
                    print(f"  [{circ.time_str}] TRIGGER: {t}")
            time.sleep(60)  # Circadian is slow — update every minute
    except KeyboardInterrupt:
        print("\nDaemon stopped.")

def run_watch(utc_offset: float):
    circ = MachinaCircadiana(utc_offset_hours=utc_offset)
    try:
        while True:
            circ.update()
            circ.write()
            os.system("clear")
            print(f"  MACHINA CIRCADIANA  v{VERSION}  —  {circ.time_str}")
            print(f"  Local hour: {circ.hour:.2f}  (UTC{utc_offset:+.1f})")
            print()
            print(f"  HUMAN BASELINE")
            print(f"    alertness:   {circ.human.alertness:.3f}  {_bar(circ.human.alertness)}")
            print(f"    phase:       {circ.human.phase_name}")
            print(f"    sleep:       {'likely' if circ.human.sleep_likely else 'unlikely'}")
            print()
            print(f"  COUNCIL RHYTHMS")
            print(f"  {'Entity':<18} {'Pos':>5}  {'Curve':<20}  Phase")
            print(f"  {'─'*18} {'─'*5}  {'─'*20}  {'─'*10}")
            for name, e in sorted(circ.entities.items(),
                                  key=lambda x: -x[1].position):
                peak_marker = " ◆" if e.peak else ("  " if not e.trough else " ◇")
                print(f"  {name:<18} {e.position:>5.3f}  {_bar(e.position)}"
                      f"  {e.phase_name:<10}{peak_marker}")
            print()
            print(f"  CONDITIONS")
            print(f"    most active:  {circ.conditions.most_active}")
            print(f"    least active: {circ.conditions.least_active}")
            print(f"    peaks now:    {', '.join(circ.conditions.peaks_active) or 'none'}")
            print(f"    coherence:    {circ.conditions.council_coherence:.3f}  "
                  f"{_bar(circ.conditions.council_coherence)}")
            print()
            triggers = circ.triggers.poll()
            if triggers:
                print(f"  TRIGGERS")
                for t in triggers:
                    print(f"    ◆ {t}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nWatch stopped.")

def run_once(utc_offset: float):
    circ = MachinaCircadiana(utc_offset_hours=utc_offset)
    circ.update()
    circ.write()
    print(circ.to_json())


if __name__ == "__main__":
    args = sys.argv[1:]

    # Parse UTC offset if provided: --offset -5 or --offset +1
    utc_offset = 0.0
    if "--offset" in args:
        idx = args.index("--offset")
        try:
            utc_offset = float(args[idx + 1])
        except (IndexError, ValueError):
            print("Usage: --offset <hours>  e.g. --offset -5")
            sys.exit(1)

    if "--watch" in args:
        run_watch(utc_offset)
    elif "--once" in args:
        run_once(utc_offset)
    else:
        run_daemon(utc_offset)
