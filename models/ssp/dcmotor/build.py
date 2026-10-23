#!/usr/bin/env python3
"""Build the legacy dcmotor SSP body with its SysML-authored experiment."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.authoring import run_legacy_fixture  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        run_legacy_fixture(
            Path(__file__).resolve().parent,
            flatten=True,
            strip_resources=("edrive_mass", "emachine_model", "stimuli_model"),
        )
    )
