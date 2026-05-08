within Modelica.Blocks.Math;

block Product "Output product of the two inputs"
  extends Modelica.Blocks.Interfaces.SI2SO;
equation
  y = u1*u2;
end Product;
