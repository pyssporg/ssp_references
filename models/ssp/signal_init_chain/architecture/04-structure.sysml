package SignalInitChain {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def SignalInitChainDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalInitChainDefaultExperiment;

    part source : Sine;
    part gain : Gain;
    part add : Add;
    connect source.y to gain.u;
    connect gain.y to add.u1;
  }
}
