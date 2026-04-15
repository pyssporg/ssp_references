from __future__ import annotations

import subprocess
from pathlib import Path

from ...config import REPO_ROOT
from ...filesystem import reset_dir
from ...model import ModelMetaData
from ...results import unpack_mat_to_csv
from ..common import EngineArtifacts, OMSIMULATOR_ENGINE, SimulationWindow, resolve_venv_python


def simulate_with_omsimulator(
    ssp_path: Path,
    *,
    result_mat: Path,
    result_csv: Path,
    start_time: float,
    stop_time: float,
    interval: float,
) -> Path:
    from OMSimulator import SSP, Settings

    Settings.suppressPath = True
    model = SSP(str(ssp_path))
    instantiated_model = model.instantiate()
    instantiated_model.setStartTime(start_time)
    instantiated_model.setStopTime(stop_time)
    instantiated_model.setLoggingInterval(interval)
    instantiated_model.setResultFile(str(result_mat))
    instantiated_model.initialize()
    instantiated_model.simulate()
    instantiated_model.terminate()
    instantiated_model.delete()

    unpack_mat_to_csv(result_mat, result_csv)
    return result_csv


def run_omsimulator(model: ModelMetaData, window: SimulationWindow) -> EngineArtifacts:
    engine_dir = model.paths.engine_results_dir(OMSIMULATOR_ENGINE)
    reset_dir(engine_dir)

    result_mat = engine_dir / "result.mat"
    result_csv = engine_dir / "result.csv"
    command = [
        str(resolve_venv_python()),
        str(REPO_ROOT / "scripts" / "cli" / "simulate_with_omsimulator.py"),
        str(model.paths.ssp_path),
        "--result-mat",
        str(result_mat),
        "--result-csv",
        str(result_csv),
        "--start-time",
        str(window.start_time),
        "--stop-time",
        str(window.stop_time),
        "--interval",
        str(window.interval),
    ]
    subprocess.run(command, check=True, cwd=REPO_ROOT)
    return EngineArtifacts(
        engine=OMSIMULATOR_ENGINE,
        result_csv=result_csv,
        extra_files=[result_mat],
    )
