#!/usr/bin/env python3
"""Build the exported scenario model and its baseline analysis.

The SysML authors the component, its five outputs, the String parameter, and
the model-owned ScenarioSet. The exported model already carries the SSV and
the inline mapping, so the build applies no analysis scenario.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=("baseline",),
    )
    raise SystemExit(report_builds(builds))
