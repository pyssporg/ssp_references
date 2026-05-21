#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile


def _write_mos(work_dir: Path, source_file: Path, class_name: str, file_name_prefix: str) -> Path:
    mos_path = work_dir / "build.mos"
    mos_path.write_text(
        "\n".join(
            [
                "loadModel(Modelica);",
                f'loadFile("{source_file}");',
                'installPackage(Modelica, "4.0.0", exactMatch=false);',
                'setCommandLineOptions("--fmiFlags=s:cvode");',
                'setCommandLineOptions("--fmuRuntimeDepends=all");',
                f'buildModelFMU({class_name}, version="2.0", fmuType="cs", platforms={{"static"}}, fileNamePrefix="{file_name_prefix}");',
                "getErrorString();",
                "",
            ]
        )
    )
    return mos_path


def _copy_archive_file(archive: ZipFile, member_name: str, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("wb") as handle:
        handle.write(archive.read(member_name))


def sync_fmu_dir(archive_path: Path, index_html_path: Path, fmu_dir: Path) -> None:
    from pyssp_standard import FMU

    shutil.rmtree(fmu_dir / "binaries" / "linux64", ignore_errors=True)
    shutil.rmtree(fmu_dir / "documentation", ignore_errors=True)
    shutil.rmtree(fmu_dir / "sources", ignore_errors=True)

    fmu_dir.mkdir(parents=True, exist_ok=True)
    (fmu_dir / "binaries" / "linux64").mkdir(parents=True, exist_ok=True)
    (fmu_dir / "documentation").mkdir(parents=True, exist_ok=True)

    shutil.copy2(index_html_path, fmu_dir / "documentation" / "index.html")

    with ZipFile(archive_path) as archive:
        if "modelDescription.xml" not in archive.namelist():
            raise FileNotFoundError(f"Missing modelDescription.xml in {archive_path}")
        _copy_archive_file(archive, "modelDescription.xml", fmu_dir / "modelDescription.xml")

        for member in archive.namelist():
            if member.startswith("binaries/linux64/") and not member.endswith("/"):
                _copy_archive_file(archive, member, fmu_dir / member)
            elif member.startswith("resources/") and not member.endswith("/"):
                _copy_archive_file(archive, member, fmu_dir / member)

    with FMU(fmu_dir, mode="a") as fmu:
        with fmu.model_description as model_description:
            model_description.strip_model_exchange()


def build_openmodelica_fmu(*, source_file: Path, class_name: str, file_name_prefix: str, fmu_dir: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f"{file_name_prefix}_") as temp_dir:
        work_dir = Path(temp_dir)
        mos_path = _write_mos(work_dir, source_file, class_name, file_name_prefix)
        subprocess.run(["omc", str(mos_path)], cwd=work_dir, check=True)

        archive_path = work_dir / f"{file_name_prefix}.fmu"
        if not archive_path.is_file():
            raise FileNotFoundError(f"Expected FMU archive not found: {archive_path}")

        index_html_path = work_dir / "index.html"
        if not index_html_path.is_file():
            raise FileNotFoundError(f"Expected documentation page not found: {index_html_path}")

        sync_fmu_dir(archive_path, index_html_path, fmu_dir)
