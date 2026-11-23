package SignalStepAdd {
  private import PysspCore::*;

  attribute def SignalStepAddDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalStepAddDefaultExperiment;

    part step_a : Step;
    part step_b : Step;
    part add : Add;
    connect step_a.y to add.u1;
    connect step_b.y to add.u2;
  }
}
