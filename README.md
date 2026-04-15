# `ssp_references`

Curated SSP model fixtures plus the scripts used to prepare them, simulate them,
and compare results across engines.

The repository is primarily a working collection of reference models under
`models/ssp/`. Most source material comes from vendored upstream projects in
`3rd_party/`, while the checked-in model directories hold the packaged SSPs,
their unpacked layouts, copied references, and any manual adjustments kept as
part of the repo.

## Layout

```text
.
├── models/
│   └── ssp/
│       └── <model_name>/
│           ├── workflow.py
│           ├── metadata.json
│           ├── <model_name>.ssp
│           ├── ssp/
│           ├── fmus/              # only when the model starts from FMU sources
│           ├── references/        # copied reference trajectories when available
│           └── simulation_results/
├── scripts/
│   ├── run_model_workflows.py
│   ├── cli/
│   └── workflow/
├── 3rd_party/
│   ├── OMSimulator
│   ├── reference_fmus
│   └── pyfmu_csv
└── requirements.txt
```

## What Lives Where

- `models/ssp/` is the main output of the repo. Each model directory is both a
  reusable fixture and the place where model-specific artifacts are kept.
- `workflow.py` is the per-model executable entrypoint discovered by
  `scripts/run_model_workflows.py`.
- `metadata.json` declares the upstream SSP, FMU, and reference-result sources
  used by the shared workflow code.
- `scripts/workflow/` contains the common implementation for setup, packaging,
  unpacking, simulation, and comparison.
- `scripts/cli/` contains small task-focused helpers for comparing engines,
  unpacking archives, packaging a single FMU as an SSP, and converting MAT
  results to CSV.
- `3rd_party/` is upstream source material. In normal repo work, it is input
  data, not the main place to edit behavior.

## Model Workflow

Each model directory under `models/ssp/<model_name>/` follows the same basic
contract:

- `workflow.py` calls the shared setup flow for that model.
- `metadata.json` points at the upstream source artifacts.
- Running the workflow prepares the local fixture by validating sources,
  building or copying FMUs when needed, packaging the `.ssp`, unpacking it into
  `ssp/`, and copying reference trajectories into `references/`.

The workflow runner discovers models from `models/*/*/workflow.py`:

```bash
python3 scripts/run_model_workflows.py list
python3 scripts/run_model_workflows.py run BouncingBall
python3 scripts/run_model_workflows.py run-all
```

## Simulation And Comparison

Simulation execution is automated separately from model setup.

- `scripts/cli/compare_engines.py` runs OMSimulator and `ssp4sim` for one or
  more prepared models, collects result CSVs, resamples onto a common time
  grid, and writes pairwise comparison reports.
- Raw outputs are written to
  `models/ssp/<model_name>/simulation_results/<engine>/`.
- Pairwise metrics are written to
  `models/ssp/<model_name>/simulation_results/comparisons/`.

Example:

```bash
python3 scripts/cli/compare_engines.py embrace \
  --ssp4sim-app ../ssp4sim/build/public/ssp4sim_app/sim_app
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
one primary `ssp` or `fmu` source and zero or more `results` files.

## Environment Notes

`requirements.txt` currently targets Linux `x86_64`:

- `pyssp4sim` is pinned to a Linux `x86_64` wheel.
- `OMSimulator` is installed from PyPI.

If you work on another platform, expect to adjust dependencies manually.
