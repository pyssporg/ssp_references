# Manifest Field Review

**Review ID:** IMP-CAND-I  
**Date:** 2026-05-20  
**Type:** Read-only schema audit  
**Scope:** `setup.json` and `simulation.json` manifest schemas

---

## 1. `setup.json` Schema (produced by `setup.py` `SimulationSetup.to_dict()`)

| # | Field | Type | Required | Source / Producer | Example |
|---|-------|------|----------|-------------------|---------|
| 1 | `model` | string | yes | CLI `--model` / `default_model` | `"Simple2R"` |
| 2 | `case` | string | yes | CLI `--case` / `default_case` | `"step"` |
| 3 | `ssp_root` | string (relative path) | yes | `SimulationSetup.__init__` derived from model/case | `"SSPs/Simple2R/step"` |
| 4 | `window.start_time` | float | yes | CLI `--window-start` / default | `0.0` |
| 5 | `window.stop_time` | float | yes | CLI `--window-stop` / default | `60.0` |
| 6 | `window.interval` | float | yes | CLI `--window-interval` / default | `0.1` |
| 7 | `tolerance` | float | yes | CLI `--tolerance` / default | `1e-4` |
| 8 | `backends` | array of string | yes | CLI `--backends` | `["ref", "oms"]` |
| 9 | `compare_signals` | array of string | yes | CLI `--compare-signals` | `["y1", "y2"]` |
| 10 | `root_system_name` | string | yes | Registry `get_root_system_name()` | `"Simple2R"` |
| 11 | `system_structure` | string (relative path) | yes | Registry `get_system_structure_path()` | `"model/system_structure.json"` |
| 12 | `ls_ref_experiments` | string (relative path) | yes | Registry `get_ls_ref_experiments_path()` | `"model/ls_ref_experiments.mat"` |
| 13 | `resources_dir` | string (relative path) | yes | Registry `get_resources_dir()` | `"resources"` |
| 14 | `description` | string or null | no | Setup comment or null | `"Step response test case"` or `null` |

**Schema size:** 14 fields (1 optional, 13 required)  
**Nesting:** Only `window` contains sub-fields. No other nested objects or arrays of objects.

### Observations

- Every required field has a clear producer in `SimulationSetup.__init__` or `to_dict()`.
- `description` is the only truly optional field.
- No deprecated or redundant fields exist.
- The `ssp_root` path is computed rather than user-provided — correct as a derived convenience field.

---

## 2. `simulation.json` Schema (produced by `simulate.py` `SimulationRun.to_dict()`)

| # | Field | Type | Required | Source / Producer | Example |
|---|-------|------|----------|-------------------|---------|
| 1 | `request.model` | string | yes | Copied from `setup.json` | `"Simple2R"` |
| 2 | `request.case` | string | yes | Copied from `setup.json` | `"step"` |
| 3 | `request.backend` | string | yes | Backend identifier from sweep | `"oms"` |
| 4 | `request.setup_manifest` | string (relative path) | yes | Path to the `setup.json` used | `"manifests/Simple2R/step/setup.json"` |
| 5 | `result` | string (relative path) | yes | Path to the output `.mat` file | `"results/Simple2R/step/oms_result.mat"` |
| 6 | `artifacts` | array of string (relative paths) | yes | List of log/config output paths | `["results/Simple2R/step/oms/oms.log"]` |
| 7 | `status` | string | yes | Enum: `"completed"`, `"failed"`, `"skipped"` | `"completed"` |
| 8 | `runtime_s` | float or null | no | Wall-clock runtime in seconds | `1.23` or `null` |
| 9 | `error` | string or null | no | Error message if failed | `"Simulation diverged"` or `null` |

**Schema size:** 9 fields (2 optional, 7 required)  
**Nesting:** `request` groups four fields that describe the simulation request. No other nested objects.

### Observations

- All required fields have a producer in `SimulationRun` during construction or post-simulation metadata capture.
- `runtime_s` and `error` are correctly optional — they may not be populated until simulation completes or may be `None`.
- `artifacts` is always present (possibly empty) which matches its role as a container rather than an optional property.
- No redundant fields.

---

## 3. Cross-Schema Review

| Aspect | Finding |
|--------|---------|
| Field name consistency | Consistent snake_case throughout both schemas. |
| Required field coverage | Every field that the comparison pipeline uses (`model`, `case`, `backend`, `result`, `status`) is present and required. |
| Optional field coverage | `description`, `runtime_s`, `error` are legitimately optional. No optional field hides a required value. |
| Redundant fields | None found. No field duplicates information available in another field. |
| Missing fields | None found. All pipeline-consumed values appear in the schemas. |
| Type consistency | Types match their producers: strings for identifiers and paths, floats for numeric simulation parameters, arrays for lists. |
| Path conventions | All paths are relative, consistent with the pipeline's working-directory-relative convention. |

---

## 4. Recommendation

**The schemas are clean. No changes needed.**

Both `setup.json` and `simulation.json` have minimal, self-consistent field sets. Every field is consumed by at least one downstream consumer (comparison, registry indexing, or run metadata). No redundant, deprecated, or missing fields were found.

The recommended action is to **keep the current schema as-is** and treat this review as a documented baseline for future changes.