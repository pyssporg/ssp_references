# `ssp_references`

Curated SSP model fixtures plus the scripts used to prepare them, simulate them,
and compare results across engines.

The repository is primarily a working collection of reference models under
`models/ssp/`. Most source material comes from vendored upstream projects in
`3rd_party/`, while the checked-in model directories hold the authored model
definitions, fixture notes, and build metadata.

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
│           ├── experiments.xml
│           ├── FIXTURE.md
│           └── ssp/               # only for authored SSP sources such as dcmotor/embrace
├── artifacts/
│   ├── models/
│   │   └── <model_name>/
│   │       └── <experiment>/
│   ├── comparisons/
│   ├── simulation_registry.json
│   └── simulation/
├── scripts/
│   ├── build_models.py
│   ├── run_simulations.py
│   ├── run_comparisons.py
│   ├── workflow/
│   └── utils/
├── 3rd_party/                # vendored helpers and upstream source material
├── product-breakdown/
│   ├── 00-intent/              # north star intent and commitments
│   ├── 01-product/              # product decisions
│   ├── 02-architecture/         # system architecture and ADRs
│   ├── 03-implementation/       # build/simulation workflow notes
│   ├── 04-verification/         # test strategy and verification
│   ├── 05-operation/            # operational guidance
│   └── 06-evolution/            # backlog and roadmap
└── requirements.txt
```


## Model Workflow

Each model directory under `models/ssp/<model_name>/` follows the same basic
contract:

- `build.py` is the source of truth for how that SSP gets assembled.
- `FIXTURE.md` provides the fixture notes for each model.
- Running `build.py` prepares the generated fixture under `artifacts/models/`
  by validating sources, packaging the `.ssp`, and unpacking a runtime layout.
- Some fixtures also carry `experiments.xml`, but that file is only packaging
  metadata for variant SSP assembly. It is not the main runtime contract.
- Simulation and comparison run through the shared entry points in `scripts/`
  and consume the built SSP root plus `artifacts/simulation_registry.json`.
  Each generated `artifacts/simulation/<model>/<case>/setup.json` records the
  explicit backend list and the explicit compare-signal list for that case.
  The current backend set is `ssp4sim`, `OMSimulator`, and `FMPy`.
  `scripts/run_comparisons.py` compares every unique backend combination from
  that setup by default, or a filtered backend subset when `--backend` is
  repeated. Runtime artifacts live under `artifacts/simulation/` and
  `artifacts/comparisons/`; they do not live in `build.py`.

The build workflow discovers models from `models/*/*/build.py`:

```bash
python3 scripts/build_models.py list
python3 scripts/build_models.py run BouncingBall
python3 scripts/build_models.py run-all
```

Simulation and comparison use the shared entry points:

```bash
python3 scripts/run_simulations.py --help
python3 scripts/run_comparisons.py --help
```

Comparative plots use the same registry and simulation outputs:

```bash
python3 scripts/generate_comparative_plots.py --help
python3 scripts/generate_comparative_plots.py
```

The plot generator writes one PNG per model, case, and variable under
`artifacts/plots/<model>/<case>/<variable>.png`. It compares every available
engine for that case and renders the full stored timeseries without resampling.
It only plots the case's registered `compare_signals`. Use `--model`, `--case`,
and `--backend` to narrow the selection.

To run the full registered suite and generate comparisons for every case that
has at least two recorded backends:

```bash
python3 scripts/run_simulations.py
python3 scripts/run_comparisons.py
```

`run_simulations.py` executes every case in `artifacts/simulation_registry.json`
by default. `run_comparisons.py` then compares each case using all backends
listed in the corresponding `setup.json`, or a filtered backend subset when
`--backend` is repeated. Cases that only have one backend, such as
`pyfmu_csv_source_sink` and `scenario`, are simulated but not comparable.

The registry maps each model to one or more cases, and each model also carries
the explicit compare-signal list used for engine-to-engine comparisons. That
keeps the runtime matrix explicit without pushing execution settings back into
the SSP build step.

## Fixture Origins

Classic baseline fixtures keep their provenance in `FIXTURE.md`. For the
reference-model cases, the matching CSV baselines live in
`models/fmu/<model>/references/`.

## Environment Notes

`requirements.txt` currently targets Linux `x86_64`:

- `pyssp4sim` is pinned to a Linux `x86_64` wheel.
- `OMSimulator` is installed from PyPI.

If you work on another platform, expect to adjust dependencies manually.

## Quick Start

This section walks you from clone to first comparison result in a few minutes.
All commands run from the repository root.

### Prerequisites

- Python 3.10+ and `python3-venv` (Ubuntu: `sudo apt install python3-venv`)
- Linux `x86_64` (required for the pinned `pyssp4sim` wheel)
- OMSimulator system libraries (Ubuntu: `sudo apt install libomsimulator libomc`)

### 1. Clone and set up

```bash
git clone <repo-url> ssp_references
cd ssp_references
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Build a model

Build the simplest reference model (`BouncingBall`) to verify the toolchain:

```bash
# See which models are available
python3 scripts/build_models.py list

# Build one model
python3 scripts/build_models.py run BouncingBall
```

Built artifacts appear under `artifacts/models/BouncingBall/`.

To build every model at once:
```bash
python3 scripts/build_models.py run-all
```

### 3. Simulate

Run `BouncingBall` against two backends for an engine-to-engine comparison:

```bash
python3 scripts/run_simulations.py --model BouncingBall --backend ssp4sim --backend omsimulator
```

Simulation results appear under `artifacts/simulation/BouncingBall/baseline/`.

### 4. Compare

Compare results across the two backends:

```bash
python3 scripts/run_comparisons.py --model BouncingBall --backend ssp4sim --backend omsimulator
```

Comparison metrics and manifests appear under `artifacts/comparisons/BouncingBall/`.

### 5. Run tests

```bash
python3 -m pytest tests/
```

### Full pipeline (one-shot)

```bash
source venv/bin/activate
python3 scripts/build_models.py run BouncingBall
python3 scripts/run_simulations.py --model BouncingBall --backend ssp4sim --backend omsimulator
python3 scripts/run_comparisons.py --model BouncingBall --backend ssp4sim --backend omsimulator
python3 -m pytest tests/
```

### Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|------------|-----|
| `pip install` fails on `pyssp4sim` | Not on Linux `x86_64` | Install manually or use an `x86_64` environment |
| `OMSimulator` import error | System libraries not installed | `sudo apt install libomsimulator libomc` (Ubuntu) |
| `build_models.py: error: argument command: invalid choice` | Subcommand missing | Use `list`, `run <model>`, or `run-all` |
| `No simulation cases matched` | Model name or backend typo | Check `artifacts/simulation_registry.json` for valid names |
| FMU or source files missing | Model needs a clean rebuild | Delete `artifacts/models/<model>` and re-run `build_models.py run <model>` |
| `ModuleNotFoundError: No module named 'workflow'` | Not running from repo root | `cd ssp_references` and verify `scripts/` is in the current directory |
