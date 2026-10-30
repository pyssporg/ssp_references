#!/usr/bin/env python3
"""Build the legal combinations of variation_conditional_excludes.

``SineExcludesHighGain`` is authored as a SysML constraint, but the pinned
adapter drops constraints. This build script owns the same rule: ``AUTHORED``
holds every source/scenario combination the architecture composes, ``is_legal``
applies the exclusion, and only the legal subset reaches ``build_fixture``. The
pruned subset is kept in ``PRUNED`` so the test can assert the guard.

The model scope must resolve every analysis scenario usage because the adapter
collects attribute usages from every analysis that composes ``System``, not just
the one being built. ``MODEL_SCENARIOS`` therefore names all four usages.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.analysis import read_scenario
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind

REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCES = ("stepImplementation", "sineImplementation")
SCENARIOS = ("baseline", "highGain")

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


def is_legal(source: str, scenario: str) -> bool:
    """Evaluate ``SineExcludesHighGain`` over one selection."""
    if source not in SOURCES:
        raise ValueError(f"unknown source variant: {source!r}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario variant: {scenario!r}")
    return not (source == "sineImplementation" and scenario == "highGain")


def _scoped(analysis: str, source: str, scenario: str) -> dict[str, dict[str, str]]:
    return {
        "analysis": {
            "sut.source": source,
            f"{analysis}_scenario": scenario,
        },
        "model": {"source": source, **MODEL_SCENARIOS},
    }


SELECTIONS = {
    analysis: _scoped(analysis, choice["source"], choice["scenario"])
    for analysis, choice in AUTHORED.items()
    if is_legal(choice["source"], choice["scenario"])
}
PRUNED = {
    analysis: _scoped(analysis, choice["source"], choice["scenario"])
    for analysis, choice in AUTHORED.items()
    if not is_legal(choice["source"], choice["scenario"])
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
    for analysis, choice in AUTHORED.items():
        legal = is_legal(choice["source"], choice["scenario"])
        if analysis in SELECTIONS and not legal:
            raise ValueError(f"selection '{analysis}' violates SineExcludesHighGain")
        if analysis in PRUNED and legal:
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
