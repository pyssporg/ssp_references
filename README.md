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
