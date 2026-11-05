#!/usr/bin/env python3
"""Export the SSP and the ``baseline`` analysis for the GainOffset fixture.

The FMU definitions are canonical in ``models/fmu/GainOffset/architecture/``
and passed to the loader as an include root beside this directory's own
``architecture/System.sysml``, which holds the system composition and the
``baseline`` analysis. The FMU is built by
``models/fmu/GainOffset/build.py`` first; this script only derives the SSP and
the analysis and embeds the committed archive at
``artifacts/build/GainOffset/Generator.fmu``.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fixture, report_builds

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
FMU_ARCHIVE = REPO_ROOT / "artifacts" / "build" / "GainOffset" / "Generator.fmu"


def main() -> int:
    if not FMU_ARCHIVE.is_file():
        raise SystemExit(
            f"Missing FMU archive {FMU_ARCHIVE}. Build the FMU first with: "
            "python3 scripts/build_models.py run GainOffset"
        )
    builds = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        analyses=("baseline",),
        # The generated FMU offers CoSimulation only, so the default validation
        # accepts it without the ModelExchange workaround the imported FMUs need.
        validate_fmus=True,
        includes=(REPO_ROOT / "models" / "fmu" / "GainOffset" / "architecture",),
    )
    return report_builds(builds)


if __name__ == "__main__":
    raise SystemExit(main())
