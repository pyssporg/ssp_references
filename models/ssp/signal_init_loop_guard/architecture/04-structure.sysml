package SignalInitLoopGuard {
  private import PysspCore::*;

  attribute def SignalInitLoopGuardDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalInitLoopGuardDefaultExperiment;

    part gain : LoopGain;
    part div : DivideGuard;
    connect gain.y to div.u;
    connect div.y to gain.u;
  }
}
