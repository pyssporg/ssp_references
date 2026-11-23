package SignalAlgebraicLoop {
  private import PysspCore::*;

  attribute def SignalAlgebraicLoopDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalAlgebraicLoopDefaultExperiment;

    part sine : Sine;
    part gain : Gain;
    part add : Add;
    connect sine.y to add.u1;
    connect gain.y to add.u2;
    connect add.y to gain.u;
  }
}
