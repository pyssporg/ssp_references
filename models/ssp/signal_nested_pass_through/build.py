#!/usr/bin/env python3
"""Build the exported signal_nested_pass_through model and its baseline study.

The SysML authors the nested ``Inner`` system, its boundary ports, and the
boundary-to-component wiring. A post-processing step applies the scenario as
inline component parameters.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.packaging import apply_inline_components

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("baseline",),
    )
    apply_inline_components(builds["baseline"])
    raise SystemExit(report_builds(builds))
