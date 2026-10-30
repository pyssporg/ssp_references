#!/usr/bin/env python3
"""Build the legal combinations of variation_conditional_excludes.

``SineExcludesHighGain`` is authored as a SysML constraint and the adapter owns
the rule: it captures the constraint and evaluates it after variation
selection. This build script only partitions the authored table: ``AUTHORED``
holds every source/scenario combination the architecture composes,
``_selection_is_legal`` asks the adapter, and only the legal subset reaches
``build_fixture``. The pruned subset is kept in ``PRUNED`` so the test can
assert the partition.

The model scope must resolve every analysis scenario usage because the adapter
collects attribute usages from every analysis that composes ``System``, not just
the one being built. ``MODEL_SCENARIOS`` therefore names all four usages.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_sysml2.model import load
from pyssp_sysml2.parameters.constraints import evaluate
from pyssp_workflow.analysis import read_scenario
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind

REPO_ROOT = Path(__file__).resolve().parents[3]

ARCHITECTURE = load(Path(__file__).resolve().parent / "architecture")

#: Every analysis the architecture composes, with its model-scope choices.
AUTHORED = {
    "step_baseline": {"source": "stepImplementation", "scenario": "baseline"},
    "step_high": {"source": "stepImplementation", "scenario": "highGain"},
    "sine_baseline": {"source": "sineImplementation", "scenario": "baseline"},
    "sine_high": {"source": "sineImplementation", "scenario": "highGain"},
}

MODEL_SCENARIOS = {
    "step_baseline_scenario": "baseline",
    "step_high_scenario": "highGain",
    "sine_baseline_scenario": "baseline",
    "sine_high_scenario": "highGain",
}


def _scoped(analysis: str, source: str, scenario: str) -> dict[str, dict[str, str]]:
    return {
        "analysis": {
            "sut.source": source,
            f"{analysis}_scenario": scenario,
        },
        "model": {"source": source, **MODEL_SCENARIOS},
    }


#: Every selection the architecture composes, before the adapter's rule.
SCOPED = {
    analysis: _scoped(analysis, choice["source"], choice["scenario"])
    for analysis, choice in AUTHORED.items()
}


def _selection_is_legal(analysis: str, scoped: dict[str, dict[str, str]]) -> bool:
    """Ask the adapter whether a selection satisfies the authored rule.

    Both the composition scope and the analysis scope are checked; a scope that
    carries no constraint returns an empty report.
    """
    for composition, selections in (
        ("System", scoped["model"]),
        (analysis, scoped["analysis"]),
    ):
        report = evaluate(ARCHITECTURE, composition, selections)
        if report.failed or report.invalid:
            return False
    return True


SELECTIONS = {
    analysis: scoped
    for analysis, scoped in SCOPED.items()
    if _selection_is_legal(analysis, scoped)
}
PRUNED = {
    analysis: scoped
    for analysis, scoped in SCOPED.items()
    if not _selection_is_legal(analysis, scoped)
}


def _validate_guard() -> None:
    expected_scenarios = {
        f"{analysis}_scenario": choice["scenario"]
        for analysis, choice in AUTHORED.items()
    }
    if MODEL_SCENARIOS != expected_scenarios:
        raise ValueError(
            "MODEL_SCENARIOS must name every authored analysis scenario; "
            f"expected {expected_scenarios!r}"
        )
    for analysis, scoped in SELECTIONS.items():
        if not _selection_is_legal(analysis, scoped):
            raise ValueError(f"selection '{analysis}' violates the authored constraint")
    for analysis, scoped in PRUNED.items():
        if _selection_is_legal(analysis, scoped):
            raise ValueError(f"pruned selection '{analysis}' is legal")


if __name__ == "__main__":
    _validate_guard()
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        analyses=tuple(SELECTIONS),
        selections=SELECTIONS,
    )
    for built in builds.values():
        scenario = read_scenario(built.descriptor)
        bind(built, scenario.ssv_path, ssm=scenario.ssm_path)
    raise SystemExit(report_builds(builds))
