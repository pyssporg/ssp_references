# `ssp_references`

Reference SSP and FMU artifacts for evaluating simulation engines.

## Available models

The repository currently provides these models under [`models`](/home/eriro/pwa/2_work/ssp_references/models):

- `BouncingBall`
- `Dahlquist`
- `Feedthrough`
- `Resource`
- `Stair`
- `VanDerPol`

## Model layout

Each model has its own folder:

```text
models/<model_name>/
├── <model_name>.ssp
├── fmus/
│   └── <model_name>.fmu
└── ssp/
    ├── SystemStructure.ssd
    └── resources/
        └── <model_name>/
```

What each part is for:

- `<model_name>.ssp`: the packaged SSP for the model.
- `fmus/<model_name>.fmu`: the FMU used inside the SSP.
- `ssp/`: an unpacked view of the SSP, useful for inspection, debugging, and tool integration tests.

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

Examples:

- [`models/BouncingBall/BouncingBall.ssp`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/BouncingBall.ssp)
- [`models/BouncingBall/fmus/BouncingBall.fmu`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/fmus/BouncingBall.fmu)
- [`models/BouncingBall/ssp/SystemStructure.ssd`](/home/eriro/pwa/2_work/ssp_references/models/BouncingBall/ssp/SystemStructure.ssd)

## Build and Maintenance

Most users do not need to rebuild the artifacts or manage the imported repositories.

Those workflows are documented in [BUILDING.md](/home/eriro/pwa/2_work/ssp_references/BUILDING.md).
