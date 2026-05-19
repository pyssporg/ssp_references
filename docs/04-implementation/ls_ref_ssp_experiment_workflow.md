# LS-REF Packaging Note

LS-REF experiment XML is used here only when a fixture needs a small number of
runnable SSP variants. It is not the main workflow contract for simulation or
comparison.

The runtime flow is driven by:

1. Built SSP artifacts under `artifacts/models/<fixture>/<experiment>/`.
2. Case and backend selection from `artifacts/simulation_registry.json`.
3. Generated `setup.json` files plus the shared simulation and comparison
   entry points under `scripts/`.

When a fixture does use `experiments.xml`:

- keep the XML focused on packaging the runnable SSP variant
- place it under `extra/org.fmi-standard.fmi-ls-ref/experiments.xml` if that is
  how the builder packages the SSP
- keep execution settings and compare-signal selection out of the XML
- keep `build.py` close to the VanDerPol pattern: validate, build, package,
  stop

Most fixtures in this repository do not rely on LS-REF at runtime. For the
current workflow details, read `README.md` and
`docs/05-verification/co_simulation_test_strategy.md`.
