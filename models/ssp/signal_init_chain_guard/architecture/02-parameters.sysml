package SignalInitChainGuard {
  private import PysspCore::*;

  attribute def ScenarioSet :> ParameterSet {
    attribute sine_amplitude = 0.5;
    attribute sine_f = 1.0;
    attribute sine_offset = 10.0;  // constant offset
    attribute sine_phase = 0.0;
    attribute sine_startTime = 0.0;
    attribute add_k1 = 1.0;
    attribute add_k2 = 0.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }
}
