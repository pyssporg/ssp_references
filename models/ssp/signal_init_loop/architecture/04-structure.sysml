package SignalInitLoop {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def SignalInitLoopDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalInitLoopDefaultExperiment;

    part gain_a : LoopGain;
    part gain_b : LoopGain;
    connect gain_a.y to gain_b.u;
    connect gain_b.y to gain_a.u;
  }
}
