# GainOffset

## Origin

Authored in this repository on 2026-11-05; no upstream fixture was imported.
The SysML interface, the C implementation, and the analytic baseline all live
here or in the FMU source directory. It was added with the
`pycps_sysml2` / `pyssp_sysml2` / `pyfmi_sysml2` split to prove that a
SysML-authored FMU can be generated, compiled, packaged, simulated, and
compared through the shared entry points.

The fixture is split by role:

- `models/fmu/GainOffset/` owns only the authored FMU definitions and source:
  `architecture/GainOffset.sysml` (ports, metadata, `GeneratorParameters`, and
  `Generator :> FmuModel`) and `src/GainOffset.c`, plus its `build.py` and
  provenance.
- `models/ssp/GainOffset/` (this directory) is the system:
  `architecture/System.sysml` (`SspModel`, `Analysis`), `build.py`, references,
  and end-to-end provenance. The FMU architecture enters as an include root,
  not as a copied file or symlink.
- `artifacts/build/GainOffset/` holds every generated file: the C interface
  headers, `modelDescription.xml`, the compiled `Generator.so`, and the
  packaged `Generator.fmu`. The committed archive is the definition copy
  consumers read. The public FMI 2.0 headers come from
  `pyfmi_sysml2.fmi2_headers()`.

## Overview

`GainOffset` is the minimal end-to-end SysML → FMI → SSP fixture. A SysML
architecture declares one component whose FMI 2.0 CoSimulation interface
(three parameters and one output) is emitted as C headers and as
`modelDescription.xml`; a fixture-local C file implements that interface and is
compiled into `Generator.so`; the packaged FMU is then wrapped in an SSP by the
normal build path. The physics is a closed-form signal source, so any
trajectory difference is a pipeline defect, not a numerical one.

## Architecture Source

- `architecture/System.sysml` declares the system: `System :> SspModel`,
  `baseline :> Analysis`, and their experiments.
- The FMU definitions (`GeneratorParameters`, `Generator :> FmuModel`) come
  from `models/fmu/GainOffset/architecture/`, which `build.py` passes to
  `build_fixture` as an include root. There is no local copy and no symlink.
- Exportable composition: `System :> SspModel`. FMU definition: `Generator`,
  marked `:> FmuModel` so `pyfmi_sysml2` exports it directly.
- Analysis composition: `baseline :> Analysis`.
- Parameter interface `GeneratorParameters` exposes `gain = 2.0`,
  `offset = 0.5`, `frequency = 1.0`; the analysis applies no scenario.
- FMU reference: `FmuMetadata.source = "artifacts/build/GainOffset/Generator.fmu"`,
  `implementation = "CoSimulation"`. The reference is a file, resolved from the
  repository root and copied verbatim into the SSP's
  `resources/Generator.fmu`.
- Generated FMU definition: `modelName="Generator"`,
  `modelIdentifier="Generator"`, `guid="{eca0627b-dad2-5d71-90b2-e450ef615122}"`
  (uuid5 of `pyssp_sysml2/Generator`).
- No legacy SSD, SSV, or SSM is checked in.

## Analyses

- `baseline :> Analysis`
- Scenario set: none; the build packages no scenario, so the authored defaults
  apply.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Artifacts: `artifacts/analyses/GainOffset/baseline/`
- Analyses are never exported as SSPs.

## Structure

- Single component `generator : Generator` with parameter input
  `parameters : GeneratorParameters` and output `y : RealSignal`.
- No connectors: the component is a source driven by its own parameters.

## Strategy Role

- Pipeline fixture: proves the generated headers, `modelDescription.xml`,
  binary, and archive agree on one variable set.
- Regression anchor for FMI emission, FMU packaging, and definition/artifact
  separation.
- Reproduction check: the definition tree and the archive must be byte-stable
  across reruns.

## Intent

- Prove the split works from this repository's side: `pycps_sysml2` parses the
  dialect, `pyfmi_sysml2` emits FMI artifacts, and `pyssp_sysml2` emits the
  SSP; no library is asked to do another's job.
- Keep authored sources in `models/` and every generated, compiled, or
  packaged file in `artifacts/`, so a checkout without a toolchain is still
  readable and the build products have one home.
- Keep the physics trivial: `y(t) = offset + gain * sin(2 * pi * frequency * t)`.

## Expected Behavior

- `y(0) = 0.5`, `y(0.25) = 2.5`, `y(0.5) = 0.5`, `y(0.75) = -1.5`,
  `y(1.0) = 0.5`.
- Reference trajectory: `references/GainOffset-cs.csv`, column
  `generator.y.value`, generated from the closed form on the simulation time
  grid.
- Measured against OMSimulator 3.0.0.post116: `max_abs_error = 4.96e-12` over
  1001 time points (double rounding of the printed reference).

## Main Failures This Catches

- Header VR set drifting from `modelDescription.xml` (stale generated headers).
- `modelIdentifier` not matching the compiled binary name.
- A missing binary or archive under `artifacts/build/GainOffset/`.
- An archive whose `modelDescription.xml` no longer matches the generated
  definition, or that drops `sources/`.
- FMU packaging that reorders archive entries.
- A `pyssp_sysml2`/`pyfmi_sysml2` boundary regression: an SSP that embeds the
  wrong FMU, or FMI files generated by the SSP library.

## Simulation Notes

- CoSimulation only; there is no Model Exchange binary (see ADR-017).
- `canGetAndSetState` is not implemented, so OMSimulator logs that it uses an
  explicit master algorithm. This is expected.
- Registered with backend `omsimulator` only; `ssp4sim` is not exercised by this
  fixture.

## Packaging Notes

- Build: `./venv/bin/python scripts/build_models.py run GainOffset`
  (also part of `run-all`; the FMU build must run first).
- `models/fmu/GainOffset/build.py` runs the FMU steps with
  `composition="Generator"`:
  1. `pyfmi_sysml2.generate_c_headers` writes the C interface headers to
     `artifacts/build/GainOffset/sources/`;
     `pyfmi_sysml2.generate_model_description` writes
     `artifacts/build/GainOffset/modelDescription.xml` (relocated from the
     generator's per-component directory to the build root).
  2. `gcc -std=c11 -O2 -fPIC -shared` compiles `src/GainOffset.c` into
     `artifacts/build/GainOffset/Generator.so`, using the generated headers and
     the `pyfmi_sysml2` FMI headers as include paths.
  3. `pyfmi_sysml2.package_fmu` writes
     `artifacts/build/GainOffset/Generator.fmu` with the model description, the
     generated headers, the `pyfmi_sysml2.fmi2_headers()`, and the binary at
     `binaries/linux64/Generator.so`.
- `models/ssp/GainOffset/build.py` then runs the SSP steps from `System`,
  passing `models/fmu/GainOffset/architecture` as an include root:
  4. `pyssp_workflow.authoring.build_fixture` loads `System.sysml` with that
     include, exports the SSP and the `baseline` analysis, embedding the
     archive as `resources/Generator.fmu`; it fails with a clear message when
     the archive is missing.
  5. `report_builds` records the baseline artifact paths.
- `generation_time` is injected as `2026-01-01T00:00:00Z`, so
  `generationDateAndTime` never moves.
- `guid` is the deterministic uuid5 derived from `pyssp_sysml2/Generator`
  (`{eca0627b-dad2-5d71-90b2-e450ef615122}`), not a random identifier; the
  generated definition carries `modelName="Generator"` and
  `modelIdentifier="Generator"`.
- FMI 2.0 standard headers come from `pyfmi_sysml2.fmi2_headers()`; the package
  bundles the three headers that `pyssp_standard` vendors under
  `3rdParty/FMI2/headers/`.
- Generated C interface headers: `artifacts/build/GainOffset/sources/GainOffset_Generator.h`
  (VR enumerators, `GainOffset_Generator_VrCount`, VR map) and
  `GainOffset_InterfaceCommon.h` (data types).
- The packaged archive is committed because the SSP build consumes it: a fresh
  clone must be able to run `build.py` without a compiler.

## Reproducibility

- Build contract: rebuild with the repository venv and the toolchain named
  below; `models/fmu/GainOffset/build.py` writes the FMU outputs and
  `models/ssp/GainOffset/build.py` writes the SSP and analysis, in that order.
  No generated file is hand-edited.
- Toolchain used: `gcc (Ubuntu 13.4.0-6ubuntu1~22~ppa2) 13.4.0`.
- Two consecutive `run GainOffset` invocations must produce an identical
  definition set under `artifacts/build/GainOffset/`
  (`modelDescription.xml` and headers, `sha256sum` per file) and a
  byte-identical `artifacts/build/GainOffset/Generator.fmu`.
- Recorded hashes: `Generator.fmu` `edd4e104a57c19de2ed65844bf2f8992edae6a5bdfa3a38f77e77aec05be5c7c`,
  `Generator.so` `cbe3e128eb676ba0518904096ec6d6b8c841f075ac1a471e46c7c85f0e416aa8`,
  `modelDescription.xml` `5f43bee0313f465562bed9e8d70fdf407b5be787e5d6351896bb4dfca48a8844`
  — the pins in `models/fmu/GainOffset/FIXTURE.md` are canonical.
- Volatile if the toolchain changes: the ELF bytes of
  `artifacts/build/GainOffset/Generator.so` (gcc version, `--build-id`, section
  ordering). `modelDescription.xml`, the headers, the archive entry list, and
  the reference CSV are byte-stable regardless of the compiler. A different
  gcc therefore changes the committed `.so` and the archive hash only; the VR
  set and the trajectory must not change.
- Volatile across a `gcc`/`binutils` upgrade but not across reruns: `readelf
  -n` build-id.

## Typical Use

- `python3 scripts/run_simulations.py --model GainOffset`, then
  `python3 scripts/run_comparisons.py --model GainOffset`.
- Gate: the comparison against `references/GainOffset-cs.csv` must stay within
  tolerance; a larger delta means the emitted interface, the compiled binary,
  or the packaged archive changed.
