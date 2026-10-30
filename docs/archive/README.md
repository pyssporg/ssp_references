<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->

# Decision Stream

Flat, dated history of every committed design choice. Current state lives
in the layer leaves named by each record's `state:` field.

Records live in the cold-storage archive; extract one with `pb archive read <ID>`.

## By Layer

### Product

- **PD-001** — Comparison Methodology — Engine-to-Engine Only · accepted · 2026-10-22 · `PD-001`
  Comparison is pairwise engine-to-engine; no engine is the golden reference.
- **PD-002** — Simulation Registry Is the Single Source of Truth · accepted · 2026-10-22 · `PD-002`
  `artifacts/simulation_registry.json` is the sole source of active model, study, and backend combinations.
- **PD-003** — Supported Simulation Backends · accepted · 2026-10-22 · `PD-003`
  The repository commits to ssp4sim, OMSimulator, and FMPy as the supported backend set.
- **PD-004** — SysML `SspModel` Definitions and Parameter Sets Are the Authoring Source · accepted · 2026-10-22 · `PD-004`
  SysML `SspModel` definitions are the authored source; exported SSPs are build artifacts.
- **PD-005** — The Reference Repository Owns Fixtures and Policy Data, Not Pipeline Implementations · accepted · 2026-10-22 · `PD-005`
  Generic build, run, compare, and verify behavior belongs to `pyssp_workflow` and capability repos.
- **PD-006** — Studies Consume Exported SSPs and Are Never Exported · accepted · 2026-10-22 · `PD-006`
  Studies consume exported SSPs with scenario and experiment data and are never exported.
- **PD-007** — Fixture Suite Preserves Parameter-Application Forms · accepted · 2026-10-23 · `PD-007`
  Reference fixtures keep the SSP parameter-application forms they exercise; authoring must not flatten them.

### Architecture

- **AD-011** — Adopt the product-breakdown skill state and archive split · accepted · 2026-10-22 · `AD-011`
  Layer leaves hold current state; dated decisions live in the cold archive; registers are generated.
- **AD-012** — Legacy Model Bodies May Carry SysML-Authored Experiments · superseded · 2026-10-23 · `AD-012`
  A legacy SSD may stay the model body while its study and experiment are authored in SysML.
- **AD-013** — SspModel Declares Its Checked-In SSP Source · accepted · 2026-10-23 · `AD-013`
  An SspModel selects a checked-in SSP body with ssp_meta.source; the study records it as model_source.
- **AD-014** — No LS-REF Artifacts or Parsing · accepted · 2026-10-23 · `AD-014`
  The study descriptor is the experiment contract; the build writes no experiments.xml and no stage parses LS-REF.
- **ADR-001** — Three-Stage Pipeline Architecture · accepted · 2026-10-22 · `ADR-001`
  The pipeline has three file-based stages: Build, Simulate, Compare.
- **ADR-002** — Fixture Hierarchy · accepted · 2026-10-22 · `ADR-002`
  Fixtures are organized in four classes: FMU blocks, simple SSPs, deterministic signal fixtures, and composite SSPs.
- **ADR-003** — Runtime Configuration Belongs to the Simulation Registry · accepted · 2026-10-22 · `ADR-003`
  The registry is the runtime configuration source; `setup.json` freezes the selected window, tolerance, and policy.
- **ADR-004** — Use-Case Coverage Taxonomy as the Primary Coverage Lens · accepted · 2026-10-22 · `ADR-004`
  The use-case taxonomy is the primary coverage lens for the fixture suite.
- **ADR-005** — Adopt the pyssp Ecosystem Behind Existing Stage Boundaries · accepted · 2026-10-22 · `ADR-005`
  The repository adopts the pyssp ecosystem behind existing stage boundaries.
- **ADR-006** — Exchange Standardized Artifacts at Tool Boundaries · accepted · 2026-10-22 · `ADR-006`
  Tool boundaries exchange standardized artifacts, never Python model objects.
- **ADR-007** — Authoring SysML at the Build Boundary · accepted · 2026-10-22 · `ADR-007`
  `pyssp_workflow.authoring` derives SSP artifacts through the `pyssp` CLI at the build boundary.
- **ADR-008** — Workflow Capability Ownership and Node Boundaries · accepted · 2026-10-22 · `ADR-008`
  `pyssp_workflow` owns generic pipeline behavior; `ssp_references` owns fixtures and policy data.
- **ADR-009** — `SspModel` and `Study` Marker Specialization · accepted · 2026-10-22 · `ADR-009`
  `SspModel` definitions are exportable; `Study` definitions supply scenario data and are never exported.
- **ADR-010** — Runtime Scenario and Experiment Application to Exported SSPs · superseded · 2026-10-22 · `ADR-010`
  Studies apply SSV, SSM, and experiment data to a runtime copy of an exported SSP.
- **ADR-011** — Library Boundaries Use Standard Artifacts or Public API · accepted · 2026-10-22 · `ADR-011`
  Library borders prefer standard artifacts; non-standard crossings use only documented public API types.
- **ADR-012** — pyssp_standard Comes From the Organization Experimental Fork · accepted · 2026-10-22 · `ADR-012`
  The pinned `pyssp_standard` checkout is the organization's experimental fork, not the release line.
- **ADR-013** — SysML Authors Structure and Experiment; pyssp_standard Applies Parameter Form · accepted · 2026-10-23 · `ADR-013`
  SysML defines wiring and the experiment; the fixture build applies the parameter form with pyssp_standard, including nested boundary wiring.

### Implementation

- **AD-015** — Per-Fixture Build Scripts Are Thin Runners · accepted · 2026-10-23 · `AD-015`
  build.py declares one fixture's inputs; shared authoring helpers own the build steps.
- **DD-001** — Simulation Settings Belong to the Runtime Layer · accepted · 2026-10-22 · `DD-001`
  The simulation window and tolerance are frozen into `setup.json`; runtime reads `setup.json`, not `experiments.xml`.
- **DD-002** — Runtime Artifacts Stay Under `artifacts/` · accepted · 2026-10-22 · `DD-002`
  Runtime artifacts live under `artifacts/simulation/` and `artifacts/comparisons/`, separate from build outputs.
- **DD-003** — `build.py` Remains Build-Only · accepted · 2026-10-22 · `DD-003`
  `build.py` builds SSPs and never runs simulations.
- **DD-004** — Signal-Propagation Fixtures Use Deterministic Algebraic FMU Blocks · accepted · 2026-10-22 · `DD-004`
  Signal-propagation fixtures use deterministic algebraic FMU blocks.
- **DD-005** — Simulation Registry Technical Mechanism · accepted · 2026-10-22 · `DD-005`
  `artifacts/simulation_registry.json` is a hand-maintained JSON schema with model, study, backend, and signal fields.
- **DD-006** — Time-Shift-Tolerant VV Metrics · accepted · 2026-10-22 · `DD-006`
  VV metrics keep pointwise error and time-shift-tolerant error per signal.
- **DD-007** — `signal_step_gain` Model Export · accepted · 2026-10-22 · `DD-007`
  `signal_step_gain` exports a `System :> SspModel` SSP with parameter interfaces and no study bindings.
- **DD-008** — Study Scenario Generation and SSM Prefix Stripping · accepted · 2026-10-22 · `DD-008`
  A study generates SSV, SSM, and an experiment descriptor; SSM targets strip the `sut.` prefix.
- **DD-009** — Runtime Scenario Injection and Registry Build/Case Split · superseded · 2026-10-22 · `DD-009`
  Runtime scenario injection copies the exported SSP, adds a root `ParameterBinding`, and never mutates the build artifact.
- **DD-010** — `pyssp_vv` Owns Comparison Measurement and Judgment · accepted · 2026-10-22 · `DD-010`
  Comparison metrics and verdicts come from pyssp_vv; this repo keeps registry and model policy.
- **DD-011** — Build Packages the Study Scenario into the SSP · accepted · 2026-10-23 · `DD-011`
  The build emits a runnable SSP per model/study/build with the scenario applied; simulation runs it as-is.
- **DD-012** — Scenario Fixture Is Fully SysML-Authored With Its Legacy SSV · accepted · 2026-10-23 · `DD-012`
  The scenario model owns the six-member SSV and its live inline mapping; the study is experiment-only.
- **DD-013** — Generic Engine, Build, Comparison, and Figure Code Lives in the pyssp Dependencies · accepted · 2026-10-23 · `DD-013`
  Engine, packaging, comparison, figure, and authoring code lives upstream; this repository keeps layout, registry, gate, and fixtures.
- **DD-014** — Registry Lists Only Backends That Run the Case · accepted · 2026-10-29 · `DD-014`
  A case's backends name the engines that can simulate it; an engine that cannot run the case is not listed.
- **DD-015** — Registry Application — Pass-Through OMSimulator Drop · accepted · 2026-10-29 · `DD-015`
  Per DD-014, an engine that cannot run the case is not listed for the case.
- **DD-016** — Registry Application — Pass-Through OMSimulator Drop · accepted · 2026-10-29 · `DD-016`
  Per DD-014, an engine that cannot run the case is not listed for the case.
