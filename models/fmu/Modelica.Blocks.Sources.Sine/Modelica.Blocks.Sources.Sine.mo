within Modelica.Blocks.Sources;

block Sine "Generate sine signal"
  import Modelica.Constants.pi;

  parameter Real amplitude=1 "Amplitude of sine wave";
  parameter Modelica.Units.SI.Frequency f(start=1) "Frequency of sine wave";
  parameter Modelica.Units.SI.Angle phase=0 "Phase of sine wave";
  parameter Boolean continuous=false
    "Make output continuous by starting at offset + amplitude*sin(phase)"
    annotation(Evaluate=true);
  extends Modelica.Blocks.Interfaces.SignalSource;
equation
  if continuous then
    y = offset + amplitude*smooth(0, if time < startTime then Modelica.Math.sin(phase) else Modelica.Math.sin(2*pi*f*(time - startTime) + phase));
  else
    y = offset + (if time < startTime then 0 else amplitude*Modelica.Math.sin(2*pi*f*(time - startTime) + phase));
  end if;
end Sine;
