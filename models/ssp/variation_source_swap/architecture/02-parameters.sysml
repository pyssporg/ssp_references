package VariationSourceSwap {
  private import PysspCore::*;
  attribute def ScenarioSet :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 0.0;
    attribute startTime = 0.5;
    attribute amplitude = 2.0;
    attribute f = 1.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }
}
