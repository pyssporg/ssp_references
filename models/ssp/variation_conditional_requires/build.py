#!/usr/bin/env python3
"""Build the legal combinations of variation_conditional_requires.

``SineRequiresSingleStage`` is authored as a SysML constraint, but the pinned
adapter drops constraints. This build script therefore owns the same rule:
``AUTHORED`` holds every combination the architecture composes, ``is_legal``
applies the implication, and only the legal subset reaches ``build_fixture``.
The pruned subset is kept in ``PRUNED`` so the test can assert the guard.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.analysis import read_scenario
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind

REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCES = ("stepImplementation", "sineImplementation")
GAINS = ("singleStage", "twoStages")

#: Every analysis the architecture composes, with its model-scope choices.
AUTHORED = {
    "step_single": {"source": "stepImplementation", "gain": "singleStage"},
    "step_two": {"source": "stepImplementation", "gain": "twoStages"},
    "sine_single": {"source": "sineImplementation", "gain": "singleStage"},
    "sine_two": {"source": "sineImplementation", "gain": "twoStages"},
}


def is_legal(source: str, gain: str) -> bool:
    """Evaluate ``SineRequiresSingleStage`` over one selection."""
    if source not in SOURCES:
        raise ValueError(f"unknown source variant: {source!r}")
    if gain not in GAINS:
        raise ValueError(f"unknown gain variant: {gain!r}")
    return not (source == "sineImplementation" and gain == "twoStages")


def _scoped(analysis: str, source: str, gain: str) -> dict[str, dict[str, str]]:
    return {
        "analysis": {"sut.source": source, "sut.gain": gain},
        "model": {"source": source, "gain": gain},
    }


SELECTIONS = {
    analysis: _scoped(analysis, choice["source"], choice["gain"])
    for analysis, choice in AUTHORED.items()
    if is_legal(choice["source"], choice["gain"])
}
PRUNED = {
    analysis: _scoped(analysis, choice["source"], choice["gain"])
    for analysis, choice in AUTHORED.items()
    if not is_legal(choice["source"], choice["gain"])
}


def _validate_guard() -> None:
    for analysis, scoped in SELECTIONS.items():
        choice = scoped["model"]
        if not is_legal(choice["source"], choice["gain"]):
            raise ValueError(f"selection '{analysis}' violates SineRequiresSingleStage")
    for analysis, scoped in PRUNED.items():
        choice = scoped["model"]
        if is_legal(choice["source"], choice["gain"]):
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
