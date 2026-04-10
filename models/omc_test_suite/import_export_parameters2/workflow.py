#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODEL_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow_lib import populate_from_ssp_directory


MODEL_NAME = "import_export_parameters2"
SOURCE_DIR = REPO_ROOT / "3rd_party" / "OMSimulator" / "testsuite" / "resources" / "import_export_parameters2"


def main() -> int:
    populate_from_ssp_directory(
        model_name=MODEL_NAME,
        model_dir=MODEL_DIR,
        source_dir=SOURCE_DIR,
    )
    print(f"Populated {MODEL_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
