#!/usr/bin/env python3
"""Build the exported signal_sine_gain_add model and its baseline study.

Parameter form: one inline root parameter set keyed by the mapped target names
(no external SSV/SSM in the exported model).
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import package_inline_root

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=package_inline_root,
        )
    )
