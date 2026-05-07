# Simulation Comparison Plan

The goal is to compare simulations between different engines with a simple
three-stage workflow:

1. Build stand-alone SSPs.
2. Run registered simulation cases with one or more backends.
3. Compare the produced trajectories.

## Current Direction

- `build.py` stays SSP-only.
- `artifacts/simulation_registry.json` maps each model to one or more case
  definitions, and each case lists its explicit backends.
- Each generated `setup.json` repeats that backend list so later stages do not
  rely on hidden defaults.
- `scripts/run_simulations.py` writes setup and run manifests under
  `artifacts/simulation/<model>/<case>/`.
- `scripts/run_comparisons.py` writes comparison artifacts under
  `artifacts/comparisons/<model>/<case>/` and compares all unique backend
  combinations from the selected setup by default.
- The setup, simulation, and comparison manifests are the fixed interface
  between stages.

## Review Plan

1. Review the registry coverage and confirm which model/case/backend
   combinations should be kept in the registry.
2. Review backend adapters for `ssp4sim` and `OMSimulator` against the current
   config shape and result CSV contract.
3. Review the setup manifest and run manifest fields for anything that is still
   missing or redundant.
4. Review comparison metrics and decide which are gate-worthy versus
   diagnostic-only.
5. Review whether additional backends or model cases should be added to the
   registry once the first comparison path is stable.

## Open Questions For Further Review

- Which summary metrics should become acceptance criteria?
- Which additional registry entries should be added?

## Current Decisions

- Simulation settings belong to the runtime registry/setup layer and backend
  adapters, not to `experiments.xml`.
- Comparison is engine-to-engine only for now.
- Runtime artifacts stay under `artifacts/`, not inside the SSP trees.
- `build.py` remains build-only.
