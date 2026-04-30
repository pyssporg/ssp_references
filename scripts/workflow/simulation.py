from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np

from .config import REPO_ROOT
from .filesystem import ensure_parent, reset_dir
from .model import ModelMetaData
from .results import load_numeric_csv, unpack_mat_to_csv

OMSIMULATOR_ENGINE = "omsimulator"
SSP4SIM_ENGINE = "ssp4sim"
DEFAULT_INTERVAL = 0.01


@dataclass(frozen=True)
class SimulationWindow:
    start_time: float
    stop_time: float
    interval: float


@dataclass(frozen=True)
class SimulationConfig:
    ssp_path: Path | None = None
    start_time: float | None = None
    stop_time: float | None = None
    interval: float | None = None
    tolerance: float = 1e-4


@dataclass(frozen=True)
class SimulationArtifacts:
    name: str
    engine: str
    config: SimulationConfig
    window: SimulationWindow
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
        "Unable to locate ssp4sim CLI. Set SSP4SIM_SIM_APP or pass an explicit path."
    )


def resolve_ssp_path(model: ModelMetaData, config: SimulationConfig) -> Path:
    return config.ssp_path or model.paths.ssp_path


def read_default_experiment(ssp_path: Path) -> tuple[float | None, float | None]:
    with ZipFile(ssp_path) as archive:
        xml_text = archive.read("SystemStructure.ssd")
    root = ET.fromstring(xml_text)
    namespace = {"ssd": "http://ssp-standard.org/SSP1/SystemStructureDescription"}
    experiment = root.find("ssd:DefaultExperiment", namespace)
    if experiment is None:
        return None, None

    start_time = experiment.attrib.get("startTime")
    stop_time = experiment.attrib.get("stopTime")
    return (
        float(start_time) if start_time is not None else None,
        float(stop_time) if stop_time is not None else None,
    )


def infer_interval_from_reference_csv(reference_csv: Path) -> float | None:
    times = load_numeric_csv(reference_csv)["columns"].get("time")
    if times is None or len(times) < 2:
        return None

    diffs = np.diff(times)
    positive_diffs = diffs[np.isfinite(diffs) & (diffs > 0)]
    if len(positive_diffs) == 0:
        return None
    return float(np.min(positive_diffs))


def infer_window(
    model: ModelMetaData,
    *,
    ssp_path: Path | None = None,
    start_time: float | None = None,
    stop_time: float | None = None,
    interval: float | None = None,
) -> SimulationWindow:
    resolved_ssp_path = ssp_path or model.paths.ssp_path
    default_start, default_stop = read_default_experiment(resolved_ssp_path)
    resolved_start = start_time if start_time is not None else default_start
    resolved_stop = stop_time if stop_time is not None else default_stop
    resolved_interval = interval

    reference_csvs = sorted(model.paths.reference_results_dir.glob("*.csv"))
    if reference_csvs:
        reference_data = load_numeric_csv(reference_csvs[0])["columns"]
        reference_time = reference_data.get("time")
        if reference_time is not None and len(reference_time) > 0:
            if resolved_start is None:
                resolved_start = float(reference_time[0])
            if resolved_stop is None:
                resolved_stop = float(reference_time[-1])
        if resolved_interval is None:
            resolved_interval = infer_interval_from_reference_csv(reference_csvs[0])

    if resolved_start is None or resolved_stop is None:
        raise ValueError(
            f"Unable to infer simulation window for {model.name}. "
            "Provide explicit start and stop times in the simulation config."
        )
    if resolved_interval is None:
        resolved_interval = DEFAULT_INTERVAL
    if resolved_interval <= 0:
        raise ValueError("Simulation interval must be > 0")
    if resolved_stop <= resolved_start:
        raise ValueError("Simulation stop time must be greater than start time")

    return SimulationWindow(
        start_time=float(resolved_start),
        stop_time=float(resolved_stop),
        interval=float(resolved_interval),
    )


def resolve_window(model: ModelMetaData, config: SimulationConfig) -> SimulationWindow:
    return infer_window(
        model,
        ssp_path=resolve_ssp_path(model, config),
        start_time=config.start_time,
        stop_time=config.stop_time,
        interval=config.interval,
    )


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


def write_ssp4sim_config(
    ssp_path: Path,
    window: SimulationWindow,
    config: SimulationConfig,
    *,
    config_path: Path,
    result_csv: Path,
    log_path: Path,
) -> None:
    payload = {
        "simulation": {
            "ssp": str(ssp_path.resolve()),
            "ssd": "SystemStructure.ssd",
            "start_time": window.start_time,
            "stop_time": window.stop_time,
            "timestep": window.interval,
            "tolerance": config.tolerance,
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
    config_path.write_text(json.dumps(payload, indent=2) + "\n")


def write_run_metadata(
    output_dir: Path,
    *,
    name: str,
    engine: str,
    config: SimulationConfig,
    window: SimulationWindow,
    ssp_path: Path,
) -> Path:
    metadata_path = output_dir / "variant.json"
    metadata_path.write_text(
        json.dumps(
            {
                "name": name,
                "engine": engine,
                "ssp": str(ssp_path),
                "config": {
                    "start_time": config.start_time,
                    "stop_time": config.stop_time,
                    "interval": config.interval,
                    "tolerance": config.tolerance,
                },
                "window": asdict(window),
            },
            indent=2,
        )
        + "\n"
    )
    return metadata_path


def simulate_oms(
    model: ModelMetaData,
    *,
    name: str = OMSIMULATOR_ENGINE,
    config: SimulationConfig | None = None,
) -> SimulationArtifacts:
    resolved_config = config or SimulationConfig()
    ssp_path = resolve_ssp_path(model, resolved_config)
    window = resolve_window(model, resolved_config)
    engine_dir = model.paths.engine_results_dir(name)
    reset_dir(engine_dir)

    result_mat = engine_dir / "result.mat"
    result_csv = engine_dir / "result.csv"
    simulate_with_omsimulator(
        ssp_path,
        result_mat=result_mat,
        result_csv=result_csv,
        start_time=window.start_time,
        stop_time=window.stop_time,
        interval=window.interval,
    )
    metadata_path = write_run_metadata(
        engine_dir,
        name=name,
        engine=OMSIMULATOR_ENGINE,
        config=resolved_config,
        window=window,
        ssp_path=ssp_path,
    )
    return SimulationArtifacts(
        name=name,
        engine=OMSIMULATOR_ENGINE,
        config=resolved_config,
        window=window,
        result_csv=result_csv,
        extra_files=[result_mat, metadata_path],
    )


def simulate_ssp4sim(
    model: ModelMetaData,
    *,
    name: str = SSP4SIM_ENGINE,
    config: SimulationConfig | None = None,
    app: str | None = None,
) -> SimulationArtifacts:
    resolved_config = config or SimulationConfig()
    ssp_path = resolve_ssp_path(model, resolved_config)
    window = resolve_window(model, resolved_config)
    engine_dir = model.paths.engine_results_dir(name)
    reset_dir(engine_dir)

    result_csv = engine_dir / "result.csv"
    log_path = engine_dir / "simulation.log"
    config_path = engine_dir / "config.json"
    stdout_path = engine_dir / "stdout.log"
    write_ssp4sim_config(
        ssp_path,
        window,
        resolved_config,
        config_path=config_path,
        result_csv=result_csv,
        log_path=log_path,
    )

    command = [str(resolve_ssp4sim_app(app)), str(config_path)]
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
            f"ssp4sim failed for {model.name} run {name} with exit code {completed.returncode}. "
            f"See {stdout_path}."
        )

    metadata_path = write_run_metadata(
        engine_dir,
        name=name,
        engine=SSP4SIM_ENGINE,
        config=resolved_config,
        window=window,
        ssp_path=ssp_path,
    )
    return SimulationArtifacts(
        name=name,
        engine=SSP4SIM_ENGINE,
        config=resolved_config,
        window=window,
        result_csv=result_csv,
        extra_files=[config_path, log_path, stdout_path, metadata_path],
    )
