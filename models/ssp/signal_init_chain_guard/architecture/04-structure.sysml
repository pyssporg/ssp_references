package SignalInitChainGuard {
  private import PysspCore::*;

  attribute def SignalInitChainGuardDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalInitChainGuardDefaultExperiment;

    part source : Sine;
    part guard : InitGuard;
    part add : Add;
    connect source.y to guard.u;
    connect guard.y to add.u1;
  }
}
