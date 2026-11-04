#!/usr/bin/env python3
"""Build the exported signal_nested_algebraic_loop model and its baseline analysis."""

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
        mapping="flatten",
    )
    raise SystemExit(report_builds(builds))
