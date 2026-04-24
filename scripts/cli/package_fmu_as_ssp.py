#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_ROOT))
sys.path.insert(0, str(SCRIPTS_ROOT.parent / "3rd_party" / "pyssp_standard"))

from pyssp_standard.fmu import FMU


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package a single FMU into an SSP using pyssp_standard."
    )
    parser.add_argument("fmu", type=Path, help="Path to the FMU file to package.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .ssp path. Defaults to <fmu-stem>.ssp next to the input FMU.",
    )
    parser.add_argument(
        "--system-name",
        help="Override the SSP system name. Defaults to the FMU model name.",
    )
    parser.add_argument(
        "--component-name",
        help="Override the component name inside the SSP. Defaults to the FMU model name.",
    )
    return parser.parse_args()


def default_output_path(fmu_path: Path) -> Path:
    return fmu_path.with_suffix(".ssp")


def main() -> int:
    args = parse_args()
    fmu_path = args.fmu.resolve()
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")
    if fmu_path.suffix.lower() != ".fmu":
        raise ValueError(f"Expected an .fmu file, got: {fmu_path.name}")

    with FMU(fmu_path, mode="r") as fmu:
        with fmu.model_description as md:
            model_name = md.xml.model_name or fmu_path.stem
    output_path = args.output.resolve() if args.output else default_output_path(fmu_path)
    system_name = args.system_name or model_name
    component_name = args.component_name or model_name

    with FMU(fmu_path, mode="r") as fmu:
        fmu.package_as_ssp(
            output_path,
            system_name=system_name,
            component_name=component_name,
            implementation="ModelExchange",
        )
    print(f"Created SSP: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
