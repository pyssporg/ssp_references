# `ssp_references`

Reference SSP and FMU artifacts for evaluating SSP-capable and FMI-capable tools.

The repository curates a set of reusable model directories together with the
workflow code used to assemble them from vendored upstream sources.

## Repository Structure

Model workflows are organized by category:

```text
models/
├── ssp/
│   └── <model_name>/
│       ├── workflow.py
│       ├── metadata.json
│       ├── <model_name>.ssp
│       ├── ssp/
│       ├── fmus/                  # optional, generated when packaging from FMU sources
│       └── references/            # optional, copied from upstream reference results
└── fmu/
    └── <model_name>/              # reserved for FMU-centric models
```

The workflow runner discovers models from `models/*/*/workflow.py`. A model
directory placed directly under `models/` will not be picked up.

Other top-level directories:

- `scripts/`: repository tooling for packaging, unpacking, and model setup.
- `3rd_party/`: vendored upstream assets used as the source material for models.
- `docs/`: generated or auxiliary documentation artifacts when present.

## Model Contract

Each model directory is expected to contain:

- `workflow.py`: executable entrypoint for setting up that model directory.
- `metadata.json`: required model metadata and source declarations.

The workflow uses `metadata.json` to locate upstream sources and produce local
artifacts. Missing metadata is a hard error.

Common generated or copied artifacts:

- `<model_name>.ssp`: packaged SSP archive for the model.
- `ssp/`: unpacked view of the packaged SSP, including recursively unpacked FMUs.
- `fmus/`: generated FMUs when the source material starts as an FMU directory or
  FMU archive rather than an SSP.
- `references/`: copied upstream reference trajectories. When `.mat` files are
  present, the workflow also emits adjacent `.csv` files.
- `simulation_results/`: engine-specific result files and cross-engine
  comparison reports produced by the comparison tooling.

Artifacts such as `fmus/` and `references/` are optional and depend on the
model's declared sources. They are not required for every model.

## Metadata Schema

Each model uses a `metadata.json` file with this structure:

```json
{
  "model_name": "BouncingBall",
  "description": "Packages the bouncing-ball reference model as an SSP.",
  "intended_use": "Simple FMI/SSP validation of hybrid dynamics.",
  "source": {
    "ssp": [],
    "fmu": [
      "3rd_party/OMSimulator/testsuite/resources/BouncingBall"
    ],
    "results": [
      "3rd_party/OMSimulator/testsuite/references/BouncingBall-cs.mat"
    ]
  }
}
```

Source entries are repository-relative paths. The workflow supports exactly one
primary source for `ssp` or `fmu`, plus zero or more `results` files.

## Quick Start

Create a virtual environment and install the Python dependencies:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Inspect the available model workflows:

```bash
python3 scripts/run_model_workflows.py list
```

Set up one model:

```bash
python3 scripts/run_model_workflows.py run BouncingBall
```

Set up all discovered models:

```bash
python3 scripts/run_model_workflows.py run-all
```

Compare two engines on a model:

```bash
python3 scripts/cli/compare_engines.py embrace \
  --ssp4sim-app ../ssp4sim/build/public/ssp4sim_app/sim_app
```

This writes raw results under
`models/ssp/<model_name>/simulation_results/<engine>/` and comparison reports
under `models/ssp/<model_name>/simulation_results/comparisons/`.

## Platform Notes

`requirements.txt` currently assumes a Linux `x86_64` environment:

- `pyssp4sim` is installed from a Linux `x86_64` wheel hosted on GitHub Releases.
- `OMSimulator` is installed from PyPI and may pull build-time dependencies.

If you are working on another platform, expect to replace or omit the
`pyssp4sim` wheel entry and validate the rest of the toolchain manually.

## Tooling Notes

The repository contains small CLI helpers under `scripts/cli/` for packaging and
unpacking archives. The main supported entrypoint for repository setup is still
`scripts/run_model_workflows.py`.

## Supported Model Categories

- `models/ssp/`: packaged SSP models that can be used directly in SSP-oriented
  interoperability and regression testing.
- `models/fmu/`: placeholder category for FMU-centric source models that may be
  packaged into SSPs or used as building blocks by future workflows.
