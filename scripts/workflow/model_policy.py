"""Model-specific verification policy.

Signal invariants describe algebraic relationships that must hold inside one
run. They are model policy, not generic comparison machinery, so they live in
the workflow layer. Trajectory measurement still comes from ``pyssp_vv``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product

import numpy as np
from pyssp_simulate.result import read_result_csv
from pyssp_vv.measure import Grid, resample

from utils.domain import ResultSet, SimulationWindow


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


def _target_times(window: SimulationWindow) -> np.ndarray:
    grid = Grid(
        start_time=window.start_time,
        stop_time=window.stop_time,
        step_size=window.interval,
    )
    return grid.time_grid()


def _select_series(
    columns: dict[str, np.ndarray],
    required_signals: tuple[str, ...],
) -> dict[str, np.ndarray]:
    missing = [signal for signal in required_signals if signal not in columns]
    if missing:
        raise KeyError(
            "Selected comparison signals missing from result sets: "
            + ", ".join(missing)
        )
    return {signal: columns[signal] for signal in required_signals}


def signal_invariant_rows(
    run: ResultSet,
    *,
    model_name: str,
    window: SimulationWindow,
    root_system_name: str,
) -> list[dict[str, float | str]]:
    """Measure model-specific algebraic invariants for one run."""
    invariants = SIGNAL_INVARIANTS.get(model_name, ())
    if not invariants:
        return []

    data = read_result_csv(run.path, root_system=root_system_name)
    columns = {name: data[name] for name in data.dtype.names or ()}
    run_time = columns.get("time")
    if run_time is None:
        raise KeyError("Result set must contain a time column")

    required_signals = tuple(
        dict.fromkeys(
            signal for invariant in invariants for signal in invariant.required_signals
        )
    )
    signal_series = _select_series(columns, required_signals)
    target_times = _target_times(window)
    # Co-simulation masters may expose a source and its downstream component
    # one communication step apart around a discontinuity. Accept either the
    # current or the previous sample for the input side of the invariant.
    previous_times = target_times - window.interval

    rows: list[dict[str, float | str]] = []
    for invariant in invariants:
        output_series = resample(
            run_time,
            signal_series[invariant.output_signal],
            target_times,
        )
        current_inputs = [
            coefficient * resample(run_time, signal_series[signal], target_times)
            for signal, coefficient in zip(
                invariant.input_signals, invariant.coefficients
            )
        ]
        previous_inputs = [
            coefficient * resample(run_time, signal_series[signal], previous_times)
            for signal, coefficient in zip(
                invariant.input_signals, invariant.coefficients
            )
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
            np.stack(
                [np.abs(output_series - expected) for expected in expected_candidates]
            ),
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
