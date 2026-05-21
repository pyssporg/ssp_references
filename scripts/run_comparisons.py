#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from workflow.comparison import ComparisonBatchRequest, compare_run_batch
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
    for spec in specs:
        layout = spec.layout
        setup = SimulationSetup.from_manifest(layout.setup_manifest_path)
        selected_backends = tuple(str(backend).lower() for backend in (args.backends or setup.backends))
        missing_backends = [backend for backend in selected_backends if backend not in setup.backends]
        if missing_backends:
            raise ValueError(
                f"Backends {missing_backends} are not listed in {layout.setup_manifest_path}"
            )
        if len(selected_backends) < 2:
            print(
                f"Skipping {spec.model_name}/{spec.case_name}: "
                f"need at least two backends for comparison"
            )
            skipped += 1
            continue

        runs = tuple(
            SimulationRun.from_manifest(layout.simulation_manifest_path(backend))
            for backend in selected_backends
        )
        result = compare_run_batch(ComparisonBatchRequest(runs=runs))
        print(result.manifest_path)
        for comparison in result.comparisons:
            print(comparison.manifest_path)
            print(comparison.metrics_path)
        print(result.summary)

    if skipped:
        print(f"Skipped {skipped} case(s) with fewer than two backends")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
