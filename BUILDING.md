# Building And Maintenance

This document covers repository maintenance tasks that are not needed for normal model consumption.

## Imported repositories

Imported upstream repositories live under [`3rd_party`](/home/eriro/pwa/2_work/ssp_references/3rd_party):

- [`3rd_party/reference_fmus`](/home/eriro/pwa/2_work/ssp_references/3rd_party/reference_fmus)
- [`3rd_party/OMSimulator`](/home/eriro/pwa/2_work/ssp_references/3rd_party/OMSimulator)

Fetch them with:

```bash
git submodule update --init --recursive
```

`OMSimulator` is configured with sparse checkout so its `testsuite/` is the relevant working content.

## Python environment

The helper scripts use the repository virtual environment and depend on `pyssp_standard`.

Typical setup:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Build reference FMUs and SSPs

Run:

```bash
./3rd_party/build_fmi2_fmus.sh
```

This builds from [`3rd_party/reference_fmus`](/home/eriro/pwa/2_work/ssp_references/3rd_party/reference_fmus), places temporary build output in [`build/reference_fmus/fmi2-export`](/home/eriro/pwa/2_work/ssp_references/build/reference_fmus/fmi2-export), and writes consumable model artifacts under [`models`](/home/eriro/pwa/2_work/ssp_references/models).

## Workflow methodology and traceability

OMSimulator resources are not uniform enough for one hardcoded build path. The repository therefore uses:

- one shared population chain: `acquire -> build -> package -> unpack`
- one per-model workflow script: [`models/<model_name>/workflow.py`](/home/eriro/pwa/2_work/ssp_references/models)
- one shared helper library: [`scripts/workflow_lib.py`](/home/eriro/pwa/2_work/ssp_references/scripts/workflow_lib.py)

This is intentional traceability back to the repository methodology:

- keep the actual model logic readable at the model location
- keep shared code limited to low-level operations
- normalize outputs under [`models`](/home/eriro/pwa/2_work/ssp_references/models)
- treat built artifacts in `models/` as the canonical consumable outputs

The main workflow patterns are:

- models built from an unpacked upstream FMU directory
- models built from an existing upstream SSP directory
- models that will eventually need custom tool calls in their own workflow script

Each populated model should end up with:

```text
models/<model_name>/
├── workflow.py
├── <model_name>.ssp
├── fmus/                    # when the workflow builds FMUs explicitly
└── ssp/
```

## Manage OMSimulator-derived artifacts

Run one model directly:

```bash
python3 models/BouncingBall/workflow.py
```

List models that provide `workflow.py`:

```bash
python3 scripts/run_model_workflows.py list
```

Run several model workflows through the thin wrapper:

```bash
python3 scripts/run_model_workflows.py run BouncingBall LinearTransformation PWMTest
```

Run every discovered model workflow:

```bash
python3 scripts/run_model_workflows.py run-all
```

Regenerate the OMSimulator resource-backed model workflows and the status registry:

```bash
python3 scripts/sync_omsimulator_models.py
```

This sync uses a co-simulation filter:

- only resource-backed systems with clear co-simulation intent are copied
- in practice, the resource must contain `SystemStructure.ssd` and more than one `.fmu`
- standalone FMUs and single-FMU SSP systems remain documented in the status registry but are not copied into `models/` by the sync step

The generated traceability files are:

- [`docs/omsimulator_model_status.md`](/home/eriro/pwa/2_work/ssp_references/docs/omsimulator_model_status.md)
- [`docs/omsimulator_model_status.json`](/home/eriro/pwa/2_work/ssp_references/docs/omsimulator_model_status.json)

## Helper scripts

Available helper scripts:

- [`3rd_party/build_fmi2_fmus.sh`](/home/eriro/pwa/2_work/ssp_references/3rd_party/build_fmi2_fmus.sh)
- [`scripts/package_fmu_as_ssp.sh`](/home/eriro/pwa/2_work/ssp_references/scripts/package_fmu_as_ssp.sh)
- [`scripts/run_model_workflows.py`](/home/eriro/pwa/2_work/ssp_references/scripts/run_model_workflows.py)
- [`scripts/sync_omsimulator_models.py`](/home/eriro/pwa/2_work/ssp_references/scripts/sync_omsimulator_models.py)
- [`scripts/unpack_model_archive.sh`](/home/eriro/pwa/2_work/ssp_references/scripts/unpack_model_archive.sh)
- [`scripts/workflow_lib.py`](/home/eriro/pwa/2_work/ssp_references/scripts/workflow_lib.py)

Examples:

```bash
./scripts/package_fmu_as_ssp.sh models/BouncingBall/fmus/BouncingBall.fmu
./scripts/unpack_model_archive.sh models/BouncingBall/BouncingBall.ssp
```
