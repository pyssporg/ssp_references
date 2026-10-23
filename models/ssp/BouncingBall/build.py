#!/usr/bin/env python3
"""Build the exported BouncingBall model and its baseline study.

The SysML authors the single ``BouncingBall`` component with its ``h`` and
``v`` outputs and the ``g``/``e`` parameter connectors. The fixture applies no
scenario, so the build packages none.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import build_fixture  # noqa: E402

MODEL_NAME = "BouncingBall"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"


def package_nothing(model_build_dir: Path, descriptor) -> None:
    """Leave the exported SSP as-is; this fixture applies no scenario."""


def main() -> int:
    output = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=STUDY_COMPOSITION,
        package=package_nothing,
        # The shared BouncingBall FMU declares both ModelExchange and
        # CoSimulation; the pyssp_standard FMI2 reader keeps only the first
        # interface, so it reports ModelExchange and rejects the CoSimulation
        # component.
        validate_fmus=False,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
