#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from workflow.registry import default_registry_path, load_registry
from workflow.setup import prepare_setup
from workflow.simulate import SimulationRequest, simulate_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run registered SSP simulation cases.")
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
        help="Limit execution to the named model. Repeat to select multiple models.",
    )
    parser.add_argument(
        "--case",
        dest="cases",
        action="append",
        help="Limit execution to the named case. Repeat to select multiple cases.",
    )
    parser.add_argument(
        "--backend",
        dest="backends",
        action="append",
        help="Limit execution to the named backend. Repeat to select multiple backends.",
    )
    return parser.parse_args()


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

    for spec in specs:
        setup = prepare_setup(spec)
        setup.write_manifest()
        for backend in spec.backends:
            request = SimulationRequest(setup=setup, backend=backend)
            run = simulate_backend(request)
            print(run.manifest_path)
            print(run.result_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
