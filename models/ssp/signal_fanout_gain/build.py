#!/usr/bin/env python3
"""Build the exported signal_fanout_gain model and its baseline study."""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import package_external_target_named

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=package_external_target_named,
        )
    )
