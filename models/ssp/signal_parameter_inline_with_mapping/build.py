#!/usr/bin/env python3
"""Build the exported signal_parameter_inline_with_mapping model and study.

Parameter form: inline root values plus an external SSM resource referenced by
the binding.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import package_inline_with_mapping

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=package_inline_with_mapping,
        )
    )
