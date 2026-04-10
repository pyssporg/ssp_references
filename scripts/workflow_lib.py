from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from package_fmu_as_ssp import package_fmu
from unpack_model_archive import unpack_archive


REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"
TESTSUITE_REFERENCES_DIR = REPO_ROOT / "3rd_party" / "OMSimulator" / "testsuite" / "references"


@dataclass(frozen=True)
class ModelPaths:
    name: str
    model_dir: Path

    @property
    def ssp_path(self) -> Path:
        return self.model_dir / f"{self.name}.ssp"

    @property
    def unpacked_ssp_dir(self) -> Path:
        return self.model_dir / "ssp"

    @property
    def fmus_dir(self) -> Path:
        return self.model_dir / "fmus"

    @property
    def references_dir(self) -> Path:
        return self.model_dir / "references"

    def fmu_path(self, fmu_name: str | None = None) -> Path:
        actual_name = fmu_name or self.name
        return self.fmus_dir / f"{actual_name}.fmu"


def model_paths(model_dir: Path, model_name: str) -> ModelPaths:
    return ModelPaths(name=model_name, model_dir=model_dir)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def reset_dir(path: Path) -> None:
    remove_path(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source}")
    remove_path(target)
    ensure_parent(target)
    shutil.copytree(source, target)


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")
    ensure_parent(target)
    shutil.copy2(source, target)


def copy_reference_results(model_dir: Path, filenames: list[str]) -> None:
    target_dir = model_dir / "references"
    remove_path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in filenames:
        copy_file(TESTSUITE_REFERENCES_DIR / filename, target_dir / filename)


def zip_directory(source_dir: Path, archive_path: Path) -> None:
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {source_dir}")
    remove_path(archive_path)
    ensure_parent(archive_path)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, path.relative_to(source_dir).as_posix())


def build_fmu_from_directory(source_dir: Path, fmu_path: Path) -> None:
    zip_directory(source_dir, fmu_path)


def package_ssp_from_directory(source_dir: Path, ssp_path: Path) -> None:
    zip_directory(source_dir, ssp_path)


def package_single_fmu_as_ssp(
    fmu_path: Path,
    ssp_path: Path,
    system_name: str,
    component_name: str,
) -> None:
    package_fmu(
        fmu_path=fmu_path,
        output_path=ssp_path,
        system_name=system_name,
        component_name=component_name,
    )


def unpack_archive_to_runtime_layout(archive_path: Path, output_dir: Path) -> None:
    remove_path(output_dir)
    unpack_archive(
        archive_path=archive_path,
        output_dir=output_dir,
        prune=True,
        recursive_fmus=True,
    )


def populate_from_fmu_directory(
    *,
    model_name: str,
    model_dir: Path,
    source_dir: Path,
    fmu_name: str | None = None,
) -> None:
    paths = model_paths(model_dir, model_name)
    actual_fmu_name = fmu_name or model_name
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    build_fmu_from_directory(source_dir, paths.fmu_path(actual_fmu_name))
    package_single_fmu_as_ssp(
        fmu_path=paths.fmu_path(actual_fmu_name),
        ssp_path=paths.ssp_path,
        system_name=model_name,
        component_name=model_name,
    )
    unpack_archive_to_runtime_layout(paths.ssp_path, paths.unpacked_ssp_dir)


def populate_from_ssp_directory(
    *,
    model_name: str,
    model_dir: Path,
    source_dir: Path,
) -> None:
    paths = model_paths(model_dir, model_name)
    copy_tree(source_dir, paths.unpacked_ssp_dir)
    package_ssp_from_directory(paths.unpacked_ssp_dir, paths.ssp_path)
    unpack_archive_to_runtime_layout(paths.ssp_path, paths.unpacked_ssp_dir)
