#!/usr/bin/env python3
"""Build the exported signal_nested_pass_through model and its baseline study.

The SysML authors the nested ``Inner`` system, its boundary ports, and the
boundary-to-component wiring. The package hook applies the scenario as inline
component parameters.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import apply_inline_components

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=apply_inline_components,
        )
    )
