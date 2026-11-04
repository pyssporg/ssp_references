package VariationNested {
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute offset = 0.0;
    attribute startTime = 0.5;
    attribute gainK = 3.0;
    attribute stageK = 5.0;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }
}
