#!/usr/bin/env python3
"""Build pyfmu_csv_source_sink and its baseline study.

The SysML authors the composition, the ``System`` scenario, and the baseline
experiment. The CsvSource FMU is generated from ``input/signals.csv`` and
attached to the exported SSP.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyfmu_csv.packaging import package_fmu_from_csv  # noqa: E402
from pyssp_standard import SSP  # noqa: E402

from utils.authoring import run_fixture  # noqa: E402

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
        run_fixture(Path(__file__).resolve().parent, package=_attach_source_fmu)
    )
