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


def discover_simulations() -> dict[str, Path]:
    simulations: dict[str, Path] = {}
    for simulate_path in sorted(MODELS_DIR.glob("*/*/simulate.py")):
        simulations[simulate_path.parent.name] = simulate_path
    return simulations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run per-model simulate.py scripts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List models that provide simulate.py.")
    subparsers.add_parser("run-all", help="Run every discovered model simulate.py script.")
    run_parser = subparsers.add_parser("run", help="Run one or more model simulate.py scripts.")
    run_parser.add_argument("models", nargs="+", help="Model names to run.")
    return parser.parse_args()


def cmd_list() -> int:
    for name in discover_simulations():
        print(name)
    return 0


def cmd_run(models: list[str]) -> int:
    simulations = discover_simulations()
    missing = [model for model in models if model not in simulations]
    if missing:
        raise KeyError(f"Unknown simulation script(s): {', '.join(sorted(missing))}")

    env = os.environ.copy()
    env[REPO_ROOT_ENV_VAR] = str(REPO_ROOT)
    python_executable = resolve_python_executable()
    for model in models:
        subprocess.run([python_executable, str(simulations[model])], check=True, cwd=REPO_ROOT, env=env)
    return 0


def cmd_run_all() -> int:
    return cmd_run(list(discover_simulations()))


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
