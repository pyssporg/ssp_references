within Modelica.Blocks.Sources;

block Step "Generate step signal of type Real"
  parameter Real height=1 "Height of step";
  extends Modelica.Blocks.Interfaces.SignalSource;
equation
  y = offset + (if time < startTime then 0 else height);
end Step;
