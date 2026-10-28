from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "scripts"
TESTS_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


# Path relative to tests/ -> the suite level that file belongs to. A test that
# declares its own ``@pytest.mark.level_*`` overrides this default.
LEVEL_BY_FILE: dict[str, str] = {
    "test_artifact_boundaries.py": "static",
    "test_artifact_corpus.py": "static",
    "test_backend_adapters.py": "component",
    "test_campaign.py": "system",
    "test_cross_project_contracts.py": "contract",
    "test_fixture_twins.py": "static",
    "test_legacy_experiment_fixtures.py": "integration",
    "test_markers.py": "static",
    "test_pipeline_integration.py": "system",
    "test_suite_policy.py": "static",
    "test_sysml_fixtures.py": "integration",
    "test_workflow.py": "component",
}

LEVEL_NAMES = (
    "level_static",
    "level_unit",
    "level_component",
    "level_contract",
    "level_integration",
    "level_system",
    "level_acceptance",
)


def test_file_key(path: Path) -> str | None:
    """Return the LEVEL_BY_FILE key for a collected test path, if inside tests/."""
    try:
        return path.resolve().relative_to(TESTS_DIR).as_posix()
    except ValueError:
        return None


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items) -> None:
    # Snapshot before -m/-k deselect, so the marker invariants can be checked
    # even when the run selects a single level.
    config._root_suite_all_items = list(items)
    for item in items:
        if any(marker.name in LEVEL_NAMES for marker in item.iter_markers()):
            continue
        key = test_file_key(item.path)
        level = LEVEL_BY_FILE.get(key) if key else None
        if level is not None:
            item.add_marker(getattr(pytest.mark, f"level_{level}"))
