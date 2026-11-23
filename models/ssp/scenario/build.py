#!/usr/bin/env python3
"""Build the exported scenario model and its baseline analysis.

The FMU definitions are canonical in ``models/fmu/scenario/architecture/`` and
passed to the loader as an include root beside this directory's own
``architecture/scenario.sysml``, which holds the system composition and the
``baseline`` analysis. This directory authors the model-owned ScenarioSet. The
exported model already carries the SSV and the inline mapping, so the build
applies no analysis scenario.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        analyses=("baseline",),
        includes=(REPO_ROOT / "models" / "fmu" / "scenario" / "architecture",),
    )
    raise SystemExit(report_builds(builds))
