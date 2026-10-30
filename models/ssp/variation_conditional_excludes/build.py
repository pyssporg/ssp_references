#!/usr/bin/env python3
"""Build the legal analyses of variation_conditional_excludes.

``SineExcludesHighGain`` is authored as a SysML constraint and asserted in every
analysis because the scenario point lives on the analysis, not on ``System``.
Each analysis composes a configuration that binds the source point and carries
its own scenario feature value; the adapter derives the selection and evaluates
the constraint. This script builds the ``legal`` plans and pins the documented
partition: ``sine_high`` is authored to be ``violated`` and must never reach
``build_fixture``.
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

#: The analyses this fixture claims the architecture admits and rejects.
EXPECTED_LEGAL = ("step_baseline", "step_high", "sine_baseline")
EXPECTED_VIOLATED = ("sine_high",)

PLANS = analysis_plans(ARCHITECTURE)
SELECTIONS = {plan.name: plan.selection for plan in PLANS if plan.legal}
CONFIGURATIONS = {plan.name: plan.configuration for plan in PLANS if plan.legal}


def _validate_partition() -> None:
    legal = tuple(plan.name for plan in PLANS if plan.legal)
    violated = tuple(plan.name for plan in PLANS if plan.status == "violated")
    invalid = [plan for plan in PLANS if plan.status == "invalid"]
    if invalid:
        details = "; ".join(f"{plan.name}: {plan.detail}" for plan in invalid)
        raise ValueError(f"invalid analysis selection: {details}")
    if (legal, violated) != (EXPECTED_LEGAL, EXPECTED_VIOLATED):
        raise ValueError(
            "authored selection partition changed: "
            f"legal={legal!r}, violated={violated!r}"
        )


if __name__ == "__main__":
    _validate_partition()
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
