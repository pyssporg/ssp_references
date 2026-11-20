package VariationBodyGain {
  private import PysspCore::*;
  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def ProductFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Product/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Sine :> FmuModel {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port y : RealSignal;
  }

  part def Gain :> FmuModel {
    attribute fmu_meta : GainFmu;
    in port parameters : GainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def Product :> FmuModel {
    attribute fmu_meta : ProductFmu;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }
}
