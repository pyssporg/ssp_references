package SignalInitGuard {
  private import PysspCore::*;

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def InitGuardFmu :> FmuMetadata {
    attribute source = "models/fmu/InitGuard/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def AddFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Add/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Sine {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port y : RealSignal;
  }

  part def InitGuard {
    attribute fmu_meta : InitGuardFmu;
    in port u : RealSignal;
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
