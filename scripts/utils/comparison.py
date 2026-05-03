from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .filesystem import ensure_parent
from .csv import load_numeric_csv


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
    common_signals = sorted(signal for signal in left_data if signal != "time" and signal in right_data)

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

