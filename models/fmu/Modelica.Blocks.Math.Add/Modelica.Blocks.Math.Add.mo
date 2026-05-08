within Modelica.Blocks.Math;

block Add "Output the sum of the two inputs"
  extends Modelica.Blocks.Interfaces.SI2SO;

  parameter Real k1=+1 "Gain of input signal 1";
  parameter Real k2=+1 "Gain of input signal 2";
equation
  y = k1*u1 + k2*u2;
end Add;
