"""Component tests for the two-phase build wrapper.

Discovery reads two fixture roots, the FMU phase first, and ``run-all`` must
finish every FMU build before it starts an SSP build. The tests use tmp roots
and a recorded ``subprocess.run`` so no build script or compiler is invoked.
"""

from __future__ import annotations

from pathlib import Path

import build_models
import pytest


def _make_root(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    root.mkdir()
    return root


def _script(root: Path, model: str, *, architecture: bool = False) -> Path:
    model_dir = root / model
    model_dir.mkdir(parents=True, exist_ok=True)
    if architecture:
        (model_dir / "architecture").mkdir()
    script = model_dir / "build.py"
    script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    return script


def _record_runs(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    calls: list[Path] = []
    monkeypatch.setattr(
        build_models.subprocess,
        "run",
        lambda argv, **_kwargs: calls.append(Path(argv[1])),
    )
    return calls


def test_gainoffset_builds_the_fmu_before_the_ssp() -> None:
    workflow = build_models.discover_workflows()["GainOffset"]
    fmu_script = build_models.FMU_MODELS_DIR / "GainOffset" / "build.py"
    ssp_script = build_models.SSP_MODELS_DIR / "GainOffset" / "build.py"

    assert workflow.fmu_build == fmu_script
    assert workflow.ssp_build == ssp_script
    assert workflow.steps() == (fmu_script, ssp_script)


def test_a_name_in_one_root_has_only_that_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fmu_root = _make_root(tmp_path, "fmu")
    ssp_root = _make_root(tmp_path, "ssp")
    fmu_script = _script(fmu_root, "OnlyFmu", architecture=True)
    _script(fmu_root, "NoArchitecture")
    ssp_script = _script(ssp_root, "OnlySsp")
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", fmu_root)
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", ssp_root)

    workflows = build_models.discover_workflows()

    assert set(workflows) == {"OnlyFmu", "OnlySsp"}
    assert workflows["OnlyFmu"].steps() == (fmu_script,)
    assert workflows["OnlySsp"].steps() == (ssp_script,)


def test_duplicate_script_within_one_phase_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fmu_root = _make_root(tmp_path, "fmu")
    first = _script(fmu_root, "Twin", architecture=True)
    collision = _script(_make_root(tmp_path, "other"), "Twin", architecture=True)
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", fmu_root)
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", _make_root(tmp_path, "ssp"))
    # One glob cannot yield two scripts for one name, so inject the collision
    # the guard exists for.
    monkeypatch.setattr(
        build_models,
        "_scan",
        lambda root, **_kwargs: [first, collision] if root == fmu_root else [],
    )

    with pytest.raises(ValueError) as excinfo:
        build_models.discover_workflows()

    assert str(first) in str(excinfo.value)
    assert str(collision) in str(excinfo.value)


def test_run_all_finishes_every_fmu_before_any_ssp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fmu_root = _make_root(tmp_path, "fmu")
    ssp_root = _make_root(tmp_path, "ssp")
    zulu_fmu = _script(fmu_root, "Zulu", architecture=True)
    _script(fmu_root, "Alpha")
    zulu_ssp = _script(ssp_root, "Zulu")
    alpha_ssp = _script(ssp_root, "Alpha")
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", fmu_root)
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", ssp_root)
    calls = _record_runs(monkeypatch)

    assert build_models.cmd_run_all() == 0

    assert calls[:1] == [zulu_fmu]
    assert set(calls[1:]) == {zulu_ssp, alpha_ssp}
    assert len(calls) == 3


def test_cmd_run_runs_both_steps_of_one_model_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fmu_root = _make_root(tmp_path, "fmu")
    ssp_root = _make_root(tmp_path, "ssp")
    zulu_fmu = _script(fmu_root, "Zulu", architecture=True)
    zulu_ssp = _script(ssp_root, "Zulu")
    _script(ssp_root, "Alpha")
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", fmu_root)
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", ssp_root)
    calls = _record_runs(monkeypatch)

    assert build_models.cmd_run(["Zulu"]) == 0

    assert calls == [zulu_fmu, zulu_ssp]


def _unexpected_run(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("no build script may run for an unknown model")


def test_cmd_run_rejects_unknown_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", _make_root(tmp_path, "fmu"))
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", _make_root(tmp_path, "ssp"))
    monkeypatch.setattr(build_models.subprocess, "run", _unexpected_run)

    with pytest.raises(KeyError, match="Nope"):
        build_models.cmd_run(["Nope"])


def test_cmd_list_prints_each_model_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fmu_root = _make_root(tmp_path, "fmu")
    ssp_root = _make_root(tmp_path, "ssp")
    _script(fmu_root, "Zulu", architecture=True)
    _script(ssp_root, "Zulu")
    _script(ssp_root, "Alpha")
    monkeypatch.setattr(build_models, "FMU_MODELS_DIR", fmu_root)
    monkeypatch.setattr(build_models, "SSP_MODELS_DIR", ssp_root)

    assert build_models.cmd_list() == 0

    lines = capsys.readouterr().out.splitlines()
    assert sorted(lines) == ["Alpha", "Zulu"]


def test_cmd_list_reports_gainoffset_once_on_the_current_tree(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert build_models.cmd_list() == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines.count("GainOffset") == 1
