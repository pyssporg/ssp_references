package SignalDelayDetector {
  private import PysspCore::*;

  attribute def SignalDelayDetectorDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalDelayDetectorDefaultExperiment;

    part step : Step;
    part gain_a : Gain;
    part gain_b : Gain;
    part add : Add;
    connect step.y to gain_a.u;
    connect gain_a.y to gain_b.u;
    connect gain_b.y to add.u1;
    connect step.y to add.u2;
  }
}
