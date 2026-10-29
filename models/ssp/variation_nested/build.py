#!/usr/bin/env python3
"""Build variation_nested with one study per outer and inner selection.

The outer point ``System.path`` chooses between a direct gain and a nested path;
the nested body carries the inner point ``path.stage``. Study keys are rooted at
the Study composition (``sut.``), model keys at ``System``.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.study import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

SELECTIONS = {
    "direct": {
        "study": {"sut.path": "directPath"},
        "model": {"path": "directPath"},
    },
    "nested_gain": {
        "study": {"sut.path": "nestedPath", "sut.path.inner_stage": "gainStage"},
        "model": {"path": "nestedPath", "path.inner_stage": "gainStage"},
    },
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("direct", "nested_gain"),
        selections=SELECTIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
