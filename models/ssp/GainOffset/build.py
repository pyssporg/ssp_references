#!/usr/bin/env python3
"""Build the SysML-authored GainOffset fixture end to end.

The fixture is split so each directory has one job:

1. ``models/fmu/GainOffset/`` holds the FMU *definition*: the C implementation,
   the FMI headers, and the generated ``modelDescription.xml`` and C interface
   headers. It is committed text and is not loadable as an FMU on its own.
2. ``artifacts/build/GainOffset/`` holds the compiled output: ``Generator.so``
   and the packaged ``Generator.fmu``.
3. The SSP and its ``baseline`` analysis are exported from this directory's
   architecture, consuming the packaged FMU through ``FmuMetadata.source``.

The stages run in that order, so the archive exists before the SSP embeds it.
Nothing generated here is hand-edited: the definition and the artifacts are
both rebuild products that the repository tracks.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pyfmi_sysml2
from pyssp_workflow.authoring import build_fixture, report_builds

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHITECTURE_DIR = MODEL_DIR / "architecture"
#: The FMU definition is model-side; the compiled artifact is build-side.
DEFINITION_DIR = REPO_ROOT / "models" / "fmu" / "GainOffset"
FMU_DIR = DEFINITION_DIR / "fmu"
INCLUDE_DIR = DEFINITION_DIR / "include"
SOURCE_FILE = DEFINITION_DIR / "src" / "GainOffset.c"
BUILD_DIR = REPO_ROOT / "artifacts" / "build" / "GainOffset"

#: SysML package name, which prefixes the generated C types and file names.
PACKAGE = "GainOffset"
#: Leaf component that becomes the FMU; its name is the FMI modelIdentifier.
COMPONENT = "Generator"
PLATFORM = "linux64"
#: Injected so ``generationDateAndTime`` does not change between rebuilds.
GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def write_definition() -> tuple[tuple[Path, ...], Path]:
    """Generate the committed FMU definition: C headers and model description."""
    headers = pyfmi_sysml2.generate_c_headers(
        ARCHITECTURE_DIR, FMU_DIR / "sources", composition="System"
    )
    (description,) = pyfmi_sysml2.generate_model_description(
        ARCHITECTURE_DIR,
        FMU_DIR,
        composition="System",
        component=COMPONENT,
        generation_time=GENERATION_TIME,
    )
    # The generator writes ``<output_dir>/<Component>/modelDescription.xml``;
    # an FMU root carries that file at the root instead.
    model_description = FMU_DIR / "modelDescription.xml"
    description.replace(model_description)
    description.parent.rmdir()
    return tuple(headers), model_description


def compile_binary() -> Path:
    """Compile the fixture's C implementation into the FMU binary."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    binary = BUILD_DIR / f"{COMPONENT}.so"
    subprocess.run(
        [
            "gcc",
            "-std=c11",
            "-O2",
            "-fPIC",
            "-shared",
            "-I",
            str(FMU_DIR / "sources"),
            "-I",
            str(INCLUDE_DIR),
            "-o",
            str(binary),
            str(SOURCE_FILE),
            "-lm",
        ],
        check=True,
    )
    return binary


def package_binary(binary: Path, headers: tuple[Path, ...], model_description: Path) -> Path:
    """Write the deterministic FMU archive from the definition and the binary."""
    fmi_headers = sorted(INCLUDE_DIR.glob("*.h"))
    return pyfmi_sysml2.package_fmu(
        BUILD_DIR / f"{COMPONENT}.fmu",
        model_description=model_description,
        binary=binary,
        platform=PLATFORM,
        headers=headers + tuple(fmi_headers),
    )


def main() -> int:
    headers, model_description = write_definition()
    binary = compile_binary()
    archive = package_binary(binary, headers, model_description)
    print(f"Definition {FMU_DIR}")
    print(f"Packaged {archive}")
    builds = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        analyses=("baseline",),
        # The generated FMU offers CoSimulation only, so the default validation
        # accepts it without the ModelExchange workaround the imported FMUs need.
        validate_fmus=True,
    )
    return report_builds(builds)


if __name__ == "__main__":
    raise SystemExit(main())
