# `ssp_references`

Reference SSP and FMU artifacts for evaluating co-simulation engines.

## Available models

The repository currently provides OMSimulator-derived model directories under [`models`](/home/eriro/pwa/2_work/ssp_references/models).


## Model layout

Each model has its own folder:

```text
models/<model_name>/
├── workflow.py
├── <model_name>.ssp
├── fmus/                    # for models that explicitly build FMUs
└── ssp/
TODO: add metadata, reference results, simulation results
```


What each part is for:

- `workflow.py`: the readable source of truth for the model's `acquire -> build -> package -> unpack` chain.
- `<model_name>.ssp`: the packaged SSP for the model.
- `fmus/`: intermediate FMUs for workflows that explicitly build them.
- `ssp/`: an unpacked view of the SSP, useful for inspection, debugging, and tool integration tests.
- references/ : stored resulting behavior that is considered correct
- simulation_results/<engine>_<version>/resulting files





## Build and Maintenance

Most users do not need to rebuild the artifacts or manage the imported repositories.

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

python3 scripts/run_model_workflows.py run-all
```