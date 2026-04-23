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
from .results import load_numeric_csv, materialize_reference_csvs, unpack_mat_to_csv

OMSIMULATOR_ENGINE = "omsimulator"
SSP4SIM_ENGINE = "ssp4sim"
DEFAULT_INTERVAL = 0.01


@dataclass(frozen=True)
class SimulationWindow:
    start_time: float
    stop_time: float
    interval: float


@dataclass(frozen=True)
class SimulationVariant:
    name: str
    engine: str
    version: str = "current"
    start_time: float | None = None
    stop_time: float | None = None
    interval: float | None = None
    ssp4sim_app: str | None = None
    executor_method: str = "jacobi"
    thread_pool_workers: int = 1
    forward_derivatives: bool = True
    jacobi_parallel: bool = True
    jacobi_method: int = 1
    seidel_parallel: bool = False


@dataclass(frozen=True)
class SimulationArtifacts:
    variant: SimulationVariant
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
    start_time: float | None = None,
    stop_time: float | None = None,
    interval: float | None = None,
) -> SimulationWindow:
    default_start, default_stop = read_default_experiment(model.paths.ssp_path)
    resolved_start = start_time if start_time is not None else default_start
    resolved_stop = stop_time if stop_time is not None else default_stop
    resolved_interval = interval

    reference_csvs = materialize_reference_csvs(model.source_results, model.paths.references_dir)
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
            "Provide explicit start and stop times in the simulation variant."
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


def infer_variant_window(model: ModelMetaData, variant: SimulationVariant) -> SimulationWindow:
    return infer_window(
        model,
        start_time=variant.start_time,
        stop_time=variant.stop_time,
        interval=variant.interval,
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
    model: ModelMetaData,
    window: SimulationWindow,
    variant: SimulationVariant,
    *,
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
                "method": variant.executor_method,
                "thread_pool_workers": variant.thread_pool_workers,
                "forward_derivatives": variant.forward_derivatives,
                "jacobi": {"parallel": variant.jacobi_parallel, "method": variant.jacobi_method},
                "seidel": {"parallel": variant.seidel_parallel},
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


def write_variant_metadata(
    output_dir: Path,
    variant: SimulationVariant,
    window: SimulationWindow,
) -> Path:
    metadata_path = output_dir / "variant.json"
    metadata_path.write_text(
        json.dumps(
            {
                "name": variant.name,
                "engine": variant.engine,
                "version": variant.version,
                "window": asdict(window),
            },
            indent=2,
        )
        + "\n"
    )
    return metadata_path


def run_omsimulator_variant(model: ModelMetaData, variant: SimulationVariant, window: SimulationWindow) -> SimulationArtifacts:
    engine_dir = model.paths.engine_results_dir(variant.name)
    reset_dir(engine_dir)

    result_mat = engine_dir / "result.mat"
    result_csv = engine_dir / "result.csv"
    simulate_with_omsimulator(
        model.paths.ssp_path,
        result_mat=result_mat,
        result_csv=result_csv,
        start_time=window.start_time,
        stop_time=window.stop_time,
        interval=window.interval,
    )
    metadata_path = write_variant_metadata(engine_dir, variant, window)
    return SimulationArtifacts(
        variant=variant,
        window=window,
        result_csv=result_csv,
        extra_files=[result_mat, metadata_path],
    )


def run_ssp4sim_variant(model: ModelMetaData, variant: SimulationVariant, window: SimulationWindow) -> SimulationArtifacts:
    engine_dir = model.paths.engine_results_dir(variant.name)
    reset_dir(engine_dir)

    result_csv = engine_dir / "result.csv"
    log_path = engine_dir / "simulation.log"
    config_path = engine_dir / "config.json"
    stdout_path = engine_dir / "stdout.log"
    write_ssp4sim_config(model, window, variant, config_path=config_path, result_csv=result_csv, log_path=log_path)

    command = [str(resolve_ssp4sim_app(variant.ssp4sim_app)), str(config_path)]
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
            f"ssp4sim failed for {model.name} variant {variant.name} with exit code {completed.returncode}. "
            f"See {stdout_path}."
        )

    metadata_path = write_variant_metadata(engine_dir, variant, window)
    return SimulationArtifacts(
        variant=variant,
        window=window,
        result_csv=result_csv,
        extra_files=[config_path, log_path, stdout_path, metadata_path],
    )


def run_simulation_variant(model: ModelMetaData, variant: SimulationVariant) -> SimulationArtifacts:
    window = infer_variant_window(model, variant)
    if variant.engine == OMSIMULATOR_ENGINE:
        return run_omsimulator_variant(model, variant, window)
    if variant.engine == SSP4SIM_ENGINE:
        return run_ssp4sim_variant(model, variant, window)
    raise ValueError(f"Unsupported simulation engine: {variant.engine}")


def run_simulation_variants(model: ModelMetaData, variants: list[SimulationVariant]) -> list[SimulationArtifacts]:
    return [run_simulation_variant(model, variant) for variant in variants]
