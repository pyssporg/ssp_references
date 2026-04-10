# `ssp_references`

Reference SSP and FMU artifacts for evaluating simulation engines.

## Available models

The repository currently provides these models under [`models`](/home/eriro/pwa/2_work/ssp_references/models):

- `BouncingBall`
- `Dahlquist`
- `Feedthrough`
- `LinearTransformation`
- `PWMTest`
- `Resource`
- `Stair`
- `VanDerPol`
- `importParameterMapping`

## Model layout

Each model has its own folder:

```text
models/<model_name>/
├── workflow.py
├── <model_name>.ssp
├── fmus/                    # for models that explicitly build FMUs
└── ssp/
```

The authoritative description of how a model is populated now lives in:

```text
models/<model_name>/workflow.py
```

What each part is for:

- `workflow.py`: the readable source of truth for the model's `acquire -> build -> package -> unpack` chain.
- `<model_name>.ssp`: the packaged SSP for the model.
- `fmus/`: intermediate FMUs for workflows that explicitly build them.
- `ssp/`: an unpacked view of the SSP, useful for inspection, debugging, and tool integration tests.

## Workflow methodology

OMSimulator-derived models do not share one upstream layout. Some start as a single unpacked FMU, some already exist as an SSP directory, and others are best represented by scripts that construct an SSP or export FMUs.

To keep the actual behavior visible, each model now owns its own workflow script:

- one common population chain: `acquire -> build -> package -> unpack`
- one explicit workflow script per model under [`models`](/home/eriro/pwa/2_work/ssp_references/models)
- one small shared helper library under [`scripts/workflow_lib.py`](/home/eriro/pwa/2_work/ssp_references/scripts/workflow_lib.py)
- one optional thin wrapper for batch execution in [`scripts/run_model_workflows.py`](/home/eriro/pwa/2_work/ssp_references/scripts/run_model_workflows.py)

This is the traceable implementation of the repository methodology:

- keep the real per-model steps readable in `workflow.py`
- keep shared code limited to filesystem and packaging helpers
- commit consumable outputs under [`models`](/home/eriro/pwa/2_work/ssp_references/models)
- skip `reference_fmus` as an upstream source for OMSimulator-derived workflows

Current workflow patterns in the repository:

- single unpacked FMU directory: zip to `fmus/<name>.fmu`, package as a one-component SSP, then unpack
- existing SSP directory: copy into `ssp/`, archive into `<name>.ssp`, then unpack again into runtime layout
- future custom models: write the exact tool calls directly in that model's `workflow.py`

## How to use the models

If you want the packaged SSP, open the model folder and use:

```text
models/<model_name>/<model_name>.ssp
```

If you want the raw FMU, use:

```text
models/<model_name>/fmus/<model_name>.fmu
```

If you want to inspect the unpacked SSP contents, look in:

```text
models/<model_name>/ssp/
```

If you want to rebuild a model from upstream OMSimulator resources, run:

```text
python3 models/<model_name>/workflow.py
```

Examples:

- [`models/BouncingBall/workflow.py`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/workflow.py)
- [`models/BouncingBall/BouncingBall.ssp`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/BouncingBall.ssp)
- [`models/BouncingBall/fmus/BouncingBall.fmu`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/fmus/BouncingBall.fmu)
- [`models/BouncingBall/ssp/SystemStructure.ssd`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/ssp/SystemStructure.ssd)

## Build and Maintenance

Most users do not need to rebuild the artifacts or manage the imported repositories.

Those workflows are documented in [BUILDING.md](/home/eriro/pwa/2_work/ssp_references/BUILDING.md).
