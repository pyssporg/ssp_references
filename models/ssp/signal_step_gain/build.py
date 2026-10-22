#!/usr/bin/env python3
"""Build the exported signal_step_gain model and its baseline study."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from pyssp_standard import unpack_archive
from pyssp_workflow.authoring import derive_ssp_from_sysml, derive_study_from_sysml


MODEL_NAME = "signal_step_gain"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "test_baseline"

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from utils.filesystem import reset_dir  # noqa: E402
from utils.fmu import strip_model_exchange  # noqa: E402

ARCHITECTURE_DIR = MODEL_DIR / "architecture"
MODEL_BUILD_DIR = REPO_ROOT / "artifacts" / "models" / MODEL_NAME / "model"


def study_dir(study: str) -> Path:
    return REPO_ROOT / "artifacts" / "studies" / MODEL_NAME / study


def _strip_model_exchange(model_root: Path) -> None:
    for description in sorted(model_root.rglob("modelDescription.xml")):
        strip_model_exchange(description.parent)


def build_model() -> Path:
    reset_dir(MODEL_BUILD_DIR.parent)

    with tempfile.TemporaryDirectory(prefix=f"{MODEL_NAME}_") as temp_dir:
        archive = Path(temp_dir) / f"{MODEL_NAME}.ssp"
        derive_ssp_from_sysml(
            ARCHITECTURE_DIR,
            archive,
            MODEL_COMPOSITION,
            fmu_root=REPO_ROOT,
        )
        unpack_archive(
            archive,
            MODEL_BUILD_DIR,
            recursive_fmus=True,
            overwrite=True,
        )

    _strip_model_exchange(MODEL_BUILD_DIR)
    return MODEL_BUILD_DIR


def build_study(study: str = STUDY_COMPOSITION) -> Path:
    output = study_dir(study)
    reset_dir(output)
    derive_study_from_sysml(
        ARCHITECTURE_DIR,
        output,
        study,
        model_name=MODEL_NAME,
    )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        choices=("all", "model", "study"),
        default="all",
        help="Build only the exported model, only the study, or both.",
    )
    parser.add_argument(
        "--study",
        default=STUDY_COMPOSITION,
        help="Study composition name to generate when building a study.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.only in ("all", "model"):
        print(f"Built {MODEL_NAME}: {build_model()}")
    if args.only in ("all", "study"):
        print(f"Built study {args.study}: {build_study(args.study)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
