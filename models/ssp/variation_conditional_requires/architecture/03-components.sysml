package VariationConditionalRequires {
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def StepFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Step/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def SignalSource {
    out port y : RealSignal;
  }

  part def Step :> SignalSource {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port :>> y : RealSignal;
  }

  part def Sine :> SignalSource {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port :>> y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    in port parameters : GainParameters;
    out port y : RealSignal;
  }

  /* Two stages: an internal part tree, not two exposed parameter ports. */
  part def CascadedGain {
    in port u : RealSignal;
    out port y : RealSignal;
    part firstStage : Gain;
    part secondStage : Gain;
    connect u to firstStage.u;
    connect firstStage.y to secondStage.u;
    connect secondStage.y to y;
  }
}
