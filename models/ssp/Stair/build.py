#!/usr/bin/env python3
"""Build the exported Stair model and its baseline study.

The SysML authors the single ``Stair`` component with its integer ``counter``
output. The fixture exposes no tunable parameters, so the build packages no
scenario.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import package_nothing

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=package_nothing,
            # The shared Stair FMU declares both ModelExchange and CoSimulation;
            # the pyssp_standard FMI2 reader keeps only the first interface, so
            # it reports ModelExchange and rejects the CoSimulation component.
            validate_fmus=False,
        )
    )
