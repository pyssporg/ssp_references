# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`docs/breakdown/00-intent/intent.md`**

It states why this repository exists, what it commits to, and what it refuses to
become. It is the first document to read, not a reference of last resort.

- Read it in full before making any change to code, tests, docs, or artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, goals, or non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

This repository is a curated collection of SSP model fixtures plus the scripts
that build, simulate, and compare them across engines. Its product is evidence:
reproducible fixtures and cross-engine comparison results, not new simulation
capability.

- `models/ssp/<model>/` holds the authored fixture, `build.py`, and `FIXTURE.md`.
- `models/fmu/` holds prepared FMU fixtures with their references.
- `artifacts/` holds generated builds, studies, simulations, and comparisons.
- `scripts/` holds the shared build, simulate, and compare entry points.
- `3rd_party/` vendors the pyssp capability checkouts; edits belong in their
  own repositories.

## Hard constraints

- **Fixtures are reproducible.** Every model carries a documented build contract
  and explicit provenance so that a rebuild produces the same artifact.
- **The built artifact is the unit under test.** Simulation runs the built SSP
  as-is; there is no runtime scenario injection.
- **Comparison results are the quality gate.** Correctness is judged by
  trajectories against trusted baselines, not by inspection or manual review.
- **Standard artifacts first at library borders.** SSP, SSD, SSV, SSM, LS-REF,
  or result CSV cross first; internal objects never do.
- **Not a production framework, not a conformance suite.** Do not grow it into
  either; see the vision's non-goals.

## Code guidelines

- Keep changes direct and explicit. Minimize duplication, but do not hide model
  setup behind abstractions.
- Treat this as experimental software: interfaces need not be stable, and
  clarity outranks compatibility shims.
- Avoid shims and thin wrappers unless they buy something substantial.

## Conventions

- `README.md` is the landing page for repository structure and usage.
- Model notes live in each model's `FIXTURE.md`; new files follow
  `docs/breakdown/03-implementation/FIXTURE-template.md`.
- `docs/breakdown/` follows the product-breakdown skill. Set
  `PB=<skills-dir>/product-breakdown/scripts/pb` and pass `--root docs/breakdown`
  to every command:
  - current state lives in layer leaves, in the present tense;
  - dated decisions live in `docs/archive/archive.zip`, read with
    `python3 $PB archive --root docs/breakdown list` and
    `... read <ID>`, and added with `... add <record>`;
  - never add per-layer `decisions/` folders or hand-maintain decision logs;
  - regenerate `docs/archive/README.md`,
    `docs/archive/design-choice-log.md`, and
    `docs/archive/traceability-map.md` with
    `python3 $PB registers --root docs/breakdown`; never edit
    them by hand;
  - run `python3 $PB check --strict --root docs/breakdown`
    and `... node-size --strict --root docs/breakdown` after edits.
- `3rd_party/pyssp_workflow/3rd_party/pyssp_standard` is the only editable
  pyssp_standard checkout. The nested
  `pyssp_sysml2/3rd_party/pyssp_standard` copy is a pinned dependency: do not
  edit it; local changes belong in the canonical checkout.
- Keep cross-cutting workflow or strategy notes in `docs/breakdown/`.
- When docs move or commands change, update the references so the documented
  build and simulation flow stays accurate.

## Environment

- Use the repo-local `venv`: `source venv/bin/activate`, or call
  `./venv/bin/python` directly.
- Tests: `python3 -m pytest tests/`.
- Build: `python3 scripts/build_models.py list` / `run <model>` / `run-all`.
- Simulate, then compare: `python3 scripts/run_simulations.py`, then
  `python3 scripts/run_comparisons.py`.
- `requirements.txt` pins local editable submodules and platform wheels. Do not
  rewrite the dependency setup unless the task requires it.
- Many workflows assume Linux `x86_64`, `OMSimulator`, and those pinned wheels.
