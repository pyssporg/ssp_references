#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fmu_from_modelica

MODEL_DIR = Path(__file__).resolve().parent


def main() -> int:
    build_fmu_from_modelica(
        source_file=MODEL_DIR / "DivideGuard.mo",
        class_name="DivideGuard",
        file_name_prefix="DivideGuard",
        fmu_dir=MODEL_DIR / "fmu",
    )
    print("Built DivideGuard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
