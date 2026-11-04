#!/usr/bin/env python3
"""Build the exported Dahlquist model and its baseline analysis.

The SysML authors the single ``Dahlquist`` component with its ``x`` output and
``k`` parameter connector. The fixture applies no scenario.
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
        # The shared Dahlquist FMU declares both ModelExchange and
        # CoSimulation; the pyssp_standard FMI2 reader keeps only the first
        # interface, so it reports ModelExchange and rejects CoSimulation.
        validate_fmus=False,
    )
    raise SystemExit(report_builds(builds))
