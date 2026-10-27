---
id: EVAL-002
type: eval
title: Ecosystem Adoption Assessment
summary: Fit of pyssp_simulate, pyssp_sysml2, pyssp_vv, and sequence_extensions to the fixture suite.
date: 2026-10-22
status: current
pb_exempt: true
---

# Ecosystem Adoption Assessment

**Date:** 2026-10-22
**Scope:** `pyssp_simulate` 0.2.0, `pyssp_sysml2` 0.1.1, `pyssp_vv` 0.1.0,
`sequence_extensions` 3.0.0, evaluated against the 21 built fixtures in this
repository.

---

## 1. What Changed

The repository now uses the pyssp ecosystem behind its existing stage
boundaries:

| Concern | Before | After |
| --- | --- | --- |
| SSP runtime prep, ssp4sim config, result CSV parsing | Local implementation in `scripts/workflow/simulate.py` | `pyssp_simulate` (`SimulationSpec`, `prepare_runtime_ssp`, backend adapters) |
| FMPy / OMSimulator calls | Local shims | `pyssp_simulate` spec fields (`fixed_step`, `validate_ssd`, `omsimulator_options`) |
| Comparison gate | Metrics only, invariant violations raised | `pyssp_vv.measure` metrics and `pyssp_vv.judge` verdicts |
| Reference baselines | Plot input only | `scripts/workflow/reference.py` compares runs to reference CSVs through `pyssp_vv` |
| Campaign orchestration | Sequential CLI loops | `scripts/run_campaign.py` via `sequence_extensions` (Python 3.11+) |
| SysML v2 authoring | Round-trip checker only | `pyssp_workflow.authoring` → `pyssp` CLI for `SspModel` export and `Study` scenario generation |
| Capability ownership | Local pipeline implementations | `pyssp_workflow` composition over `pyssp_standard` / `pyssp_simulate` / `pyssp_vv` / `pyssp_sysml2` |

The Build → Simulate → Compare stage contract is unchanged. Migrated fixtures
add a model SSP plus study artifacts, and the build packages the scenario into
the SSP (`DD-011`). The runtime venv is now Python 3.11.
See `ADR-005`, `ADR-007`, and `ADR-013`.

---

## 2. Simulation Results

All registered cases were executed after the swap. The run matrix is the
registry's, not an ad-hoc list. 57 of 58 registered simulation runs complete;
the remaining OMSimulator run is the parameter-mapping parsing gap in §4.

| Fixture group | Result |
| --- | --- |
| BouncingBall, Dahlquist, Resource, Stair, VanDerPol | All registered backends run |
| Deterministic signal fixtures (`signal_*`) | All registered backends run, except the known OMSimulator/ssp4sim gaps in §4 |
| dcmotor, embrace | Both registered backends run |
| `pyfmu_csv_source_sink`, `scenario` | ssp4sim runs; these cases are registered for ssp4sim only |
| `signal_parameter_inline_with_mapping` | ssp4sim runs; OMSimulator fails on parameter-mapping parsing |

`pyssp_simulate` was **not a regression** for the registered matrix. The cases
that still fail through the new substrate failed through the old adapters for
the same reasons. The substrate also removed the need for local ssp4sim JSON
construction, runtime SSP copying, and result CSV normalization.

### Gate outcome after adoption

`run_comparisons.py` records a verdict per pair and per reference. Current
results (raw engine output, default gate `atol=1e-3`, `rtol=1e-2`):

| Case | Gate | Main reason |
| --- | --- | --- |
| Dahlquist, Resource, Stair, VanDerPol baseline | pass | agreement within 5e-7 (shift-tolerant) |
| signal_algebraic_loop, signal_fanout_gain, signal_sine_gain_add, signal_step_add, signal_step_gain, signal_step_product | pass | timing skew removed by shift tolerance |
| BouncingBall | fail | OMSimulator misses bounce events (`h`/`v` diverge) |
| VanDerPol fast | pass | all registered backends agree within the gate tolerance |
| dcmotor, embrace | fail | composite engines diverge by 32–287 |
| signal_delay_detector, signal_nested_algebraic_loop | fail | initialization/iteration difference up to 1.0 |

These failures are evidence, not test noise. They are the first concrete VV
backlog produced by the gate.

---

## 3. Library Findings

### `pyssp_simulate`

**Works:** runtime SSP normalization, unpacked-FMU repackaging, ssp4sim
subprocess isolation, result canonicalization, reference/engine comparison
primitives, permutation runs, CLI.

**Boundary behavior:**

1. **FMPy applies the parameter set the SSD declares.** The backend reads the
   binding from the system definition and applies the SSM mapping to target
   names. If the SSD declares no binding, no parameter set is passed: an
   unreferenced SSV is never merged (`DD-013`).
2. **FMPy SSP 2.0 details need the validation bypass.** `validate_ssd=False`
   skips FMPy's bundled SSP 1.0 schema check, and the backend resolves
   system-boundary connections with its own traversal.
3. **OMSimulator fixed step is opt-in.** With `fixed_step=False` the backend
   sets only the logging interval, so the master keeps event handling and
   BouncingBall keeps its bounces. `fixed_step=True` forces the step size.

**Gaps and policy:**

1. **OMSimulator runs in-process.** A malformed fixture can abort the host
   process (`scenario`, `pyfmu_csv_source_sink`). The campaign runner isolates
   each simulation in a subprocess.
2. **Comparison policy stays in the repository.** Signal selection, window,
   tolerances, and manifests are repository-specific; measurement and judgment
   come from `pyssp_vv.measure` and `pyssp_vv.judge`.

### `pyssp_sysml2`

**Works:** `generate sysml` bootstraps a minimal SysML v2 architecture from an
existing SSD; `generate ssd` regenerates a runnable SSD; the CLI and Python
module APIs both work.

**Direction:** SysML is now an authoring source, not only a round-trip checker.
`part def ... :> SspModel` definitions are exported as SSPs;
`part def ... :> Study` definitions generate scenario SSV/SSM and experiment
descriptors but are never exported as SSPs. Part-def specialization must be
recorded for the role markers. Studies compose the model with `part sut : Model`;
structural inheritance of parts/connections is not supported and is not
required.

**Gap: the round-trip was lossy.** For
`artifacts/models/signal_step_gain/baseline/SystemStructure.ssd` the original
implementation lost connector `kind`, parameter bindings, the default
experiment, and `implementation`, and rewrote connectors as `port.attribute`.

**Patched in 0.1.1:** SSD metadata that has no first-class SysML equivalent is
carried as `pyssp_*` control attributes and skipped by the SSV/FMI generators.
The same fixture now round-trips structurally: connector kinds, parameter
values/source, `implementation="CoSimulation"`, and `DefaultExperiment`
(`0.0..1.0`) survive. The generated architecture is preserved at
[`examples/signal_step_gain.architecture.sysml`](examples/signal_step_gain.architecture.sysml)
as an evaluation artifact, not a build input.

**Interface gap closed:** `pyssp_sysml2` now targets the refactored
`pyssp_standard` model API directly (`SSD.xml`, `SSV.xml`,
`Connector.type_name`). No compatibility layer is added to `pyssp_standard`.

**Tool boundary:** `check_sysml_roundtrip.py` no longer imports
`pyssp_sysml2`/`pyssp_standard`. It invokes an external `pyssp` executable and
exchanges only SSD files, so the SysML tool can run in a separate environment
with its own library versions (ADR-006).

**Remaining limitations:**

- Nested SSD systems are still unsupported by the SysML sync path.
- Part-def structural inheritance is not modeled; `SspModel`/`Study` roles use
  marker specialization and studies compose the model with `part sut`.
- One study declares one experiment initially. Multiple experiments per study
  require a registry/layout distinction between study/build and case/experiment.

### `sequence_extensions`

**Works:** `@node`/`execute_flow`, bounded thread pool, JSON-lines audit log,
dependency edges when futures are passed as direct arguments, child runs, and
CLI-free embedding.

**Gaps / constraints:**

1. Requires **Python 3.11+**; the runtime venv is now 3.11.
2. PyPI `sequence-extensions==0.1.4` is a different, older package with no
   `flow` module. The current project builds as
   `sequence-extensions-flow` (same import package).
3. Futures inside a list are not dependency edges. Pass each future as a
   direct argument (the campaign runner does this).
4. A thread pool cannot contain a native engine abort. The campaign runner
   shells out to `run_simulations.py`, so the abort stays in the child process.
5. Retry/error policy is exception-based: a node body that returns a nonzero
   subprocess exit as a value never triggers retries and does not stop
   dependents. The campaign's `_run` helper returns a result dict, so this is the
   live behavior.
6. Node timeout abandons the attempt and cancels the future, but cannot
   interrupt a body blocked in `subprocess.run`; no process-group kill or
   external-engine cancellation exists.
7. Failure handling is not fail-fast: on a run error the pool cancels pending
   nodes but waits for already-running nodes, so a long child process delays the
   failure return.
8. The library's worker sizing is one fixed global bound (default 16) with no
   machine-derived default, no per-node resource class, priority, or affinity;
   all nodes share one FIFO pool. The campaign now derives
   `min(16, CPU count)` and accepts `--max-workers`, but the library itself
   offers no resource-aware scheduling.
9. The resolved `RunOptions` are not recorded in `run_start`; the audit log
   records node args/kwargs. The campaign passes `workers` as a campaign
   argument so it appears there, but pool sizing is otherwise invisible after
   the fact.

**Tradeoff:** `ProcessGraphPool` is not a fix for this pattern. It requires
picklable payloads and forbids submit/return-future inside workers, while the
thread pool is the correct fit for nodes that shell out to subprocesses.

These items are recorded for a later `sequence_extensions` review; no fix is in
scope now.

---

## 4. Running the New Workflows

Core pipeline (Python 3.11 venv):

```bash
source venv/bin/activate
python3 scripts/run_simulations.py
python3 scripts/run_comparisons.py
python3 scripts/run_comparisons.py --fail-on-gate
```

Campaign (same Python 3.11 venv with `sequence-extensions-flow` 3.0.0):

```bash
python3 scripts/run_campaign.py --model BouncingBall --model Dahlquist
python3 scripts/run_campaign.py --model BouncingBall --fail-on-gate
```

Logs are written under `artifacts/runs/<run_id>.jsonl`.

SysML authoring and round-trip (point at the SysML tool environment):

```bash
# Exported model SSP from an SspModel composition
pyssp generate ssp \
  --architecture models/ssp/signal_step_gain/architecture \
  --composition System \
  --output artifacts/models/signal_step_gain/model/model.ssp \
  --fmu-root .

# Study scenario + experiment data (no SSP)
pyssp generate study \
  --architecture models/ssp/signal_step_gain/architecture \
  --composition test_baseline \
  --model signal_step_gain \
  --output-dir artifacts/studies/signal_step_gain/test_baseline

# Structural round-trip check
python3 scripts/check_sysml_roundtrip.py \
  artifacts/models/signal_step_gain/model/SystemStructure.ssd \
  --output /tmp/sysml_roundtrip \
  --pyssp /path/to/venv-sysml/bin/pyssp
```

---

## 5. Gap Status

| Gap | Repository | Status |
| --- | --- | --- |
| FMPy backend does not apply SSV parameter bindings | pyssp_simulate | Closed: applies the parameter set the SSD declares |
| FMPy SSP 2.0 validation/boundary connections | pyssp_simulate / FMPy | Closed: `validate_ssd` spec field plus the backend connection resolver |
| OMSimulator fixed step suppresses events | pyssp_simulate | Closed: `fixed_step=False` keeps event handling |
| OMSimulator crashes abort the caller | pyssp_simulate | Open |
| No reference-CSV comparison | pyssp_simulate | Patched in 0.1.1 |
| No explicit comparison window | pyssp_simulate | Patched in 0.1.1 |
| SSD → SysML → SSD loses metadata | pyssp_sysml2 | Patched in 0.1.1 |
| No `SspModel`/`Study` role markers or study generation | pyssp_sysml2 | Implemented in pilot (ADR-009) |
| Scenario packaging in the build | pyssp_workflow | Implemented: `pyssp_workflow.binding` packaging forms (`DD-011`) |
| Comparison and gate ownership | this repo → pyssp_vv | Migrated to `pyssp_vv.measure` and `pyssp_vv.judge` (DD-010) |
| `pyssp_standard` version skew / LS-REF split | pyssp_sysml2 / pyssp_standard | Resolved by artifact boundary: pyssp_sysml2 targets the refactored API; checker invokes `pyssp` via CLI |
| PyPI name collision | sequence_extensions | Patched: publishes as `sequence-extensions-flow` |
| Broken `latest` ssp4sim wheel URL | ssp4sim / this repo | Pinned to `v0.3.2` |

---

## 6. VV Implications

- **Pass/fail/invalid are first-class.** Every pair and reference comparison
  records `gate.status` and reasons in its manifest. `invalid` means the
  comparison was not fit to judge; campaign exit codes do not collapse it into
  `fail`.
- **Model and study evidence are separate.** The exported SSP checksum is part
  of provenance; the study scenario and experiment descriptor are run inputs.
  Neither is rewritten by simulation.
- **Timing skew is handled explicitly.** The gate uses a ±2-sample
  shift-tolerant maximum error; raw pointwise `max_abs_error` remains in the
  metrics for diagnosis. Startup/shutdown samples are excluded from the gate.
- **Reference baselines are gated only when appropriate.** Model-exchange
  references are retained as diagnostics and marked `"gate": false` in the
  registry because the fixtures run co-simulation.
- **The registry remains authoritative.** Gate thresholds and reference
  applicability are registry data, not inferred from directory names.
