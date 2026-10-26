#!/usr/bin/env python3
"""Build the exported signal_step_gain model and its test_baseline study.

Parameter form: one root external SSV+SSM binding applied after the model build.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import ExternalStudy, apply_bindings

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("test_baseline",),
    )
    apply_bindings(builds["test_baseline"], ExternalStudy())
    raise SystemExit(report_builds(builds))
