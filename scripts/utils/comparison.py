from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from itertools import product
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


@dataclass(frozen=True)
class SignalInvariant:
    name: str
    output_signal: str
    input_signals: tuple[str, ...]
    coefficients: tuple[float, ...]

    @property
    def required_signals(self) -> tuple[str, ...]:
        return (self.output_signal, *self.input_signals)


SIGNAL_INVARIANTS: dict[str, tuple[SignalInvariant, ...]] = {
    "signal_step_gain": (
        SignalInvariant(
            name="gain.y = 3.0 * step.y",
            output_signal="gain.y",
            input_signals=("step.y",),
            coefficients=(3.0,),
        ),
    ),
    "signal_step_add": (
        SignalInvariant(
            name="add.y = step_a.y + step_b.y",
            output_signal="add.y",
            input_signals=("step_a.y", "step_b.y"),
            coefficients=(1.0, 1.0),
        ),
    ),
    "signal_fanout_gain": (
        SignalInvariant(
            name="gain_a.y = 2.0 * step.y",
            output_signal="gain_a.y",
            input_signals=("step.y",),
            coefficients=(2.0,),
        ),
        SignalInvariant(
            name="gain_b.y = -1.0 * step.y",
            output_signal="gain_b.y",
            input_signals=("step.y",),
            coefficients=(-1.0,),
        ),
    ),
    "signal_nested_pass_through": (
        SignalInvariant(
            name="add.y = step.y",
            output_signal="add.y",
            input_signals=("step.y",),
            coefficients=(1.0,),
        ),
    ),
}


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


SHIFT_TOLERANCE_SAMPLES = 2


def shift_tolerant_error(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    max_shift: int = SHIFT_TOLERANCE_SAMPLES,
) -> np.ndarray:
    """Absolute error that tolerates a small sample shift in either direction.

    Co-simulation masters may expose a source and its downstream component a
    few communication steps apart. Pointwise error then reports a large spike
    at every discontinuity even when the signals are otherwise identical. This
    metric compares each sample against candidate samples shifted by up to
    ``max_shift`` steps and keeps the smallest error.
    """
    error = np.abs(reference - candidate)
    for shift in range(1, max_shift + 1):
        if error.size <= shift:
            break
        error[shift:] = np.minimum(error[shift:], np.abs(reference[shift:] - candidate[:-shift]))
        error[:-shift] = np.minimum(error[:-shift], np.abs(reference[:-shift] - candidate[shift:]))
    return error


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


def compare_column_sets(
    run_a_data: dict[str, np.ndarray],
    run_b_data: dict[str, np.ndarray],
    *,
    run_a_label: str,
    run_b_label: str,
    engine_a: str | None,
    engine_b: str | None,
    window: SimulationWindow,
    selected_signals: tuple[str, ...],
    root_system_name: str,
) -> tuple[dict, list[dict[str, float | str]]]:
    run_a_signals = _select_signal_series(
        run_a_data,
        selected_signals,
        engine=engine_a,
        root_system_name=root_system_name,
    )
    run_b_signals = _select_signal_series(
        run_b_data,
        selected_signals,
        engine=engine_b,
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
        shift_errors = shift_tolerant_error(run_a_series, run_b_series)
        if shift_errors.size > 2 * SHIFT_TOLERANCE_SAMPLES:
            # The first/last samples are initialization and shutdown artifacts
            # in several engines; they are not comparable transient behavior.
            shift_errors[:SHIFT_TOLERANCE_SAMPLES] = np.nan
            shift_errors[-SHIFT_TOLERANCE_SAMPLES:] = np.nan

        metrics.append(
            {
                "signal": signal,
                "max_abs_error": float(np.nanmax(errors)),
                "max_shift_abs_error": float(np.nanmax(shift_errors)),
                "mean_abs_error": float(np.nanmean(errors)),
                "rmse": float(math.sqrt(np.nanmean(np.square(errors)))),
                "run_a_label": run_a_label,
                "run_a_min": float(np.nanmin(run_a_series)),
                "run_a_max": float(np.nanmax(run_a_series)),
                "run_b_label": run_b_label,
                "run_b_min": float(np.nanmin(run_b_series)),
                "run_b_max": float(np.nanmax(run_b_series)),
            }
        )

    summary = {
        "run_a_label": run_a_label,
        "run_b_label": run_b_label,
        "time_points": int(len(target_times)),
        "compared_signal_count": len(selected_signals),
        "max_abs_error": max((row["max_abs_error"] for row in metrics), default=0.0),
        "max_shift_abs_error": max((row["max_shift_abs_error"] for row in metrics), default=0.0),
        "mean_abs_error": float(np.nanmean([row["mean_abs_error"] for row in metrics])) if metrics else 0.0,
        "rmse": float(np.nanmean([row["rmse"] for row in metrics])) if metrics else 0.0,
    }
    return summary, metrics


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
    return compare_column_sets(
        run_a_data,
        run_b_data,
        run_a_label=run_a.label,
        run_b_label=run_b.label,
        engine_a=run_a.engine,
        engine_b=run_b.engine,
        window=window,
        selected_signals=selected_signals,
        root_system_name=root_system_name,
    )


def signal_invariant_metrics(
    run: ResultSet,
    *,
    model_name: str,
    window: SimulationWindow,
    root_system_name: str,
) -> list[dict[str, float | str]]:
    invariants = SIGNAL_INVARIANTS.get(model_name, ())
    if not invariants:
        return []

    run_data = load_numeric_csv(
        run.path,
        engine=run.engine,
        root_system_name=root_system_name,
    )["columns"]
    run_time = run_data.get("time")
    if run_time is None:
        raise KeyError("Result set must contain a time column")

    required_signals = tuple(
        dict.fromkeys(signal for invariant in invariants for signal in invariant.required_signals)
    )
    signal_series = _select_signal_series(
        run_data,
        required_signals,
        engine=run.engine,
        root_system_name=root_system_name,
    )
    target_times = build_time_grid(window)
    # Co-simulation masters may expose a source and its downstream component
    # one communication step apart around a discontinuity. Accept either the
    # current or the previous sample for the input side of the invariant.
    previous_times = target_times - window.interval

    rows: list[dict[str, float | str]] = []
    for invariant in invariants:
        output_series = resample_series(
            run_time,
            signal_series[invariant.output_signal],
            target_times,
        )
        current_inputs = [
            coefficient
            * resample_series(run_time, signal_series[signal], target_times)
            for signal, coefficient in zip(invariant.input_signals, invariant.coefficients)
        ]
        previous_inputs = [
            coefficient
            * resample_series(run_time, signal_series[signal], previous_times)
            for signal, coefficient in zip(invariant.input_signals, invariant.coefficients)
        ]
        # Each input may independently be one communication step behind.
        expected_candidates = [
            sum(
                previous_inputs[index] if lag else current_inputs[index]
                for index, lag in enumerate(lags)
            )
            for lags in product((False, True), repeat=len(current_inputs))
        ]
        residual = np.nanmin(
            np.stack([np.abs(output_series - expected) for expected in expected_candidates]),
            axis=0,
        )
        # The first recorded sample is an initialization artifact for engines
        # that start recording one communication step after t0; do not judge it
        # as an algebraic error.
        finite_times = run_time[np.isfinite(run_time)]
        if finite_times.size:
            first_index = int(np.searchsorted(target_times, finite_times.min()))
            residual[: first_index + 1] = np.nan
        rows.append(
            {
                "run_label": run.label,
                "invariant": invariant.name,
                "max_abs_error": float(np.nanmax(residual)),
                "mean_abs_error": float(np.nanmean(residual)),
                "rmse": float(math.sqrt(np.nanmean(np.square(residual)))),
            }
        )

    return rows


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
        "max_shift_abs_error",
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
