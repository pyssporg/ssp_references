#!/usr/bin/env python3
"""Build the SysML-authored GainOffset fixture end to end.

The fixture is split so each directory has one job:

1. ``models/fmu/GainOffset/`` holds the authored FMU input: the C
   implementation. It is committed text and is not loadable as an FMU on its
   own.
2. ``artifacts/build/GainOffset/`` holds every generated file: the C interface
   headers, the ``modelDescription.xml`` definition, the compiled
   ``Generator.so``, and the packaged ``Generator.fmu``. The public FMI 2.0
   headers come from ``pyfmi_sysml2.fmi2_headers()``.
3. The SSP and its ``baseline`` analysis are exported from this directory's
   architecture, consuming the packaged FMU through ``FmuMetadata.source``.

The stages run in that order, so the archive exists before the SSP embeds it.
Nothing generated here is hand-edited: the definition and the artifacts are
both untracked rebuild products under ``artifacts/``.
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
#: The authored FMU input is model-side; every generated file is build-side.
DEFINITION_DIR = REPO_ROOT / "models" / "fmu" / "GainOffset"
SOURCE_FILE = DEFINITION_DIR / "src" / "GainOffset.c"
BUILD_DIR = REPO_ROOT / "artifacts" / "build" / "GainOffset"
GENERATED_HEADER_DIR = BUILD_DIR / "sources"

#: SysML package name, which prefixes the generated C types and file names.
PACKAGE = "GainOffset"
#: Leaf component that becomes the FMU; its name is the FMI modelIdentifier.
COMPONENT = "Generator"
PLATFORM = "linux64"
#: Injected so ``generationDateAndTime`` does not change between rebuilds.
GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def write_definition() -> tuple[tuple[Path, ...], Path]:
    """Generate the definition and the build-side C interface headers."""
    headers = pyfmi_sysml2.generate_c_headers(
        ARCHITECTURE_DIR, GENERATED_HEADER_DIR, composition="System"
    )
    (description,) = pyfmi_sysml2.generate_model_description(
        ARCHITECTURE_DIR,
        BUILD_DIR,
        composition="System",
        component=COMPONENT,
        generation_time=GENERATION_TIME,
    )
    # The generator writes ``<output_dir>/<Component>/modelDescription.xml``;
    # the build tree carries that file at the build root instead.
    model_description = BUILD_DIR / "modelDescription.xml"
    description.replace(model_description)
    description.parent.rmdir()
    return tuple(headers), model_description


def compile_binary() -> Path:
    """Compile the fixture's C implementation into the FMU binary."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    binary = BUILD_DIR / f"{COMPONENT}.so"
    fmi_headers = pyfmi_sysml2.fmi2_headers()
    include_dirs = {GENERATED_HEADER_DIR, *(header.parent for header in fmi_headers)}
    command = ["gcc", "-std=c11", "-O2", "-fPIC", "-shared"]
    for directory in sorted(include_dirs):
        command.extend(["-I", str(directory)])
    command.extend(["-o", str(binary), str(SOURCE_FILE), "-lm"])
    subprocess.run(command, check=True)
    return binary


def package_binary(
    binary: Path, generated_headers: tuple[Path, ...], model_description: Path
) -> Path:
    """Write the deterministic FMU archive from the definition and the binary."""
    return pyfmi_sysml2.package_fmu(
        BUILD_DIR / f"{COMPONENT}.fmu",
        model_description=model_description,
        binary=binary,
        platform=PLATFORM,
        headers=generated_headers + pyfmi_sysml2.fmi2_headers(),
    )


def main() -> int:
    headers, model_description = write_definition()
    binary = compile_binary()
    archive = package_binary(binary, headers, model_description)
    print(f"Definition {model_description}")
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
