#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from workflow.registry import RegistryReferenceCsv, default_registry_path, load_registry
from workflow.setup import SimulationSetup
from workflow.simulate import SimulationRun
from utils.config import REPO_ROOT
from utils.csv import load_numeric_csv, normalize_column_name, unpack_mat_to_csv


@dataclass(frozen=True)
class EngineSeries:
    engine: str
    time: list[float]
    values_by_variable: dict[str, list[float]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate comparative time-series plots from registered simulation outputs."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=default_registry_path(),
        help="Path to the simulation registry JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts") / "plots",
        help="Directory where PNG plots will be written.",
    )
    parser.add_argument(
        "--model",
        dest="models",
        action="append",
        help="Limit plotting to the named model. Repeat to select multiple models.",
    )
    parser.add_argument(
        "--case",
        dest="cases",
        action="append",
        help="Limit plotting to the named case. Repeat to select multiple cases.",
    )
    parser.add_argument(
        "--backend",
        dest="backends",
        action="append",
        help="Limit plotting to the named backend. Repeat to select multiple backends.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=160,
        help="PNG output resolution.",
    )
    return parser.parse_args()


def _sanitize_filename(value: str) -> str:
    cleaned = []
    for character in value:
        cleaned.append(character if character.isalnum() or character in {"-", "_", "."} else "_")
    result = "".join(cleaned).strip("._")
    return result or "variable"


def _load_engine_series(run: SimulationRun, setup: SimulationSetup) -> EngineSeries:
    result_path = run.result_path
    if not result_path.is_file():
        mat_path = setup.layout.simulation_mat_path(run.request.backend)
        if mat_path.is_file():
            result_path = unpack_mat_to_csv(mat_path, result_path)
        else:
            raise FileNotFoundError(
                f"Missing result file for {setup.model_name}/{setup.case_name}/{run.request.backend}"
            )

    payload = load_numeric_csv(
        result_path,
        engine=run.request.backend,
        root_system_name=setup.root_system_name,
    )["columns"]

    time_series = payload.get("time")
    if time_series is None:
        raise KeyError(f"Result file does not contain a time column: {result_path}")

    values_by_variable: dict[str, list[float]] = {}
    for raw_name, series in payload.items():
        if raw_name == "time":
            continue
        canonical_name = normalize_column_name(
            raw_name,
            engine=run.request.backend,
            root_system_name=setup.root_system_name,
        )
        values_by_variable[canonical_name] = series.tolist()

    return EngineSeries(
        engine=run.request.backend,
        time=time_series.tolist(),
        values_by_variable=values_by_variable,
    )


def _load_reference_series(reference: RegistryReferenceCsv, setup: SimulationSetup) -> EngineSeries:
    result_path = reference.path
    if not result_path.is_absolute():
        result_path = (REPO_ROOT / result_path).resolve()
    if not result_path.is_file():
        raise FileNotFoundError(
            f"Missing reference CSV for {setup.model_name}/{setup.case_name}/{reference.label}: {result_path}"
        )

    payload = load_numeric_csv(
        result_path,
        root_system_name=f"default.{setup.model_name}",
    )["columns"]

    time_series = payload.get("time")
    if time_series is None:
        raise KeyError(f"Reference CSV does not contain a time column: {result_path}")

    values_by_variable: dict[str, list[float]] = {}
    for raw_name, series in payload.items():
        if raw_name == "time":
            continue
        canonical_name = normalize_column_name(
            raw_name,
            root_system_name=f"default.{setup.model_name}",
        )
        values_by_variable[canonical_name] = series.tolist()

    return EngineSeries(
        engine=reference.label,
        time=time_series.tolist(),
        values_by_variable=values_by_variable,
    )


def _plot_variable(
    *,
    output_path: Path,
    model_name: str,
    case_name: str,
    variable: str,
    series_by_engine: dict[str, EngineSeries],
    dpi: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 6))
    for engine, series in series_by_engine.items():
        ax.plot(series.time, series.values_by_variable[variable], label=engine, linewidth=1.2)

    ax.set_title(f"{model_name}/{case_name} - {variable}")
    ax.set_xlabel("time")
    ax.set_ylabel(variable)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    registry = load_registry(args.registry)
    specs = registry.expand(
        model_names=args.models,
        case_names=args.cases,
        backend_names=args.backends,
    )
    if not specs:
        raise ValueError("No simulation cases matched the selected registry filters")

    created = 0
    skipped = 0
    for spec in specs:
        setup = SimulationSetup.from_manifest(spec.layout.setup_manifest_path)
        runs: list[SimulationRun] = []
        for backend in setup.backends:
            manifest_path = spec.layout.simulation_manifest_path(backend)
            if not manifest_path.is_file():
                skipped += 1
                continue
            runs.append(SimulationRun.from_manifest(manifest_path))

        if not runs:
            skipped += 1
            continue

        engine_series: dict[str, EngineSeries] = {}
        for run in runs:
            engine_series[run.request.backend] = _load_engine_series(run, setup)
        for reference in spec.reference_csvs:
            engine_series[reference.label] = _load_reference_series(reference, setup)

        variables = [
            variable
            for variable in dict.fromkeys(setup.compare_signals)
            if any(variable in series.values_by_variable for series in engine_series.values())
        ]
        if not variables:
            skipped += 1
            continue

        for variable in variables:
            available = {
                engine: series
                for engine, series in engine_series.items()
                if variable in series.values_by_variable
            }
            if not available:
                continue

            output_path = (
                args.output_dir
                / _sanitize_filename(setup.model_name)
                / _sanitize_filename(setup.case_name)
                / f"{_sanitize_filename(variable)}.png"
            )
            _plot_variable(
                output_path=output_path,
                model_name=setup.model_name,
                case_name=setup.case_name,
                variable=variable,
                series_by_engine=available,
                dpi=args.dpi,
            )
            print(output_path)
            created += 1

    print(f"Created {created} plots; skipped {skipped} cases or runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
