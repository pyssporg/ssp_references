#!/usr/bin/env python3
"""Build the exported signal_parameter_inline_with_mapping model and analysis.

Parameter form: inline root values plus an external SSM resource referenced by
the binding.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.analysis import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=("baseline",),
    )
    scenario = read_scenario(builds["baseline"].descriptor)
    bind(
        builds["baseline"],
        scenario.ssv_path,
        ssm=scenario.ssm_path,
        mode="inline",
    )
    raise SystemExit(report_builds(builds))
