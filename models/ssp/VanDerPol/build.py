#!/usr/bin/env python3
"""Build the VanDerPol model and its baseline and fast studies.

The SysML authors the single ``VanDerPol`` component with its ``x0``/``x1``
outputs and ``mu`` parameter connector. The baseline study applies no scenario
and uses the FMU default ``mu = 1.0``; the fast study packages ``mu = 2.0`` as
a root external SSV+SSM binding.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import build_fixture  # noqa: E402

MODEL_NAME = "VanDerPol"
MODEL_COMPOSITION = "System"
BASELINE_STUDY = "baseline"
FAST_STUDY = "fast"


def package_nothing(model_build_dir: Path, descriptor) -> None:
    """Leave the exported SSP as-is; the baseline applies no scenario."""


def _build(study: str, package=None) -> Path:
    return build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=study,
        package=package,
        # The shared VanDerPol FMU declares both ModelExchange and CoSimulation;
        # the pyssp_standard FMI2 reader keeps only the first interface, so it
        # reports ModelExchange and rejects the CoSimulation component.
        validate_fmus=False,
    )


def main() -> int:
    baseline = _build(BASELINE_STUDY, package=package_nothing)
    fast = _build(FAST_STUDY)
    print(f"Built {MODEL_NAME} {BASELINE_STUDY}: {baseline}")
    print(f"Built {MODEL_NAME} {FAST_STUDY}: {fast}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
