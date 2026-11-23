# GainOffset — FMU architecture and source

## Provenance

This directory holds only the authored FMU *architecture* and *source* for
`GainOffset`. `architecture/GainOffset.sysml` declares the FMI 2.0
CoSimulation interface and marks the `Generator` definition `:> FmuModel`;
`src/GainOffset.c` implements it. The system that embeds the FMU, its
`baseline` analysis, and the end-to-end provenance live in
`models/ssp/GainOffset/FIXTURE.md`.

- `architecture/GainOffset.sysml` is the canonical FMU architecture. It
  declares only the FMU — ports, `GeneratorParameters`, `FmuMetadata`, and
  `Generator :> FmuModel` — and refers to no embedding system. The system
  fixture consumes this directory as an include root; it holds no copy and no
  symlink.
- `Generator` is the FMU definition. The `FmuModel` marker declares it as the
  export unit, so the generators export this definition directly instead of
  selecting leaf components below a container root.
- `src/GainOffset.c` implements the generated FMI 2.0 CoSimulation interface;
  its `MODEL_NAME` is `"Generator"`.
- The build names the definition with `composition="Generator"` (and
  `component="Generator"`). Generated C interface headers and
  `modelDescription.xml` are build outputs under
  `artifacts/build/GainOffset/`; the FMI 2.0 standard headers come from
  `pyfmi_interfaces.fmi2_headers()`.
- There is no binary and no definition text here, so this directory is not
  loadable as an FMU on its own. The committed
  `artifacts/build/GainOffset/Generator.fmu` archive is the definition copy
  consumers read.

## Rebuild

`./venv/bin/python scripts/build_models.py run GainOffset`

`models/fmu/GainOffset/build.py` builds the FMU:

1. `pyfmi_sysml.generate_c_headers` and
   `generate_model_description` (both `composition="Generator"`) write the C
   interface headers and
   `modelDescription.xml` to `artifacts/build/GainOffset/`.
2. `gcc -std=c11 -O2 -fPIC -shared` compiles `src/GainOffset.c` into
   `artifacts/build/GainOffset/Generator.so`.
3. `pyssp_standard.FMU.package` writes
   `artifacts/build/GainOffset/Generator.fmu`.

The SSP build then runs `models/ssp/GainOffset/build.py`, which derives the SSP
and the `baseline` analysis from the system architecture (`System`) and embeds
the archive.

## Determinism

`generation_time` is injected as `2026-01-01T00:00:00Z`, and the `guid` is the
uuid5 derived from `pyssp_sysml2/Generator`; `modelName` and `modelIdentifier`
are both `"Generator"`. The definition records
`generationTool="pyfmi_interfaces tooling"` and emits real starts in shortest
form (`2`, `1`). Two consecutive rebuilds produce an identical definition set
(headers and `modelDescription.xml`, `sha256sum` per file) and a byte-identical
archive on the same toolchain.

Producing packages: `pyfmi_interfaces 0.5.1`, `pyfmi_sysml 0.2.0`,
`pycps_sysml2 0.3.0`, `pyssp_standard 0.9.4.dev0`.

Recorded hashes with `gcc (Ubuntu 13.4.0-6ubuntu1~22~ppa2) 13.4.0`:

- `Generator.fmu`: `11e8fe209ce62c43ca0eb46f7c0417316d27076ebd4d4b1b01af9351b16b7c65`
- `Generator.so`: `cbe3e128eb676ba0518904096ec6d6b8c841f075ac1a471e46c7c85f0e416aa8`
- `modelDescription.xml`: `19de66f098b3aa3f81c2a431d4037b6befe7418954ea9c75d16528ba65f21c2b`
- `sources/GainOffset_Generator.h`: `6548f130bd5447f28c61692acc0e5d169c9a46d5aad7c23baf65a778ac1abe4b`
- `sources/GainOffset_InterfaceCommon.h`: `3b5f7f1548352c5eac364fcb8006e52c017360cf179b5e1be8828e973cb67b96`
