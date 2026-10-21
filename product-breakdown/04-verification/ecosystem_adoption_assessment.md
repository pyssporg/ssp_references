# Ecosystem Adoption Assessment

**Date:** 2026-10-21
**Scope:** `pyssp_simulate` 0.1.1, `pyssp_sysml2` 0.1.1, `sequence_extensions`
3.0.0, evaluated against the 21 built fixtures in this repository.

---

## 1. What Changed

The repository now uses the pyssp ecosystem behind its existing stage
boundaries:

| Concern | Before | After |
| --- | --- | --- |
| SSP runtime prep, ssp4sim config, result CSV parsing | Local implementation in `scripts/workflow/simulate.py` | `pyssp_simulate` (`SimulationSpec`, `prepare_runtime_ssp`, backend adapters) |
| FMPy / OMSimulator calls | Local adapters | Local adapters only where upstream behavior differs; see §4 |
| Comparison gate | Metrics only, invariant violations raised | `scripts/workflow/gate.py`, records `gate` pass/fail |
| Reference baselines | Plot input only | `scripts/workflow/reference.py` compares runs to reference CSVs |
| Campaign orchestration | Sequential CLI loops | `scripts/run_campaign.py` via `sequence_extensions` (Python 3.11+) |
| SysML v2 authoring | None | `scripts/check_sysml_roundtrip.py` evaluation tool (separate env) |

The build, simulate, and compare stage contracts and artifact locations are
unchanged. The runtime venv is now Python 3.11. See
[ADR-005](../02-architecture/decisions/ADR-005.md).

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
| VanDerPol fast | fail | FMPy differs from ssp4sim/OMSimulator by ~0.37 |
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

**Gaps found:**

1. **FMPy ignores SSP parameter bindings.** `simulate_ssp` accepts a
   `parameter_set`, but the upstream FMPy backend does not pass one, so SSV
   values are silently ignored. This repository now passes the SSD's first
   parameter set explicitly.
2. **FMPy rejects SSP 2.0 details and some boundary connections.** The
   repository keeps its validation bypass and connection resolver as a scoped
   shim (`engine_compat.py`).
3. **OMSimulator fixed-step mode suppresses events.** The upstream backend
   calls `setFixedStepSize`, which makes BouncingBall fall through the floor.
   The repository keeps the OMSimulator call local and sets only the logging
   interval.
4. **OMSimulator runs in-process.** A malformed fixture can abort the host
   process (`scenario`, `pyfmu_csv_source_sink`). The campaign runner isolates
   each simulation in a subprocess.
5. **Comparison is engine-to-engine only.** There is no reference-CSV mode and
   no explicit signal-selection/window contract. This repository keeps its
   comparison layer for that reason.
   **Patched upstream in 0.1.1:** `compare_to_reference`,
   `SimulationResult.from_reference_csv`, and `ComparisonWindow` now exist, and
   the CLI accepts `--reference`, `--model-name`, and an explicit grid.

### `pyssp_sysml2`

**Works:** `generate sysml` bootstraps a minimal SysML v2 architecture from an
existing SSD; `generate ssd` regenerates a runnable SSD; the CLI and Python
module APIs both work.

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

**Remaining limitation:** nested SSD systems are still unsupported by the
SysML sync path.

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

SysML round-trip (artifact-only; point at the SysML tool environment):

```bash
python3 scripts/check_sysml_roundtrip.py \
  artifacts/models/signal_step_gain/baseline/SystemStructure.ssd \
  --output /tmp/sysml_roundtrip \
  --pyssp /path/to/venv-sysml/bin/pyssp
```

---

## 5. Gaps to Push Upstream

| Gap | Repository | Status |
| --- | --- | --- |
| FMPy backend does not apply SSV parameter bindings | pyssp_simulate | Open |
| FMPy SSP 2.0 validation/boundary connections | pyssp_simulate / FMPy | Open |
| OMSimulator fixed step suppresses events | pyssp_simulate | Open |
| OMSimulator crashes abort the caller | pyssp_simulate | Open |
| No reference-CSV comparison | pyssp_simulate | Patched in 0.1.1 |
| No explicit comparison window | pyssp_simulate | Patched in 0.1.1 |
| SSD → SysML → SSD loses metadata | pyssp_sysml2 | Patched in 0.1.1 |
| `pyssp_standard` version skew / LS-REF split | pyssp_sysml2 / pyssp_standard | Resolved by artifact boundary: pyssp_sysml2 targets the refactored API; checker invokes `pyssp` via CLI |
| PyPI name collision | sequence_extensions | Patched: publishes as `sequence-extensions-flow` |
| Broken `latest` ssp4sim wheel URL | ssp4sim / this repo | Pinned to `v0.3.2` |

---

## 6. VV Implications

- **Pass/fail is now first-class.** Every pair and reference comparison records
  `gate.status` and reasons in its manifest.
- **Timing skew is handled explicitly.** The gate uses a ±2-sample
  shift-tolerant maximum error; raw pointwise `max_abs_error` remains in the
  metrics for diagnosis. Startup/shutdown samples are excluded from the gate.
- **Reference baselines are gated only when appropriate.** Model-exchange
  references are retained as diagnostics and marked `"gate": false` in the
  registry because the fixtures run co-simulation.
- **The registry remains authoritative.** Gate thresholds and reference
  applicability are registry data, not inferred from directory names.
