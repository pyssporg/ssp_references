# Backend and Case Expansion Assessment

- **Assessment ID:** IMP-CAND-K
- **Layer:** Evolution (06)
- **Theme:** Scope assessment — determine if additional backends or model cases should be added
- **Date:** 2026-05-20
- **Status:** Completed

## Assessment

### Backend Coverage

All three committed backends (ssp4sim, OMSimulator, FMPy) are in use in the registry. Each backend has a working adapter, and all backends are documented in `models/README.md` and the relevant FIXTURE.md files. No new backends are needed at this time.

| Backend | Status | Notes |
|---------|--------|-------|
| ssp4sim | In use | Primary simulation backend |
| OMSimulator | In use | Alternative simulation backend |
| FMPy | In use | FMU import / reference backend |

### Fixture Coverage

All four fixture classes are represented in the registry:

| Fixture Class | Representation | Status |
|---------------|---------------|--------|
| Simple Reference | Present | Adequate |
| Deterministic Signal-Propagation | Present | Adequate (see case expansion below) |
| Composite | Present | Adequate |
| Special-Purpose | Present | Adequate |

All 15 on-disk models are registered in `artifacts/simulation_registry.json`. No models were found to be missing (IMP-CAND-G previously added dcmotor, pyfmu_csv_source_sink, and scenario to close the last gap). No new models are needed.

### Case Expansion

Currently only VanDerPol has multiple cases (`baseline` and `fast`). All other models have a single `baseline` case. The assessment is:

- **Signal-propagation models** could benefit from additional cases with varying input amplitudes and frequencies. This would exercise the comparison pipeline more thoroughly and validate metric thresholds across different dynamic regimes.
- **Simple Reference and Composite models** have stable, configuration-driven behavior that is well-covered by the `baseline` case. Additional cases would add maintenance burden without proportional benefit at this stage.
- **Special-Purpose models** (e.g., scenario) are inherently single-configuration and do not benefit from case expansion.

**Recommendation:** Defer case expansion for signal-propagation models until the comparison pipeline is stable and gate thresholds are established (IMP-CAND-J findings on per-fixture-class thresholds are the prerequisite).

### FMPy Assessment

FMPy is already integrated as a third backend:
- Present in `simulation_registry.json` for applicable models
- Documented in `models/README.md` with Backend Key + model tables
- Listed in FIXTURE.md files via `## Backends` sections (added in IMP-CAND-G)

FMPy fills a useful role as an FMU-native reference backend, but its comparison output has not yet been deeply analyzed. **Recommendation:** Let comparison results accumulate before expanding FMPy-specific cases or investing in deeper FMPy integration.

## Recommendations

1. **Defer backend expansion.** The current set of three backends (ssp4sim, OMSimulator, FMPy) is sufficient. No new backends should be added until the comparison pipeline is stable with the current set and a concrete need arises (e.g., a model that only runs on a specific backend not yet supported, or a comparison discrepancy that requires a tie-breaking backend).

2. **Consider additional cases for signal-propagation models** as a future improvement. This should be re-evaluated after the comparison gate (IMP-CAND-J) is implemented and per-fixture-class thresholds are operational. The additional cases would validate that thresholds hold across input variations.

3. **Re-evaluate quarterly or when comparison gates are established.** The assessment should be revisited when any of these triggers occur:
   - A new model type is added that requires a backend not in the current set
   - The comparison gate implementation reveals gaps in case coverage
   - Quarterly review cycle (next: 2026-08-20)

## Traceability

- **Product:** PD-003 (supported backends) — which backends to support; PD-005 (simulation registry) — which models/cases/backends are registered
- **Architecture:** Fixture hierarchy from `02-architecture/architecture.md` — which fixture classes need coverage
- **Previous improvements:** IMP-CAND-G (registry coverage review) — confirmed all 15 models registered; IMP-CAND-H (backend adapter review) — confirmed adapter functionality; IMP-CAND-J (comparison metrics gate review) — established gate prerequisites