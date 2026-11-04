"""Invariants for the root suite's level markers.

The marker is what selects a level (``pytest -m level_contract``), so the
mapping file -> level has to stay total and unambiguous. Every discoverable test
file must be in ``LEVEL_BY_FILE``, no entry may be stale, and every collected
test must resolve to exactly one level.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import LEVEL_BY_FILE, LEVEL_NAMES

TESTS_DIR = Path(__file__).resolve().parent


def _key(item: pytest.Item) -> str:
    return Path(item.path).resolve().relative_to(TESTS_DIR.resolve()).as_posix()


def _levels(item: pytest.Item) -> list[str]:
    return [marker.name for marker in item.iter_markers() if marker.name in LEVEL_NAMES]


def _all_items(request: pytest.FixtureRequest) -> list[pytest.Item]:
    # Snapshot taken before -m/-k deselect in conftest.
    return getattr(request.config, "_root_suite_all_items", list(request.session.items))


def _files_at(level: str) -> set[str]:
    return {path for path, mapped in LEVEL_BY_FILE.items() if mapped == level}


def test_level_by_file_is_total_and_not_stale(request: pytest.FixtureRequest) -> None:
    on_disk = {path.name for path in TESTS_DIR.glob("test_*.py")}
    mapped = set(LEVEL_BY_FILE)

    assert on_disk - mapped == set(), f"unmapped test files: {sorted(on_disk - mapped)}"
    assert mapped - on_disk == set(), f"stale LEVEL_BY_FILE entries: {sorted(mapped - on_disk)}"


def test_every_test_has_exactly_one_level(request: pytest.FixtureRequest) -> None:
    wrong = {
        f"{_key(item)}::{item.name}": _levels(item)
        for item in _all_items(request)
        if len(_levels(item)) != 1
    }
    assert wrong == {}


def test_static_selection_is_real_and_does_not_leak_integration(
    request: pytest.FixtureRequest,
) -> None:
    static_files = _files_at("static")
    selected = [item for item in _all_items(request) if _key(item) in static_files]

    assert selected, "-m level_static selected nothing"
    assert all(_levels(item) == ["level_static"] for item in selected)
    leaked = [
        item
        for item in _all_items(request)
        if _levels(item) == ["level_static"] and _key(item) in _files_at("integration")
    ]
    assert leaked == [], f"-m level_static selected integration tests: {[_key(i) for i in leaked]}"


def test_contract_selection_is_real(request: pytest.FixtureRequest) -> None:
    contract_files = _files_at("contract")
    assert contract_files, "LEVEL_BY_FILE maps no contract file"

    collected = {_key(item) for item in _all_items(request)}
    if not contract_files & collected:
        pytest.skip("contract file not collected in this run")

    selected = [item for item in _all_items(request) if _levels(item) == ["level_contract"]]
    assert selected, "-m level_contract selected nothing"
    assert {_key(item) for item in selected} <= contract_files


def test_explicit_marker_wins_over_the_file_default(
    request: pytest.FixtureRequest,
) -> None:
    overrides = [
        item
        for item in _all_items(request)
        if item.name == "test_reference_csvs_are_not_inverted"
    ]
    if not overrides:
        pytest.skip("override test not collected in this run")

    [override] = overrides
    assert _levels(override) == ["level_integration"]
