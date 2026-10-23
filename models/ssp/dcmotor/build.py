#!/usr/bin/env python3
"""Build the legacy dcmotor SSP body with its SysML-authored experiment."""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import build_legacy_fixture  # noqa: E402

MODEL_NAME = "dcmotor"
STUDY = "baseline"
STRIP_RESOURCES = ("edrive_mass", "emachine_model", "stimuli_model")


def main() -> int:
    output = build_legacy_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        study=STUDY,
        flatten=True,
        strip_resources=STRIP_RESOURCES,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
