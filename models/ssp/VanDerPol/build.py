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

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import StudyBuild, package_nothing, run_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            studies=(
                StudyBuild("baseline", package=package_nothing),
                "fast",
                "slow",
            ),
            # The shared VanDerPol FMU declares both ModelExchange and
            # CoSimulation; the pyssp_standard FMI2 reader keeps only the first
            # interface, so it reports ModelExchange and rejects CoSimulation.
            validate_fmus=False,
        )
    )
