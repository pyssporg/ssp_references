# simple_chain

The smallest end-to-end example in this repository: one SysML architecture,
two existing FMUs, and one simulation script. It uses only the public APIs of
`pyssp_sysml2` and `pyssp_simulate`; no repository workflow, registry, or
artifact-layout code is involved.

## What it builds

```text
architecture/simple_chain.sysml
        │  pyssp_sysml2.generate_ssp
        ▼
build/simple_chain.ssp
        │  pyssp_simulate.simulate(backend="ssp4sim")
        ▼
build/ssp4sim.csv
```

The architecture wires two leaf FMUs:

- `Sine` — `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `Gain` — `models/fmu/Modelica.Blocks.Math.Gain/fmu`

```text
Sine.y ──▶ Gain.u
```

Both FMUs keep their model-description defaults (`amplitude=1`, `f=1`,
`k=1`), so `Gain.y` follows the sine wave. The example demonstrates the
pipeline, not a behavioral fixture.

## Setup

`requirements.txt` installs only what the example needs:

- `pyssp_sysml2` from its GitHub release asset (tag `v0.3.0`)
- `pyssp_simulate` from its GitHub release asset (tag `v0.2.0`)
- the experimental `experimental-pyssp-standard` distribution from its GitHub
  release asset (`pyssporg/experimental_pyssp_standard`, tag `v0.9.2.dev0`;
  the distribution name is `experimental-pyssp-standard` and the import name
  stays `pyssp_standard`), because the PyPI release predates the API
  `pyssp_sysml2` needs
- the pinned `ssp4sim` backend wheel (Linux `x86_64`)

Run from the repository root so the relative paths to the requirements file
and `run.py` resolve. The environment lives under `build/`, which is
git-ignored:

```bash
python3 -m venv examples/simple_chain/build/venv
examples/simple_chain/build/venv/bin/pip install -r examples/simple_chain/requirements.txt
```

## Run it

```bash
examples/simple_chain/build/venv/bin/python examples/simple_chain/run.py
```

Generated files:

- `build/simple_chain.ssp` — the packaged architecture, SSD, and both FMUs
- `build/ssp4sim.csv` — the simulated trajectory

`build/` is git-ignored.

## Script

`run.py` has two steps:

```python
ssp_path = generate_ssp(
    architecture_path=EXAMPLE_DIR / "architecture",
    output_path=BUILD_DIR / "simple_chain.ssp",
    composition="SimpleChain",
    fmu_root=REPO_ROOT,
)

result = simulate(
    SimulationSpec(
        ssp=ssp_path,
        start_time=0.0,
        stop_time=1.0,
        step_size=0.001,
        tolerance=1e-6,
        result_file=BUILD_DIR / "ssp4sim.csv",
    ),
    backend="ssp4sim",
)
```

`ssp4sim` requires an explicit `tolerance`; the backend raises `ValueError`
when it is omitted. The SSP is a standard artifact at the library border:
`pyssp_sysml2` writes it and `pyssp_simulate` reads it. Neither package hands
an internal object to the other.

## Files

| Path | Purpose |
|------|---------|
| `architecture/simple_chain.sysml` | Authored architecture: two `part def`s, ports, and one connection |
| `run.py` | Builds the SSP and runs the ssp4sim backend |
| `requirements.txt` | Minimal pip environment for the example |
| `build/` | Generated SSP and result CSV (not checked in) |
