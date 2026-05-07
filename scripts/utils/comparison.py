from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .filesystem import ensure_parent
from .csv import load_numeric_csv, normalize_column_name


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


def canonicalize_signal_name(
    column_name: str,
    *,
    engine: str | None = None,
    root_system_name: str | None = None,
) -> str:
    normalized = column_name.strip()
    if normalized == "time":
        return "time"
    return normalize_column_name(
        normalized,
        engine=engine,
        root_system_name=root_system_name,
    )


def _select_signal_series(
    columns: dict[str, np.ndarray],
    selected_signals: tuple[str, ...],
    *,
    engine: str | None,
    root_system_name: str,
) -> dict[str, np.ndarray]:
    selected_set = set(selected_signals)
    selected_series: dict[str, np.ndarray] = {}

    for signal in selected_signals:
        if signal in columns:
            selected_series[signal] = columns[signal]

    for raw_name, series in columns.items():
        canonical_name = canonicalize_signal_name(
            raw_name,
            engine=engine,
            root_system_name=root_system_name,
        )
        if canonical_name in selected_set and canonical_name not in selected_series:
            selected_series[canonical_name] = series

    missing_signals = [signal for signal in selected_signals if signal not in selected_series]
    if missing_signals:
        raise KeyError(
            "Selected comparison signals missing from result sets: "
            + ", ".join(missing_signals)
        )

    return selected_series


def compare_result_sets(
    run_a: ResultSet,
    run_b: ResultSet,
    *,
    window: SimulationWindow,
    selected_signals: tuple[str, ...],
    root_system_name: str,
) -> tuple[dict, list[dict[str, float | str]]]:
    run_a_data = load_numeric_csv(
        run_a.path,
        engine=run_a.engine,
        root_system_name=root_system_name,
    )["columns"]
    run_b_data = load_numeric_csv(
        run_b.path,
        engine=run_b.engine,
        root_system_name=root_system_name,
    )["columns"]

    run_a_signals = _select_signal_series(
        run_a_data,
        selected_signals,
        engine=run_a.engine,
        root_system_name=root_system_name,
    )
    run_b_signals = _select_signal_series(
        run_b_data,
        selected_signals,
        engine=run_b.engine,
        root_system_name=root_system_name,
    )

    run_a_time = run_a_data.get("time")
    run_b_time = run_b_data.get("time")
    if run_a_time is None or run_b_time is None:
        raise KeyError("Both result sets must contain a time column")

    target_times = build_time_grid(window)

    metrics: list[dict[str, float | str]] = []
    for signal in selected_signals:
        run_a_series = resample_series(run_a_time, run_a_signals[signal], target_times)
        run_b_series = resample_series(run_b_time, run_b_signals[signal], target_times)
        errors = np.abs(run_a_series - run_b_series)

        metrics.append(
            {
                "signal": signal,
                "max_abs_error": float(np.nanmax(errors)),
                "mean_abs_error": float(np.nanmean(errors)),
                "rmse": float(math.sqrt(np.nanmean(np.square(errors)))),
                "run_a_label": run_a.label,
                "run_a_min": float(np.nanmin(run_a_series)),
                "run_a_max": float(np.nanmax(run_a_series)),
                "run_b_label": run_b.label,
                "run_b_min": float(np.nanmin(run_b_series)),
                "run_b_max": float(np.nanmax(run_b_series)),
            }
        )

    summary = {
        "run_a_label": run_a.label,
        "run_b_label": run_b.label,
        "time_points": int(len(target_times)),
        "compared_signal_count": len(selected_signals),
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


def comparison_run_name(run_a_label: str, run_b_label: str) -> str:
    return f"{sanitize_label(run_a_label)}_vs_{sanitize_label(run_b_label)}"


def comparison_stem(run_a: ResultSet, run_b: ResultSet) -> str:
    return comparison_run_name(run_a.label, run_b.label)


def write_metrics_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    ensure_parent(path)
    fieldnames = [
        "signal",
        "max_abs_error",
        "mean_abs_error",
        "rmse",
        "run_a_label",
        "run_a_min",
        "run_a_max",
        "run_b_label",
        "run_b_min",
        "run_b_max",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
