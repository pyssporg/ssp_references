package SimpleChain {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def RealSignal {
    attribute value : Real;
  }

  attribute def SimpleChainDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Sine :> FmuModel {
    attribute fmu_meta : SineFmu;
    out port y : RealSignal;
  }

  part def Gain :> FmuModel {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def SimpleChain :> SspModel {
    attribute defaults : SimpleChainDefaultExperiment;
    part sine : Sine;
    part gain : Gain;
    connect sine.y to gain.u;
  }
}
