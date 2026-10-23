#!/usr/bin/env python3
"""Build the exported signal_nested_pass_through model and its baseline study.

The SysML authors the nested ``Inner`` system, its boundary ports, and the
boundary-to-component wiring. The package hook applies the scenario as inline
component parameters.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import apply_inline_components, run_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            package=apply_inline_components,
        )
    )
