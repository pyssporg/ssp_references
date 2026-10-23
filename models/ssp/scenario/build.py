#!/usr/bin/env python3
"""Build the exported scenario model and its baseline study.

The SysML authors the component, its five outputs, the String parameter, and
the model-owned ScenarioSet. The exported model already carries the SSV and
the inline mapping, so the build packages no study scenario.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import build_fixture  # noqa: E402

MODEL_NAME = "scenario"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"


def package_nothing(model_build_dir: Path, descriptor) -> None:
    """Leave the exported SSP as-is; the model owns the scenario."""


def main() -> int:
    output = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=STUDY_COMPOSITION,
        package=package_nothing,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
