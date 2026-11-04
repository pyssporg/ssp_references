package Embrace {
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute 'pipeA.L' = 0.976535328081166;
    attribute 'pipeB.L' = 0.976535328081166;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.01;
  }
}
