#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_ROOT))

from workflow.config import MODELS_DIR, REPO_ROOT_ENV_VAR, get_repo_root

REPO_ROOT = get_repo_root()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one or more per-model simulate.py scripts."
    )
    parser.add_argument("models", nargs="+", help="Model names under models/*/<model_name>.")
    return parser.parse_args()


def find_model_script(model_name: str) -> Path:
    matches = sorted(MODELS_DIR.glob(f"*/{model_name}"))
    if not matches:
        raise FileNotFoundError(f"Model directory not found for {model_name}")
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous model name {model_name}: {matches}")
    script_path = matches[0] / "simulate.py"
    if not script_path.is_file():
        raise FileNotFoundError(f"simulate.py not found for {model_name}")
    return script_path


def resolve_python_executable() -> str:
    venv_python = REPO_ROOT / "venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    return sys.executable or "python3"


def main() -> int:
    args = parse_args()
    env = os.environ.copy()
    env[REPO_ROOT_ENV_VAR] = str(REPO_ROOT)
    python_executable = resolve_python_executable()
    for model_name in args.models:
        subprocess.run(
            [python_executable, str(find_model_script(model_name))],
            check=True,
            cwd=REPO_ROOT,
            env=env,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
