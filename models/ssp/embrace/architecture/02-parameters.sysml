package Embrace {
  private import PysspCore::*;

  attribute def ScenarioSet :> ParameterSet {
    attribute 'pipeA.L' = 0.976535328081166;
    attribute 'pipeB.L' = 0.976535328081166;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.01;
  }
}
