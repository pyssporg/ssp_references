# AGENTS

## AGENT/DEVELOPMENT RULES

1. Don’t assume. Don’t hide confusion. Surface tradeoffs.

2. Minimum code that solves the problem. Nothing speculative

3. Touch only what you must. Clean up only your own mess.

4. Define success criteria. Loop until verified.


## Repository Focus

This repository is a curated collection of SSP model fixtures plus the scripts
used to build them, simulate them, and compare engine outputs.

## Code Guidelines

Keep changes direct and explicit.

- Minimize duplication, but do not introduce abstractions that hide model setup
  details unnecessarily
- Treat this as experimental software:
  interfaces do not need to be stable, and clarity is more important than
  compatibility shims
- Avoid if possible shims and thin wrappers unless a substantial upside

## Environment Guidelines

- Use the repo-local `venv` for Python commands, test runs, and workflow scripts
  when it exists
- `requirements.txt` includes local editable and platform-specific dependencies;
  do not casually rewrite dependency setup unless the task requires it
- Many workflows assume Linux `x86_64` tooling, `OMSimulator`, and the pinned
  wheels in `requirements.txt`

## Documentation Guidelines

- Keep docs short, focused, and tied to the actual workflow in this repository
- Treat `README.md` as the landing page for repository structure and usage
- Keep model-specific notes in each model's `FIXTURE.md`
- Use the canonical template at `product-breakdown/03-implementation/FIXTURE-template.md`
  when creating new FIXTURE.md files; reformat existing files to match when
  editing them
- Follow the `product-breakdown` skill for `product-breakdown/`:
  - current state lives in layer leaves, present tense
  - dated decisions live in `product-breakdown/archive.zip`, read via
    `python3 .agents/skills/product-breakdown/scripts/pb archive list` and
    `... archive read <ID>`
  - add a decision record with
    `python3 .agents/skills/product-breakdown/scripts/pb archive add <record>`
  - never add per-layer `decisions/` folders or hand-maintain decision logs
  - regenerate `decisions/README.md`, `design-choice-log.md`, and
    `traceability-map.md` with `pb registers`; never edit them by hand
  - run `pb check --strict` and `pb node-size --strict` after edits
- Keep cross-cutting workflow or strategy notes in `product-breakdown/`
- When docs move or commands change, update references so the documented build
  and simulation flow stays accurate
