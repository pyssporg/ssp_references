#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from contextlib import ExitStack
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow.model import ModelMetaData
from workflow.packaging import materialize_fmu_archive, package_fmu_as_ssp, unpack_archive_to_runtime_layout


def main() -> int:
    model = ModelMetaData(MODEL_DIR)

    with ExitStack() as stack:
        fmu_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Resource"), "Resource.fmu")
        )
        package_fmu_as_ssp(
            fmu_path=fmu_path,
            output_path=model.paths.ssp_path,
            system_name=model.name,
            component_name="fmu",
        )

    unpack_archive_to_runtime_layout(model.paths.ssp_path, model.paths.unpacked_ssp_dir)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
