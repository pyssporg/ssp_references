#!/usr/bin/env python3
"""Build the exported signal_nested_pass_through model and its baseline study.

The SysML authors the nested ``Inner`` system and its boundary ports; the
SysML dialect cannot express the boundary-to-component wiring, so the package
hook adds it with ``pyssp_standard`` and applies the scenario as inline
component parameters.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyssp_standard import SSP  # noqa: E402
from pyssp_standard.ssd import Connection, Connector  # noqa: E402

from utils.authoring import apply_inline_components, build_fixture  # noqa: E402
from utils.authoring import StudyDescriptor  # noqa: E402

MODEL_NAME = "signal_nested_pass_through"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"


def _wire_boundaries(model_build_dir: Path) -> None:
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            root = ssd.xml.system
            root.connectors.append(Connector(name="y", kind="output", type_name="Real"))
            root.connections.append(
                Connection(start_element="add", start_connector="y", end_connector="y")
            )
            inner = next(
                element
                for element in root.elements
                if element.name == "inner"
            )
            inner.connections.extend(
                [
                    Connection(
                        start_connector="u",
                        end_element="gain",
                        end_connector="u",
                    ),
                    Connection(
                        start_element="gain",
                        start_connector="y",
                        end_connector="v",
                    ),
                ]
            )


def package(model_build_dir: Path, descriptor: StudyDescriptor) -> None:
    _wire_boundaries(model_build_dir)
    apply_inline_components(model_build_dir, descriptor)


def main() -> int:
    output = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=STUDY_COMPOSITION,
        package=package,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
