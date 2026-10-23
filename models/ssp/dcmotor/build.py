#!/usr/bin/env python3
"""Build the legacy dcmotor SSP body with its SysML-authored experiment."""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import run_legacy_fixture

REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    raise SystemExit(
        run_legacy_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            flatten=True,
            strip_resources=("edrive_mass", "emachine_model", "stimuli_model"),
        )
    )
