package SignalInitLoop {
  private import PysspCore::*;

  attribute def ScenarioSet :> ParameterSet {
    attribute gain_a_k = 0.5;
    attribute gain_a_c = 10.0;  // loop excitation
    attribute gain_b_k = 0.5;
    attribute gain_b_c = 0.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }
}
