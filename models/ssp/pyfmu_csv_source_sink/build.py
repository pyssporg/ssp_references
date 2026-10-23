#!/usr/bin/env python3
"""Build pyfmu_csv_source_sink and its baseline study.

The SysML authors the composition, the ``System`` scenario, and the baseline
experiment. The CsvSource FMU is generated from ``input/signals.csv`` and
attached to the exported SSP.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pyfmu_csv.packaging import package_fmu_from_csv
from pyssp_standard import SSP
from pyssp_workflow.authoring import run_fixture

REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCE_CSV = Path(__file__).resolve().parent / "input" / "signals.csv"


def _attach_source_fmu(model_build_dir: Path, descriptor) -> None:
    """Attach the CsvSource FMU generated from ``input/signals.csv``."""
    with tempfile.TemporaryDirectory(prefix="pyfmu_csv_source_sink_") as temp_dir:
        fmu_path = Path(temp_dir) / "CsvSource.fmu"
        package_fmu_from_csv(SOURCE_CSV, fmu_path, "CsvSource")
        with SSP(model_build_dir, mode="a") as ssp:
            ssp.attach_fmu("source", fmu_path)


if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=_attach_source_fmu,
        )
    )
