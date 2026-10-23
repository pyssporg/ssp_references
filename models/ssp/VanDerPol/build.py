#!/usr/bin/env python3
"""Build the VanDerPol model and its baseline, fast, and slow studies.

The SysML authors the single ``VanDerPol`` component with its ``x0``/``x1``
outputs and ``mu`` parameter connector. The baseline study applies no scenario
and uses the FMU default ``mu = 1.0``; the fast and slow studies package
``mu = 2.0`` and ``mu = 0.5`` as root external SSV+SSM bindings.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import StudyBuild, build_studies  # noqa: E402

MODEL_NAME = "VanDerPol"
MODEL_COMPOSITION = "System"


def package_nothing(model_build_dir: Path, descriptor) -> None:
    """Leave the exported SSP as-is; the baseline applies no scenario."""


def main() -> int:
    outputs = build_studies(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        studies=(
            StudyBuild("baseline", package=package_nothing),
            StudyBuild("fast"),
            StudyBuild("slow"),
        ),
        # The shared VanDerPol FMU declares both ModelExchange and CoSimulation;
        # the pyssp_standard FMI2 reader keeps only the first interface, so it
        # reports ModelExchange and rejects the CoSimulation component.
        validate_fmus=False,
    )
    for study, path in outputs.items():
        print(f"Built {MODEL_NAME} {study}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
