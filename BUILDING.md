# Building And Maintenance

This document covers repository maintenance tasks that are not needed for normal model consumption.

## Imported repositories

Imported upstream repositories live under [`3rd_party`](/home/eriro/pwa/2_work/ssp_references/3rd_party):

- [`3rd_party/reference_fmus`](/home/eriro/pwa/2_work/ssp_references/3rd_party/reference_fmus)
- [`3rd_party/OMSimulator`](/home/eriro/pwa/2_work/ssp_references/3rd_party/OMSimulator)

Fetch them with:

```bash
git submodule update --init --recursive
```

`OMSimulator` is configured with sparse checkout so its `testsuite/` is the relevant working content.

## Python environment

The helper scripts use the repository virtual environment and depend on `pyssp_standard`.

Typical setup:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Build reference FMUs and SSPs

Run:

```bash
./3rd_party/build_fmi2_fmus.sh
```

This builds from [`3rd_party/reference_fmus`](/home/eriro/pwa/2_work/ssp_references/3rd_party/reference_fmus), places temporary build output in [`build/reference_fmus/fmi2-export`](/home/eriro/pwa/2_work/ssp_references/build/reference_fmus/fmi2-export), and writes consumable model artifacts under [`models`](/home/eriro/pwa/2_work/ssp_references/models).

## Helper scripts

Available helper scripts:

- [`3rd_party/build_fmi2_fmus.sh`](/home/eriro/pwa/2_work/ssp_references/3rd_party/build_fmi2_fmus.sh)
- [`scripts/package_fmu_as_ssp.sh`](/home/eriro/pwa/2_work/ssp_references/scripts/package_fmu_as_ssp.sh)
- [`scripts/unpack_model_archive.sh`](/home/eriro/pwa/2_work/ssp_references/scripts/unpack_model_archive.sh)

Examples:

```bash
./scripts/package_fmu_as_ssp.sh models/BouncingBall/fmus/BouncingBall.fmu
./scripts/unpack_model_archive.sh models/BouncingBall/BouncingBall.ssp
```
