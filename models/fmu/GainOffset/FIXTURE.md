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
  `pyfmi_sysml2.fmi2_headers()`.
- There is no binary and no definition text here, so this directory is not
  loadable as an FMU on its own. The committed
  `artifacts/build/GainOffset/Generator.fmu` archive is the definition copy
  consumers read.

## Rebuild

`./venv/bin/python scripts/build_models.py run GainOffset`

`models/fmu/GainOffset/build.py` builds the FMU:

1. `pyfmi_sysml2.generate_c_headers` and
   `generate_model_description` (both `composition="Generator"`) write the C
   interface headers and
   `modelDescription.xml` to `artifacts/build/GainOffset/`.
2. `gcc -std=c11 -O2 -fPIC -shared` compiles `src/GainOffset.c` into
   `artifacts/build/GainOffset/Generator.so`.
3. `pyfmi_sysml2.package_fmu` writes
   `artifacts/build/GainOffset/Generator.fmu`.

The SSP build then runs `models/ssp/GainOffset/build.py`, which derives the SSP
and the `baseline` analysis from the system architecture (`System`) and embeds
the archive.

## Determinism

`generation_time` is injected as `2026-01-01T00:00:00Z`, and the `guid` is the
uuid5 derived from `pyssp_sysml2/Generator`; `modelName` and `modelIdentifier`
are both `"Generator"`. Two consecutive rebuilds produce an identical
definition set (headers and `modelDescription.xml`, `sha256sum` per file) and a
byte-identical archive on the same toolchain.

Recorded hashes with `gcc (Ubuntu 13.4.0-6ubuntu1~22~ppa2) 13.4.0`:

- `Generator.fmu`: `edd4e104a57c19de2ed65844bf2f8992edae6a5bdfa3a38f77e77aec05be5c7c`
- `Generator.so`: `cbe3e128eb676ba0518904096ec6d6b8c841f075ac1a471e46c7c85f0e416aa8`
- `modelDescription.xml`: `5f43bee0313f465562bed9e8d70fdf407b5be787e5d6351896bb4dfca48a8844`
- `sources/GainOffset_Generator.h`: `c6ad6f147ffd24fe42d4514e543435f923f2f486a266f6c43a56263c2b706e29`
- `sources/GainOffset_InterfaceCommon.h`: `3b5f7f1548352c5eac364fcb8006e52c017360cf179b5e1be8828e973cb67b96`
