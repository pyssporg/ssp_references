package SignalStepProduct {
  private import PysspCore::*;

  attribute def SignalStepProductDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalStepProductDefaultExperiment;

    part step : Step;
    part sine : Sine;
    part product : Product;
    connect step.y to product.u1;
    connect sine.y to product.u2;
  }
}
