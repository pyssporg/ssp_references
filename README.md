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
│           ├── FIXTURE.md
│           └── ssp/               # only for authored SSP sources such as dcmotor/embrace
├── build/
│   └── models/ssp/<model_name>/
│       ├── <model_name>.ssp
│       ├── ssp/
│       ├── references/            # generated CSV baselines for supported fixtures
│       └── simulation_results/
├── scripts/
│   ├── build_models.py
│   ├── run_simulations.py
│   └── utils/
├── 3rd_party/                # vendored helpers and upstream source material
└── requirements.txt
```


## Model Workflow

Each model directory under `models/ssp/<model_name>/` follows the same basic
contract:

- `build.py` is the source of truth for how that SSP gets assembled.
- `FIXTURE.md` provides the fixture notes for each model.
- Running `build.py` prepares the generated fixture under `build/` by
  validating sources, packaging the `.ssp`, and unpacking a runtime layout.

The workflow runner discovers models from `models/*/*/build.py`:

```bash
python3 scripts/build_models.py list
python3 scripts/build_models.py run BouncingBall
python3 scripts/build_models.py run-all
```

Simulation runners are discovered from `models/*/*/simulate.py`:

```bash
python3 scripts/run_simulations.py list
python3 scripts/run_simulations.py run BouncingBall
python3 scripts/run_simulations.py run-all
```

## Fixture Origins

Classic baseline fixtures keep their provenance in `FIXTURE.md`. For the
reference-model cases, the matching CSV baselines live in
`models/fmu/<model>/references/`.

## Environment Notes

`requirements.txt` currently targets Linux `x86_64`:

- `pyssp4sim` is pinned to a Linux `x86_64` wheel.
- `OMSimulator` is installed from PyPI.

If you work on another platform, expect to adjust dependencies manually.
