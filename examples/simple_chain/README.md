# simple_chain

Builds the `SimpleChain` architecture — two existing Modelica FMUs wired
`Sine.y → Gain.u` — into an `.ssp`, then simulates it with the `ssp4sim`
backend.

## Run

From the workspace root, in the workspace venv:

```bash
python repos/ssp_references/examples/simple_chain/run.py
```

Everything lands under the gitignored `build/examples/simple_chain/`:

| Path | What |
| --- | --- |
| `simple_chain.ssp` | the packaged architecture, SSD, and both FMUs |
| `ssp4sim.csv` | the simulated trajectory |

Expected output:

```text
SSP: build/examples/simple_chain/simple_chain.ssp
CSV: build/examples/simple_chain/ssp4sim.csv
```

`--out DIR` writes both artifacts to another directory. The `SimulationSpec`
sets `tolerance=1e-6` because the `ssp4sim` backend rejects an omitted
tolerance.

## Setup

Activate the workspace venv from the root `README.md`, which supplies
`pyssp_sysml`, `pycps_sysml`, `pyssp_simulate`, and the `ssp4sim` backend:

```bash
source .venv-experimental/bin/activate
```

This example's `requirements.txt` pins its standalone release-wheel set:
`pyssp_sysml` `v0.7.0` (which pulls `experimental-pyssp-standard`
`v0.9.4.dev0` transitively), `pyssp_simulate` `v0.4.0`, and `ssp4sim`
`v0.3.6`.

## What the definition encodes

`architecture/simple_chain.sysml` uses the `PysspCore` dialect roles owned by
`pyssp_sysml_definitions` and re-exported by
`pycps_sysml.core_definitions()`
(`repos/pyssp_sysml_definitions/src/pyssp_sysml_definitions/core.sysml`):

- `Sine` and `Gain` are `FmuModel`s. Each `fmu_meta :> FmuMetadata` names its
  `source` under `models/fmu/` and `implementation = "CoSimulation"`.
- `RealSignal` is the one port definition: an `attribute value : Real`.
- `SimpleChain :> SspModel` is the exportable SSP boundary, with
  `DefaultExperiment` start `0.0` and stop `1.0`.

Both FMUs keep their model-description defaults (`amplitude=1`, `f=1`,
`k=1`), so `Gain.y` follows the sine wave. The example demonstrates the
pipeline, not a behavioral fixture.

## Composition

`SimpleChain` declares `part sine : Sine`, `part gain : Gain`, and one
connection:

```text
sine.y ──▶ gain.u
```

`Sine` is output-only and `Gain` takes that signal in and publishes its own
output, so the composition is the two components plus that single wire.

## Files

| Path | Purpose |
| --- | --- |
| `architecture/simple_chain.sysml` | Authored architecture: two `part def`s, ports, and one connection |
| `run.py` | Builds the SSP and runs the `ssp4sim` backend |
| `requirements.txt` | Release-wheel pins for a standalone install |
