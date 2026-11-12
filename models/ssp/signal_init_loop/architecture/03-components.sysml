package SignalInitLoop {
  private import PysspCore::*;

  attribute def LoopGainFmu :> FmuMetadata {
    attribute source = "models/fmu/LoopGain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def LoopGain {
    attribute fmu_meta : LoopGainFmu;
    in port parameters : LoopGainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }
}
