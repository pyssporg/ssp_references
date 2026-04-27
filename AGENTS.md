# AGENTS

## Repository Focus

This repository is a curated collection of SSP model fixtures plus the scripts
used to build them, simulate them, and compare engine outputs.

The main authored code lives in:
- `models/ssp/<model_name>/` for per-model fixture definitions
- `scripts/run_model_workflows.py` for build workflow discovery/execution
- `scripts/run_model_simulations.py` for simulation discovery/execution
- `scripts/workflow/` for shared packaging, simulation, filesystem, and
  comparison helpers
- `scripts/cli/` for smaller task-focused utilities

The main data inputs live in:
- `models/fmu/` for reusable FMU fixtures
- `3rd_party/` for vendored upstream source material

Generated output lives in:
- `build/`, which is disposable and should be treated as generated state

## AI Context Guidelines

Keep repository context narrow. Do not scan the whole repo by default.

Read in this order:
- `AGENTS.md`
- `README.md`
- the specific workflow entrypoint relevant to the task:
  `scripts/run_model_workflows.py`,
  `scripts/run_model_simulations.py`,
  or a file under `scripts/cli/`
- the smallest relevant shared helper under `scripts/workflow/`
- the specific model directory under `models/ssp/<model_name>/` when the task is
  model-specific:
  `build.py`,
  `simulate.py`,
  `metadata.json`,
  and `FIXTURE.md` as needed
- `docs/` only when the task is documentation-related

Prefer opening one file at a time over reading complete directories.

Avoid reading these paths unless the task explicitly requires them:
- `venv/`
- `.git/`
- `.pytest_cache/`
- `__pycache__/`
- `build/`
- large generated or packaged artifacts such as `*.fmu`, `*.ssp`, `*.zip`, `*.mat`

Do not start by reading all of `3rd_party/`. Treat it as source material to
reference only when a model's metadata or workflow points there.

Ask questions if anything is unclear

## Search Strategy

- Prefer targeted `rg` queries scoped to `models/`, `scripts/`, `docs/`, or one
  model directory
- Prefer opening the model or workflow file you will edit before reading related
  files
- If a task is about one fixture, inspect that model's `FIXTURE.md` and
  `metadata.json` before chasing shared helpers
- If a task is about workflow behavior, inspect `scripts/workflow/` before
  looking into vendored code

## Code Guidelines

Keep changes direct and explicit.

- Keep scripts simple and easy to run from the repository root
- Minimize duplication, but do not introduce abstractions that hide model setup
  details unnecessarily
- Preserve the current design where each model's `build.py` and `simulate.py`
  are the source of truth for that model
- For authored SSP composition in `models/ssp/<model_name>/build.py`, use
  `pyssp_standard` facades such as `SSP`, `system_structure()`, `add_fmu()`,
  `Connection`, and parameter-set helpers. Do not hand-write
  `SystemStructure.ssd` XML or manually assemble SSP zip files unless the task
  is explicitly about testing malformed or low-level archive behavior.
- Prefer editing repository-owned workflow code over patching vendored upstream
  code in `3rd_party/` unless the task is explicitly about vendored content
- Treat this as experimental software:
  interfaces do not need to be stable, and clarity is more important than
  compatibility shims

## Environment Guidelines

- Use the repo-local `venv` for Python commands, test runs, and workflow scripts
  when it exists
- Prefer `. venv/bin/activate && <command>` or `venv/bin/python <command>` over
  the system Python
- `requirements.txt` includes local editable and platform-specific dependencies;
  do not casually rewrite dependency setup unless the task requires it
- Many workflows assume Linux `x86_64` tooling, `OMSimulator`, and the pinned
  wheels in `requirements.txt`

## Validation Guidelines

Choose the smallest validation that proves the change.

- For workflow discovery changes, run:
  `venv/bin/python scripts/run_model_workflows.py list`
  or
  `venv/bin/python scripts/run_model_simulations.py list`
- For model build changes, prefer:
  `venv/bin/python scripts/run_model_workflows.py run <model>`
- For simulation changes, prefer:
  `venv/bin/python scripts/run_model_simulations.py run <model>`
- For comparison or utility changes, run the smallest relevant script in
  `scripts/cli/`
- Use `pytest` only when the task actually touches test-covered behavior; do not
  assume broad automated coverage exists in this repo

## Documentation Guidelines

- Keep docs short, focused, and tied to the actual workflow in this repository
- Treat `README.md` as the landing page for repository structure and usage
- Keep model-specific notes in each model's `FIXTURE.md`
- Keep cross-cutting workflow or strategy notes in `docs/`
- When docs move or commands change, update references so the documented build
  and simulation flow stays accurate
