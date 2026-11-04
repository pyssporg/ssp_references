package SignalStepProduct {
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute step_height = 1.0;
    attribute step_offset = 0.0;
    attribute step_startTime = 0.25;
    attribute sine_amplitude = 1.0;
    attribute sine_f = 1.0;
    attribute sine_offset = 0.0;
    attribute sine_phase = 0.0;
    attribute sine_startTime = 0.0;
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
