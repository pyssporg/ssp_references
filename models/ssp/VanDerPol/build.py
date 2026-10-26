#!/usr/bin/env python3
"""Build the VanDerPol model and its baseline, fast, and slow studies.

The SysML authors the single ``VanDerPol`` component with its ``x0``/``x1``
outputs and ``mu`` parameter connector. The baseline study applies no scenario
and uses the FMU default ``mu = 1.0``; the fast and slow studies apply
``mu = 2.0`` and ``mu = 0.5`` as root external SSV+SSM bindings.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.study import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("baseline", "fast", "slow"),
        # The shared VanDerPol FMU declares both ModelExchange and
        # CoSimulation; the pyssp_standard FMI2 reader keeps only the first
        # interface, so it reports ModelExchange and rejects CoSimulation.
        validate_fmus=False,
    )
    fast = read_scenario(builds["fast"].descriptor)
    bind(builds["fast"], fast.ssv_path, ssm=fast.ssm_path)
    slow = read_scenario(builds["slow"].descriptor)
    bind(builds["slow"], slow.ssv_path, ssm=slow.ssm_path)
    raise SystemExit(report_builds(builds))
