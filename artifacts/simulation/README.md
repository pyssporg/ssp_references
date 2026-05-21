# Simulation Artifacts

This directory holds runtime outputs for the registered simulation suite.
The default suite is controlled by `artifacts/simulation_registry.json`.

Some authored fixtures are intentionally omitted from the default sweep
because they do not currently satisfy the registered backend set:

- `scenario`: kept as an authored fixture, but limited to `ssp4sim` because
  the other engines do not initialize cleanly for the current parameter setup.
- `dcmotor`: kept as an authored fixture, but omitted because the nested SSP
  structure is not currently accepted by `ssp4sim` or `OMSimulator`.
- `pyfmu_csv_source_sink`: kept as an authored fixture, but limited to
  `ssp4sim` because `fmpy` and `OMSimulator` do not initialize cleanly with
  the current CSV-backed source/sink setup.

These exclusions are deliberate, not accidental. If either fixture is
reintroduced, it should first pass the registered simulation and comparison
flow end to end and then be added back through `artifacts/simulation_registry.json`.
