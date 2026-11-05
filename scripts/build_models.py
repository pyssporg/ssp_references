#!/usr/bin/env python3
"""Thin wrapper around the per-fixture build scripts.

Two fixture roots contribute buildable models:

* ``models/ssp/*/build.py`` — SysML-authored SSP fixtures.
* ``models/fmu/<name>/build.py`` — SysML-authored FMI fixtures, recognised by
  an ``architecture/`` directory next to the script.

``models/fmu/`` also holds Modelica FMU *sources* (``Modelica.Blocks.*``); their
``build.py`` rebuilds an FMU from a ``.mo`` file with ``omc``. They have no
``architecture/`` directory, they are inputs to other fixtures, and they are not
part of ``run`` or ``run-all``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SSP_MODELS_DIR = REPO_ROOT / "models" / "ssp"
FMU_MODELS_DIR = REPO_ROOT / "models" / "fmu"


def discover_workflows() -> dict[str, Path]:
    """Every buildable fixture, keyed by model name, in build order."""
    workflows: dict[str, Path] = {}

    def add(name: str, workflow_path: Path) -> None:
        if name in workflows:
            raise ValueError(
                f"Model name {name!r} is used by both "
                f"{workflows[name]} and {workflow_path}"
            )
        workflows[name] = workflow_path

    for workflow_path in sorted(SSP_MODELS_DIR.glob("*/build.py")):
        add(workflow_path.parent.name, workflow_path)

    for workflow_path in sorted(FMU_MODELS_DIR.glob("*/build.py")):
        if not (workflow_path.parent / "architecture").is_dir():
            continue
        add(workflow_path.parent.name, workflow_path)

    return workflows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Thin wrapper around per-model build.py scripts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List models that provide build.py.")
    subparsers.add_parser("run-all", help="Run every discovered model build script.")

    run_parser = subparsers.add_parser("run", help="Run one or more model build scripts.")
    run_parser.add_argument("models", nargs="+", help="Model names to run.")
    return parser.parse_args()


def cmd_list() -> int:
    for name in discover_workflows():
        print(name)
    return 0


def cmd_run(models: list[str]) -> int:
    workflows = discover_workflows()
    missing = [model for model in models if model not in workflows]
    if missing:
        raise KeyError(f"Unknown workflow(s): {', '.join(sorted(missing))}")

    for model in models:
        subprocess.run(
            [sys.executable, str(workflows[model])],
            check=True,
            cwd=REPO_ROOT,
        )
    return 0


def cmd_run_all() -> int:
    workflows = discover_workflows()
    for model in workflows:
        subprocess.run(
            [sys.executable, str(workflows[model])],
            check=True,
            cwd=REPO_ROOT,
        )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "list":
        return cmd_list()
    if args.command == "run-all":
        return cmd_run_all()
    if args.command == "run":
        return cmd_run(args.models)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
