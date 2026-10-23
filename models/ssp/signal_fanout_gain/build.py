#!/usr/bin/env python3
"""Build the exported signal_fanout_gain model and its baseline study."""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import (  # noqa: E402
    build_fixture,
    package_external_target_named,
)

MODEL_NAME = "signal_fanout_gain"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"


def main() -> int:
    output = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=STUDY_COMPOSITION,
        package=package_external_target_named,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
