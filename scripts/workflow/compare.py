from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import asdict, dataclass
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

REFERENCES_ENGINE = "references"


@dataclass(frozen=True)
class ResultSet:
    label: str
    path: Path
    engine: str


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


def discover_simulation_result_sets(model: ModelMetaData) -> list[ResultSet]:
    result_sets: list[ResultSet] = []
    root = model.paths.simulation_results_dir
    if not root.is_dir():
        return result_sets

    for engine_dir in sorted(path for path in root.iterdir() if path.is_dir() and path.name != "comparisons"):
        csv_files = sorted(engine_dir.glob("*.csv"))
        for csv_path in csv_files:
            label = engine_dir.name if csv_path.name == "result.csv" else f"{engine_dir.name}:{csv_path.stem}"
            result_sets.append(
                ResultSet(
                    label=label,
                    path=csv_path,
                    engine=engine_dir.name,
                )
            )
    return result_sets


def discover_reference_result_sets(model: ModelMetaData) -> list[ResultSet]:
    if not model.paths.references_dir.is_dir():
        return []

    return [
        ResultSet(
            label=f"references:{csv_path.stem}",
            path=csv_path,
            engine=REFERENCES_ENGINE,
        )
        for csv_path in sorted(model.paths.references_dir.glob("*.csv"))
    ]


def discover_result_sets(model: ModelMetaData, *, include_references: bool = True) -> list[ResultSet]:
    result_sets = discover_simulation_result_sets(model)
    if include_references:
        result_sets.extend(discover_reference_result_sets(model))
    return result_sets


def compare_result_sets(
    left: ResultSet,
    right: ResultSet,
    *,
    window: SimulationWindow,
) -> tuple[dict, list[dict[str, float | str]]]:
    left_data = load_numeric_csv(left.path, engine=left.engine)["columns"]
    right_data = load_numeric_csv(right.path, engine=right.engine)["columns"]

    left_time = left_data.get("time")
    right_time = right_data.get("time")
    if left_time is None or right_time is None:
        raise KeyError("Both result sets must contain a time column")

    target_times = build_time_grid(window)
    common_signals = sorted(
        signal
        for signal in left_data
        if signal != "time" and signal in right_data
    )

    metrics: list[dict[str, float | str]] = []
    for signal in common_signals:
        left_series = resample_series(left_time, left_data[signal], target_times)
        right_series = resample_series(right_time, right_data[signal], target_times)
        errors = np.abs(left_series - right_series)

        metrics.append(
            {
                "signal": signal,
                "max_abs_error": float(np.nanmax(errors)),
                "mean_abs_error": float(np.nanmean(errors)),
                "rmse": float(math.sqrt(np.nanmean(np.square(errors)))),
                "left_label": left.label,
                "left_min": float(np.nanmin(left_series)),
                "left_max": float(np.nanmax(left_series)),
                "right_label": right.label,
                "right_min": float(np.nanmin(right_series)),
                "right_max": float(np.nanmax(right_series)),
            }
        )

    summary = {
        "left_label": left.label,
        "right_label": right.label,
        "time_points": int(len(target_times)),
        "common_signal_count": len(common_signals),
        "max_abs_error": max((row["max_abs_error"] for row in metrics), default=0.0),
        "mean_abs_error": float(np.nanmean([row["mean_abs_error"] for row in metrics])) if metrics else 0.0,
        "rmse": float(np.nanmean([row["rmse"] for row in metrics])) if metrics else 0.0,
    }
    return summary, metrics


def sanitize_label(label: str) -> str:
    sanitized = []
    for character in label:
        sanitized.append(character if character.isalnum() or character in {"-", "_"} else "_")
    return "".join(sanitized).strip("_")


def comparison_stem(left: ResultSet, right: ResultSet) -> str:
    return f"{sanitize_label(left.label)}_vs_{sanitize_label(right.label)}"


def write_metrics_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    ensure_parent(path)
    fieldnames = [
        "signal",
        "max_abs_error",
        "mean_abs_error",
        "rmse",
        "left_label",
        "left_min",
        "left_max",
        "right_label",
        "right_min",
        "right_max",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compare_available_results(
    model: ModelMetaData,
    *,
    window: SimulationWindow,
    include_references: bool = True,
) -> dict:
    result_sets = discover_result_sets(model, include_references=include_references)
    if len(result_sets) < 2:
        raise ValueError(
            f"Need at least two result sets to compare for {model.name}, found {len(result_sets)}."
        )

    comparison_dir = model.paths.comparisons_dir
    comparison_dir.mkdir(parents=True, exist_ok=True)

    comparisons: list[dict] = []
    for left, right in itertools.combinations(result_sets, 2):
        stem = comparison_stem(left, right)
        metrics_csv = comparison_dir / f"{stem}.csv"
        summary_json = comparison_dir / f"{stem}.json"
        summary, metrics = compare_result_sets(left, right, window=window)
        write_metrics_csv(metrics_csv, metrics)

        payload = {
            "model": model.name,
            "window": asdict(window),
            "left": {"label": left.label, "path": str(left.path), "engine": left.engine},
            "right": {"label": right.label, "path": str(right.path), "engine": right.engine},
            "summary": summary,
            "metrics_csv": str(metrics_csv),
        }
        summary_json.write_text(json.dumps(payload, indent=2) + "\n")
        comparisons.append(payload)

    return {
        "model": model.name,
        "window": asdict(window),
        "result_sets": [
            {"label": result_set.label, "path": str(result_set.path), "engine": result_set.engine}
            for result_set in result_sets
        ],
        "comparisons": comparisons,
    }


def compare_model_results(
    model: ModelMetaData,
    *,
    start_time: float | None = None,
    stop_time: float | None = None,
    interval: float | None = None,
    ssp4sim_app: str | None = None,
    include_references: bool = True,
) -> dict:
    window = infer_window(
        model,
        start_time=start_time,
        stop_time=stop_time,
        interval=interval,
    )
    run_omsimulator(model, window)
    run_ssp4sim(model, window, ssp4sim_app=ssp4sim_app)
    return compare_available_results(
        model,
        window=window,
        include_references=include_references,
    )
