#!/usr/bin/env python3
"""Build the exported Stair model and its baseline study.

The SysML authors the single ``Stair`` component with its integer ``counter``
output. The fixture exposes no tunable parameters, so the build packages no
scenario.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import package_nothing, run_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            package=package_nothing,
            # The shared Stair FMU declares both ModelExchange and CoSimulation;
            # the pyssp_standard FMI2 reader keeps only the first interface, so
            # it reports ModelExchange and rejects the CoSimulation component.
            validate_fmus=False,
        )
    )
