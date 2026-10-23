#!/usr/bin/env python3
"""Build the exported signal_step_gain model and its test_baseline study."""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            studies=("test_baseline",),
        )
    )
