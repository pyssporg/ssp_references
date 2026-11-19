package SignalNestedPassThrough {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def SignalNestedPassThroughDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  part def System :> SspModel {
    attribute defaults : SignalNestedPassThroughDefaultExperiment;

    out port y : RealSignal;
    part step : Step;
    part add : Add;
    part inner : Inner;
    connect step.y to inner.u;
    connect inner.v to add.u1;
    connect add.y to y;
  }
}
