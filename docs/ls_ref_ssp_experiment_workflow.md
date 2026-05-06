# LS-REF SSP Experiment Workflow

LS-REF experiment files define the runnable contract for SSP fixtures:

- what SSP/SSD to run
- which parameter, stimuli, and reference resources to package
- how file signals map to SSP connectors
- which outputs to compare

The current repository convention is intentionally small: every fixture has an
`experiments.xml`; the build materializes one SSP layout per experiment; and
referenced artifacts are packaged under `resources/`.

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
build/models/<fixture>/
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
   `build/models/<fixture>/<experiment>/`.

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

## Runner Workflow

For engine comparison, run materialized experiment SSPs:

```text
(engine, experiment_ssp) -> simulation result -> LS-REF comparison
```

A runner should:

1. Read the single-experiment LS-REF document from the SSP.
2. Resolve `target`, defaulting to `SystemStructure.ssd`.
3. Configure `startTime`, `stopTime`, and `stepSize`.
4. Run the SSP with the selected engine.
5. Load references, apply signal selection and mapping, then compare with the
   experiment `tolerance`.
6. Create a simulation entry containing the key values used to compare
   simulation engines.

Missing selected reference signals or missing mapped SSP outputs should fail the
experiment.

## Current Gaps

- There is no shared helper yet for materializing per-experiment SSPs.
- There is no generic LS-REF-aware SSP runner yet.
- Existing CSV comparison does not consume LS-REF mappings or `<Signal>`
  selections.
- Solver, master algorithm, and interpolation settings are not described by the
  fields currently used here.
