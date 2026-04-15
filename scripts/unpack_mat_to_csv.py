#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from workflow.results import unpack_mat_to_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract an OMSimulator/OpenModelica trajectory MAT file into a wide CSV. "
            "The script understands the standard Dymola-style result layout "
            "(Aclass/name/description/dataInfo/data_1/data_2)."
        )
    )
    parser.add_argument("mat_file", type=Path, help="Path to the .mat result file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV path. Defaults to <mat-file-stem>.csv next to the input.",
    )
    parser.add_argument(
        "--include-description-row",
        action="store_true",
        help="Write a second header row with variable descriptions.",
    )
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    output_path = unpack_mat_to_csv(
        mat_path=args.mat_file,
        output_path=args.output,
        include_description_row=args.include_description_row,
    )
    print(f"Wrote CSV: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
