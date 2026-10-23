#!/usr/bin/env python3
"""Build the exported signal_parameter_inline_with_mapping model and study.

Parameter form: inline root values plus an external SSM resource referenced by
the binding.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import (  # noqa: E402
    package_inline_with_mapping,
    run_fixture,
)

if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            package=package_inline_with_mapping,
        )
    )
