package SignalStepAdd {
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def StepFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Step/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def AddFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Add/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Step {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port y : RealSignal;
  }

  part def Add {
    attribute fmu_meta : AddFmu;
    in port parameters : AddParameters;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }
}
