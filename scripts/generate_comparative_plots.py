#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "matplotlib-cache"))

from pyssp_simulate import read_result_csv
from pyssp_vv.measure import Trajectory, build_figure_spec, render_figure

from utils.config import REPO_ROOT
from workflow.registry import RegistryReferenceCsv, default_registry_path, load_registry
from workflow.setup import SimulationSetup
from workflow.simulate import SimulationRun


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


def _trajectory(values, *, label: str, source: Path) -> Trajectory:
    names = values.dtype.names or ()
    if "time" not in names:
        raise KeyError(f"Result file does not contain a time column: {source}")
    return Trajectory(
        time=values["time"],
        channels={name: values[name] for name in names if name != "time"},
        label=label,
    )


def _load_engine_series(run: SimulationRun, setup: SimulationSetup) -> Trajectory:
    result_path = run.result_path
    if not result_path.is_file():
        raise FileNotFoundError(
            f"Missing result file for {setup.model_name}/{setup.case_name}/{run.request.backend}"
        )

    return _trajectory(
        read_result_csv(result_path, setup.root_system_name, prefix="fmu."),
        label=run.request.backend,
        source=result_path,
    )


def _load_reference_series(reference: RegistryReferenceCsv, setup: SimulationSetup) -> Trajectory:
    result_path = reference.path
    if not result_path.is_absolute():
        result_path = (REPO_ROOT / result_path).resolve()
    if not result_path.is_file():
        raise FileNotFoundError(
            f"Missing reference CSV for {setup.model_name}/{setup.case_name}/{reference.label}: {result_path}"
        )

    return _trajectory(
        read_result_csv(result_path, prefix=f"default.{setup.model_name}."),
        label=reference.label,
        source=result_path,
    )


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

        trajectories: dict[str, Trajectory] = {}
        for run in runs:
            trajectories[run.request.backend] = _load_engine_series(run, setup)
        for reference in spec.reference_csvs:
            trajectories[reference.label] = _load_reference_series(reference, setup)

        signals = [
            signal
            for signal in dict.fromkeys(setup.compare_signals)
            if any(signal in trajectory.channels for trajectory in trajectories.values())
        ]
        if not signals:
            skipped += 1
            continue

        for signal in signals:
            available = [
                trajectory for trajectory in trajectories.values() if signal in trajectory.channels
            ]
            output_path = (
                args.output_dir
                / _sanitize_filename(setup.model_name)
                / _sanitize_filename(setup.case_name)
                / f"{_sanitize_filename(signal)}.png"
            )
            render_figure(
                build_figure_spec(
                    available,
                    signal=signal,
                    title=f"{setup.model_name}/{setup.case_name} - {signal}",
                ),
                output_path,
                dpi=args.dpi,
            )
            print(output_path)
            created += 1

    print(f"Created {created} plots; skipped {skipped} cases or runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
