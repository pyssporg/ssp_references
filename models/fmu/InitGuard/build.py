#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from pyssp_workflow.authoring import build_fmu_from_modelica

MODEL_DIR = Path(__file__).resolve().parent


def main() -> int:
    build_fmu_from_modelica(
        source_file=MODEL_DIR / "InitGuard.mo",
        class_name="InitGuard",
        file_name_prefix="InitGuard",
        fmu_dir=MODEL_DIR / "fmu",
    )
    print("Built InitGuard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
