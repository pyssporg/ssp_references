"""Small shared workflow records.

These are repository-internal records, not SSP interchange artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SimulationWindow:
    start_time: float
    stop_time: float
    interval: float


@dataclass(frozen=True)
class ResultSet:
    label: str
    path: Path
    engine: str
