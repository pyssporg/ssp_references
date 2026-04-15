FMU-centric model directories belong here.

This category is reserved for models whose primary source artifact is an FMU or
an FMU source directory rather than an already-packaged SSP.

If a workflow is added under `models/fmu/<model_name>/`, it follows the same
basic contract as the SSP models:

- `workflow.py` is the entrypoint discovered by `scripts/run_model_workflows.py`
- `metadata.json` declares the repository-relative source paths

These directories are intended as source-oriented building blocks for packaging
or reuse, not as a statement that a raw FMU should be treated as a standalone
SSP.
