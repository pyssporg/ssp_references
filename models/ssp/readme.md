Packaged SSP model directories live here.

Each subdirectory under `models/ssp/` is expected to be a workflow-managed model
with at least these files:

- `workflow.py`
- `metadata.json`

Typical generated artifacts in a model directory:

- `<model_name>.ssp`
- `ssp/`
- `fmus/` when the model is built from FMU sources
- `references/` when upstream result files are available

These models are the main repository outputs and are intended to be simulated,
inspected, unpacked, or used as regression/interoperability fixtures.
