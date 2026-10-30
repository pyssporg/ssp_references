#!/usr/bin/env python3
"""Build every legal analysis of variation_attribute_set.

Each analysis composes a model-level configuration that authors its variation
selection. This script asks the adapter for a plan per analysis, builds the legal
ones, and packages each analysis's scenario.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_sysml2.model import load
from pyssp_sysml2.parameters.selection import analysis_plans
from pyssp_workflow.analysis import read_scenario
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind

REPO_ROOT = Path(__file__).resolve().parents[3]

ARCHITECTURE = load(Path(__file__).resolve().parent / "architecture")

PLANS = analysis_plans(ARCHITECTURE)
SELECTIONS = {plan.name: plan.selection for plan in PLANS if plan.legal}
CONFIGURATIONS = {plan.name: plan.configuration for plan in PLANS if plan.legal}


def _validate_plans() -> None:
    invalid = [plan for plan in PLANS if plan.status == "invalid"]
    if invalid:
        details = "; ".join(f"{plan.name}: {plan.detail}" for plan in invalid)
        raise ValueError(f"invalid analysis selection: {details}")


if __name__ == "__main__":
    _validate_plans()
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=tuple(SELECTIONS),
        selections=SELECTIONS,
        configurations=CONFIGURATIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
