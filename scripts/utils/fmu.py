from __future__ import annotations

from pathlib import Path

from pyssp_standard.fmu import FMU


def strip_model_exchange(fmu_dir: Path) -> None:
    with FMU(fmu_dir, mode="a") as fmu:
        with fmu.model_description as model_description:
            model_description.strip_model_exchange()
