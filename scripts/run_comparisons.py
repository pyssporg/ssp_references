#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from utils.config import REPO_ROOT
from utils.filesystem import reset_dir
from workflow.comparison import ComparisonBatchRequest, compare_run_batch
from workflow.reference import compare_references
from workflow.registry import default_registry_path, load_registry
from workflow.setup import SimulationSetup
from workflow.simulate import SimulationRun


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare registered engine outputs.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=default_registry_path(),
        help="Path to the simulation registry JSON.",
    )
    parser.add_argument(
        "--model",
        dest="models",
        action="append",
        help="Limit comparison to the named model. Repeat to select multiple models.",
    )
    parser.add_argument(
        "--case",
        dest="cases",
        action="append",
        help="Limit comparison to the named case. Repeat to select multiple cases.",
    )
    parser.add_argument(
        "--backend",
        dest="backends",
        action="append",
        help=(
            "Limit comparison to the named backend. Repeat to select multiple "
            "backends. Defaults to all backends listed in setup.json."
        ),
    )
    parser.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit nonzero when any engine-to-engine or reference comparison fails its gate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_registry(args.registry)
    specs = registry.expand(
        model_names=args.models,
        case_names=args.cases,
    )
    if not specs:
        raise ValueError("No simulation cases matched the selected registry filters")

    skipped = 0
    gate_failures: list[str] = []
    for spec in specs:
        layout = spec.layout
        setup = SimulationSetup.from_manifest(layout.setup_manifest_path)
        selected_backends = tuple(str(backend).lower() for backend in (args.backends or setup.backends))
        missing_backends = [backend for backend in selected_backends if backend not in setup.backends]
        if missing_backends:
            raise ValueError(
                f"Backends {missing_backends} are not listed in {layout.setup_manifest_path}"
            )

        runs = tuple(
            SimulationRun.from_manifest(layout.simulation_manifest_path(backend))
            for backend in selected_backends
            if layout.simulation_manifest_path(backend).is_file()
        )
        missing_runs = [
            backend
            for backend in selected_backends
            if not layout.simulation_manifest_path(backend).is_file()
        ]
        if missing_runs:
            print(
                f"Skipping missing simulation manifest(s) for "
                f"{spec.model_name}/{spec.case_name}: {', '.join(missing_runs)}"
            )

        reset_dir(layout.comparison_case_root)

        if len(runs) >= 2:
            result = compare_run_batch(ComparisonBatchRequest(runs=runs))
            print(result.manifest_path)
            for comparison in result.comparisons:
                print(comparison.manifest_path)
                print(comparison.metrics_path)
            print(result.summary)
            if result.gate.status == "fail":
                gate_failures.extend(
                    f"{spec.model_name}/{spec.case_name} engine pair: {reason}"
                    for reason in result.gate.reasons
                )
        else:
            skipped += 1

        for run in runs:
            for reference_run in compare_references(
                run, spec.reference_csvs, repo_root=REPO_ROOT
            ):
                print(reference_run.manifest_path)
                print(reference_run.metrics_path)
                print(reference_run.summary)
                if reference_run.gate.status == "fail":
                    gate_failures.extend(
                        f"{spec.model_name}/{spec.case_name} {run.request.backend} "
                        f"vs {reference_run.request.label}: {reason}"
                        for reason in reference_run.gate.reasons
                    )

    if skipped:
        print(f"Skipped {skipped} case(s) with fewer than two engine results")
    if gate_failures:
        print("Gate failures:")
        for failure in gate_failures:
            print(f"  - {failure}")
        if args.fail_on_gate:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
