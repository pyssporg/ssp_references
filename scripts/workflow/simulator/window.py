from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np

from ..model import ModelMetaData
from ..results import load_numeric_csv
from .common import DEFAULT_INTERVAL, SimulationWindow


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

    reference_csvs = sorted(model.paths.references_dir.glob("*.csv"))
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
            "Provide --start-time and --stop-time explicitly."
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
