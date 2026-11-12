package SignalInitLoopGuard {
  private import PysspCore::*;

  attribute def LoopGainFmu :> FmuMetadata {
    attribute source = "models/fmu/LoopGain/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def DivideGuardFmu :> FmuMetadata {
    attribute source = "models/fmu/DivideGuard/fmu";
    attribute implementation = "CoSimulation";
  }

  part def LoopGain {
    attribute fmu_meta : LoopGainFmu;
    in port parameters : LoopGainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def DivideGuard {
    attribute fmu_meta : DivideGuardFmu;
    in port parameters : DivideGuardParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }
}
