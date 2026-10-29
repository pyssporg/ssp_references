#!/usr/bin/env python3
"""Build variation_source_swap with one study per source selection.

The single variation point ``System.source`` chooses between the Step and Sine
FMUs; each study selects one variant at build time. Study selections are rooted
at the Study composition, model selections at ``System``.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

REPO_ROOT = Path(__file__).resolve().parents[3]

SELECTIONS = {
    "step": {"study": {"sut.source": "step"}, "model": {"source": "step"}},
    "sine": {"study": {"sut.source": "sine"}, "model": {"source": "sine"}},
}

if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("step", "sine"),
        selections=SELECTIONS,
    )
    raise SystemExit(report_builds(builds))
