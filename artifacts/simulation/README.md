# Simulation Artifacts

This directory holds runtime outputs for the registered simulation suite.
The default suite is controlled by `artifacts/simulation_registry.json`.

Some authored fixtures are intentionally omitted from the default sweep
because they do not currently satisfy the registered backend set:

- `scenario`: kept as an authored fixture, but omitted because the current
  setup does not initialize cleanly on `OMSimulator` and has failed during
  scenario parameter binding and initialization.
- `dcmotor`: kept as an authored fixture, but omitted because the nested SSP
  structure is not currently accepted by `ssp4sim` or `OMSimulator`.
- `pyfmu_csv_source_sink`: omitted because it does not run cleanly on both
  supported backends in the current setup. `ssp4sim` hits unsupported value
  references and `OMSimulator` aborts during execution.

These exclusions are deliberate, not accidental. If either fixture is
reintroduced, it should first pass the registered simulation and comparison
flow end to end and then be added back through `artifacts/simulation_registry.json`.
