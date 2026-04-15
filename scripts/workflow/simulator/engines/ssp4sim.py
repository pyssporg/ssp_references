from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ...config import REPO_ROOT
from ...filesystem import ensure_parent, reset_dir
from ...model import ModelMetaData
from ..common import EngineArtifacts, SSP4SIM_ENGINE, SimulationWindow, resolve_ssp4sim_app


def write_ssp4sim_config(
    model: ModelMetaData,
    window: SimulationWindow,
    config_path: Path,
    result_csv: Path,
    log_path: Path,
) -> None:
    config = {
        "simulation": {
            "ssp": str(model.paths.ssp_path.resolve()),
            "ssd": "SystemStructure.ssd",
            "start_time": window.start_time,
            "stop_time": window.stop_time,
            "timestep": window.interval,
            "tolerance": 1e-4,
            "executor": {
                "method": "jacobi",
                "thread_pool_workers": 1,
                "forward_derivatives": True,
                "jacobi": {"parallel": True, "method": 1},
                "seidel": {"parallel": False},
            },
            "recording": {
                "enable": True,
                "wait_for": True,
                "interval": window.interval,
                "result_file": str(result_csv),
            },
            "log": {
                "file": str(log_path),
                "fmu": False,
            },
        }
    }
    ensure_parent(config_path)
    config_path.write_text(json.dumps(config, indent=2) + "\n")


def run_ssp4sim(
    model: ModelMetaData,
    window: SimulationWindow,
    *,
    ssp4sim_app: str | None = None,
) -> EngineArtifacts:
    engine_dir = model.paths.engine_results_dir(SSP4SIM_ENGINE)
    reset_dir(engine_dir)

    result_csv = engine_dir / "result.csv"
    log_path = engine_dir / "simulation.log"
    config_path = engine_dir / "config.json"
    stdout_path = engine_dir / "stdout.log"
    write_ssp4sim_config(model, window, config_path, result_csv, log_path)

    command = [str(resolve_ssp4sim_app(ssp4sim_app)), str(config_path)]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    stdout_path.write_text(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(
            f"ssp4sim failed for {model.name} with exit code {completed.returncode}. "
            f"See {stdout_path}."
        )

    return EngineArtifacts(
        engine=SSP4SIM_ENGINE,
        result_csv=result_csv,
        extra_files=[config_path, log_path, stdout_path],
    )
