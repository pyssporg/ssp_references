"""Campaign orchestration tests: one build per model, single-writer setup."""

from __future__ import annotations

from pathlib import Path

import pytest
import run_campaign
from sequence_extensions.flow import RunOptions, execute_flow
from workflow.registry import RegistryCase, RegistryModel, SimulationRegistry


def make_registry(path: Path) -> Path:
    registry = SimulationRegistry(
        models=(
            RegistryModel(
                name="Example",
                compare_signals=("y",),
                build="model",
                cases=(
                    RegistryCase(name="case_a", backends=("ssp4sim", "omsimulator")),
                    RegistryCase(name="case_b", backends=("ssp4sim", "omsimulator")),
                ),
            ),
        )
    )
    return registry.write(path)


def test_campaign_deduplicates_builds_and_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry_path = make_registry(tmp_path / "registry.json")
    commands: list[list[str]] = []

    def fake_run(command: list[str]) -> dict[str, object]:
        commands.append(list(command))
        return {
            "command": command,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr(run_campaign, "_run", fake_run)

    run = execute_flow(
        run_campaign.campaign,
        models=("Example",),
        registry_path=registry_path,
        workers=2,
        options=RunOptions(name="test-campaign", max_workers=2, log=None),
    )
    result = run.result

    builds = [cmd for cmd in commands if "scripts/build_models.py" in cmd]
    prepares = [cmd for cmd in commands if "--prepare-only" in cmd]
    simulations = [cmd for cmd in commands if "--skip-setup-manifest" in cmd]
    comparisons = [cmd for cmd in commands if "scripts/run_comparisons.py" in cmd]

    assert len(builds) == 1
    assert builds[0][-2:] == ["run", "Example"]
    assert len(prepares) == 2
    assert all("scripts/run_simulations.py" in cmd for cmd in prepares)
    assert len(simulations) == 4
    assert all("--backend" in cmd for cmd in simulations)
    assert len(comparisons) == 2
    assert result["workers"] == 2
    assert result["failed_cases"] == []
