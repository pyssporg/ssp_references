#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from workflow.config import REPO_ROOT_ENV_VAR, get_repo_root

REPO_ROOT = get_repo_root()
MODELS_DIR = REPO_ROOT / "models"


def resolve_python_executable() -> str:
    venv_python = REPO_ROOT / "venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    return sys.executable or "python3"


def discover_workflows() -> dict[str, Path]:
    workflows: dict[str, Path] = {}
    for workflow_path in sorted(MODELS_DIR.glob("*/*/build.py")):
        workflows[workflow_path.parent.name] = workflow_path
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

    env = os.environ.copy()
    env[REPO_ROOT_ENV_VAR] = str(REPO_ROOT)
    python_executable = resolve_python_executable()

    for model in models:
        subprocess.run(
            [python_executable, str(workflows[model])],
            check=True,
            cwd=REPO_ROOT,
            env=env,
        )
    return 0


def cmd_run_all() -> int:
    workflows = discover_workflows()
    env = os.environ.copy()
    env[REPO_ROOT_ENV_VAR] = str(REPO_ROOT)
    python_executable = resolve_python_executable()
    for model in workflows:
        subprocess.run(
            [python_executable, str(workflows[model])],
            check=True,
            cwd=REPO_ROOT,
            env=env,
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
