#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODEL_DIR.parent))

from _build_openmodelica_fmu import build_openmodelica_fmu


def main() -> int:
    build_openmodelica_fmu(
        source_file=MODEL_DIR / "Modelica.Blocks.Math.Product.mo",
        class_name="Modelica.Blocks.Math.Product",
        file_name_prefix="Modelica_Blocks_Math_Product",
        fmu_dir=MODEL_DIR / "fmu",
    )
    print("Built Modelica.Blocks.Math.Product")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
