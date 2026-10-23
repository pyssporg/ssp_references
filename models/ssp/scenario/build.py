#!/usr/bin/env python3
"""Build the exported scenario model and its baseline study.

The SysML authors the component, its five outputs, the String parameter, and
the model-owned ScenarioSet. The exported model already carries the SSV and
the inline mapping, so the build packages no study scenario.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import package_nothing, run_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            package=package_nothing,
        )
    )
