#!/usr/bin/env python3
"""Build the exported signal_fanout_gain model and its baseline study."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import (  # noqa: E402
    package_external_target_named,
    run_fixture,
)

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            package=package_external_target_named,
        )
    )
