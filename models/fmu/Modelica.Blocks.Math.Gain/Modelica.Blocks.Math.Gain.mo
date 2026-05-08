within Modelica.Blocks.Math;

block Gain "Output the product of a gain value with the input signal"
  parameter Real k(start=1) "Gain value multiplied with input signal";
  extends Modelica.Blocks.Interfaces.SISO;
equation
  y = k*u;
end Gain;
