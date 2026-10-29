"""Corpus gate: the committed inputs the suite reads must exist.

Normal mode checks only the tracked corpus (registry, reference CSVs). Strict
mode (``SSP_REQUIRE_ARTIFACTS=1`` or ``CI``) also demands the generated build
output for every registry case, so a checkout with no build cannot report a
green run that proves nothing.

Regenerate with ``python3 scripts/build_models.py run <model>`` and
``python3 scripts/run_simulations.py``.
"""

from __future__ import annotations

import ast
import csv
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "artifacts" / "simulation_registry.json"
MODELS_ROOT = REPO_ROOT / "models" / "ssp"


def _strict() -> bool:
    return os.environ.get("SSP_REQUIRE_ARTIFACTS") == "1" or "CI" in os.environ


def _analysis_name(case: dict) -> str:
    return case.get("analysis") or case["name"]


def _registry() -> dict:
    assert REGISTRY_PATH.is_file(), f"missing registry: {REGISTRY_PATH}"
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _build_py_csv_paths() -> list[Path]:
    """CSV inputs declared in models/ssp/*/build.py, resolved from the model dir.

    A build script joins the model directory with string segments, e.g.
    ``Path(__file__).resolve().parent / "input" / "signals.csv"``.
    """
    paths: list[Path] = []
    for build_py in sorted(MODELS_ROOT.glob("*/build.py")):
        tree = ast.parse(build_py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            segments = [
                part.value
                for part in ast.walk(node.value)
                if isinstance(part, ast.Constant)
                and isinstance(part.value, str)
                and not part.value.startswith(("/", "{", "http"))
            ]
            if segments and segments[-1].lower().endswith(".csv"):
                paths.append(build_py.parent.joinpath(*segments))
    return paths


def test_registry_parses_and_the_first_case_names_an_analysis() -> None:
    data = _registry()

    assert data["models"], "registry lists no models"
    first_case = data["models"][0]["cases"][0]
    assert first_case.get("analysis"), f"first registry case has no analysis: {first_case}"

    # Every case still resolves to an analysis directory (explicit or by name).
    for model in data["models"]:
        for case in model["cases"]:
            assert _analysis_name(case)


def test_reference_csvs_and_build_inputs_exist_and_parse() -> None:
    data = _registry()

    referenced: list[Path] = []
    for model in data["models"]:
        for case in model["cases"]:
            for reference in case.get("reference_csvs", ()):
                referenced.append(REPO_ROOT / reference["path"])
    referenced.extend(_build_py_csv_paths())

    missing = [path for path in referenced if not path.is_file()]
    assert missing == [], "missing committed CSV inputs:\n" + "\n".join(map(str, missing))

    empty: list[Path] = []
    for path in referenced:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if len(rows) < 2 or not rows[0]:
            empty.append(path)
    assert empty == [], "unparseable or empty CSV inputs:\n" + "\n".join(map(str, empty))


def test_generated_corpus_exists_in_strict_mode() -> None:
    if not _strict():
        pytest.skip("strict artifact mode off (set SSP_REQUIRE_ARTIFACTS=1 or CI)")

    data = _registry()
    expected: list[tuple[Path, str]] = []
    for model in data["models"]:
        model_name = model["name"]
        for case in model["cases"]:
            analysis = _analysis_name(case)
            expected.extend(
                [
                    (
                        REPO_ROOT
                        / "artifacts" / "models" / model_name / analysis / "model"
                        / "SystemStructure.ssd",
                        f"python3 scripts/build_models.py run {model_name}",
                    ),
                    (
                        REPO_ROOT / "artifacts" / "analyses" / model_name / analysis / "analysis.json",
                        f"python3 scripts/build_models.py run {model_name}",
                    ),
                    (
                        REPO_ROOT / "artifacts" / "simulation" / model_name / analysis / "setup.json",
                        "python3 scripts/run_simulations.py",
                    ),
                ]
            )

    missing = [(path, remedy) for path, remedy in expected if not path.is_file()]
    assert missing == [], "missing generated corpus:\n" + "\n".join(
        f"  {path.relative_to(REPO_ROOT)}  ->  {remedy}" for path, remedy in missing
    ) + "\nRegenerate: python3 scripts/build_models.py run <model>; python3 scripts/run_simulations.py"
