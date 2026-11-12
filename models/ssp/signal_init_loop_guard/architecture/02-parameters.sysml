package SignalInitLoopGuard {
  private import PysspCore::*;

  attribute def ScenarioSet :> ParameterSet {
    attribute gain_k = 0.5;
    attribute gain_c = 10.0;  // loop excitation
    attribute div_c = 100.0;  // dividend
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }
}
