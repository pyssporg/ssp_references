# Simulation Artifacts

This directory holds runtime outputs for the registered simulation suite.
The default suite is controlled by `artifacts/simulation_registry.json`.

Run the full registered suite with:

```bash
python3 scripts/run_simulations.py
python3 scripts/run_comparisons.py
```

`run_simulations.py` uses every registered case unless you pass `--model`,
`--case`, or `--backend`. `run_comparisons.py` then compares each case across
the backends recorded in that case's `setup.json`. It requires at least two
backends for a case, so single-backend fixtures are simulated but not compared.
Those cases are skipped with a short message and do not stop the remaining
comparisons.

`scripts/generate_comparative_plots.py` uses the same registry and only emits
plots for the case's registered `compare_signals`.

Some authored fixtures are intentionally omitted from the default sweep
because they do not currently satisfy the registered backend set:

- `scenario`: kept as an authored fixture, but limited to `ssp4sim` because
  the other engines do not initialize cleanly for the current parameter setup.
- `pyfmu_csv_source_sink`: kept as an authored fixture, but limited to
  `ssp4sim` because `fmpy` and `OMSimulator` do not initialize cleanly with
  the current CSV-backed source/sink setup.

These exclusions are deliberate, not accidental. If either fixture is
reintroduced, it should first pass the registered simulation and comparison
flow end to end and then be added back through `artifacts/simulation_registry.json`.
