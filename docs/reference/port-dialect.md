# Port Dialect Notes

SysML-authored fixtures shape ports around FMU variable names, which use
characters a SysML identifier cannot (dots and array brackets).

- A fluid port carries both directions in one usage through member-level
  `in`/`out`: `FluidState` marks `p`, `h`, and `X` as outputs and `m` and `hn`
  as inputs.
- The mirrored side types the same port with an authored conjugate definition,
  `FluidStateConjugate`, which declares `p`, `h`, and `X` as inputs and `m` and
  `hn` as outputs. Write the reversal out: `sysmlpy` records `~FluidState`
  literally and never registers the conjugated symbol.
- Each collapsed port keeps one `connect`; the SSD expands every member with
  its own direction.
- A fixed attribute array (`attribute X : Real[3];`) is expanded to
  `X[1]`–`X[3]` at export.
- A `RealSignal` port has one member named `value`, so it is a scalar port:
  the exporter names its connector for the port itself and no flat export
  option is needed.
