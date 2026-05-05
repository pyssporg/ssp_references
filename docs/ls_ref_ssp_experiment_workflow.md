# LS-REF SSP Experiment Workflow

LS-REF experiment files define the runnable contract for SSP fixtures:

- what SSP/SSD to run
- which parameter, stimuli, and reference resources to package
- how file signals map to SSP connectors
- which outputs to compare

The current repository convention is intentionally small: keep `experiments.xml`
at the SSP root and put all referenced artifacts in `resources/`.

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


The build materializes one runner-ready SSP directory per experiment, place all references and resources in the same directory:

```text
build/models/<fixture>/
  <experiment1>/
    SystemStructure.ssd
    experiments.xml
    resources/
      parameters_baseline.ssv
      parameter_mapping.ssm
      reference_baseline.csv
      reference_mapping.ssm
  <experiment1>/

```

Each generated `experiments.xml` contains exactly one `<Experiment>` and must
point at the paths packaged in that SSP. If build code renames files while
copying them into `resources/`, it must rewrite the experiment paths.

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

For each fixture `build.py`:

1. Validate the authored `experiments.xml`.
2. For each `<Experiment>`, build a normal SSP from the model fixture.
3. If references are csv, create csv fmus and create connections .
4. Copy referenced parameter, mapping, stimuli, and reference files into
   `resources/`.
5. Add experiment parameters as the active SSD parameter binding. Experiment
   parameters override packaged defaults.
6. Write a root-level, single-experiment `experiments.xml`.
7. Unpack or publish the materialized SSP under
   `build/models/<fixture>/<experiment>/`.

The build should fail if `target`, `source`, or `mapping` paths cannot be
resolved.

## Runner Workflow

For engine comparison, run materialized experiment SSPs:

```text
(engine, experiment_ssp) -> simulation result -> LS-REF comparison
```

A runner should:

1. Read root-level `experiments.xml`.
2. Resolve `target`, defaulting to `SystemStructure.ssd`.
3. Configure `startTime`, `stopTime`, and `stepSize`.
4. Run the SSP with the selected engine.
5. Load references, apply signal selection and mapping, then compare with the
   experiment `tolerance`.
6. create a simulation entry, containing the key values that can be used to compare simulation engines.

Missing selected reference signals or missing mapped SSP outputs should fail the
experiment.

## Current Gaps

- There is no shared helper yet for materializing per-experiment SSPs.
- There is no generic LS-REF-aware SSP runner yet.
- Existing CSV comparison does not consume LS-REF mappings or `<Signal>`
  selections.
- Solver, master algorithm, and interpolation settings are not described by the
  fields currently used here.
