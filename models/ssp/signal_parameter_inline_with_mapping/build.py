#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard import LSRefExperiments, SSP
from pyssp_standard.common.archive import unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from pyssp_standard.ssd import Connection, DefaultExperiment
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1ParameterMappingReference
from utils.fmu import strip_model_exchange
from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:
    ssp_path = temp_dir / "model.ssp"
    ssp_path.unlink(missing_ok=True)

    with SSP(ssp_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        copied_resource_name = ssp.add_fmu(
            "step",
            model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"),
            resource_name="Step.fmu",
            implementation="CoSimulation",
        )
        strip_model_exchange(ssp.runtime.resolve(f"resources/{copied_resource_name}"))

        with ssp.system_structure() as ssd:
            system = ssd.xml.system
            # Inline SSV with flat names (no component prefix)
            ssd.extend_system_parameterset(
                {
                    "step_height": 1.0,
                    "step_offset": 0.0,
                    "step_startTime": 0.25,
                }
            )

            # Add external ParameterMapping to the inline ParameterBinding
            for binding in system.parameter_bindings:
                if binding.source is None and binding.parameter_set is not None:
                    binding.parameter_mapping = Ssd1ParameterMappingReference(
                        source="resources/inline_mapping.ssm"
                    )
                    break


        # Add the external SSM file as an SSP resource
        ssp.add_resource(MODEL_DIR / "ssp" / "resources" / "inline_mapping.ssm")

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)

    unpack_archive(ssp_path, model.paths.build_dir / exp.name, recursive_fmus=True, overwrite=True)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="signal_parameter_inline_with_mapping_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
