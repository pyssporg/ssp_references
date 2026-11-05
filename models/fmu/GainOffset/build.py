#!/usr/bin/env python3
"""Build the FMU for the GainOffset fixture.

This directory owns both the FMU's authored source (``src/GainOffset.c``) and
its architecture (``architecture/GainOffset.sysml``). Every generated file goes
to ``artifacts/build/GainOffset/``: the C interface headers, the
``modelDescription.xml`` definition, the compiled ``Generator.so``, and the
packaged ``Generator.fmu``. The public FMI 2.0 headers come from
``pyfmi_sysml2.fmi2_headers()``.

The system fixture at ``models/ssp/GainOffset/`` links
``architecture/GainOffset.sysml`` into its own ``architecture`` directory and
builds the SSP afterwards, embedding the archive this script packages. The
FMU build uses ``composition="Fmu"``: the architecture declares only the FMU,
and the generator exports components below an explicit one-part root. The FMU
architecture relies on the dialect core definitions. Nothing generated here is
hand-edited: the definition and the artifacts are both untracked rebuild
products under ``artifacts/``.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pycps_sysml2
import pyfmi_sysml2

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHITECTURE_DIR = MODEL_DIR / "architecture"
SOURCE_FILE = MODEL_DIR / "src" / "GainOffset.c"
BUILD_DIR = REPO_ROOT / "artifacts" / "build" / "GainOffset"
GENERATED_HEADER_DIR = BUILD_DIR / "sources"

#: Leaf component that becomes the FMU; its name is the FMI modelIdentifier.
COMPONENT = "Generator"
PLATFORM = "linux64"
#: Injected so ``generationDateAndTime`` does not change between rebuilds.
GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def write_definition() -> tuple[tuple[Path, ...], Path]:
    """Generate the definition and the build-side C interface headers."""
    architecture = pycps_sysml2.load(
        ARCHITECTURE_DIR, pycps_sysml2.core_definitions()
    )
    # The FMU architecture declares only the FMU, so the generator needs an
    # explicit composition root to export the component below it.
    headers = pyfmi_sysml2.generate_c_headers(
        architecture, GENERATED_HEADER_DIR, composition="Fmu"
    )
    (description,) = pyfmi_sysml2.generate_model_description(
        architecture,
        BUILD_DIR,
        composition="Fmu",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
