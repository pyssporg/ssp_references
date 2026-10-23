#!/usr/bin/env python3
"""Build the exported signal_sine_gain_add model and its baseline study.

Parameter form: one inline root parameter set keyed by the mapped target names
(no external SSV/SSM in the exported model).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import package_inline_root, run_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(Path(__file__).resolve().parent, package=package_inline_root)
    )
