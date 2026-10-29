#!/usr/bin/env python3
"""Build variation_attribute_set with one study per attribute variant.

The single variation point ``ScenarioChoice`` is used by one attribute per
Study. Each study selects its own attribute; the model export resolves the
points reachable from ``System``, which is none.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

REPO_ROOT = Path(__file__).resolve().parents[3]

# The variation usage sits in the composition, so the model build selects it.
SELECTIONS = {
    "nominal_k3": {"study": {"sut.scenario": "nominalK3"}, "model": {"scenario": "nominalK3"}},
    "boosted_k9": {"study": {"sut.scenario": "boostedK9"}, "model": {"scenario": "boostedK9"}},
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("nominal_k3", "boosted_k9"),
        selections=SELECTIONS,
    )
    raise SystemExit(report_builds(builds))
