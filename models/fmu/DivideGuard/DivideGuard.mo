block DivideGuard
  "Loop block that divides a constant by its connected input, and refuses
  initialization while that input is zero.

  A zero connected input during initialization is doubly wrong: the loop's
  consistent start values are its fixed point (never zero with a nonzero
  dividend), and evaluating c/u with u = 0 would divide by zero. The FMI
  2.0 contract lets the FMU reject initialization: if the engine calls
  exitInitializationMode while this block's input still holds its default
  start value instead of an iterated loop solution, this model reports
  the violation with a hard assert and the engine must abort.
  "
  parameter Real c = 100.0 "Dividend";
  input Real u(start = 0.0);
  output Real y;

initial equation
  assert(u > 1e-6,
    "DivideGuard: connected input u is zero during initialization; "
    + "evaluating c/u would divide by zero. The loop value was not "
    + "iterated to the fixed point before exitInitializationMode.");

equation
  y = c / u;
end DivideGuard;
