#!/usr/bin/env python3
"""Build variation_attribute_set; each analysis selects its variants and packages its scenario SSP."""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.analysis import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

MODEL_SELECTION = {
    "nominal_scenario": "nominalK3",
    "boosted_scenario": "boostedK9",
}

SELECTIONS = {
    "nominal_k3": {
        "analysis": {"nominal_scenario": "nominalK3"},
        "model": MODEL_SELECTION,
    },
    "boosted_k9": {
        "analysis": {"boosted_scenario": "boostedK9"},
        "model": MODEL_SELECTION,
    },
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=("nominal_k3", "boosted_k9"),
        selections=SELECTIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
