#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_ROOT))

from workflow.unpack import default_output_dir, unpack_archive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Unpack an SSP or FMU into a directory, preserving archive folder layout "
            "while pruning files not needed for runtime examples."
        )
    )
    parser.add_argument("archive", type=Path, help="Path to a .ssp or .fmu archive.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Destination directory. Defaults to <archive-stem> next to the archive.",
    )
    parser.add_argument(
        "--keep-sources",
        action="store_true",
        help="Keep source and documentation directories instead of pruning them.",
    )
    parser.add_argument(
        "--no-recursive-fmus",
        action="store_true",
        help="For SSP inputs, do not unpack nested resources/*.fmu archives.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive_path = args.archive.resolve()
    if not archive_path.is_file():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    output_dir = args.output.resolve() if args.output else default_output_dir(archive_path)
    unpack_archive(
        archive_path=archive_path,
        output_dir=output_dir,
        prune=not args.keep_sources,
        recursive_fmus=not args.no_recursive_fmus,
    )
    print(f"Unpacked archive to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
