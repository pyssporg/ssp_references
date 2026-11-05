# GainOffset — FMU architecture and source

## Provenance

This directory holds only the authored FMU *architecture* and *source* for
`GainOffset`. `architecture/GainOffset.sysml` declares the FMI 2.0
CoSimulation interface and the `Fmu` composition root; `src/GainOffset.c`
implements it. The system that embeds the FMU, its `baseline` analysis, and the
end-to-end provenance live in `models/ssp/GainOffset/FIXTURE.md`.

- `architecture/GainOffset.sysml` is the canonical FMU architecture. It
  declares only the FMU — ports, `FmuMetadata`, `Generator`, and the one-part
  `Fmu` root — and links nothing. The system fixture links this file as
  `models/ssp/GainOffset/architecture/GainOffset.sysml`.
- `Fmu` is a one-part root because `pyfmi_sysml2` exports components below a
  composition root; it holds the FMU's single component.
- `src/GainOffset.c` implements the generated FMI 2.0 CoSimulation interface;
  its `MODEL_NAME` is `"Fmu.Generator"`.
- The build exports with `composition="Fmu"`. Generated C interface headers and
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
   `generate_model_description` (both `composition="Fmu"`) write the C
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
uuid5 derived from `Fmu.Generator`; `modelName` is `"Fmu.Generator"`. Two
consecutive rebuilds produce an identical definition set (headers and
`modelDescription.xml`, `sha256sum` per file) and a byte-identical archive on
the same toolchain.

Recorded hashes with `gcc (Ubuntu 13.4.0-6ubuntu1~22~ppa2) 13.4.0`:

- `Generator.fmu`: `3167ed08f91fef3b45a4fa036f58bef63b0a2c66428dff003640c33c3ccfd97b`
- `Generator.so`: `c6ba67695ab0273643a911c5d8e6b7a3c0b58ec912019307f93c4fb37cbd54ac`
- `modelDescription.xml`: `f4af3faacad6aac591e3d1fa5d68bd22c9c313b59536ae06c7de9ac4bf242245`
