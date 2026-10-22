"""Measurement adapter over :mod:`pyssp_vv.measure`.

The alignment, resampling, metric families, and shift search live in
``pyssp_vv``. This module only loads repository result sets, selects the
canonical signals, and maps the measurement back to the local CSV/manifest
shape.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pyssp_vv.measure import (
    Alignment,
    Comparison,
    Grid,
    Trajectory,
    compare,
    local_shift_error,
    resample,
)

from .domain import ResultSet, SimulationWindow
from .filesystem import ensure_parent

SHIFT_TOLERANCE_SAMPLES = 2


@dataclass(frozen=True)
class Measurement:
    """A ``pyssp_vv`` comparison plus edge-masked local shift errors."""

    comparison: Comparison
    local_shift_errors: dict[str, float]


def _grid(window: SimulationWindow) -> Grid | None:
    if window.stop_time <= window.start_time or window.interval <= 0:
        return None
    return Grid(
        start_time=window.start_time,
        stop_time=window.stop_time,
        step_size=window.interval,
    )


def _load_columns(result: ResultSet, *, root_system_name: str) -> dict[str, np.ndarray]:
    # Local import keeps this module importable without the simulation backend.
    from pyssp_simulate.result import read_result_csv

    data = read_result_csv(
        result.path,
        root_system=root_system_name,
        prefix="fmu.",
    )
    return {name: data[name] for name in data.dtype.names or ()}


def _trajectory(
    columns: dict[str, np.ndarray],
    *,
    label: str,
    selected_signals: tuple[str, ...],
) -> Trajectory:
    missing = [signal for signal in selected_signals if signal not in columns]
    if missing:
        raise KeyError(
            "Selected comparison signals missing from result sets: "
            + ", ".join(missing)
        )
    time = columns.get("time")
    if time is None:
        raise KeyError("Both result sets must contain a time column")
    return Trajectory(
        time=time,
        channels={signal: columns[signal] for signal in selected_signals},
        label=label,
    )


def _local_shift_errors(
    reference: Trajectory,
    candidate: Trajectory,
    *,
    target: np.ndarray,
    selected_signals: tuple[str, ...],
) -> dict[str, float]:
    errors: dict[str, float] = {}
    for signal in selected_signals:
        reference_values = resample(reference.time, reference[signal], target)
        candidate_values = resample(candidate.time, candidate[signal], target)
        local = local_shift_error(
            reference_values,
            candidate_values,
            max_shift=SHIFT_TOLERANCE_SAMPLES,
        )
        if local.size > 2 * SHIFT_TOLERANCE_SAMPLES:
            # Initialization and shutdown samples are not comparable transients.
            local[:SHIFT_TOLERANCE_SAMPLES] = np.nan
            local[-SHIFT_TOLERANCE_SAMPLES:] = np.nan
        errors[signal] = float(np.nanmax(local))
    return errors


def compare_column_sets(
    run_a_data: dict[str, np.ndarray],
    run_b_data: dict[str, np.ndarray],
    *,
    run_a_label: str,
    run_b_label: str,
    window: SimulationWindow,
    selected_signals: tuple[str, ...],
) -> Measurement:
    """Measure two canonical column sets with ``pyssp_vv``."""
    reference = _trajectory(
        run_a_data, label=run_a_label, selected_signals=selected_signals
    )
    candidate = _trajectory(
        run_b_data, label=run_b_label, selected_signals=selected_signals
    )
    grid = _grid(window)
    comparison = compare(
        reference,
        candidate,
        signals=selected_signals,
        alignment=Alignment(
            grid=grid,
            shift_samples=SHIFT_TOLERANCE_SAMPLES,
            max_gap_samples=None,
        ),
    )
    target = grid.time_grid() if grid is not None else reference.time
    return Measurement(
        comparison=comparison,
        local_shift_errors=_local_shift_errors(
            reference,
            candidate,
            target=target,
            selected_signals=selected_signals,
        ),
    )


def compare_result_sets(
    run_a: ResultSet,
    run_b: ResultSet,
    *,
    window: SimulationWindow,
    selected_signals: tuple[str, ...],
    root_system_name: str,
) -> Measurement:
    """Load two result files and measure them with ``pyssp_vv``."""
    return compare_column_sets(
        _load_columns(run_a, root_system_name=root_system_name),
        _load_columns(run_b, root_system_name=root_system_name),
        run_a_label=run_a.label,
        run_b_label=run_b.label,
        window=window,
        selected_signals=selected_signals,
    )


def comparison_metric_rows(
    measurement: Measurement,
) -> list[dict[str, float | int | str]]:
    """Map ``pyssp_vv`` signal metrics to the repository metrics CSV shape."""
    comparison = measurement.comparison
    rows: list[dict[str, float | int | str]] = []
    for item in comparison.signals:
        rows.append(
            {
                "signal": item.signal,
                "max_abs_error": item.max_abs_error,
                "max_shift_abs_error": measurement.local_shift_errors[item.signal],
                "mean_abs_error": item.mean_abs_error,
                "rmse": item.rmse,
                "run_a_label": comparison.reference_label,
                "run_a_min": item.reference_min,
                "run_a_max": item.reference_max,
                "run_b_label": comparison.candidate_label,
                "run_b_min": item.candidate_min,
                "run_b_max": item.candidate_max,
                "coverage": item.coverage,
                "shift_samples": item.shift_samples,
                "normalisation": item.normalisation,
                "denominator": item.denominator,
                "normalised_max_abs_error": item.normalised_max_abs_error,
                "undefined": ";".join(item.undefined),
            }
        )
    return rows


def comparison_summary(
    measurement: Measurement, *, window: SimulationWindow
) -> dict[str, float | int | str]:
    """Summarize one ``pyssp_vv`` comparison for the local manifest."""
    comparison = measurement.comparison
    metrics = comparison.signals
    rows = comparison_metric_rows(measurement)
    grid = _grid(window)
    finite_rel = [
        float(row["normalised_max_abs_error"])
        for row in rows
        if math.isfinite(float(row["normalised_max_abs_error"]))
    ]
    return {
        "run_a_label": comparison.reference_label,
        "run_b_label": comparison.candidate_label,
        "time_points": int(grid.time_grid().size) if grid is not None else 0,
        "compared_signal_count": len(metrics),
        "max_abs_error": max((item.max_abs_error for item in metrics), default=0.0),
        "max_shift_abs_error": max(
            measurement.local_shift_errors.values(), default=0.0
        ),
        "mean_abs_error": float(np.nanmean([item.mean_abs_error for item in metrics]))
        if metrics
        else 0.0,
        "rmse": float(np.nanmean([item.rmse for item in metrics])) if metrics else 0.0,
        "max_rel_error": max(finite_rel, default=0.0),
        "min_coverage": min((item.coverage for item in metrics), default=0.0),
    }


def write_metrics_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    ensure_parent(path)
    fieldnames = [
        "signal",
        "max_abs_error",
        "max_shift_abs_error",
        "mean_abs_error",
        "rmse",
        "run_a_label",
        "run_a_min",
        "run_a_max",
        "run_b_label",
        "run_b_min",
        "run_b_max",
        "coverage",
        "shift_samples",
        "normalisation",
        "denominator",
        "normalised_max_abs_error",
        "undefined",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
