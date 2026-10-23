#!/usr/bin/env python3
"""Run the registered suite as an audited, parallel campaign.

This is an orchestration layer: simulation and comparison stay in
``run_simulations.py`` and ``run_comparisons.py``. ``sequence_extensions``
adds bounded parallelism, task timeouts, and a JSON-lines run log.

Requires Python 3.11+ (``sequence_extensions`` requirement).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit(
        "run_campaign.py requires Python 3.11+ for sequence_extensions; "
        "use scripts/run_simulations.py and scripts/run_comparisons.py instead."
    )

from sequence_extensions.flow import RunOptions, execute_flow, gather, node

from workflow.registry import default_registry_path, load_registry

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


@node(retries=1, retry_delay_seconds=0.5, timeout=1800.0)
def build_model_task(model: str) -> dict[str, object]:
    return _run(
        [
            sys.executable,
            "scripts/build_models.py",
            "run",
            model,
        ]
    )


@node(retries=1, retry_delay_seconds=0.5, timeout=1800.0)
def simulate_task(
    model: str,
    case: str,
    backend: str,
    *dependencies: object,
) -> dict[str, object]:
    return _run(
        [
            sys.executable,
            "scripts/run_simulations.py",
            "--model",
            model,
            "--case",
            case,
            "--backend",
            backend,
        ]
    )


@node(timeout=600.0)
def compare_task(
    model: str,
    case: str,
    fail_on_gate: bool,
    *simulations: object,
) -> dict[str, object]:
    command = [
        sys.executable,
        "scripts/run_comparisons.py",
        "--model",
        model,
        "--case",
        case,
    ]
    if fail_on_gate:
        command.append("--fail-on-gate")
    return _run(command)


@node
def summarize_campaign(payload: dict[str, object]) -> dict[str, object]:
    results = payload["comparisons"]
    assert isinstance(results, list)
    return {
        "case_count": len(results),
        "failed_cases": [
            result
            for result in results
            if int(result["returncode"]) != 0
        ],
    }


@node(name="ssp-campaign")
def campaign(
    models: tuple[str, ...] = (),
    cases: tuple[str, ...] = (),
    *,
    fail_on_gate: bool = False,
    build: bool = True,
    registry_path: Path | None = None,
) -> dict[str, object]:
    registry = load_registry(registry_path or default_registry_path())
    specs = registry.expand(model_names=models or None, case_names=cases or None)
    if not specs:
        raise ValueError("No simulation cases matched the selected registry filters")

    comparisons = []
    for spec in specs:
        dependencies: tuple[object, ...] = ()
        if build:
            dependencies = (build_model_task.submit(spec.model_name),)

        simulations = [
            simulate_task.submit(
                spec.model_name,
                spec.case_name,
                backend,
                *dependencies,
            )
            for backend in spec.backends
        ]
        comparisons.append(
            compare_task.submit(
                spec.model_name,
                spec.case_name,
                fail_on_gate,
                *simulations,
            )
        )

    return summarize_campaign.submit(gather({"comparisons": comparisons}))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an audited simulation campaign.")
    parser.add_argument("--model", dest="models", action="append", default=[])
    parser.add_argument("--case", dest="cases", action="append", default=[])
    parser.add_argument("--fail-on-gate", action="store_true")
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Use existing model and study artifacts instead of building them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run = execute_flow(
        campaign,
        tuple(args.models),
        tuple(args.cases),
        fail_on_gate=args.fail_on_gate,
        build=not args.no_build,
        options=RunOptions(
            name="ssp-campaign",
            log=str(REPO_ROOT / "artifacts" / "runs"),
            summary=True,
        ),
    )
    result = run.result

    print(result)
    print(f"log: {run.log}")
    return 1 if result["failed_cases"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
