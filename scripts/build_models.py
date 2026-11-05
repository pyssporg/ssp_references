#!/usr/bin/env python3
"""Thin wrapper around the per-fixture build scripts.

Two fixture roots contribute buildable models, scanned in two phases:

* ``models/fmu/*/build.py`` — the FMU phase, scanned first. A script counts
  only when an ``architecture/`` directory sits next to it, so the prepared
  FMUs and Modelica FMU *sources* (``Modelica.Blocks.*``) stay inputs to other
  fixtures rather than models of their own.
* ``models/ssp/*/build.py`` — the SSP phase, scanned second.

A name may appear in both roots: that is one workflow that builds the FMU and
then the SSP. Two scripts for one name in the same phase are an authoring
error. ``run-all`` finishes every FMU build before it starts any SSP build.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SSP_MODELS_DIR = REPO_ROOT / "models" / "ssp"
FMU_MODELS_DIR = REPO_ROOT / "models" / "fmu"

PHASES = ("fmu_build", "ssp_build")


@dataclass(frozen=True)
class Workflow:
    """The build scripts for one model, at most one per phase."""

    name: str
    fmu_build: Path | None = None
    ssp_build: Path | None = None

    def steps(self) -> tuple[Path, ...]:
        """The scripts to run, FMU before SSP."""
        return tuple(
            script for script in (self.fmu_build, self.ssp_build) if script is not None
        )


def _scan(root: Path, *, require_architecture: bool) -> list[Path]:
    scripts = sorted(root.glob("*/build.py"))
    if require_architecture:
        return [s for s in scripts if (s.parent / "architecture").is_dir()]
    return scripts


def _record(
    workflows: dict[str, Workflow], name: str, phase: str, script: Path
) -> None:
    workflow = workflows.setdefault(name, Workflow(name))
    existing = getattr(workflow, phase)
    if existing is not None:
        raise ValueError(
            f"Model {name!r} has two {phase.removesuffix('_build')} build scripts: "
            f"{existing} and {script}"
        )
    workflows[name] = replace(workflow, **{phase: script})


def discover_workflows() -> dict[str, Workflow]:
    """Every buildable fixture, keyed by model name, in build order."""
    workflows: dict[str, Workflow] = {}
    for script in _scan(FMU_MODELS_DIR, require_architecture=True):
        _record(workflows, script.parent.name, "fmu_build", script)
    for script in _scan(SSP_MODELS_DIR, require_architecture=False):
        _record(workflows, script.parent.name, "ssp_build", script)
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


def _run(script: Path) -> None:
    subprocess.run([sys.executable, str(script)], check=True, cwd=REPO_ROOT)


def cmd_list() -> int:
    for name in sorted(discover_workflows()):
        print(name)
    return 0


def cmd_run(models: list[str]) -> int:
    workflows = discover_workflows()
    missing = [model for model in models if model not in workflows]
    if missing:
        raise KeyError(f"Unknown workflow(s): {', '.join(sorted(missing))}")

    for model in models:
        for script in workflows[model].steps():
            _run(script)
    return 0


def cmd_run_all() -> int:
    workflows = discover_workflows()
    for phase in PHASES:
        for workflow in workflows.values():
            script = getattr(workflow, phase)
            if script is not None:
                _run(script)
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
