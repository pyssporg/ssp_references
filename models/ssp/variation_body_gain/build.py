#!/usr/bin/env python3
"""Build variation_body_gain with one analysis per path body.

The single variation point ``System.path`` chooses between a body with one Gain
and a body with a Product feeding a Gain; each analysis selects one variant. Each
analysis packages its own scenario SSV and SSM into the exported SSP.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.analysis import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

SELECTIONS = {
    "one_stage": {"analysis": {"sut.path": "oneStage"}, "model": {"path": "oneStage"}},
    "two_stages": {
        "analysis": {"sut.path": "twoStages"},
        "model": {"path": "twoStages"},
    },
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=("one_stage", "two_stages"),
        selections=SELECTIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
