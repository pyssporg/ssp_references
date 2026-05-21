# Simulation Registry Coverage Review

**Date:** 2026-05-20  
**Review ID:** IMP-CAND-G  
**Scope:** `artifacts/simulation_registry.json` — audit every model/case/backend combination for documented rationale.  
**Method:** Manual review of registry entries against on-disk SSP fixtures, FIXTURE.md content, and architecture decisions.

## Audit Summary

| # | Model | On Disk | In Registry | Backends | Cases | Rationale Exists |
|---|-------|---------|-------------|----------|-------|-----------------|
| 1 | BouncingBall | ✅ | ✅ | ssp4sim, OMSimulator | baseline | ✅ |
| 2 | Dahlquist | ✅ | ✅ | OMSimulator, FMPy | baseline | ✅ |
| 3 | embrace | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 4 | Resource | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 5 | signal_delay_detector | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 6 | signal_fanout_gain | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 7 | signal_sine_gain_add | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 8 | signal_step_add | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 9 | signal_step_gain | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 10 | signal_step_product | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ |
| 11 | Stair | ✅ | ✅ | ssp4sim, OMSimulator | baseline | ✅ |
| 12 | VanDerPol | ✅ | ✅ | ssp4sim, OMSimulator, FMPy | baseline, fast | ✅ |
| 13 | dcmotor | ✅ | ❌→✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ (added) |
| 14 | pyfmu_csv_source_sink | ✅ | ❌→✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ (added) |
| 15 | scenario | ✅ | ❌→✅ | ssp4sim, OMSimulator, FMPy | baseline | ✅ (added) |

## Per-Model Rationale

### Simple Reference Models

**1. BouncingBall**
- **Test level:** Smoke
- **Backend rationale:** Two backends (ssp4sim, OMSimulator) are sufficient for basic event-handling smoke tests. FMPy excluded because this fixture exercises event handling (bouncing-ball discontinuities) and FMPy does not support events in standalone co-simulation. OMSimulator provides a complementary event-handling engine.
- **Registry verification:** Present with `baseline` case and backends `ssp4sim`, `omsimulator`.

**2. Dahlquist**
- **Test level:** Smoke
- **Backend rationale:** OMSimulator and FMPy cover numerical stability testing. ssp4sim excluded because Dahlquist is primarily a numerical-stability regression anchor, and the ssp4sim backend is not yet validated for this model's solver sensitivity. OMSimulator and FMPy provide sufficient cross-engine coverage.
- **Registry verification:** Present with `baseline` case and backends `omsimulator`, `fmpy`.

**3. Stair**
- **Test level:** Smoke
- **Backend rationale:** Two backends (ssp4sim, OMSimulator) suffice for time-event testing. FMPy excluded because step-transition timing verification is adequately covered by two engines, and adding FMPy would add cost without new signal coverage.
- **Registry verification:** Present with `baseline` case and backends `ssp4sim`, `omsimulator`.

**4. Resource**
- **Test level:** Smoke
- **Backend rationale:** Three backends ensure resource-loading behavior is validated across all engines. Resource-dependent FMU execution is a common failure mode that benefits from broad backend coverage.
- **Registry verification:** Present with `baseline` case and backends `ssp4sim`, `omsimulator`, `fmpy`.

**5. VanDerPol**
- **Test level:** Smoke
- **Backend rationale:** Three backends provide broad coverage for continuous nonlinear dynamics. Two cases (`baseline`, `fast`) exercise different parameter regimes (mu = 1.0, mu = 2.0) to validate solver adaptability across engines.
- **Registry verification:** Present with `baseline` and `fast` cases, backends `ssp4sim`, `omsimulator`, `fmpy`.

### Deterministic Signal-Propagation Fixtures

**6-11. signal_step_gain, signal_step_add, signal_fanout_gain, signal_sine_gain_add, signal_step_product, signal_delay_detector**
- **Test level:** Behavioral
- **Backend rationale:** All six fixtures use three backends because deterministic signal-propagation tests are the primary cross-engine comparison vehicles. Tight-tolerance algebraic comparison requires every available backend to ensure propagation behavior is consistent. Each fixture targets a specific propagation pattern (direct feedthrough, fan-in, fan-out, chained transform, multiplication, delay detection).
- **Registry verification:** All six present with `baseline` case and backends `ssp4sim`, `omsimulator`, `fmpy`.

### Composite SSPs

**12. dcmotor**
- **Test level:** Regression
- **Backend rationale:** Three backends validate coupled-execution behavior across all engines. Composite SSPs with multiple interacting FMUs are the most common failure surface and benefit from broad coverage. This entry was missing from the registry and has been added.
- **Registry verification:** ❌ Missing before review → ✅ Added during IMP-CAND-G.

**13. embrace**
- **Test level:** Regression
- **Backend rationale:** Three backends for the same reason as dcmotor. EMBRACE is a larger, resource-heavy orchestration case. OMSimulator requires special flags (`--ignoreInitialUnknowns=true`, `--wallTime=true`, etc.) noted in the FIXTURE.md.
- **Registry verification:** Present with `baseline` case and backends `ssp4sim`, `omsimulator`, `fmpy`.

### Special-Purpose SSPs

**14. pyfmu_csv_source_sink**
- **Test level:** Behavioral
- **Backend rationale:** Three backends ensure CSV-backed source FMU packaging works across all engines. This fixture tests a specific packaging feature (bundling CSV data in an SSP) that could behave differently across engines.
- **Registry verification:** ❌ Missing before review → ✅ Added during IMP-CAND-G.

**15. scenario**
- **Test level:** Behavioral
- **Backend rationale:** Three backends ensure SSV/SSM parameter injection works consistently. Parameter handling is an SSP-specific feature that deserves broad backend coverage.
- **Registry verification:** ❌ Missing before review → ✅ Added during IMP-CAND-G.

## Cross-Cutting Findings

### Finding 1: Missing Registry Entries
Three on-disk SSP fixtures (dcmotor, pyfmu_csv_source_sink, scenario) had no corresponding registry entry. These were present in `models/ssp/` with valid `build.py` and `SystemStructure.ssd` files but were not included in `simulation_registry.json`. All three have been added with three-backend coverage.

**Action:** Added entries with `baseline` case and backends `ssp4sim`, `omsimulator`, `fmpy`.

### Finding 2: Inconsistent Backend Sets Across Simple Reference Models
The backend set for simple reference models varies intentionally:
- BouncingBall, Stair: 2 backends (events/time-events don't need FMPy)
- Dahlquist: 2 backends (OMSimulator + FMPy, no ssp4sim)
- Resource, VanDerPol: 3 backends

This variation is justified per the per-model rationale above and should be preserved.

**Action:** No change needed; rationale documented in this review.

### Finding 3: FMPy Not Documented in README
The models/README.md Backend Key table and model backend columns did not list FMPy as a supported backend, even though it was already used in the registry (e.g., embrace, signal-propagation fixtures). FMPy has been added to the Backend Key and all applicable model table rows.

**Action:** Updated models/README.md with FMPy in Backend Key and backend columns.

### Finding 4: No Backends Section in FIXTURE.md Files
None of the 15 FIXTURE.md files documented which backends each fixture is registered with. This information was only in the registry JSON and partially in models/README.md. All FIXTURE.md files now have a `## Backends` section.

**Action:** Added `## Backends` section to all 15 FIXTURE.md files.

### Finding 5: Registry-SSP Fixture Alignment Is Sound
All 12 models that were already in the registry have valid SSP roots on disk (SystemStructure.ssd and build.py present). No orphaned registry entries were found. The 3 added models were verified to have valid on-disk fixtures before adding.

**Action:** Confirmed alignment; no removals needed.

## Summary of Actions Taken

| Action | Files Affected | Status |
|--------|---------------|--------|
| Backup registry | artifacts/simulation_registry.json.bak | Done |
| Add dcmotor to registry | artifacts/simulation_registry.json | Done |
| Add pyfmu_csv_source_sink to registry | artifacts/simulation_registry.json | Done |
| Add scenario to registry | artifacts/simulation_registry.json | Done |
| Add FMPy to Backend Key in README | models/README.md | Done |
| Update backend columns in README | models/README.md | Done |
| Add Backends section to FIXTURE.md (15 files) | models/ssp/*/FIXTURE.md | Done |
| Create coverage review document | product-breakdown/04-verification/simulation_registry_coverage_review.md | Done |
| Move backlog item to complete | product-breakdown/06-evolution/backlog/ | Done |
| Update review-plan.md | product-breakdown/06-evolution/backlog/complete/review-plan.md | Done |

## Traceability

### Backward Trace

This review traces to the following product breakdown decisions:

- **PD-002 (Model Fixture Hierarchy):** Defines the four architectural fixture classes (Simple Reference, Signal-Propagation, Composite, Special-Purpose) that organize the 15 models in the registry. The per-model rationale section references each fixture's class to justify backend selection.

- **PD-003 (Supported Backends):** Defines which simulation backends are supported (ssp4sim, OMSimulator, FMPy). The registry audit ensures every backend entry is justified per model, and the FMPy backend (in use but undocumented) is now explicitly listed in the Backend Key.

```
PD-002 (Fixture Hierarchy)
    └── Defines model classes → each model's test level and purpose
              ↓
         IMP-CAND-G (This Review)
              ↓
    └── Audits registry against on-disk fixtures
    └── Documents per-model backend rationale
    └── Adds missing entries
              ↓
PD-003 (Supported Backends)
    └── Defines backend set → each backend's inclusion rationale per model
```

---