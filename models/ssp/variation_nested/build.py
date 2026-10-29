#!/usr/bin/env python3
"""Build variation_nested with one analysis per outer and inner selection.

The outer point ``System.path`` chooses between a direct gain and a nested path;
the nested body carries the inner point ``path.stage``. Analysis keys are rooted at
the Analysis composition (``sut.``), model keys at ``System``.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.analysis import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

SELECTIONS = {
    "direct": {
        "analysis": {"sut.path": "directPath"},
        "model": {"path": "directPath"},
    },
    "nested_gain": {
        "analysis": {"sut.path": "nestedPath", "sut.path.inner_stage": "gainStage"},
        "model": {"path": "nestedPath", "path.inner_stage": "gainStage"},
    },
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=("direct", "nested_gain"),
        selections=SELECTIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
