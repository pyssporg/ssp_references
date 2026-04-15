from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .filesystem import ensure_parent
from .model import ModelMetaData
from .results import load_numeric_csv
from .simulator import (
    OMSIMULATOR_ENGINE,
    SSP4SIM_ENGINE,
    SimulationWindow,
    infer_window,
    run_omsimulator,
    run_ssp4sim,
)


def build_time_grid(window: SimulationWindow) -> np.ndarray:
    span = window.stop_time - window.start_time
    steps = int(round(span / window.interval))
    return np.linspace(window.start_time, window.stop_time, steps + 1, dtype=float)


def resample_series(times: np.ndarray, values: np.ndarray, target_times: np.ndarray) -> np.ndarray:
    valid_mask = np.isfinite(times) & np.isfinite(values)
    valid_times = times[valid_mask]
    valid_values = values[valid_mask]
    if len(valid_times) == 0:
        return np.full(target_times.shape, np.nan, dtype=float)

    order = np.argsort(valid_times)
    valid_times = valid_times[order]
    valid_values = valid_values[order]
    unique_times, unique_indices = np.unique(valid_times, return_index=True)
    unique_values = valid_values[unique_indices]

    if len(unique_times) == 1:
        return np.full(target_times.shape, unique_values[0], dtype=float)

    return np.interp(
        target_times,
        unique_times,
        unique_values,
        left=unique_values[0],
        right=unique_values[-1],
    )


def compare_csv_results(
    omsimulator_csv: Path,
    ssp4sim_csv: Path,
    *,
    window: SimulationWindow,
) -> tuple[dict, list[dict[str, float | str]]]:
    oms_data = load_numeric_csv(omsimulator_csv, engine=OMSIMULATOR_ENGINE)["columns"]
    ssp4sim_data = load_numeric_csv(ssp4sim_csv, engine=SSP4SIM_ENGINE)["columns"]

    oms_time = oms_data.get("time")
    ssp4sim_time = ssp4sim_data.get("time")
    if oms_time is None or ssp4sim_time is None:
        raise KeyError("Both engine results must contain a time column")

    target_times = build_time_grid(window)
    common_signals = sorted(
        signal
        for signal in oms_data
        if signal != "time" and signal in ssp4sim_data
    )

    metrics: list[dict[str, float | str]] = []
    for signal in common_signals:
        oms_series = resample_series(oms_time, oms_data[signal], target_times)
        ssp4sim_series = resample_series(ssp4sim_time, ssp4sim_data[signal], target_times)
        errors = np.abs(oms_series - ssp4sim_series)

        metrics.append(
            {
                "signal": signal,
                "max_abs_error": float(np.nanmax(errors)),
                "mean_abs_error": float(np.nanmean(errors)),
                "rmse": float(math.sqrt(np.nanmean(np.square(errors)))),
                "omsimulator_min": float(np.nanmin(oms_series)),
                "omsimulator_max": float(np.nanmax(oms_series)),
                "ssp4sim_min": float(np.nanmin(ssp4sim_series)),
                "ssp4sim_max": float(np.nanmax(ssp4sim_series)),
            }
        )

    summary = {
        "time_points": int(len(target_times)),
        "common_signal_count": len(common_signals),
        "max_abs_error": max((row["max_abs_error"] for row in metrics), default=0.0),
        "mean_abs_error": float(np.nanmean([row["mean_abs_error"] for row in metrics])) if metrics else 0.0,
        "rmse": float(np.nanmean([row["rmse"] for row in metrics])) if metrics else 0.0,
    }
    return summary, metrics


def write_metrics_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    ensure_parent(path)
    fieldnames = [
        "signal",
        "max_abs_error",
        "mean_abs_error",
        "rmse",
        "omsimulator_min",
        "omsimulator_max",
        "ssp4sim_min",
        "ssp4sim_max",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compare_model_results(
    model: ModelMetaData,
    *,
    start_time: float | None = None,
    stop_time: float | None = None,
    interval: float | None = None,
    ssp4sim_app: str | None = None,
) -> dict:
    window = infer_window(
        model,
        start_time=start_time,
        stop_time=stop_time,
        interval=interval,
    )
    omsimulator = run_omsimulator(model, window)
    ssp4sim = run_ssp4sim(model, window, ssp4sim_app=ssp4sim_app)

    comparison_dir = model.paths.comparisons_dir
    comparison_dir.mkdir(parents=True, exist_ok=True)
    metrics_csv = comparison_dir / f"{OMSIMULATOR_ENGINE}_vs_{SSP4SIM_ENGINE}.csv"
    summary_json = comparison_dir / f"{OMSIMULATOR_ENGINE}_vs_{SSP4SIM_ENGINE}.json"

    summary, metrics = compare_csv_results(
        omsimulator.result_csv,
        ssp4sim.result_csv,
        window=window,
    )
    write_metrics_csv(metrics_csv, metrics)

    payload = {
        "model": model.name,
        "window": asdict(window),
        "engines": {
            OMSIMULATOR_ENGINE: str(omsimulator.result_csv),
            SSP4SIM_ENGINE: str(ssp4sim.result_csv),
        },
        "summary": summary,
        "metrics_csv": str(metrics_csv),
    }
    summary_json.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
