#!/usr/bin/env python3
"""Build the SysML-authored GainOffset fixture end to end.

Unlike the SSP fixtures, which consume a prepared FMU, this one authors its FMI
interface in SysML and generates the FMU here. The build therefore has an extra
stage before ``build_fixture``:

1. ``pyfmi_sysml2.generate_c_headers`` writes the interface headers from
   ``architecture/``.
2. the fixture's own ``gcc`` compiles ``src/GainOffset.c`` against them into
   ``Generator.so``; the FMI ``modelIdentifier`` is the component name.
3. ``pyfmi_sysml2.generate_model_description`` writes ``modelDescription.xml``
   with a fixed ``generation_time``, so a rebuild is byte-stable.
4. ``pyfmi_sysml2.package_fmu`` stages the extracted FMU directory at ``fmu/``
   and writes the archive from that same staged tree, so the two cannot differ.
5. ``pyssp_workflow.authoring.build_fixture`` exports the SSP and the baseline
   analysis, consuming ``fmu/`` through ``FmuMetadata.source``.

Nothing generated here is hand-edited: ``fmu/`` is a build product that the
repository tracks, as it does for the other ``models/fmu/`` fixtures.
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
BUILD_DIR = MODEL_DIR / "build"
FMU_DIR = MODEL_DIR / "fmu"
INCLUDE_DIR = MODEL_DIR / "include"
SOURCE_FILE = MODEL_DIR / "src" / "GainOffset.c"

#: SysML package name, which prefixes the generated C types and file names.
PACKAGE = "GainOffset"
#: Leaf component that becomes the FMU; its name is the FMI modelIdentifier.
COMPONENT = "Generator"
PLATFORM = "linux64"
#: Injected so ``generationDateAndTime`` does not change between rebuilds.
GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def compile_binary(headers_dir: Path) -> Path:
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
            str(headers_dir),
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


def build_fmu() -> Path:
    """Generate headers and model description, then stage and package the FMU."""
    headers = pyfmi_sysml2.generate_c_headers(
        ARCHITECTURE_DIR, BUILD_DIR / "sources", composition="System"
    )
    binary = compile_binary(BUILD_DIR / "sources")
    model_descriptions = pyfmi_sysml2.generate_model_description(
        ARCHITECTURE_DIR,
        BUILD_DIR / "model_description",
        composition="System",
        component=COMPONENT,
        generation_time=GENERATION_TIME,
    )
    fmi_headers = sorted(INCLUDE_DIR.glob("*.h"))
    archive = pyfmi_sysml2.package_fmu(
        BUILD_DIR / f"{PACKAGE}.fmu",
        model_description=model_descriptions[0],
        binary=binary,
        platform=PLATFORM,
        headers=tuple(headers) + tuple(fmi_headers),
        stage_dir=FMU_DIR,
    )
    return archive


def main() -> int:
    archive = build_fmu()
    print(f"Staged {FMU_DIR}")
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
