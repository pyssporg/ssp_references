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
│           ├── architecture/      # authored SysML (migrated fixtures)
│           ├── build.py
│           ├── experiments.xml    # legacy fixtures only
│           ├── FIXTURE.md
│           └── ssp/               # legacy authored SSP sources
├── artifacts/
│   ├── models/
│   │   └── <model_name>/
│   │       └── <study_name>/
│   │           └── <build_name>/
│   ├── studies/
│   │   └── <model_name>/
│   │       └── <study_name>/
│   ├── comparisons/
│   ├── simulation_registry.json
│   └── simulation/
├── scripts/
│   ├── build_models.py
│   ├── run_simulations.py
│   ├── run_comparisons.py
│   ├── workflow/
│   └── utils/
├── 3rd_party/                # git submodule: pyssp_workflow, which owns the capability checkouts
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

- `architecture/*.sysml` is the authored source for migrated fixtures.
- `part def <Model> :> SspModel` exports one SSP; `part def <Study> :> Study`
  supplies scenario data, a description, and one experiment (`startTime`,
  `stopTime`, `stepSize`) and is never exported as an SSP. A model may author
  several studies; each is built and registered as its own case.
- A fixture may keep a legacy `ssp/` body and author only the study. Its
  `SspModel` composition is then a boundary marker that selects the body with
  `ssp_meta.source`, and is not exported.
- `build.py` derives the model SSP and the study, then packages the scenario
  into a runnable SSP. `build_studies` builds one runnable SSP per study. A
  fixture that exercises a different parameter form applies it with
  `pyssp_standard` in its build hook.
- `FIXTURE.md` provides the fixture notes for each model.
- Running `build.py` writes the runnable SSP under
  `artifacts/models/<model>/<study>/<build>/` and study artifacts under
  `artifacts/studies/<model>/<study>/`.
- A study artifact directory contains a scenario SSV, an SSM mapping, and
  `study.json` with the experiment window and the authored description; it
  contains no SSD or SSP.
- Simulation runs the built SSP as-is; there is no runtime scenario injection.
  Each generated `artifacts/simulation/<model>/<study>/setup.json` records the
  window, explicit backend list, and explicit compare-signal list for that case.
  Tolerance is read from the composed FMUs.
  The current backend set is `ssp4sim`, `OMSimulator`, and `FMPy`.
  `pyssp_simulate` is the execution substrate; local shims remain only for
  documented upstream gaps (FMPy SSP-2.0 loading and OMSimulator step mode).
  `scripts/run_comparisons.py` compares every unique backend combination from
  that setup by default, or a filtered backend subset when `--backend` is
  repeated. Runtime artifacts live under `artifacts/simulation/` and
  `artifacts/comparisons/`; they do not live in `build.py`.

The canonical artifact contract for the stages and external tools is
[Pipeline and Tool Boundaries](product-breakdown/02-architecture/pipeline-boundaries.md):

```text
Build    -> runnable SSP + study SSV/SSM/study.json
Simulate -> reads runnable SSP + study window + registry, writes CSV + run manifests
Compare  -> reads run manifests + CSV, writes comparisons
SysML    -> reads .sysml, invokes external pyssp CLI, writes SSP/study
```

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

### VV gate and reference baselines

`run_comparisons.py` records a `gate` verdict on every engine-to-engine pair
and on every reference comparison. Measurement and judgment come from
`pyssp_vv`; `invalid` is distinct from `fail` when a comparison is not fit to
judge. The gate uses a small time-shift tolerance so ordinary co-simulation
scheduling skew does not fail an otherwise matching signal; raw pointwise error
stays in `metrics.csv` for diagnosis.

```bash
# Record gates without failing the command
python3 scripts/run_comparisons.py

# Exit nonzero if any gate fails or is invalid (CI / campaign use)
python3 scripts/run_comparisons.py --fail-on-gate
```

Reference baselines configured in the registry are compared automatically and
written under `artifacts/comparisons/<model>/<case>/references/`. A reference
entry can set `"gate": false` when it is diagnostic only, such as a
model-exchange baseline for a co-simulation fixture.

### Campaign runner

`run_campaign.py` runs the registered matrix as an audited, parallel campaign
using `sequence_extensions`. It shells out to the normal entry points, so the
simulation and comparison logic has a single home.

```bash
python3 scripts/run_campaign.py --model BouncingBall --model Dahlquist
python3 scripts/run_campaign.py --model BouncingBall --fail-on-gate
python3 scripts/run_campaign.py --model signal_step_gain --fail-on-gate
```

The campaign runs in the same Python 3.11+ environment as the core pipeline.
Run logs are written to `artifacts/runs/<run_id>.jsonl`.

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

- `pyssp4sim` is pinned to the `v0.3.2` Linux `x86_64` wheel.
- `pyssp_simulate` is installed editable from
  `3rd_party/pyssp_workflow/3rd_party/pyssp_simulate` so the repository and its
  simulation substrate develop together.
- `OMSimulator` is installed from PyPI; its sdist can fail when nightly
  binaries have been removed, so a manual install may be needed.

If you work on another platform, expect to adjust dependencies manually.

The campaign runner and `pyssp_sysml2` round-trip tool have their own
environment constraints:

- `scripts/run_campaign.py` requires Python 3.11+ and the editable
  `3rd_party/pyssp_workflow/3rd_party/sequence_extensions` checkout. The project
  declares the distribution name `sequence-extensions-flow` to avoid the
  unrelated PyPI project named `sequence-extensions` (same `sequence_extensions`
  import). Use `requirements-campaign.txt`.
- `scripts/check_sysml_roundtrip.py` is an artifact-only checker. It invokes
  an external `pyssp` executable and exchanges only `SystemStructure.ssd`
  files; it does not import `pyssp_sysml2` or `pyssp_standard`. Point it at a
  dedicated SysML tool environment with `--pyssp /path/to/venv/bin/pyssp` or
  the `PYSSP` environment variable. `requirements-sysml.txt` describes that
  environment. The build stage also needs `pyssp_sysml2`; `requirements.txt`
  installs it through the `pyssp_workflow` submodule.

The pyssp and sequence submodules are editable checkouts. See
[`3rd_party/README.md`](3rd_party/README.md) for initialization, update, and
local-patch guidance.

See [the ecosystem assessment](product-breakdown/04-verification/ecosystem_adoption_assessment.md)
for the evaluated versions and remaining gaps.

## Quick Start

This section walks you from clone to first comparison result in a few minutes.
All commands run from the repository root.

### Prerequisites

- Python 3.11+ and `python3-venv` (Ubuntu: `sudo apt install python3-venv`)
- Linux `x86_64` (required for the pinned `pyssp4sim` wheel)
- OMSimulator system libraries (Ubuntu: `sudo apt install libomsimulator libomc`)

### 1. Clone and set up

```bash
git clone --recurse-submodules <repo-url> ssp_references
cd ssp_references

# If the repository was cloned without submodules:
# git submodule update --init --recursive

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

Built artifacts appear under `artifacts/models/BouncingBall/baseline/model/`.

To build a SysML-authored signal fixture and its study:

```bash
python3 scripts/build_models.py run signal_step_gain
```

This writes `artifacts/models/signal_step_gain/test_baseline/model/` and
`artifacts/studies/signal_step_gain/test_baseline/`.

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
