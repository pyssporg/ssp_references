# `ssp_references`

Curated SSP model fixtures plus the scripts used to prepare them, simulate them,
and compare results across engines.

The repository is primarily a working collection of reference models under
`models/ssp/`. Most source material comes from vendored upstream projects in
`3rd_party/`, while the checked-in model directories hold the authored model
definitions, fixture notes, and explicit build/simulation entrypoints.

## Layout

```text
.
├── models/
│   ├── fmu/
│   │   └── <fmu_name>/
│   │       ├── fmu/
│   │       └── references/
│   └── ssp/
│       └── <model_name>/
│           ├── build.py
│           ├── simulate.py
│           ├── metadata.json
│           ├── FIXTURE.md
│           └── ssp/               # only for authored SSP sources such as dcmotor/embrace
├── build/
│   └── models/ssp/<model_name>/
│       ├── <model_name>.ssp
│       ├── ssp/
│       ├── references/            # generated CSV references from metadata sources
│       └── simulation_results/
├── scripts/
│   ├── run_model_workflows.py
│   ├── run_model_simulations.py
│   ├── cli/
│   └── workflow/
├── 3rd_party/
│   ├── OMSimulator
│   ├── reference_fmus
│   └── pyfmu_csv
└── requirements.txt
```

## What Lives Where

- `models/fmu/` holds reusable FMU fixtures that can be shared by multiple SSP
  models.
- `models/ssp/` is the main SSP fixture area. Each model directory is both a
  reusable fixture and the place where model-specific source files are kept.
- `build/` holds generated SSP archives, unpacked runtime layouts, converted
  reference CSVs, and simulation outputs. It is disposable and not versioned.
- `build.py` is the per-model executable entrypoint discovered by
  `scripts/run_model_workflows.py`. Each model script is intentionally explicit
  about how its SSP is assembled.
- `simulate.py` is the per-model executable entrypoint discovered by
  `scripts/run_model_simulations.py`. Each model script declares the simulation
  configuration and explicit engine calls for that system.
- `metadata.json` declares the upstream SSP, FMU, and reference-result sources
  still needed by the shared workflow code. When `build.py` assembles the SSP
  itself, metadata is typically only needed for descriptive fields and results.
- `scripts/workflow/packaging.py` contains shared SSP/FMU packaging helpers
  built on `pyssp_standard`.
- `scripts/workflow/simulation.py` contains shared simulation-engine helpers
  and the common simulation configuration type.
- `scripts/workflow/comparison.py` contains result discovery and comparison
  helpers.
- `scripts/cli/` contains small task-focused helpers for comparing engines,
  unpacking archives, packaging a single FMU as an SSP, and converting MAT
  results to CSV.
- `3rd_party/` is upstream source material. In normal repo work, it is input
  data, not the main place to edit behavior.

## Model Workflow

Each model directory under `models/ssp/<model_name>/` follows the same basic
contract:

- `build.py` is the source of truth for how that SSP gets assembled.
- Authored SSP composition in `build.py` should use `pyssp_standard` facades
  (`SSP`, `system_structure()`, `add_fmu()`, `Connection`, and parameter-set
  helpers) rather than hand-writing `SystemStructure.ssd` or assembling SSP zip
  files directly.
- `simulate.py` is the source of truth for how that model is simulated and
  compared across engines.
- `metadata.json` provides model metadata plus any upstream files that still
  need to be validated or referenced by the shared workflow code.
- Running `build.py` prepares the generated fixture under `build/` by
  validating sources, packaging the `.ssp`, and unpacking a runtime layout.

The workflow runner discovers models from `models/*/*/build.py`:

```bash
python3 scripts/run_model_workflows.py list
python3 scripts/run_model_workflows.py run BouncingBall
python3 scripts/run_model_workflows.py run-all
```

Simulation runners are discovered from `models/*/*/simulate.py`:

```bash
python3 scripts/run_model_simulations.py list
python3 scripts/run_model_simulations.py run BouncingBall
python3 scripts/run_model_simulations.py run-all
```

## Simulation And Comparison

Simulation execution is automated separately from model setup.

- Each model's `simulate.py` declares a `SimulationConfig` and calls the
  relevant engine helpers explicitly.
- `scripts/run_model_simulations.py` executes those per-model simulation
  scripts.
- `scripts/workflow/comparison.py` collects result CSVs, resamples onto a
  common time grid, and writes pairwise comparison reports.
- Raw outputs are written to
  `build/models/ssp/<model_name>/simulation_results/<engine>/`.
- Pairwise metrics are written to
  `build/models/ssp/<model_name>/simulation_results/comparisons/`.

Example:

```bash
python3 scripts/run_model_simulations.py run embrace
```

## Metadata Shape

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

Source entries are repository-relative. The current setup flow expects exactly
one primary `ssp` or `fmu` source and zero or more `results` files when using
the metadata-driven path. Models can also leave `ssp` and `fmu` empty and let
`build.py` assemble the SSP from shared fixtures in `models/fmu/`.

## Environment Notes

`requirements.txt` currently targets Linux `x86_64`:

- `pyssp4sim` is pinned to a Linux `x86_64` wheel.
- `OMSimulator` is installed from PyPI.

If you work on another platform, expect to adjust dependencies manually.
