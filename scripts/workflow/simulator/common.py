from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from ..config import REPO_ROOT

OMSIMULATOR_ENGINE = "omsimulator"
SSP4SIM_ENGINE = "ssp4sim"
DEFAULT_INTERVAL = 0.01


@dataclass(frozen=True)
class SimulationWindow:
    start_time: float
    stop_time: float
    interval: float


@dataclass(frozen=True)
class EngineArtifacts:
    engine: str
    result_csv: Path
    extra_files: list[Path]


def resolve_venv_python() -> Path:
    venv_python = REPO_ROOT / "venv" / "bin" / "python"
    if venv_python.is_file():
        return venv_python
    return Path(sys.executable)


def resolve_ssp4sim_app(explicit_path: str | None = None) -> Path:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))

    env_path = os.environ.get("SSP4SIM_SIM_APP")
    if env_path:
        candidates.append(Path(env_path))

    candidates.append(REPO_ROOT.parent / "ssp4sim" / "build" / "public" / "ssp4sim_app" / "sim_app")

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "Unable to locate ssp4sim CLI. Set SSP4SIM_SIM_APP or pass --ssp4sim-app."
    )
