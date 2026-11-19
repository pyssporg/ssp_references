package SignalNestedParameterBindings {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def SignalNestedParameterBindingsDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalNestedParameterBindingsDefaultExperiment;

    out port y : RealSignal;
    part step : Step;
    part add : Add;
    part inner : Inner;
    connect step.y to add.u1;
    connect inner.y to add.u2;
    connect add.y to y;
  }
}
