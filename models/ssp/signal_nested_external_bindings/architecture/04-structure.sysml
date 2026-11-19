package SignalNestedExternalBindings {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def SignalNestedExternalBindingsDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalNestedExternalBindingsDefaultExperiment;

    out port y : RealSignal;
    part step : Step;
    part inner : Inner;
    connect step.y to y;
  }
}
