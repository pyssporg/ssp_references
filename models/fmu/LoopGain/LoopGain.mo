block LoopGain
  "Loop building block whose connected input and output form one hop of a
  cross-FMU algebraic loop.

  Two instances wired in a cycle (a.y -> b.u, b.y -> a.u) have no
  topological initialization order: the consistent start values are the
  fixed point of the loop, so an engine must iterate during
  initialization (or accept inconsistent defaults) instead of following
  a source-first ordering. With the loop gains below (k = 0.5 per hop)
  the fixed point is unique and the iteration contracts by 0.25 per
  turn, so the required initialization iteration converges quickly.
  "
  parameter Real k = 0.5 "Loop gain";
  parameter Real c = 0.0 "Loop excitation offset";
  input Real u(start = 0.0);
  output Real y;

equation
  y = k * u + c;
end LoopGain;
