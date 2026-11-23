package SignalSineGainAdd {
  private import PysspCore::*;

  attribute def SignalSineGainAddDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalSineGainAddDefaultExperiment;

    part sine : Sine;
    part step : Step;
    part gain : Gain;
    part add : Add;
    connect sine.y to gain.u;
    connect gain.y to add.u1;
    connect step.y to add.u2;
  }
}
