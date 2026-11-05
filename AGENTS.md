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

- `models/ssp/<model>/` holds the authored fixture, `build.py`, and `FIXTURE.md`;
  for SysML-authored fixtures the system composition lives in
  `architecture/System.sysml`.
- `models/fmu/` holds only the FMU's side of a SysML-authored fixture:
  `architecture/*.sysml` (its complete definition, with the component declared
  directly as `part def ... :> FmuModel`), `src/`, `build.py`, and
  `FIXTURE.md`; a prepared fixture keeps its `fmu/` body and `references/`.
  The SSP fixture consumes that architecture directory through
  `build_fixture(includes=...)`; it does not copy or link the FMU file.
  Generated FMI definitions (headers, `modelDescription.xml`) plus compiled or
  packaged outputs live under `artifacts/build/<model>/`. The build runs FMU
  then SSP: `run-all` builds every FMU before any SSP.
- `artifacts/` holds generated builds, analyses, simulations, and comparisons.
- `scripts/` holds the shared build, simulate, and compare entry points.
- `3rd_party/` holds one submodule, `pyssp_workflow`, the composition package
  whose base dependencies cover the whole pyssp and SysML stack; it nests the
  capability checkouts plus the SysML dialect (`pycps_sysml2`) and FMI artifact
  (`pyfmi_sysml2`) libraries, and imports none of them. `pycps_sysml2` also
  ships the dialect core definitions (`definitions/core.sysml`), which fixtures
  load instead of redeclaring. Edits belong in their own repositories.

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
- `3rd_party/pyssp_workflow/3rd_party/experimental_pyssp_standard` is the only
  editable `pyssp_standard` checkout; it is the experimental fork
  (`pyssporg/experimental_pyssp_standard`), not the release line. The nested
  `pyssp_sysml2/3rd_party/experimental_pyssp_standard` copy is a pinned
  dependency: do not edit it; local changes belong in the canonical checkout.
- `3rd_party/pyssp_workflow/3rd_party/pycps_sysml2` and
  `.../pyfmi_sysml2` are nested checkouts, not repo-level submodules;
  `3rd_party/pyssp_workflow` is the only top-level submodule and also carries
  both SysML libraries as base dependencies. They are released v0.1.0 libraries;
  the editables point at these nested locations.
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
- `requirements.txt` is the default install: one plain `pyssp-workflow`
  reference whose base dependencies transitively pin the eight pyssp and SysML
  distributions as sibling GitHub release assets
  (`releases/download/v<version>/`). Six are pyssp capability libraries; two
  are the SysML dialect (`pycps-sysml2`) and FMI artifact (`pyfmi-sysml2`)
  libraries. There are no feature extras; the only optional-dependencies group
  is `dev`. The tags must exist before any install or editable checkout
  resolves.
  `requirements-dev.txt` replaces the wheels with editable checkouts under
  `3rd_party/pyssp_workflow/3rd_party/` but still resolves those URLs.
- Many workflows assume Linux `x86_64`, `OMSimulator`, and those pinned wheels.
