#!/usr/bin/env python3
"""Build variation_body_gain with one study per path body.

The single variation point ``System.path`` chooses between a body with one Gain
and a body with a Product feeding a Gain; each study selects one variant.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

REPO_ROOT = Path(__file__).resolve().parents[3]

SELECTIONS = {
    "one_stage": {"study": {"sut.path": "oneStage"}, "model": {"path": "oneStage"}},
    "two_stages": {
        "study": {"sut.path": "twoStages"},
        "model": {"path": "twoStages"},
    },
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("one_stage", "two_stages"),
        selections=SELECTIONS,
    )
    raise SystemExit(report_builds(builds))
