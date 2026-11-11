model InitGuard
  "Guard that fails initialization when its connected input is zero.

  The FMI 2.0 contract lets an FMU reject initialization: if the engine
  calls exitInitializationMode while a connected input still holds its
  default start value instead of a committed upstream output, this model
  reports the violation with a hard assert and the engine must abort.
  "
  input Real u(start = 0.0);
  output Real y;

initial equation
  assert(u > 1e-6,
    "InitGuard: connected input u is zero during initialization; "
    + "the upstream value was not propagated into this component "
    + "before exitInitializationMode.");

equation
  y = u;
end InitGuard;
