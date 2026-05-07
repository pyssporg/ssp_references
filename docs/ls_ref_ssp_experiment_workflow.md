# LS-REF SSP Experiment Workflow

This workflow covers the first part of the broader comparison goal in this
repository:

1. Build stand-alone SSP artifacts that contain everything needed to run a
   system.
2. Execute those SSPs with different engines and simulation settings.
3. Compare the results across engines.

LS-REF is the contract used for step 1. In the current direction it is used to
assemble the correct runnable SSP variant and preserve related metadata, not to
drive execution settings. Each `experiments.xml` defines:

- what SSP/SSD to run
- which parameter, stimuli, and reference resources to package
- how file signals map to SSP connectors
- which outputs or related artifacts belong to that variant

The current repository convention is: every fixture has an `experiments.xml`;
the build materializes one SSP layout per experiment; and referenced artifacts
are packaged into the generated SSP. Runtime simulations and comparisons are
separate and write their outputs under `artifacts/simulation/` and
`artifacts/comparisons/`.

## Supported Fields

- `target`: SSD path inside the SSP. Use `SystemStructure.ssd` unless the
  fixture has more than one SSD.
- `<Parameters source="..." mapping="...">`: SSV parameters plus optional SSM
  mapping.
- `<Stimuli source="..." matchBy="systemConnectorName" mapping="...">`: input
  data plus optional SSM mapping.
- `<References source="..." matchBy="systemConnectorName" mapping="...">`:
  reference data plus optional SSM mapping.
- `<Signal name="...">`: optional reference signal selection. If omitted, compare
  all reference signals after mapping.

## Fixture Layout

The build materializes one runner-ready SSP directory per experiment:

```text
artifacts/models/<fixture>/
  baseline/
    SystemStructure.ssd
    extra/org.fmi-standard.fmi-ls-ref/
      experiments.xml
    resources/
      ...
```

Each generated `experiments.xml` contains exactly one `<Experiment>` and must
point at archive-root-relative paths packaged in that SSP. It may live in
`extra/org.fmi-standard.fmi-ls-ref/`; do not rewrite paths just because the XML
is stored under `extra/`.

`artifacts/simulation_registry.json` maps each model to one or more case
definitions, and each case lists its explicit backend set. That is the runtime
selection layer used by `scripts/run_simulations.py`. The generated
`setup.json` files repeat that explicit backend list so later stages do not
need hidden defaults. `scripts/run_comparisons.py` reads that list and
compares every unique backend combination by default.

## Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Experiments name="signal_step_gain experiments">
  <Experiment
      name="baseline"
      target="SystemStructure.ssd"
      startTime="0.0"
      stopTime="1.0"
      stepSize="0.001"
      tolerance="1e-9">
    <Parameters
        source="resources/parameters.ssv"
        mapping="resources/parameter_mapping.ssm"/>
    <References
        source="resources/reference.csv"
        matchBy="systemConnectorName"
        mapping="resources/reference_mapping.ssm">
      <Signal name="step_y"/>
      <Signal name="gain_y"/>
    </References>
  </Experiment>
</Experiments>
```

Use `matchBy="systemConnectorName"` when file columns already match SSP system
connectors. Use `mapping` when file names differ from SSP names.

## Build Workflow

Use `models/ssp/VanDerPol/build.py` as the pattern for every fixture:

1. Validate the authored `experiments.xml`.
2. For each `<Experiment>`, build a normal SSP from the model fixture.
3. Add experiment `<Parameters>` as active SSD parameter bindings. Experiment
   parameters override packaged defaults.
4. Copy referenced stimuli/reference artifacts and mappings into `resources/`.
5. Add the single experiment with `ssp.ls_ref_experiments()`.
6. Unpack or publish the materialized SSP under
   `artifacts/models/<fixture>/<experiment>/`.

`build.py` stops here. It is only responsible for SSP assembly and does not
simulate or compare.

Simulation and comparison entry points keep their files out of the SSP tree and
write under:

- `artifacts/simulation/<fixture>/<experiment>/`
- `artifacts/comparisons/<fixture>/<experiment>/`

If the authored LS-REF XML still names `references/...` resources, the runtime
adapters mirror the packaged `resources/*.csv` and `resources/*.ssm` files into
a temporary `references/` tree before invoking the engines.

Keep `main()` close to VanDerPol:

```python
model = ModelMetaData(MODEL_DIR)
model.reset_build_dir()
LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

with tempfile.TemporaryDirectory(prefix="<fixture>_") as temp_dir:
    with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
        for exp in experiments.xml.experiments:
            create_ssp(model, Path(temp_dir), exp)
```

It is fine for a fixture to start with one `baseline` experiment. Add more
experiments by extending `experiments.xml`; avoid changing `main()` for each new
case. The build should fail if `target`, `source`, or `mapping` paths cannot be
resolved.

Simulation and comparison are separate entry points that consume the built SSP
root and the registry-selected case list. Keep those runners out of `build.py`
so the SSP assembly step stays easy to review and extend.

## Execution And Comparison

Once the per-experiment SSPs exist, later tooling should treat them as the
execution input:

```text
(engine, experiment_ssp) -> simulation result -> LS-REF comparison
```

Execution should:

1. Select the materialized SSP variant to run.
2. Configure engine, interval, step size, algorithm, and other execution
   settings from the execution matrix, not from `experiments.xml`.
3. Run the SSP with the selected engine.
4. Record result files and status/configuration data for comparison.

Comparison should:

1. Compare engine outputs against each other for the same SSP variant and
   execution case.
2. Apply any needed signal mapping or alignment rules.
3. Report mapping differences, phase shifts, numerical errors, execution time,
   and other relevant attributes.
4. Treat missing mapped outputs or incompatible result sets as failures.

## Current Gaps

- The shared workflow layer exists for setup, simulation, and comparison, and
  the first comparison combination is `ssp4sim` versus `OMSimulator`.
- Additional backends can be added behind the same manifest contract and the
  same registry file.
- Solver, master algorithm, and interpolation settings are still backend
  configuration, not LS-REF fields, and that is intentional for now.
